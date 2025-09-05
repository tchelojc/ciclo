import unittest
from config import path_manager, style_loader

class TestStyleSystem(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(hasattr(path_manager, 'get'))
        
    def test_styles(self):
        style = style_loader.load("maya")
        self.assertIsInstance(style, str)

if __name__ == "__main__":
    unittest.main()