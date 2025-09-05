import math
from datetime import date, datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CosmicCycle:
    name: str
    days: int
    frequency: float
    glyph_sequence: List[int]

CYCLES = {
    'tzolkin': CosmicCycle('Tzolk\'in', 260, 136.1, list(range(1, 261))),
    'venus': CosmicCycle('Venus', 584, 221.23, [3, 8, 11, 16, 19, 24]),
    'galactic': CosmicCycle('Galáctico', 26000, 1.36, list(range(1, 26001)))
}

class AstronomyUtils:
    @staticmethod
    def angular_distance(pos1, pos2):
        """Calcula distância angular entre duas posições"""
        ra1, dec1 = math.radians(pos1[0]), math.radians(pos1[1])
        ra2, dec2 = math.radians(pos2[0]), math.radians(pos2[1])
        return math.degrees(math.acos(
            math.sin(dec1)*math.sin(dec2) + 
            math.cos(dec1)*math.cos(dec2)*math.cos(ra1-ra2)
        ))

    @staticmethod    
    def calculate_venus_energy(venus):
        """Calcula energia de Vênus"""
        return (radius * phase * 1361) / 1000

    @staticmethod
    def calculate_cosmic_data(target_date=None) -> Dict:
        """Calcula dados cósmicos sem dependência de MayanAstronomy"""
        if target_date is None:
            target_date = datetime.now().date()
        
        # Implementação alternativa que não depende de MayanAstronomy
        days_since_2012 = (target_date - date(2012, 12, 21)).days
        return {
            'earth_position': (days_since_2012 % 365) / 365 * 360,
            'venus_position': (days_since_2012 % 584) / 584 * 360,
            'galactic_progress': (days_since_2012 / 26000) * 100
        }
        
    @staticmethod
    def calculate_cycles(target_date: date = None) -> Dict:
        """Calcula os ciclos principais baseados em Fibonacci"""
        target_date = target_date or datetime.now().date()
        
        mayan_astro = MayanAstronomy()
        positions = mayan_astro.get_planetary_positions(target_date)
        
        return {
            'tzolkin': (positions['venus']['position'] + positions['terra']['position']) % 260,
            'harmonic': (positions['venus']['phase'] * positions['terra']['phase']) / 136.1,
            'fibonacci_sequence': AstronomyUtils.generate_fibonacci_sequence(target_date)
        }

    @staticmethod
    def generate_fibonacci_sequence(date_obj: date) -> List[int]:
        """Gera sequência Fibonacci modificada para a data"""
        day_of_year = date_obj.timetuple().tm_yday
        a, b = 0, 1
        sequence = []
        for _ in range(8):  # 8 números da sequência
            a, b = b, a + b
            sequence.append((day_of_year + a) % 260)  # Ajusta para ciclo Tzolk'in
        return sequence

    @staticmethod
    def calculate_alignment(cycle_type: str, current_position: int) -> Dict:
        """Calcula próximos alinhamentos baseados em ciclos e glifos"""
        cycle = CYCLES.get(cycle_type)
        if not cycle:
            raise ValueError(f"Ciclo desconhecido: {cycle_type}")

        fib_seq = [8, 13, 21, 34, 55, 89]  # Números de Fibonacci relevantes
        
        return {
            'cycle': cycle.name,
            'current_glyph': cycle.glyph_sequence[current_position % len(cycle.glyph_sequence)],
            'next_alignments': sorted(
                (current_position + fib) % cycle.days
                for fib in fib_seq
            ),
            'resonance_frequencies': [cycle.frequency * (fib/34) for fib in fib_seq]
        }

    @staticmethod
    def find_cross_cycle_alignments() -> List[Dict]:
        """Encontra alinhamentos entre diferentes ciclos"""
        significant_alignments = []
        
        for cycle1 in CYCLES.values():
            for cycle2 in CYCLES.values():
                if cycle1.name == cycle2.name:
                    continue
                    
                common_days = AstronomyUtils.lcm(cycle1.days, cycle2.days)
                significant_alignments.append({
                    'cycles': f"{cycle1.name}-{cycle2.name}",
                    'alignment_days': [
                        (common_days // cycle1.days) * i 
                        for i in range(1, 5)
                    ],
                    'harmonic_frequency': (cycle1.frequency + cycle2.frequency)/2
                })
        
        return significant_alignments

    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Calcula mínimo múltiplo comum"""
        return abs(a*b) // math.gcd(a, b)

    @staticmethod
    def get_current_cycle_positions() -> Dict:
        """Retorna posições atuais em todos os ciclos"""
        now = datetime.now()
        
        return {
            'tzolkin': (now.timetuple().tm_yday + 120) % 260,
            'venus': (now.timetuple().tm_yday * 584 // 365) % 584,
            'galactic': (now.year - 2012) % 26000
        }
