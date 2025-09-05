from typing import List, Dict, Any
from constants.simbolos import LINHAGENS_INFO

class LinhagensEstelares:
    def __init__(self):
        self.linhagens = LINHAGENS_INFO

    def obter_linhagem(self, nome: str) -> Dict[str, Any]:
        """Retorna todos os dados de uma linhagem estelar"""
        return self.linhagens.get(nome, {})
    
    def listar_linhagens(self) -> List[str]:
        """Retorna a lista de todas as linhagens disponíveis"""
        return list(self.linhagens.keys())
    
    def calcular_ressonancia(self, nome: str) -> float:
        """Calcula a ressonância atual da linhagem"""
        linhagem = self.obter_linhagem(nome)
        if not linhagem:
            return 0.0
        return (linhagem['frequencia'] * linhagem['constantes'].get('φ', 1.618)) % 528