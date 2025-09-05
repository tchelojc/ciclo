# calendario_maya/constants/astronomia.py
"""
Módulo centralizado para constantes astronômicas e de época.
"""
from datetime import date

# --- Datas de Referência (Épocas) ---
# Define a data de referência (solstício de 2012) como a fonte única da verdade.
REFERENCE_DATE = date(2012, 12, 21)

# Dia Juliano correspondente à data de referência.
GALACTIC_EPOCH_JD = 2456282.5

# --- Períodos Orbitais ---
PERIODOS_ORBITAIS = {
    'terra': {
        'sideral': 365.256363004,   # Dias para uma volta completa ao redor do Sol
        'tropical': 365.24219,     # Dias de uma estação à mesma estação
    },
    'venus': {
        'sideral': 224.70079922,   # Dias para uma volta completa ao redor do Sol
        'sinodico': 583.92,        # Dias para reaparecer no mesmo ponto no nosso céu
    }
}

# --- Constantes Derivadas para facilitar o uso ---
EARTH_ORBITAL_PERIOD = PERIODOS_ORBITAIS['terra']['sideral']
VENUS_ORBITAL_PERIOD = PERIODOS_ORBITAIS['venus']['sideral']
GALACTIC_YEAR_DAYS = 225000000  # Dias em um ano galáctico (aproximado)