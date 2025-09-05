import unittest
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestImports(unittest.TestCase):
    def test_imports(self):
        """Testa se todos os imports principais funcionam"""
        from calendario_maya.core.data_manager import DataManager
        from calendario_maya.interface.widgets.glyph_viewer import GlyphViewer
        from calendario_maya.interface.widgets.tzolkin_tab import TzolkinTab
        from calendario_maya.interface.widgets.tonal_tab import TonalTab
        from calendario_maya.interface.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QAction
        
        self.assertTrue(True)  # Se chegou aqui, os imports funcionaram

if __name__ == '__main__':
    unittest.main()