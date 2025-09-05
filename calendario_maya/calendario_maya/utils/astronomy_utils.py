import math
from datetime import date, datetime
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from astropy.time import Time
from functools import lru_cache

@dataclass
class CosmicCycle:
    name: str
    days: int
    frequency: float
    glyph_sequence: List[int]
    color: str  # Adicionado para integração com UI

class AstronomyUtils:
    # Constantes melhoradas
    GALACTIC_EPOCH = date(2012, 12, 21)
    EARTH_ORBITAL_PERIOD = 365.256  # dias (ano sidéreo)
    VENUS_SYNODIC_PERIOD = 583.92   # dias
    VENUS_ORBITAL_PERIOD = 224.701  # dias
    
    # Ciclos atualizados com informações completas
    CYCLES = {
        'tzolkin': CosmicCycle(
            name='Tzolk\'in',
            days=260,
            frequency=136.1,
            glyph_sequence=list(range(1, 261)),
            color='#4B0082'
        ),
        'venus': CosmicCycle(
            name='Venus',
            days=584,
            frequency=221.23,
            glyph_sequence=[3, 8, 11, 16, 19, 24],
            color='#E6E6FA'
        ),
        'galactic': CosmicCycle(
            name='Galáctico',
            days=26000,
            frequency=1.36,
            glyph_sequence=list(range(1, 26001)),
            color='#4682B4'
        )
    }

    @staticmethod
    @lru_cache(maxsize=128)  # Cache para melhor performance
    def angular_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calcula distância angular entre duas posições com validação"""
        try:
            ra1, dec1 = math.radians(pos1[0]), math.radians(pos1[1])
            ra2, dec2 = math.radians(pos2[0]), math.radians(pos2[1])
            
            # Evitar erros de arredondamento em acos
            angle = math.sin(dec1)*math.sin(dec2) + math.cos(dec1)*math.cos(dec2)*math.cos(ra1-ra2)
            angle = max(min(angle, 1), -1)  # Força dentro do domínio [-1, 1]
            
            return math.degrees(math.acos(angle))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid position data: {e}")

    @staticmethod
    def calculate_venus_energy(venus_radius: float, venus_phase: float) -> float:
        """Calcula energia de Vênus com parâmetros validados"""
        if not (0 <= venus_phase <= 1):
            raise ValueError("Venus phase must be between 0 and 1")
            
        solar_constant = 1361  # W/m²
        return (venus_radius * venus_phase * solar_constant) / 1000  # kW/m²

    @staticmethod
    def calculate_cosmic_data(target_date: Optional[date] = None) -> Dict[str, float]:
        """Calcula dados cósmicos com fallback seguro"""
        try:
            target_date = target_date or datetime.now().date()
            days_since_epoch = (target_date - AstronomyUtils.GALACTIC_EPOCH).days
            
            return {
                'earth_position': AstronomyUtils.calculate_orbital_position(
                    days_since_epoch, 
                    AstronomyUtils.EARTH_ORBITAL_PERIOD
                ),
                'venus_position': AstronomyUtils.calculate_orbital_position(
                    days_since_epoch, 
                    AstronomyUtils.VENUS_ORBITAL_PERIOD
                ),
                'galactic_progress': (days_since_epoch / AstronomyUtils.CYCLES['galactic'].days) * 100,
                'is_fallback': False
            }
        except Exception:
            # Fallback seguro
            return {
                'earth_position': 0.0,
                'venus_position': 0.0,
                'galactic_progress': 0.0,
                'is_fallback': True
            }

    @staticmethod
    def calculate_orbital_position(days: float, period: float) -> float:
        """Calcula posição orbital normalizada (0-360°) com validação"""
        if period <= 0:
            raise ValueError("Orbital period must be positive")
        return (days % period) / period * 360 % 360

    @staticmethod
    def date_to_jd(date_obj: Union[date, datetime]) -> float:
        """Conversão segura para Julian Date com suporte a datas antigas"""
        try:
            if hasattr(date_obj, 'toPyDate'):
                date_obj = date_obj.toPyDate()
            elif isinstance(date_obj, datetime):
                date_obj = date_obj.date()
                
            return Time(date_obj.isoformat()).jd
        except Exception:
            # Fallback para datas muito antigas (pré-4713 AEC)
            try:
                return 1721423.5 + (date_obj.year - 1) * 365.2425 + (date_obj.month - 1) * 30.44 + date_obj.day
            except Exception:
                return 2451545.0  # J2000 como fallback absoluto

    @staticmethod
    def generate_fibonacci_sequence(date_obj: date, length: int = 8) -> List[int]:
        """Gera sequência Fibonacci modificada para a data com validação"""
        if length <= 0:
            return []
            
        day_of_year = date_obj.timetuple().tm_yday
        sequence = []
        a, b = 0, 1
        
        for _ in range(length):
            a, b = b, a + b
            sequence.append((day_of_year + a) % 260)  # Ajusta para ciclo Tzolk'in
            
        return sequence

    @staticmethod
    def calculate_alignment(cycle_type: str, current_position: float) -> Dict:
        """Calcula próximos alinhamentos com validação de entrada"""
        cycle = AstronomyUtils.CYCLES.get(cycle_type.lower())
        if not cycle:
            raise ValueError(f"Ciclo desconhecido: {cycle_type}. Opções válidas: {list(AstronomyUtils.CYCLES.keys())}")

        fib_seq = [8, 13, 21, 34, 55, 89]  # Números de Fibonacci relevantes
        
        return {
            'cycle': cycle.name,
            'current_glyph': cycle.glyph_sequence[int(current_position) % len(cycle.glyph_sequence)],
            'next_alignments': sorted(
                (int(current_position) + fib) % cycle.days
                for fib in fib_seq
            ),
            'resonance_frequencies': [cycle.frequency * (fib/34) for fib in fib_seq],
            'color': cycle.color  # Para integração com UI
        }

    @staticmethod
    def find_cross_cycle_alignments(max_alignments: int = 5) -> List[Dict]:
        """Encontra alinhamentos entre ciclos com limite de resultados"""
        alignments = []
        cycles = list(AstronomyUtils.CYCLES.values())
        
        for i in range(len(cycles)):
            for j in range(i+1, len(cycles)):
                cycle1, cycle2 = cycles[i], cycles[j]
                common_days = AstronomyUtils.lcm(cycle1.days, cycle2.days)
                
                alignments.append({
                    'cycles': f"{cycle1.name}-{cycle2.name}",
                    'alignment_days': [
                        (common_days // cycle1.days) * k 
                        for k in range(1, max_alignments+1)
                    ],
                    'harmonic_frequency': (cycle1.frequency + cycle2.frequency)/2,
                    'color1': cycle1.color,
                    'color2': cycle2.color
                })
        
        return alignments

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calcula mínimo múltiplo comum com validação"""
        if a == 0 or b == 0:
            return 0
        return abs(a*b) // math.gcd(a, b)

    @staticmethod
    def get_current_cycle_positions(date_obj: Optional[date] = None) -> Dict[str, int]:
        """Retorna posições atuais em todos os ciclos com data opcional"""
        date_obj = date_obj or datetime.now().date()
        day_of_year = date_obj.timetuple().tm_yday
        
        return {
            'tzolkin': (day_of_year + 120) % 260,
            'venus': (day_of_year * AstronomyUtils.VENUS_SYNODIC_PERIOD // 365) % AstronomyUtils.VENUS_SYNODIC_PERIOD,
            'galactic': (date_obj.year - AstronomyUtils.GALACTIC_EPOCH.year) % 26000
        }

    @staticmethod
    def normalize_angle(angle: float) -> float:
        """Normaliza ângulo para 0-360 graus"""
        return angle % 360

    @staticmethod
    def calculate_orbital_velocity(semi_major_axis: float, mass: float = 1.0) -> float:
        """Calcula velocidade orbital em km/s"""
        G = 6.67430e-11  # Constante gravitacional
        return math.sqrt(G * mass / (semi_major_axis * 1.496e8))  # Converte UA para km