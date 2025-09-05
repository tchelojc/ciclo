import numpy as np
from typing import Dict, List, TypedDict, Union
from pathlib import Path
import json
from .matematicas import RELACAO_AUREA, PI_QUANTICO
from .fisica import c, G, h

# Verificação de constantes fundamentais
if not isinstance(RELACAO_AUREA, float):
    RELACAO_AUREA = (1 + 5**0.5) / 2
    
if not isinstance(c, (int, float)):
    c = 299792458

# Tipos avançados
class NumerologiaSignificado(TypedDict):
    elemento: str
    cor: str
    planeta: str
    caracteristicas: str
    equacao: str

class GeometriaSagrada(TypedDict):
    vertices: int
    faces: int
    angulos: float
    frequencia_base: int

class LinhagemInfo(TypedDict):
    caracteristicas: str
    frequencia: float
    cor: str
    missao: str
    emoji: str
    dna: int
    era: str
    cristais: List[str]
    mantras: List[str]
    equacao: str
    constantes: Dict[str, float]

# Dados fundamentais
VIBRACOES_BASE: Dict[int, int] = {
    1: 396, 2: 417, 3: 528, 4: 639, 5: 741, 6: 852, 7: 963
}

NUMEROLOGIA_SIGNIFICADOS: Dict[int, NumerologiaSignificado] = {
    1: {
        "elemento": "Fogo",
        "cor": "Vermelho",
        "planeta": "Sol",
        "caracteristicas": "Liderança, iniciativa",
        "equacao": "E = mc²"
    },
    2: {
        "elemento": "Água",
        "cor": "Laranja",
        "planeta": "Lua",
        "caracteristicas": "Cooperação, sensibilidade",
        "equacao": "F = G(m₁m₂)/r²"
    },
    3: {
        "elemento": "Ar",
        "cor": "Amarelo",
        "planeta": "Júpiter",
        "caracteristicas": "Criatividade",
        "equacao": "λ = h/p"
    },
    4: {
        "elemento": "Terra",
        "cor": "Verde",
        "planeta": "Urano",
        "caracteristicas": "Estabilidade",
        "equacao": "V = IR"
    },
    5: {
        "elemento": "Éter",
        "cor": "Azul",
        "planeta": "Mercúrio",
        "caracteristicas": "Liberdade",
        "equacao": "S = k lnΩ"
    },
    6: {
        "elemento": "Luz",
        "cor": "Anil",
        "planeta": "Vênus",
        "caracteristicas": "Amor",
        "equacao": "E = hν"
    },
    7: {
        "elemento": "Som",
        "cor": "Violeta",
        "planeta": "Netuno",
        "caracteristicas": "Espiritualidade",
        "equacao": "ψ = Σcₙφₙ"
    },
    8: {
        "elemento": "Cristal",
        "cor": "Rosa",
        "planeta": "Saturno",
        "caracteristicas": "Poder",
        "equacao": "F = qE + q(v×B)"
    },
    9: {
        "elemento": "Universo",
        "cor": "Dourado",
        "planeta": "Marte",
        "caracteristicas": "Compaixão",
        "equacao": "Rμν - ½Rgμν = 8πTμν"
    }
}

CHAKRAS_DICT = {
    1: 'Raiz',
    2: 'Sacral',
    3: 'Plexo Solar',
    4: 'Cardíaco',
    5: 'Laríngeo',
    6: 'Frontal',
    7: 'Coroa'
}

CHAKRAS_NUMEROLOGIA = {
    1: "Coronário",
    2: "Frontal",
    3: "Laríngeo",
    4: "Cardíaco",
    5: "Plexo Solar",
    6: "Esplênico",
    7: "Básico",
    8: "Estelar",
    9: "Cármico"
}

ELEMENTOS_ALQUIMICOS = {
    0: 'Éter',
    1: 'Fogo',
    2: 'Terra',
    3: 'Ar',
    4: 'Água'
}

GEOMETRIAS_SAGRADAS = {
    'estrela_tetraedro': {
        'vertices': 144,          # Número de vértices na grade cristal
        'faces': 72,              # Faces da geometria sagrada
        'angulos': 60,            # Ângulo interno padrão em graus
        'frequencia_base': 528    # Frequência de ressonância em Hz
    },
    'merkaba': {
        'vertices': 1440,
        'faces': 720,
        'angulos': 51.84,         # 51°50'24" - Ângulo da pirâmide de Gizé
        'frequencia_base': 432    # Frequência de sincronização planetária
    },
    'flor_da_vida': {
        'vertices': 144,
        'faces': 72,
        'angulos': 30,            # Padrão hexagonal sagrado
        'frequencia_base': 963    # Frequência de ativação quântica
    }
}

FREQUENCIAS_ALMA = {
    'BASE': 432,
    'AMOR': 528,
    'CURA': 639,
    'EXPANSAO': 741,
    'INTUICAO': 852,
    'TRANSMUTACAO': 963
}

FREQUENCIAS_QUANTICAS = [
    "Delta (0.5-4Hz)",
    "Theta (4-8Hz)",
    "Alpha (8-13Hz)",
    "Beta (13-30Hz)",
    "Gamma (30-100Hz)",
    "Lambda (100-200Hz)",
    "Epsilon (200-400Hz)",
    "Zeta (400-800Hz)"
]

# Campos Morfogenéticos
CAMPOS_MORFOGENETICOS = [
    "Campo Akáshico",
    "Campo Etérico",
    "Campo Astral",
    "Campo Mental",
    "Campo Causal",
    "Campo Búdico",
    "Campo Átmico"
]

CORES_VIBRACIONAIS = {
    "AMETISTA": "#4B0082",
    "VERMELHO": "#FF0000",
    "VERDE": "#00FF00",
    "AZUL": "#0000FF",
    "DOURADO": "#FFD700"
}
    
LINHAGENS_INFO: Dict[str, LinhagemInfo] = {
    "Arcturianos": {
        "caracteristicas": "Tecnologia espiritual avançada",
        "frequencia": 147 * np.cos(np.radians(9)),
        "cor": "#8A2BE2",
        "missao": "Cura planetária multidimensional",
        "emoji": "👽",
        "dna": 9,
        "era": "Era Dourada de Arcturus",
        "cristais": ["Apophyllita", "Moldavita"],
        "mantras": ["OM-RA-TU", "ARCTURIS LUMINA"],
        "equacao": "E = mφc²",
        "constantes": {"φ": RELACAO_AUREA, "c": c}
    },
    "Pleiadianos": {
        "caracteristicas": "Compassivos, artísticos, comunicadores",
        "frequencia": 144 * np.cos(np.radians(18)),
        "cor": "#ADD8E6",
        "missao": "Despertar o amor incondicional",
        "emoji": "🌌",
        "dna": 7,
        "era": "Era de Luz de Pleiades",
        "cristais": ["Ametista", "Selenita"],
        "mantras": ["PLE-RA-NI", "AMARIS LUMEN"],
        "equacao": "λ = h/(mv)",
        "constantes": {"h": 6.626e-34, "v": 0.1*c}
    },
    "Sirianos": {
        "caracteristicas": "Místicos, conectados à água e à sabedoria antiga",
        "frequencia": 128 * np.cos(np.radians(27)),
        "cor": "#00008B",
        "missao": "Preservar o conhecimento ancestral",
        "emoji": "🌀",
        "dna": 5,
        "era": "Era Cristal de Sirius",
        "cristais": ["Lápis-Lazúli", "Selenita"],
        "mantras": ["SIRIUS-OM", "AQUARIS NOVA"],
        "equacao": "∇²ψ + (8π²m/h²)(E-V)ψ = 0",
        "constantes": {"m": 9.11e-31, "E": 1.6e-19}
    },
    "Andromedanos": {
        "caracteristicas": "Libertadores galácticos, visionários",
        "frequencia": 112 * np.cos(np.radians(36)),
        "cor": "#50C878",
        "missao": "Libertação de sistemas opressivos",
        "emoji": "🧪",
        "dna": 3,
        "era": "Era Quântica de Andrômeda",
        "cristais": ["Moldavita", "Esmeralda"],
        "mantras": ["ANDROMEDA-RA", "LIBERATIS NOVA"],
        "equacao": "Ψ(x,t) = Ae^(i(kx-ωt))",
        "constantes": {"A": 1.0, "k": 2*np.pi}
    }
}

def _load_symbol_data(filename: str) -> Dict:
    """Carrega dados simbólicos de arquivos JSON"""
    path = Path(__file__).parent.parent / 'data' / filename
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Carrega dados externos
SIMBOLOS_MAYA = _load_symbol_data('simbolos_maya.json')
GLIFOS_SAGRADOS = _load_symbol_data('glifos_sagrados.json')

class SimbolosManager:
    """Gerenciador central de símbolos para integração com outros módulos"""
    
    def __init__(self):
        self.symbols = {
            'numerologia': NUMEROLOGIA_SIGNIFICADOS,
            'geometria': GEOMETRIAS_SAGRADAS,
            'linhagens': LINHAGENS_INFO,
            'maya': SIMBOLOS_MAYA,
            'glifos': GLIFOS_SAGRADOS
        }
        
    def get_symbol(self, category: str, key: Union[str, int]):
        """Obtém um símbolo específico"""
        return self.symbols.get(category, {}).get(key)
    
    def connect_to_calendar(self, calendar_type: str):
        """Conecta símbolos ao calendário específico"""
        if calendar_type == 'maya':
            return {
                'nahuales': self.symbols['maya'].get('nahuales', []),
                'glifos': self.symbols['glifos']
            }
        elif calendar_type == 'aztec':
            return {
                'signos': self.symbols['maya'].get('tonalpohualli', [])
            }
        return {}

# Instância global para acesso fácil
simbolos_manager = SimbolosManager()

# Funções de utilidade para outros módulos
def get_frequencia_alma(nome: str) -> int:
    return FREQUENCIAS_ALMA.get(nome.upper(), 432)

def get_linhagem_info(linhagem: str) -> LinhagemInfo:
    return LINHAGENS_INFO.get(linhagem, {})

def get_chakra_numero(numero: int) -> str:
    return CHAKRAS_DICT.get(numero, "Desconhecido")

# Exportações principais
__all__ = [
    'simbolos_manager',
    'get_frequencia_alma',
    'get_linhagem_info',
    'get_chakra_numero',
    'VIBRACOES_BASE',
    'NUMEROLOGIA_SIGNIFICADOS',
    'GEOMETRIAS_SAGRADAS',
    'LINHAGENS_INFO',
    'FREQUENCIAS_ALMA'
]