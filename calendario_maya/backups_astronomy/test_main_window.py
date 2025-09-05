import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from calendario_maya.interface.main_window import MainWindow
from calendario_maya.core.connector import Connector

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.connector = Connector()
        
    def test_window_creation(self):
        window = MainWindow(self.connector)
        self.assertIsNotNone(window)

if __name__ == '__main__':
    unittest.main()