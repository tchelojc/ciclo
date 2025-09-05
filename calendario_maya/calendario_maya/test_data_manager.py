# test_data_manager.py
from core.data_manager import DataManager

dm = DataManager()
print(f"Diretório de dados: {dm.data_dir}")
print("tzolk.json:", dm.load_json('tzolk.json').keys())