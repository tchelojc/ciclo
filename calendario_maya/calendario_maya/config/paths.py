from pathlib import Path
import os

class PathManager:
    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent
        self.data_dir = self.root / 'data'
        
    def get(self, file_name):
        """Retorna o caminho absoluto ou None"""
        path = self.data_dir / file_name
        return path if path.exists() else None

# Singleton global
path_manager = PathManager()