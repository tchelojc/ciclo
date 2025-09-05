"""
CONSTANTES FÍSICAS E ASTRONÔMICAS PARA O DECODIFICADOR MAYA-ASTECA

Inclui constantes fundamentais e valores específicos para cálculos de calendários cósmicos
"""
from datetime import date, timedelta  # ✅ Importar timedelta corretamente
import math  # ✅ Necessário para funções trigonométricas

# Constantes fundamentais
VELOCIDADE_LUZ = 299792458  # m/s
CONSTANTE_GRAVITACIONAL = 6.67430e-11  # m³·kg⁻¹·s⁻²
CONSTANTE_PLANCK = 6.62607015e-34  # J·Hz⁻¹

# Constantes solares e astronômicas
CONSTANTE_SOLAR = 1361  # W/m² - Fluxo solar na Terra
CONSTANTE_GALACTICA = 2.5e8  # anos - Período de rotação galáctica
MASSA_SOLAR = 1.9885e30  # kg
RAIO_SOLAR = 6.957e8  # metros

# Constantes de tempo cósmico
CICLO_MAIA = 1872000  # dias (13 baktuns)
CICLO_AZTECA = 18980  # dias (52 anos)
ANO_GALACTICO = 2.25e8  # anos terrestres

# Definições alternativas para compatibilidade
c = VELOCIDADE_LUZ
G = CONSTANTE_GRAVITACIONAL
h = CONSTANTE_PLANCK

# Constantes derivadas para cálculos
MASSA_PADRAO = 1.78266192e-36  # kg
ANO_LUZ = 9.4607e15  # metros
GRAVIDADE_QUANTICA = 9.81 * ((1 + 5**0.5) / 2)  # φ * gravidade terrestre
FATOR_TEMPORAL_BASE = (VELOCIDADE_LUZ**2) / (4 * CONSTANTE_GRAVITACIONAL)

# Relações astronômicas importantes
RELACAO_LUA_TERRA = 27.321661  # dias siderais
RELACAO_TERRA_SOL = 365.256363  # dias siderais
RELACAO_SOL_GALAXIA = 1 / 250000000  # fração do ano galáctico
VENUS_RADIUS = 6051.8  # km

# Fatores de conversão temporal
FATOR_MAIA_AZTECA = CICLO_MAIA / CICLO_AZTECA
FATOR_COSMICO = ANO_GALACTICO / CICLO_MAIA

# Coordenadas do centro galáctico
GALACTIC_CENTER_COORDS = {
    "ra": 266.4168,    # Ascensão reta em graus
    "dec": -29.0078,   # Declinação em graus
    "distance_ly": 26000  # Distância em anos-luz
}

# Data de referência do ciclo Maia
REFERENCE_DATE = date(2012, 12, 21)

# Períodos orbitais dos planetas
PERIODOS_ORBITAIS = {
    'terra': {
        'sideral': 365.256363004,  # Dias (período sideral exato)
        'sinodico': 365.24219,     # Ano tropical
        'inclinacao': 23.4392811   # Inclinação eclíptica
    },
    'venus': {
        'sideral': 224.70079922,   # Dias
        'sinodico': 583.92,
        'inclinacao': 3.39458
    }
}

# Constantes derivadas
EARTH_ORBITAL_PERIOD = PERIODOS_ORBITAIS['terra']['sideral']
VENUS_ORBITAL_PERIOD = PERIODOS_ORBITAIS['venus']['sideral']

# Parâmetros orbitais simplificados
POSICOES_PLANETARIAS = {
    'venus': {
        'cycle': VENUS_ORBITAL_PERIOD,
        'ratio': 0.615,
        'eccentricity': 0.0067
    },
    'terra': {
        'cycle': EARTH_ORBITAL_PERIOD,
        'ratio': 1.0,
        'eccentricity': 0.0167
    }
}

# Função para calcular a posição angular planetária com correção de excentricidade
def calcular_posicao_planetaria(dias, planeta='venus'):
    """Calcula a posição angular com correção de excentricidade"""
    params = POSICOES_PLANETARIAS.get(planeta.lower(), {})
    if not params:
        return 0.0

    ciclo = params['cycle']
    anomalia_media = (dias % ciclo) / ciclo * 2 * math.pi
    correcao = params['eccentricity'] * math.sin(anomalia_media)
    posicao = (anomalia_media + correcao) * 180 / math.pi

    return posicao % 360  # Garantir valor entre 0-360°

# Função para calcular dilatação temporal gravitacional
def calcular_dilatacao_temporal(massa, distancia):
    """
    Calcula o fator de dilatação temporal gravitacional
    massa: em unidades solares
    distancia: em anos-luz
    """
    return (G * massa * MASSA_SOLAR) / (distancia * ANO_LUZ * c**2)
