# core/data_manager.py
import json
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta  # ✅ IMPORT CORRIGIDO

class DateUtils:
    GALACTIC_CYCLE = 25772
    VENUS_CYCLE = 583.92
    MAYA_EPOCH = "-3114-08-11"

    @classmethod
    def safe_date(cls, year, month=6, day=15):
        try:
            return datetime(year, month, day)
        except Exception:
            return f"{year:04d}-{month:02d}-{day:02d}"

class DataManager:
    def __init__(self, quantum=False):
        if quantum:
            from core.quantum_connector import qc
            self._quantum = qc
        self.data_dir = self._find_data_dir()
        logging.info(f"DataManager inicializado. Diretório de dados: {self.data_dir}")
        
    def get_data_path(filename):
        base_dir = Path(__file__).parent.parent
        return os.path.join(base_dir, "data", filename)

    def _find_data_dir(self):
        """Busca em múltiplas localizações possíveis"""
        possible_paths = [
            Path(__file__).parent.parent / 'data',
            Path.cwd() / 'data',
            Path('C:/Users/Marcelo/portal/calendario_maya/data')
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        return Path.cwd()

    def load_json(self, filename):
        """Carrega arquivo JSON com tratamento de erros"""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Erro ao carregar {filename}: {str(e)}")
            raise

__all__ = ['DataManager']