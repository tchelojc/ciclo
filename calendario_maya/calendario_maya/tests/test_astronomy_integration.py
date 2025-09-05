# tests/test_astronomy_integration.py
import unittest
import sys
from pathlib import Path
from datetime import datetime, date  # Adicionar no início do arquivo

# Adiciona o diretório raiz ao path do Python
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from calendario_maya.utils.mayan_astronomy import MayanAstronomy

class TestAstronomyIntegration(unittest.TestCase):
    def setUp(self):
        self.astro = MayanAstronomy()
        
    def test_earth_position(self):
        result = self.astro.get_planetary_positions(date(2024, 12, 31))
        self.assertIn('earth', result)
        self.assertIn('position', result['earth'])
        self.assertTrue(0 <= result['earth']['position'] <= 360)
    
    def test_venus_position(self):
        result = self.astro.get_planetary_positions(date(2024, 12, 31))
        self.assertTrue(0 <= result['venus']['position'] < 360)

    def test_cosmic_calculations(self):
        test_date = date(2012, 12, 21)
        result = self.astro.get_cosmic_calendar(test_date)  # Corrigido para self.astro
        self.assertIsInstance(result, dict)
        self.assertIn('baktun', result)
        self.assertAlmostEqual(result['baktun'], 13.0, delta=0.1)
    
if __name__ == "__main__":
    unittest.main()