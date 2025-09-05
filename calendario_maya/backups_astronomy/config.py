# core/config.py
from pathlib import Path

def load_config():
    """Configurações básicas do aplicativo"""
    return {
        'app_name': 'Decodificador Maya-Asteca',
        'version': '1.0'
    }
    
def get_project_root():
    """Retorna o caminho absoluto para a raiz do projeto"""
    return Path(__file__).parent.parent.parent

def verify_data_files():
    """Verifica se os arquivos essenciais existem"""
    data_dir = get_data_path()
    required_files = [
        'tzolk.json',
        'tonalpohualli.json',
        'historical_events.json'
    ]
    
    missing = [f for f in required_files if not (data_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"Arquivos essenciais faltando: {', '.join(missing)}")

def get_data_path(filename=None):
    """Retorna o caminho absoluto para o diretório de dados"""
    project_root = Path(__file__).parent.parent
    data_path = project_root / "data"
    
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
        print(f"⚠️ Diretório de dados criado em: {data_path}")
    
    if filename:
        return data_path / filename
    return data_path

def get_glyph_path():
    return get_data_path() / "tzolk.json"

def get_timeline_events_path():
    return get_data_path() / "timeline_events.json"