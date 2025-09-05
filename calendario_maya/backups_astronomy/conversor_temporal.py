from constants.fisica import *
from datetime import datetime, timedelta
import math

class ConversorTemporal:
    """Conversor entre tempo quântico, cósmico e terrestre"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        
        # Fatores de conversão baseados nas constantes físicas
        self.FATOR_QUANTICO = (VELOCIDADE_LUZ**2) / (4 * CONSTANTE_GRAVITACIONAL)
        self.CICLO_BASE_MAIA = CICLO_MAIA / RELACAO_TERRA_SOL  # Em anos terrestres
        
    def quantico_para_terrestre(self, tempo_quantico: float, unidade: str = 'dias') -> float:
        """
        Converte unidades de tempo quântico para terrestre
        Opções de unidade: 'segundos', 'minutos', 'horas', 'dias', 'anos'
        """
        # Converter para segundos terrestres primeiro
        segundos = tempo_quantico * self.FATOR_QUANTICO
        
        # Converter para unidade desejada
        fatores = {
            'segundos': 1,
            'minutos': 1/60,
            'horas': 1/3600,
            'dias': 1/86400,
            'anos': 1/(86400*365.256363)
        }
        
        return segundos * fatores.get(unidade, 1)
    
    def maya_para_gregoriano(self, data_maya: dict) -> datetime:
        """Converte data do calendário Maia para Gregoriana"""
        # Implementação básica - ajuste conforme seu sistema de data Maia
        dias = data_maya.get('dias', 0)
        return datetime(2000, 1, 1) + timedelta(days=dias)
    
    def azteca_para_gregoriano(self, data_azteca: dict) -> datetime:
        """Converte data do calendário Asteca para Gregoriana"""
        ciclos = data_azteca.get('ciclos', 0)
        return datetime(2000, 1, 1) + timedelta(days=ciclos * (CICLO_AZTECA/52))
    
    def calcular_ciclo_solar(self, data: datetime) -> float:
        """Calcula a posição no ciclo solar galáctico"""
        dias_desde_2000 = (data - datetime(2000, 1, 1)).days
        return (dias_desde_2000 % ANO_GALACTICO) / ANO_GALACTICO

# Instância global
conversor_temporal = ConversorTemporal()