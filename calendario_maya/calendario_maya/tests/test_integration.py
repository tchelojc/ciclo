# test_integration.py
import unittest
from datetime import date
from calendario_maya.core.connector import Connector

class TestConnectorIntegration(unittest.TestCase):
    def setUp(self):
        self.conn = Connector()
        
    def test_celestial_data(self):
        data = self.conn.get_celestial_data(date.today())
        self.assertIn('sun', data)
        self.assertIn('venus', data)
        self.assertIn('tzolkin', data)

if __name__ == "__main__":
    unittest.main()