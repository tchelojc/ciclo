import logging
import ephem
import numpy as np
from datetime import datetime, date, timedelta
from datetime import date as datetime_date
from math import degrees, radians, acos, sin, cos, sqrt
from typing import Dict, Any, Optional, Tuple
import os
from abc import ABC, abstractmethod
from pathlib import Path
from astropy.time import Time

from .date_utils import safe_date_convert, MAYA_EPOCH, GALACTIC_EPOCH
from calendario_maya.utils.astronomy_utils import AstronomyUtils
from calendario_maya.utils.prophecy_manager import ProphecyManager
from calendario_maya.constants.astronomia import (
    PERIODOS_ORBITAIS,
    EARTH_ORBITAL_PERIOD,
    VENUS_ORBITAL_PERIOD,
    GALACTIC_YEAR_DAYS
)
from calendario_maya.core.data_manager import DataManager
from calendario_maya.constants.fisica import (
    VELOCIDADE_LUZ,
    CONSTANTE_SOLAR,
    VENUS_RADIUS,
    ANO_GALACTICO,
    CICLO_MAIA,
    FATOR_COSMICO
)

# Definir constantes específicas
GALACTIC_EPOCH = datetime(2012, 12, 21).date()
VENUS_SYNODIC = 583.92  # Ciclo sinódico de Vênus em dias
AU_TO_KM = 149597870.7  # 1 UA em km
SOLAR_GM = 1.32712440018e20  # Parâmetro gravitacional do Sol (km³/s²)

# Modificar a classe MayanAstronomy para incluir o ProphecyManager
class MayanAstronomy:
    def __init__(self, connector=None):
        self.connector = connector
        self.start_long_count = 584283  # JDN para 11 de agosto de -3113
        self.observer = ephem.Observer()
        self.set_tikal_location()
        self.MAYA_EPOCH = date(3114, 8, 11)
        self.REFERENCE_DATE = datetime(2012, 12, 21).date()
        self.GALACTIC_CENTER = (266.4, -28.9)
        self.earth_period = EARTH_ORBITAL_PERIOD  # 365.256 dias
        self.venus_period = VENUS_ORBITAL_PERIOD  # 224.7 dias, vindo de calendario_maya/constants/astronomia.py
        self.last_venus_perihelion = Time("2022-10-22").jd
        self.last_earth_perihelion = Time("2023-01-04").jd
        self._cache = {
            'galactic': {}, 
            'planetary': {},
            'heliocentric': {}
        }
        self.logger = logging.getLogger(__name__)

        # Inicializa o gerenciador de profecias
        self.prophecy_manager = ProphecyManager(
            connector.get_data_path() if connector else None
        )

    # Métodos de configuração
    def set_tikal_location(self):
        """Configura o observador em Tikal"""
        self.observer.lat = '17.222'
        self.observer.long = '-89.624'
        self.observer.elevation = 200
        self.observer.pressure = 0
        self.observer.horizon = '-0:34'
        
    def date_to_jd(self, date):
        """Conversão segura para datas antigas"""
        try:
            if hasattr(date, 'toPyDate'):
                date = date.toPyDate()
        
            # Usa astropy para lidar com datas antigas
            return Time(f"{date.year}-{date.month}-{date.day}", format='iso').jd
        except:
            # Fallback para datas muito antigas
            base_jd = 1721423.5  # JD para 1 CE
            days_per_year = 365.2425
            return base_jd + (date.year - 1) * days_per_year
    
    def calculate_orbital_angle(self, jd, body):
        """Calcula ângulo orbital baseado em JD"""
        if body.lower() == 'venus':
            days_since_perihelion = jd - self.last_venus_perihelion
            period = self.venus_period
        else:  # Terra
            days_since_perihelion = jd - self.last_earth_perihelion
            period = self.earth_period
        
        # Normaliza para evitar valores negativos
        days_since_perihelion = days_since_perihelion % period
        return (days_since_perihelion / period) * 360

    def earth_heliocentric_position(self, date_obj):
        """Calcula a posição heliocêntrica da Terra"""
        try:
            date_norm = self._normalize_date(date_obj)
            self.observer.date = date_norm
        
            # Usando posição do Sol (geocêntrica) para inferir posição da Terra
            sun = ephem.Sun()
            sun.compute(self.observer)
        
            # A posição heliocêntrica da Terra é oposta à posição geocêntrica do Sol
            helio_lon = (degrees(sun.ra) + 180) % 360
            helio_lat = -degrees(sun.dec)
        
            return {
                'longitude': helio_lon,
                'latitude': helio_lat,
                'distance': 1.0,  # Assumindo 1 UA como aproximação
                'velocity': 29.78,  # km/s
                'is_fallback': False
            }
        
        except Exception as e:
            self.logger.error(f"Erro cálculo heliocêntrico: {str(e)}")
            # Fallback simples
            days_since_epoch = (date_norm - self.REFERENCE_DATE).days
            return {
                'longitude': (days_since_epoch / 365.256 * 360) % 360,
                'latitude': 0.0,
                'distance': 1.0,
                'velocity': 29.78,
                'is_fallback': True
            }

    def _calculate_orbital_velocity(self, distance_au):
        """Calcula velocidade orbital baseada na distância ao Sol"""
        # Constante gravitacional do Sol (km^3/s^2)
        GM = 1.32712440018e20  
        # Converter UA para km
        r = distance_au * 1.496e8  
        return sqrt(GM / r) / 1000  # km/s

    def get_planetary_positions(self, target_date):
        """Retorna posições planetárias padronizadas"""
        try:
            # Normaliza a data de entrada
            if hasattr(target_date, 'toPyDate'):
                py_date = target_date.toPyDate()
            elif isinstance(target_date, datetime):
                py_date = target_date.date()
            else:
                py_date = target_date

            # Calcula dias desde uma data de referência
            days_since_ref = (py_date - date(2012, 12, 21)).days
        
            # Calcula posições normalizadas (0-360°)
            earth_pos = (days_since_ref % self.earth_period) / self.earth_period * 360
            venus_pos = (days_since_ref % self.venus_period) / self.venus_period * 360

            return {
                'earth': {'position': earth_pos % 360},  # Garante 0-360°
                'venus': {'position': venus_pos % 360}   # Garante 0-360°
            }
        except Exception as e:
            self.logger.error(f"Erro cálculo posições planetárias: {e}")
            # Fallback básico
            return {
                'earth': {'position': 0},
                'venus': {'position': 0}
            }
    
    def _calculate_heliocentric_position(self, jd, body):
        """Cálculo simplificado de posição heliocêntrica"""
        # Implementação real usaria efemérides precisas
        if body == 'earth':
            return ((jd % 365.256) / 365.256) * 360
        else:  # Vênus
            return ((jd % 224.701) / 224.701) * 360
        
    def get_local_glyph_meaning(self, date_obj, latitude, longitude):
        """Calcula o significado local baseado na posição geográfica"""
        try:
            # Calcula fatores locais
            solar_angle = self._calculate_solar_angle(date_obj, latitude, longitude)
            magnetic_var = self._get_magnetic_variation(latitude, longitude)
        
            # Obtém o glifo do dia
            tzolkin_day = self._calculate_tzolkin_day_number(date_obj)
            glyph_data = self.connector.tzolk_data['nahuales'][tzolkin_day % 20]
        
            # Ajusta o significado baseado nos fatores locais
            local_meaning = {
                'base': glyph_data['significado_tradicional'],
                'solar_influence': self._interpret_solar_angle(solar_angle),
                'magnetic_influence': self._interpret_magnetic(magnetic_var),
                'energy_factor': (solar_angle + magnetic_var) % 1
            }
            return local_meaning
        except Exception as e:
            self.logger.error(f"Erro cálculo local: {e}")
            return {'error': 'Dados locais indisponíveis'}

    def calculate_galactic_venus_cycles(self, date_obj) -> Dict[str, Any]:
        """Calcula ciclos de Vênus em relação ao centro galáctico"""
        date_norm = self._normalize_date(date_obj)
        if date_norm in self._cache['galactic']:
            return self._cache['galactic'][date_norm]
        
        try:
            self.observer.date = date_norm
            venus = ephem.Venus()
            venus.compute(self.observer)
            
            result = {
                'date': date_norm.isoformat(),
                'angular_dist_gc': self._angular_distance(
                    (degrees(venus.ra), degrees(venus.dec)),
                    self.GALACTIC_CENTER
                ),
                'venus_phase': degrees(venus.phase),
                'next_alignment': self._next_venus_alignment(date_norm)
            }
            
            self._cache['galactic'][date_norm] = result
            return result
        except Exception as e:
            return self._get_fallback_venus_data(date_norm)

    def _normalize_date(self, date_input):
        """Converte vários formatos de data para date"""
        if isinstance(date_input, datetime):
            return date_input.date()
        if hasattr(date_input, 'toPyDate'):  # QDate
            return date_input.toPyDate()
        if isinstance(date_input, date):  # Já é date
            return date_input
        raise ValueError(f"Tipo de data não suportado: {type(date_input)}")

    def _calculate_earth_position(self, days_since: int) -> Dict[str, Any]:
        """Calcula posição da Terra"""
        position = (days_since % EARTH_ORBITAL_PERIOD) / EARTH_ORBITAL_PERIOD * 360
        return {
            'position': position % 360,
            'cycle': EARTH_ORBITAL_PERIOD,
            'phase': (days_since % 365.24219) / 365.24219
        }

    def _calculate_venus_position(self, days_since: int) -> Dict[str, Any]:
        """Calcula posição de Vênus"""
        position = (days_since % VENUS_ORBITAL_PERIOD) / VENUS_ORBITAL_PERIOD * 360
        return {
            'position': position % 360,
            'cycle': VENUS_ORBITAL_PERIOD,
            'phase': (days_since % 583.92) / 583.92
        }

    def _angular_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calcula distância angular entre duas posições"""
        ra1, dec1 = radians(pos1[0]), radians(pos1[1])
        ra2, dec2 = radians(pos2[0]), radians(pos2[1])
        return degrees(acos(sin(dec1)*sin(dec2) + cos(dec1)*cos(dec2)*cos(ra1-ra2)))

    def _get_fallback_positions(self, date_obj):
        """Dados de fallback para quando cálculos precisos falham"""
        return {
            'terra': {'position': 0, 'cycle': 365.256, 'phase': 0},
            'venus': {'position': 0, 'cycle': 224.701, 'phase': 0},
            'sol': {'position': 0, 'cycle': 365.256, 'phase': 0}
        }

    def _calculate_keplerian_position(self, days, elements, period):
        """Calcula posição usando equações de Kepler"""
        # 1. Anomalia média
        n = 2 * math.pi / period  # Movimento médio
        M = n * days
        
        # 2. Solucionar equação de Kepler (M = E - e*sinE)
        E = self._solve_kepler(M, elements['excentricidade'])
        
        # 3. Calcular anomalia verdadeira
        v = 2 * math.atan(
            math.sqrt((1 + elements['excentricidade']) / 
                     (1 - elements['excentricidade'])) * math.tan(E/2)
        )
        
        return degrees(v) % 360

    def _solve_kepler(self, M, e, epsilon=1e-6):
        """Solução iterativa para equação de Kepler"""
        E = M
        while True:
            delta = E - e * math.sin(E) - M
            if abs(delta) < epsilon:
                return E
            E -= delta / (1 - e * math.cos(E))        

    def safe_create_date(self, year, month=6, day=15):
        """Cria datas mesmo para anos BCE"""
        try:
            if year <= 0:
                return date(abs(year) + 1, month, day)
            return date(year, month, day)
        except Exception as e:
            self.logger.error(f"Erro criando data: {e}")
            return self.GALACTIC_EPOCH  # Fallback
        
    def _create_logger(self):
        import logging
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.NullHandler())
        return logger

    def _calculate_sun_position(self, days_since: int) -> Dict[str, Any]:
        """Calcula posição do Sol"""
        position = (days_since % EARTH_ORBITAL_PERIOD) / EARTH_ORBITAL_PERIOD * 360
        return {
            'position': position % 360,
            'cycle': EARTH_ORBITAL_PERIOD,
            'phase': (days_since % 365.24219) / 365.24219
        }

    def _next_venus_alignment(self, date_norm):
        """Calcula próximo alinhamento de Vênus"""
        try:
            self.observer.date = date_norm
            venus = ephem.Venus()
            venus.compute(self.observer)
            next_conjunction = ephem.next_primary_junction(venus)
            return next_conjunction.datetime().date().isoformat()
        except Exception:
            return "Desconhecido"
        
    def calcular_posicao_orbital_real(self, date_obj: date) -> Dict[str, float]:
        """
        Calcula a posição orbital heliocêntrica REAL para Terra e Vênus.
        Esta função usa o período orbital sidéreo e não reseta anualmente.
        """
        from calendario_maya.constants.fisica import POSICOES_PLANETARIAS

        # Data de referência para o início do cálculo (solstício de 2012)
        # Pode-se ajustar para um alinhamento conhecido para maior precisão (ex: periélio)
        epoch_date = self.GALACTIC_EPOCH # 21/12/2012

        days_since_epoch = (self._normalize_date(date_obj) - epoch_date).days

        # Períodos orbitais corretos
        periodo_terra = POSICOES_PLANETARIAS['terra']['orbital_period']
        periodo_venus = POSICOES_PLANETARIAS['venus']['orbital_period']

        # Cálculo do ângulo total percorrido desde a época
        graus_totais_terra = (days_since_epoch / periodo_terra) * 360.0
        graus_totais_venus = (days_since_epoch / periodo_venus) * 360.0

        # Posição atual no círculo de 0-360 graus
        posicao_terra = graus_totais_terra % 360.0
        posicao_venus = graus_totais_venus % 360.0
        
        return {
            'terra': posicao_terra,
            'venus': posicao_venus
        }
    
    def galactic_year_progress(self, date):
        """Progresso no ano galáctico (ciclo de ~26,000 anos)"""
        try:
            if hasattr(date, 'toPyDate'):
                date = date.toPyDate()
            elif isinstance(date, datetime):
                date = date.date()
            
            galactic_year_days = 26000 * 365.25  # dias
            days_since_epoch = (date - self.REFERENCE_DATE).days
            return (days_since_epoch % galactic_year_days) / galactic_year_days * 100
        except Exception as e:
            self.logger.error(f"Erro cálculo ano galáctico: {e}")
            return 0.0

    def venus_phase_angle(self, date):
        """Cálculo do ângulo de fase de Vênus"""
        try:
            if hasattr(date, 'toPyDate'):
                date = date.toPyDate()
            elif isinstance(date, datetime):
                date = date.date()
            
            days_since_epoch = (date - self.REFERENCE_DATE).days
            phase = (days_since_epoch % VENUS_SYNODIC) / VENUS_SYNODIC * 360
            return round(phase, 2)
        except Exception as e:
            self.logger.error(f"Erro cálculo fase Vênus: {e}")
            return 0.0

    def calculate_baktun(self, date):
        """Calcula o baktun atual corrigido"""
        try:
            if hasattr(date, 'toPyDate'):
                date = date.toPyDate()
            elif isinstance(date, datetime):
                date = date.date()
        
            # Dias desde a época maia (11/08/3114 AEC)
            days_since_epoch = (date - self.MAYA_EPOCH).days
        
            # 1 baktun = 144000 dias
            # Já estamos no 13º baktun (começou em 21/12/2012)
            baktun = 13 + (days_since_epoch - 1872000) / 144000
            return round(baktun, 2)
        except Exception as e:
            self.logger.error(f"Erro cálculo baktun: {e}")
            return 13.0  # Fallback para o 13º baktun
    
    def _get_fallback_cosmic_data(self):
        """Dados de fallback quando o cálculo principal falha"""
        return {
            'baktun': 13,
            'sun_position': 0,
            'earth_position': 0,
            'venus_position': 0,
            'galactic_progress': 0,
            'is_aligned': False,
            'new_cycle': True
        }

    def calculate_venus_alignment(date_obj):
        """Calcula o próximo alinhamento Terra-Vênus"""
        # Ciclo sinódico de Vênus (aproximadamente 584 dias)
        venus_cycle = 583.92
        # Data do último alinhamento conhecido
        last_alignment = datetime(2022, 10, 22)
        days_since = (date_obj - last_alignment).days
        cycles = days_since / venus_cycle
        next_align = last_alignment + timedelta(days=venus_cycle * math.ceil(cycles))
        return next_align

    def get_cosmic_calendar(self, date_obj):
        """Retorna todos os dados cósmicos integrados"""
        try:
            days_since = (self._normalize_date(date_obj) - self.REFERENCE_DATE).days
            return {
                'baktun': self.calculate_baktun(date_obj),
                'sun_position': self._calculate_sun_position(days_since)['position'],
                'earth_position': self._calculate_earth_position(days_since)['position'],
                'venus_position': self._calculate_venus_position(days_since)['position'],
                'galactic_progress': (days_since / GALACTIC_YEAR_DAYS) * 100,
                'is_aligned': self._check_galactic_alignment(date_obj)
            }
        except Exception as e:
            self.logger.error(f"Erro no calendário cósmico: {e}")
            return self._get_fallback_cosmic_data()

    def check_galactic_alignment(self, date_obj: date) -> bool:
        """Verifica alinhamentos com margem de 5 graus"""
        angle = self.galactic_sun_angle(date_obj)
        return any(abs(angle - x) < 5 or abs(angle - (360 - x)) < 5 
               for x in [0, 90, 180, 270])

    def get_timeline_data(self, date_obj):
        """Dados completos para exibição na timeline"""
        cosmic = self.get_cosmic_calendar(date_obj)
        venus = self.calculate_galactic_venus_cycles(date_obj)
    
        return {
            'baktun': cosmic.get('baktun', 0),
            'venus_phase': venus.get('venus_phase', 0),
            'galactic_year': cosmic.get('galactic_progress', 0),
            'is_aligned': cosmic.get('is_aligned', False),
            'harmonic': self._harmonic_convergence(date_obj)
        }
        
    def get_astronomy_data(self, date):
        """Obtém dados com fallback hierárquico"""
        try:
            if self.advanced_astronomy_available:
                return self.mayan_astronomy.get_cosmic_calendar(date)
            return self.basic_astronomy.get_cosmic_calendar(date)
        except Exception:
            return {
                'baktun': ((date - date(2012, 12, 21)).days / 144000) + 13,
                'venus_phase': ((date - date(2012, 12, 21)).days % 584) / 584,
                'status': 'fallback'
            }
            
    def generate_localized_content(self, date, location):
        """Combina dados astronômicos com localização"""
        astronomy_data = self.get_astronomy_data(date)
        glyph = self.get_glyph_for_date(date)
    
        return {
            **astronomy_data,
            'local_meaning': self.calculate_local_meaning(glyph, location),
            'energy_matrix': self.calculate_energy_matrix(date, location)
        }
        
    def _next_venus_galactic_alignment(self, date_obj: date) -> Dict[str, Any]:
        """Calcula o próximo alinhamento significativo de Vênus"""
        next_conjunctions = []
        for i in range(3):  # Próximos 3 alinhamentos
            next_date = date_obj + timedelta(days=i * self.VENUS_SYNODIC)
            self.observer.date = next_date
            venus = ephem.Venus()
            venus.compute(self.observer)
            
            angular_dist = self._angular_distance(
                (degrees(venus.ra), degrees(venus.dec)),
                self.GALACTIC_CENTER
            )
            
            if angular_dist < 5:  # Considera alinhamento abaixo de 5 graus
                next_conjunctions.append({
                    'date': next_date.isoformat(),
                    'angular_distance': angular_dist,
                    'energy_level': self._calculate_venus_energy(venus)
                })
        
        return {
            'next_alignments': next_conjunctions,
            'current_cycle': self._current_venus_cycle(date_obj)
        }

    def _current_venus_cycle(self, date_obj: date) -> Dict[str, Any]:
        """Detalhes do ciclo atual de Vênus"""
        days_since_2012 = (date_obj - self.REFERENCE_DATE).days
        current_cycle = days_since_2012 / self.VENUS_SYNODIC
        
        return {
            'cycle_number': int(current_cycle),
            'cycle_progress': current_cycle % 1,
            'days_to_next': int(self.VENUS_SYNODIC * (1 - (current_cycle % 1)))
        }

    def _get_fallback_venus_data(self, date_obj):
        """Dados básicos quando cálculos precisos falham"""
        days_since_2012 = (date_obj - self.REFERENCE_DATE).days
        return {
            'angular_dist_gc': (days_since_2012 % 584) / 584 * 360,
            'venus_phase': (days_since_2012 % 584) / 584,
            'is_fallback': True
        }

    def _quantum_phase(self, cycles: float) -> float:
        """Fase quântica baseada em ciclos de Vênus"""
        return (cycles * CICLO_MAIA / self.VENUS_SYNODIC) % 1

    def get_venus_matrix(self, date_obj: date) -> np.ndarray:
        """Matriz quântica 13x20 aprimorada"""
        try:
            date_obj = self._normalize_date(date_obj)
            cycles = self.calculate_galactic_venus_cycles(date_obj).get('cycles_since_2012', 0)
            
            matrix = np.zeros((13, 20))
            for i in range(13):
                for j in range(20):
                    matrix[i][j] = (cycles + (i+1)*(j+1)/260) % 1
                    
            return matrix
        except Exception as e:
            self.logger.error(f"Erro em get_venus_matrix: {str(e)}")
            return np.zeros((13, 20))

    def _harmonic_convergence(self, date_obj: date) -> float:
        """Calcula o fator de convergência harmônica"""
        try:
            days_since_2012 = (date_obj - self.REFERENCE_DATE).days
            
            maya_cycle = (days_since_2012 % CICLO_MAIA) / CICLO_MAIA
            venus_cycle = (days_since_2012 % self.VENUS_SYNODIC) / self.VENUS_SYNODIC
            galactic_cycle = self._galactic_year_progress(date_obj)
            
            return (1 - abs(maya_cycle - venus_cycle)) * (1 - abs(venus_cycle - galactic_cycle))
        except Exception:
            return 0.0

    def _get_mayan_date(self, date_obj: date) -> Dict[str, Any]:
        """Retorna a data no calendário maia"""
        # Implementação simplificada - pode ser expandida
        days_since_2012 = (date_obj - self.REFERENCE_DATE).days
        return {
            'long_count': days_since_2012,
            'tzolkin': (days_since_2012 % 260) + 1,
            'haab': (days_since_2012 % 365) + 1
        }
    
    def handle_ancient_dates(year):
        """Normaliza anos muito antigos"""
        if year <= 0:
            return 2012  # Fallback para anos BCE
        return year
    
    def get_prophecies(self, start_date, end_date):
        """Obtém profecias para o período"""
        if not self._loaded:
            self.events = self.generate_cyclic_prophecies(
                start_date, 
                (end_date - start_date).days // 365
            )
        return [e for e in self.events if start_date <= e['date'] <= end_date]
    
# Em utils/mayan_astronomy.py
class HeliocentricReference:
    def __init__(self):
        # Elementos orbitais (simplificados)
        self.earth_elements = {
            'perihelion_jd': Time("2023-01-04").jd,
            'orbital_period': 365.256,
            'eccentricity': 0.0167
        }
        
        self.venus_elements = {
            'perihelion_jd': Time("2022-10-22").jd,
            'orbital_period': 224.701,
            'eccentricity': 0.0067
        }
    
    def get_heliocentric_position(self, jd, body):
        """Retorna posição heliocêntrica em graus"""
        elements = self.earth_elements if body == 'earth' else self.venus_elements
        days_since_perihelion = (jd - elements['perihelion_jd']) % elements['orbital_period']
        
        # Cálculo simplificado da anomalia média
        mean_anomaly = (360 * days_since_perihelion) / elements['orbital_period']
        
        # Aproximação para anomalia verdadeira (ignorando excentricidade para simplificar)
        return mean_anomaly % 360