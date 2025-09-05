from datetime import date, datetime, timedelta
from typing import Dict, Any
import numpy as np

from calendario_maya.constants.astronomia import (
    EARTH_ORBITAL_PERIOD,
    VENUS_ORBITAL_PERIOD,
    GALACTIC_YEAR_DAYS
)
from calendario_maya.constants.fisica import (
    VELOCIDADE_LUZ,
    ANO_LUZ,
    MASSA_SOLAR,
    VENUS_RADIUS,
    GALACTIC_CENTER_COORDS
)

class MayanAstronomy:
    def __init__(self, connector=None):
        self.connector = connector
        self.set_tikal_location()
        self.VENUS_SYNODIC = 583.92
        self.GALACTIC_CENTER = GALACTIC_CENTER  # Definir como atributo
        self.REFERENCE_DATE = REFERENCE_DATE    # Definir como atributo
        self._cache = {
            'venus': {},
            'cosmic': {},
            'galactic': {}
        }

    def set_tikal_location(self) -> None:
        """Configuração precisa do observador em Tikal"""
        self.observer.lat = '17.222'    # Latitude de Tikal
        self.observer.long = '-89.624'  # Longitude de Tikal
        self.observer.elevation = 200   # Elevação em metros
        self.observer.pressure = 0      # Sem correção atmosférica
        self.observer.horizon = '-0:34' # Horizonte astronômico
        self.observer.temp = 25         # Temperatura em °C

    def calculate_galactic_venus_cycles(self, date_obj: date) -> Dict[str, Any]:
        """Calcula ciclos de Vênus com tratamento robusto de erros"""
        try:
            if date_obj in self._cache['galactic']:
                return self._cache['galactic'][date_obj]
            
            self.observer.date = date_obj
            venus = ephem.Venus()
            venus.compute(self.observer)
            
            venus_ra = degrees(venus.ra)
            venus_dec = degrees(venus.dec)
            
            angular_dist = self._angular_distance(
                (venus_ra, venus_dec),
                GALACTIC_CENTER
            )
            
            days_since_2012 = (date_obj - REFERENCE_DATE).days
            venus_cycles = days_since_2012 / self.VENUS_SYNODIC
            
            result = {
                'date': date_obj.isoformat(),
                'angular_dist_gc': angular_dist,
                'venus_phase': degrees(venus.phase),
                'cycles_since_2012': venus_cycles,
                'energy_level': self._calculate_venus_energy(venus)
            }
            
            self._cache['galactic'][date_obj] = result
            return result
            
        except Exception as e:
            return {
                'date': date_obj.isoformat(),
                'error': str(e),
                'fallback_data': self._get_fallback_venus_data(date_obj)
            }

    def _get_fallback_venus_data(self, date_obj):
        """Dados básicos quando cálculos precisos falham"""
        days_since_2012 = (date_obj - REFERENCE_DATE).days
        return {
            'angular_dist_gc': (days_since_2012 % 584) / 584 * 360,
            'venus_phase': (days_since_2012 % 584) / 584,
            'is_fallback': True
        }

    def get_cosmic_calendar(self, date_obj: date) -> Dict[str, Any]:
        return {
            'date': date_obj.isoformat(),
            'mayan_calendar': cosmic_time,
            'venus_cycles': venus_data,
            'harmonic_convergence': self._harmonic_convergence(date_obj),
            'energy_matrix': self.get_venus_matrix(date_obj)
        }

    def _harmonic_convergence(self, date_obj: date) -> float:
        # Ciclos normalizados
        maya_cycle = (days_since_2012 % CICLO_MAIA) / CICLO_MAIA
        venus_cycle = (days_since_2012 % self.VENUS_SYNODIC) / self.VENUS_SYNODIC
        galactic_cycle = self._galactic_year_progress(date_obj)
        
        # Fator de convergência (0-1)
        return (1 - abs(maya_cycle - venus_cycle)) * (1 - abs(venus_cycle - galactic_cycle))

    def generate_venus_galactic_chart(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Gera dados para gráfico da relação Vênus-Galáxia
        no período especificado
        """
        current_date = start_date
        delta = timedelta(days=1)
        chart_data = []
        
        while current_date <= end_date:
            data = self.calculate_galactic_venus_cycles(current_date)
            if 'error' not in data:
                chart_data.append({
                    'date': current_date.isoformat(),
                    'angular_dist': data['angular_dist_gc'],
                    'energy': data['energy_level'],
                    'harmonic': self._harmonic_convergence(current_date)
                })
            current_date += delta
        
        return {
            'metadata': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'venus_cycles': len(chart_data)/self.VENUS_SYNODIC
            },
            'data_points': chart_data
        }

    def get_significant_dates(self, years: int = 10) -> Dict[str, Any]:
        """
        Encontra datas significativas nos próximos anos onde:
        - Vênus está alinhado com centro galáctico
        - Coincide com ciclos maias importantes
        - Altos níveis de convergência harmônica
        """
        end_date = datetime.now().date() + timedelta(days=365*years)
        significant_dates = []
        
        # Verifica cada dia do ciclo de Vênus
        venus_days = int(years * 365 / self.VENUS_SYNODIC)
        for i in range(venus_days):
            check_date = datetime.now().date() + timedelta(days=i * self.VENUS_SYNODIC)
            data = self.calculate_galactic_venus_cycles(check_date)
            
            if data['angular_dist_gc'] < 5:  # Alinhamento próximo
                cosmic = self.get_cosmic_time(check_date)
                harmonic = self._harmonic_convergence(check_date)
                
                if harmonic > 0.8:  # Alta convergência
                    significant_dates.append({
                        'date': check_date.isoformat(),
                        'angular_dist': data['angular_dist_gc'],
                        'harmonic': harmonic,
                        'mayan_date': cosmic,
                        'energy': data['energy_level']
                    })
        
        return {
            'analysis_period': f"{years} years",
            'significant_dates': sorted(significant_dates, key=lambda x: x['harmonic'], reverse=True),
            'strongest_alignment': max(significant_dates, key=lambda x: x['harmonic']) if significant_dates else None
        }

    def get_venus_matrix(self, date_obj: date) -> np.ndarray:
        matrix = np.zeros((13, 20))
        for i in range(13):
            for j in range(20):
                # Combina ciclo de Vênus com harmônicos 13 e 20
                matrix[i][j] = (cycles + (i+1)*(j+1)/260) % 1
                
        return matrix
    
    def calculate_cosmic_data(target_date):
        try:
            # Converter para date se for datetime
            if hasattr(target_date, 'date'):
                target_date = target_date.date()
        
            # Cálculos modernos (pós-1582)
            if target_date.year >= 1582:
                jd = julian_day(target_date.year, target_date.month, target_date.day)
                earth_pos = calculate_earth_position(jd)
                venus_pos = calculate_venus_position(jd)
                galactic_angle = calculate_galactic_angle(jd)
        
                base_date = date(2012, 12, 21)
                days_passed = (target_date - base_date).days
                galactic_progress = (days_passed / 25920) * 100
        
                return {
                    'earth_position': earth_pos,
                    'venus_position': venus_pos,
                    'galactic_angle': galactic_angle,
                    'galactic_progress': galactic_progress
                }
            else:
                # Cálculos aproximados para datas antigas
                days_since_2012 = (target_date - date(2012, 12, 21)).days
                return {
                    'earth_position': (days_since_2012 % 365) * 0.9856,
                    'venus_position': (days_since_2012 % 584) * 0.616,
                    'galactic_angle': 0,
                    'galactic_progress': (days_since_2012 / 25920) * 100
                }
        
        except Exception as e:
            print(f"Erro em calculate_cosmic_data: {str(e)}")
            return None

    def _calculate_ancient_data(self, year):
        """Cálculos aproximados para anos BCE"""
        try:
            # Converter ano BCE para ano astronômico (1 BCE = 0, 2 BCE = -1, etc.)
            astro_year = year if year > 0 else (year * -1) + 1
        
            return {
                'earth_position': (astro_year * 0.9856) % 360,  # Aproximação
                'venus_position': (astro_year * 1.602) % 360,
                'galactic_angle': (astro_year * 0.014) % 360,
                'julian_day': 0
            }
        except Exception as e:
            print(f"Erro em _calculate_ancient_data: {str(e)}")
            return None
        
def get_constellation_positions(date=None, hemisphere="Norte"):
    """Versão simplificada para testes"""
    constellations = {
        "Ursa Maior": {
            "stars": [
                {"name": "Dubhe", "ra": 165, "dec": 56, "magnitude": 1.8},
                {"name": "Merak", "ra": 155, "dec": 49, "magnitude": 2.4}
            ],
            "lines": [(0, 1)]
        }
    }
    
    if hemisphere == "Norte":
        return constellations
    return {}
        