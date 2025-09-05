import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

class _DataBridgeInternal:
    """Implementação interna da ponte de dados"""
    
    def __init__(self):
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self._load_all_data()

    def _load_all_data(self):
        """Carrega todos os conjuntos de dados com tratamento de erros"""
        try:
            self.tzolk_data = self._load_json_file('tzolk.json')
            self.tonal_data = self._load_json_file('tonalpohualli.json')
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.tzolk_data = self._get_fallback_data('tzolk.json')
            self.tonal_data = self._get_fallback_data('tonalpohualli.json')

    @lru_cache(maxsize=4)
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Carrega um arquivo JSON com fallback"""
        possible_paths = [
            self.PROJECT_ROOT / filename,
            self.PROJECT_ROOT / 'data' / filename,
            self.PROJECT_ROOT / 'interface' / 'data' / filename
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    continue
        
        return self._get_fallback_data(filename)

    def _get_fallback_data(self, filename: str) -> Dict[str, Any]:
        """Dados padrão com estrutura quântica/tradicional"""
        fallbacks = {
            'tzolk.json': {
                'nahuales': [{
                    'nome': 'Imix',
                    'glifo': '🐊',
                    'significado_tradicional': 'Início, água primordial',
                    'significado_quantico': 'Ponto zero do universo',
                    'frequencia': 396,
                    'direcao': 'Leste',
                    'equacao': 'ψ(0) = ∫φ(k)dk',
                    'chakra': 7
                }],
                'constantes': {'ciclo_sagrado': 260}
            },
            'tonalpohualli.json': {
                'signos': [{
                    'nome': 'Cipactli',
                    'glifo': '🐟',
                    'significado': 'Criação primordial',
                    'energia': 'KIN 1'
                }],
                'trecenas': []
            }
        }
        return fallbacks.get(filename, {})

# Interface pública
_instance = _DataBridgeInternal()

def get_data_bridge() -> _DataBridgeInternal:
    """Função de acesso à instância singleton"""
    return _instance

# Compatibilidade com código existente
data_bridge = _instance