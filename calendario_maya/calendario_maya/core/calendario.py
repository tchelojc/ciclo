import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from constants.matematicas import RELACAO_AUREA
from constants.simbolos import CHAKRAS_NUMEROLOGIA, CORES_VIBRACIONAIS
from core.symbol_connector import symbol_connector
from core.data_bridge import data_bridge

class CalendarioSagrado:
    def __init__(self):
        """Unifica os calendários Tzolk'in e Tonalpohualli"""
        self._bridge = data_bridge
        # Registra apenas handlers para mensagens existentes
        self._bridge.register_handler('data_loaded', self._on_data_loaded)
        self._bridge.register_handler('system_sync', self._on_system_sync)
        
        self.ciclos_maya = {
            'kin': 1,
            'uinal': 20,
            'tun': 360,
            'katun': 7200,
            'baktun': 144000
        }
        self._carregar_dados()
        
        # Conexão com SymbolConnector
        self.nahuales = symbol_connector.get_nahuales()
        self.tonals = symbol_connector.get_tonals()
        
    def _on_data_loaded(self, payload):
        """Reage ao carregamento inicial de dados"""
        print(f"📊 Dados carregados: Tzolk'in={payload['tzolk']}, Tonal={payload['tonalpohualli']}")

    def _on_system_sync(self, payload):
        """Reage a sincronizações do sistema"""
        if payload['status'] == 'completed':
            self._carregar_dados()
        
    def _on_data_updated(self, payload):
        """Reage a atualizações de dados"""
        if payload['type'] in ['tzolk', 'tonalpohualli']:
            self._carregar_dados()

    def _carregar_dados(self) -> None:
        """Carrega todos os dados necessários com tratamento robusto"""
        try:
            # Define caminhos absolutos para os arquivos
            data_dir = Path(__file__).parent.parent / 'data'
        
            # Carrega Tzolk'in
            tzolk_path = data_dir / 'tzolk.json'
            if tzolk_path.exists():
                with open(tzolk_path, 'r', encoding='utf-8') as f:
                    self.tzolk_data = json.load(f)
                    print(f"✅ Dados Tzolk'in carregados: {len(self.tzolk_data.get('nahuales', []))} nahuales")
            else:
                raise FileNotFoundError(f"Arquivo tzolk.json não encontrado em {tzolk_path}")

            # Carrega Tonalpohualli
            tonal_path = data_dir / 'tonalpohualli.json'
            if tonal_path.exists():
                with open(tonal_path, 'r', encoding='utf-8') as f:
                    self.tonal_data = json.load(f)
                    print(f"✅ Dados Tonalpohualli carregados: {len(self.tonal_data.get('signos', []))} signos")
            else:
                raise FileNotFoundError(f"Arquivo tonalpohualli.json não encontrado em {tonal_path}")

        except Exception as e:
            print(f"⚠️ Erro crítico ao carregar dados: {e}")
            # Cria estruturas mínimas de fallback
            self.tzolk_data = {
                "nahuales": [{"nome": f"Nahual {i+1}", "glifo": "🌀"} for i in range(20)],
                "constantes": {"ciclo_sagrado": 260}
            }
            self.tonal_data = {
                "signos": [{"nome": f"Signo {i+1}", "glifo": "⭐"} for i in range(20)]
            }
            # Notifica o sistema sobre o fallback
            self._bridge.send_message('data_fallback', {
                'error': str(e),
                'fallback_data': True
            })

    def _calcular_posicao_ciclica(self, dias: int, ciclo: int) -> Tuple[int, int]:
        """Calcula dia e componente (trecena/veintena)"""
        dia = (dias % ciclo) + 1
        componente = (dia - 1) % 20 + 1 if ciclo == 260 else (dia - 1) % 13 + 1
        return dia, componente

    def converter_data(self, data: datetime = None) -> Dict[str, Any]:
        """Converte data gregoriana para todos os sistemas calendáricos"""
        data = data or datetime.now()
        dias_desde_epoch = (data - datetime(2012, 12, 21)).days

        # Cálculos comuns
        kin, trecena = self._calcular_posicao_ciclica(dias_desde_epoch, 260)
        dia_tonal, veintena = self._calcular_posicao_ciclica(
            data.timetuple().tm_yday + int(data.year * 1.033), 260)

        return {
            "gregoriana": data.strftime("%Y-%m-%d"),
            "tzolkin": {
                "kin": kin,
                "nahual": self._obter_nahual(kin),
                "trecena": trecena,
                "energia": self.tzolk_data.get("numeros", {}).get("energias", {}).get(str(trecena), {})
            },
            "tonalpohualli": {
                "dia": dia_tonal,
                "signo": self._obter_signo(dia_tonal),
                "veintena": veintena
            }
        }

    def _obter_nahual(self, kin: int) -> Dict[str, Any]:
        """Obtém nahual com tratamento robusto de erros"""
        try:
            kin_index = (kin - 1) % 20
        
            # Verifica se temos dados válidos
            if not isinstance(self.tzolk_data.get('nahuales'), list):
                raise ValueError("Estrutura de dados inválida para nahuales")
            
            # Garante que o índice está dentro dos limites
            if kin_index >= len(self.tzolk_data['nahuales']):
                kin_index = kin_index % len(self.tzolk_data['nahuales'])
            
            nahual = self.tzolk_data['nahuales'][kin_index]
        
            # Garante que é um dicionário
            if not isinstance(nahual, dict):
                nahual = {"nome": str(nahual), "glifo": "🌀"}
            
            return {
                "nome": nahual.get("nome", f"Nahual {kin_index+1}"),
                "glifo": nahual.get("glifo", "🌀"),
                "chakra": CHAKRAS_NUMEROLOGIA.get(nahual.get("chakra", 0)),
                "ressonancia": (nahual.get("frequencia", 432) * RELACAO_AUREA) % 432
            }
        
        except Exception as e:
            print(f"⚠️ Erro ao obter nahual {kin}: {e}")
            return {
                "nome": "Desconhecido",
                "glifo": "�",
                "chakra": "Indefinido",
                "ressonancia": 432
            }

    def _obter_signo(self, dia: int) -> Dict[str, Any]:
        """Obtém os dados completos de um signo (com SymbolConnector como fallback)"""
        try:
            # Tenta primeiro com SymbolConnector
            tonal = symbol_connector.get_tonal(dia % 20 + 1)
            if tonal:
                return {
                    **tonal,
                    "chakra": CHAKRAS_NUMEROLOGIA.get(tonal.get("chakra", 0)),
                    "cor": CORES_VIBRACIONAIS.get(tonal.get("cor", ""), "#FFFFFF"),
                    "ressonancia": (tonal.get("frequencia", 432) * RELACAO_AUREA) % 432
                }
            
            # Fallback para dados locais
            idx = (dia - 1) % len(self.tonal_data.get("signos_dias", []))
            signo = self.tonal_data["signos_dias"][idx]
            return {
                **signo,
                "chakra": CHAKRAS_NUMEROLOGIA.get(signo.get("chakra", 0)),
                "cor": CORES_VIBRACIONAIS.get(signo.get("cor", ""), "#FFFFFF"),
                "ressonancia": (signo.get("frequencia", 432) * RELACAO_AUREA) % 432
            }
        except Exception as e:
            print(f"⚠️ Erro ao obter signo: {e}")
            return {
                "nome": "Desconhecido",
                "glifo": "�",
                "chakra": "Indefinido",
                "cor": "#FFFFFF",
                "ressonancia": 432
            }

    def converter_longcount(self, baktun: int, katun: int, tun: int, uinal: int, kin: int) -> Dict[str, Any]:
        """Converte do formato Long Count"""
        dias = sum([
            baktun * 144000,
            katun * 7200,
            tun * 360,
            uinal * 20,
            kin
        ])
        kin_tzolkin = (dias % 260) + 1
        
        return {
            "longcount": f"{baktun}.{katun}.{tun}.{uinal}.{kin}",
            "dias": dias,
            "tzolkin": self._obter_nahual(kin_tzolkin),
            "tonalpohualli": self._obter_signo(kin_tzolkin),
            "ciclo_52": "Ativo" if dias % 52 == 0 else "Normal"
        }
    
    def get_current_nahual(self, day_number: int) -> Optional[Dict[str, Any]]:
        """Nova interface simplificada usando SymbolConnector"""
        return symbol_connector.get_nahual(day_number % 20 + 1)
        
CalendarioMaya = CalendarioSagrado
CalendarioAsteca = CalendarioSagrado