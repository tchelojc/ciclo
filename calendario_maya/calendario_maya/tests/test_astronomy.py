# test_astronomy.py
import unittest
import datetime
from datetime import date
from calendario_maya.core.connector import Connector
from calendario_maya.utils.mayan_astronomy import MayanAstronomy
from calendario_maya.utils.date_utils import safe_date_convert

class TestMayanAstronomy(unittest.TestCase):
    def setUp(self):
        self.astro = MayanAstronomy()
        
    def test_baktun_calculation(self):
        """Testa o cálculo do Baktun"""
        test_date = datetime.date(2012, 12, 21)
        calculated_baktun = self.astro.calculate_baktun(test_date)
        self.assertAlmostEqual(calculated_baktun, 13.0, delta=0.1)

    def test_planetary_positions(self):
        """Testa se retorna earth e venus"""
        positions = self.astro.get_planetary_positions(date.today())
        self.assertIn('earth', positions)
        self.assertIn('venus', positions)

if __name__ == "__main__":
    unittest.main()