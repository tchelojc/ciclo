import math
from datetime import date
from typing import Dict

class MayanMath:
    @staticmethod
    def calculate_kin(target_date: date) -> Dict[str, int]:
        """Calcula o Kin (dia sagrado) no Tzolk'in"""
        day = target_date.day
        month = target_date.month
        year = target_date.year
        
        # Cálculo do número do Kin (1-260)
        kin_number = (day + month * 20 + year * 13) % 260
        kin_number = 260 if kin_number == 0 else kin_number
        
        return {
            'number': kin_number,
            'nahual': (kin_number - 1) % 20 + 1,
            'tonalli': (kin_number - 1) % 13 + 1
        }

    @staticmethod
    def calculate_venus_cycle(target_date: date) -> Dict[str, float]:
        """Calcula a posição no ciclo de Vênus (584 dias)"""
        jd = MayanMath.julian_day(target_date)
        venus_cycle = 583.92  # Dias no ciclo sinódico de Vênus
        
        # Posição no ciclo (0-1)
        position = (jd % venus_cycle) / venus_cycle
        
        # Fases importantes (baseado no Códice Dresden)
        phases = {
            0.0: "Conjunção Superior",
            0.25: "Estrela da Manhã",
            0.5: "Conjunção Inferior",
            0.75: "Estrela da Tarde"
        }
        
        return {
            'position': position,
            'phase': next((v for k,v in phases.items() if position >= k), "Transição"),
            'days_remaining': venus_cycle - (jd % venus_cycle)
        }

    @staticmethod
    def julian_day(target_date: date) -> float:
        """Converte data gregoriana para dia juliano"""
        a = (14 - target_date.month) // 12
        y = target_date.year + 4800 - a
        m = target_date.month + 12 * a - 3
        
        return (target_date.day + (153 * m + 2) // 5 + 365 * y + 
                y // 4 - y // 100 + y // 400 - 32045)