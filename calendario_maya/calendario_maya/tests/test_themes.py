import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest import TestCase
from interface.main_window import MainWindow
from core.connector import Connector

class TestThemeApplication(TestCase):
    def setUp(self):
        self.connector = Connector()
        self.window = MainWindow(self.connector)
    
    def test_maya_theme_application(self):
        """Testa a aplicação do tema maia"""
        self.window.apply_maya_theme()
        self.assertIn("0a0a1a", self.window.styleSheet().lower(), 
                     "Tema maia não aplicado corretamente")
    
    def test_aztec_theme_application(self):
        """Testa a aplicação do tema asteca"""
        self.window.apply_aztec_theme()
        self.assertIn("1a0a0a", self.window.styleSheet().lower(), 
                     "Tema asteca não aplicado corretamente")