import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache

class SymbolConnector:
    """
    Conector inteligente que unifica o acesso a todos os símbolos sagrados
    a partir dos arquivos existentes (tzolk.json e tonalpohualli.json)
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(__file__).parent.parent / data_dir
        self._cache = {}

    @lru_cache(maxsize=2)
    def _load_file(self, filename: str) -> Dict[str, Any]:
        """Carrega um arquivo JSON com cache"""
        try:
            with open(self.data_dir / filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Erro ao carregar {filename}: {str(e)}")
            return {}

    def get_nahuales(self) -> list:
        """Obtém todos os nahuales do Tzolk'in"""
        tzolk_data = self._load_file("tzolk.json")
        return tzolk_data.get("nahuales", [])

    def get_tonals(self) -> list:
        """Obtém todos os signos do Tonalpohualli"""
        tonal_data = self._load_file("tonalpohualli.json")
        return tonal_data.get("signos", [])

    def get_nahual(self, numero: int) -> Optional[dict]:
        """Busca um nahual específico por número"""
        for nahual in self.get_nahuales():
            if nahual.get("numero") == numero:
                return self._enhance_nahual(nahual)
        return None

    def get_tonal(self, dia: int) -> Optional[dict]:
        """Busca um signo tonal por dia"""
        for tonal in self.get_tonals():
            if tonal.get("dia") == dia:
                return self._enhance_tonal(tonal)
        return None

    def _enhance_nahual(self, nahual: dict) -> dict:
        """Enriquece os dados do nahual com informações vibracionais"""
        return {
            **nahual,
            "frequencia": self._calculate_frequency(nahual.get("numero", 1)),
            "chakra": self._map_chakra(nahual.get("numero", 1))
        }

    def _enhance_tonal(self, tonal: dict) -> dict:
        """Enriquece os dados tonal com informações elementais"""
        return {
            **tonal,
            "elemento": self._map_element(tonal.get("dia", 1))
        }

    @staticmethod
    def _calculate_frequency(numero: int) -> int:
        """Calcula a frequência baseada em numerologia sagrada"""
        frequencies = {1: 396, 2: 417, 3: 528, 4: 639, 5: 741, 6: 852, 7: 963}
        return frequencies.get(numero % 7 + 1, 432)

    @staticmethod
    def _map_chakra(numero: int) -> str:
        """Mapeia para o sistema de chakras"""
        chakras = {
            1: "Raiz", 2: "Sacral", 3: "Plexo Solar",
            4: "Cardíaco", 5: "Laríngeo", 6: "Frontal", 7: "Coroa"
        }
        return chakras.get(numero % 7 + 1, "Desconhecido")

    @staticmethod
    def _map_element(dia: int) -> str:
        """Mapeia para elementos alquímicos"""
        elements = ["Fogo", "Terra", "Ar", "Água", "Éter"]
        return elements[dia % 5]

# Instância global para uso em todo o sistema
symbol_connector = SymbolConnector()