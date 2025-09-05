# utils/approximate_date.py
from datetime import date

class ApproximateDate:
    def __init__(self, year, new_cycle_reference=2012):
        self.year = year
        self.new_cycle_reference = new_cycle_reference
        
    def to_date(self):
        """Retorna uma data aproximada considerando o novo ciclo"""
        from datetime import date
        if self.year >= self.new_cycle_reference:
            # Pós-2012: usa 21 de dezembro como referência
            return date(self.year, 12, 21)
        else:
            # Pré-2012: usa 21 de junho como referência
            return date(self.year, 6, 21)
    
    def __str__(self):
        return f"Aprox. {self.year}-{self.month:02d}-{self.day:02d}"