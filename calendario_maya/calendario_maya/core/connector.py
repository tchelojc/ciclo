import logging
from PyQt6.QtCore import QObject, pyqtSignal, QDate, QThread
from PyQt6.QtWidgets import QWidget
from pathlib import Path
from datetime import date as datetime_date
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import os
import importlib

from config import path_manager
from .calendario_cosmico import CalendarioCosmico
from calendario_maya.utils.mayan_astronomy import MayanAstronomy
from calendario_maya.core.data_bridge import data_bridge

class QuantumMayanMathPlaceholder:
    @staticmethod
    def calculate_venus_quantum_cycle(date):
        return {
            'quantum_phase': 0.0,
            'distance': 0.7,
            'significance': 'Kukulkán (Placeholder)'
        }
    
    @staticmethod
    def calculate_galactic_alignment(date):
        return {
            'quantum_entanglement': 0.5,
            'alignment': 'Partial (Placeholder)'
        }
        
class _ConnectorLoader(QObject):
    initialized = pyqtSignal(bool)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, connector):
        super().__init__()
        self.connector = connector
        
    def run(self):
        try:
            self.connector._load_core_data_config()
            self.connector._setup_utility_modules()
            self.connector._setup_astronomy_module()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class Connector(QObject):
    VERSION = "3.0"
    date_changed = pyqtSignal(QDate)
    data_loaded = pyqtSignal()

    def __init__(self, data_path=None):
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.root_path = Path(__file__).parent.parent
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.data_dir = Path(data_path) if data_path else self.root_path / 'data'

        self._initialized = False
        self._current_date = QDate.currentDate()
        self._utils_modules = {}
        self.tzolk_data = {}
        self.tonal_data = {}
        self.long_count_data = {}
        self.prophecy_data = {}

        self.astronomy = None
        self.calendario_cosmico = None
        self.graph_service = None
        self.QuantumMathViewer = None

        self._setup_components()

    def _setup_components(self):
        """Inicialização modular de componentes"""
        try:
            print("Connector: Carregando configurações e dados base...")
            self._load_core_data_config()

            print("Connector: Configurando módulos utilitários...")
            self._setup_utility_modules()

            print("🔶 Modo básico ativado (gráficos simplificados)")
            self._setup_graph_connector()

            print("Connector: Configurando módulo de astronomia...")
            self._setup_astronomy_module()

            print("🌀 Inicializando calendário cósmico...")
            self.calendario_cosmico = CalendarioCosmico()

            self.prophecy_data = self._load_prophecy_data()

            self._initialized = bool(self.tzolk_data and self.tonal_data)
            if self._initialized:
                print(f"🌀 Connector v{self.version} inicializado com sucesso.")
            else:
                raise ValueError("Dados essenciais não foram carregados corretamente.")

        except Exception as e:
            self.logger.critical(f"🚨 ERRO na inicialização do Connector: {e}")
            from utils.basic_astronomy import BasicAstronomy
            self.astronomy = BasicAstronomy()
            self._initialized = False
            
    def initialize_async(self):
        """Inicialização assíncrona dos componentes"""
        self._load_thread = QThread()
        self._loader = _ConnectorLoader(self)
        self._loader.moveToThread(self._load_thread)
    
        self._load_thread.started.connect(self._loader.run)
        self._loader.finished.connect(self._on_loaded)
        self._loader.error.connect(self._on_load_error)
    
        self._load_thread.start()

    def _on_loaded(self):
        print("✅ Connector inicializado com sucesso")
        self._initialized = True
        self.initialized.emit(True)

    def _on_load_error(self, error):
        print(f"🚨 Erro na inicialização: {error}")
        self._initialized = False
        self.initialized.emit(False)

    def _setup_astronomy_module(self):
        """Configuração robusta do módulo de astronomia"""
        try:
            # Verifica se temos todos os requisitos
            if not hasattr(self, 'get_data_path'):
                self.get_data_path = lambda f: Path(__file__).parent.parent / 'data' / f
        
            from calendario_maya.utils.mayan_astronomy import MayanAstronomy
            self.astronomy = MayanAstronomy(self)
            self.version = "4.0"  # Adiciona versão
        
            # Verifica se o módulo está funcional
            test_date = date(2020, 1, 1)
            if not self.astronomy.get_cosmic_calendar(test_date):
                raise RuntimeError("Módulo astronômico retornou dados vazios")
            
        except Exception as e:
            print(f"⚠️ Falha no módulo avançado: {e}")
            from calendario_maya.utils.basic_astronomy import BasicAstronomy
            self.astronomy = BasicAstronomy(self)
            self.version = "4.0-basic"

    def _load_core_data_config(self):
        """Carrega e valida os arquivos JSON principais"""
        print("Connector: Carregando configurações e dados base...")
    
        self.tzolk_data = self._load_and_validate_json('tzolk.json', required_keys=['nahuales', 'constantes'])
        self.tonal_data = self._load_and_validate_json('tonalpohualli.json', required_keys=['signos'])
        self.long_count_data = self._load_json_from_root('longcount.json', optional=True)
    
        if self.tzolk_data: 
            data_bridge.tzolk_data = self.tzolk_data
        if self.tonal_data: 
            data_bridge.tonal_data = self.tonal_data
        
        if self.tzolk_data and self.tonal_data:
            self.data_loaded.emit()
            print("  Dados Tzolk'in e Tonalpohualli carregados")
        else:
            print("  AVISO: Falha ao carregar arquivos principais")

    def _setup_utility_modules(self):
        """Carrega módulos da pasta 'utils' de forma centralizada."""
        print("Connector: Configurando módulos utilitários...")
        utils_to_load = ['astronomy', 'cache', 'historical', 'timeline'] # Especifique os módulos
        for module_name in utils_to_load:
            try:
                module = importlib.import_module(f'utils.{module_name}')
                self._utils_modules[module_name] = module
                print(f"  Módulo utilitário carregado: utils.{module_name}")
            except ImportError as e:
                print(f"⚠️ Falha ao carregar módulo utilitário utils.{module_name}: {e}")
        print("  Módulos utilitários configurados.")

    def _setup_graph_connector(self):
        """Configura o sistema de gráficos com fallback elegante"""
        if not hasattr(self.graph_service, '_has_charts') or not self.graph_service._has_charts:
            print("🔶 Modo básico ativado (gráficos simplificados)")
        
            # Cria dados simulados consistentes
            self.graph_data = {
                'status': 'simulated',
                'series': [{'name': 'Dados Básicos', 'values': []}]
            }
        
            # Fallback para o math_viewer
            from interface.widgets.basic_math import BasicMathViewer
            self.QuantumMathViewer = BasicMathViewer
        else:
            try:
                from interface.widgets.math_viewer import QuantumMathViewer
                self.QuantumMathViewer = QuantumMathViewer
            except ImportError:
                print("🔶 QuantumMathViewer não disponível - usando modo básico")
                from interface.widgets.basic_math import BasicMathViewer
                self.QuantumMathViewer = BasicMathViewer

    def _load_prophecy_data(self):
        try:
            with open(self.get_data_path('prophecy_data.json'), 'r') as f:
                return json.load(f)
        except:
            return [{
                'year': '2020',
                'title': 'Evento de Teste',
                'description': 'Evento de profecia para testes',
                'category': 'Teste'
            }]
        
# Example for theme loading
    def get_theme_path(self, theme_name):
        try:
            themes_dir = self.root_path / 'interface' / 'assets' / 'styles'
            qss_path = themes_dir / f"{theme_name}_theme.qss"
        
            if not qss_path.exists():
                # Create basic fallback theme
                basic_theme = themes_dir / 'basic_theme.qss'
                if not basic_theme.exists():
                    basic_theme.write_text("/* Basic fallback theme */\nQWidget { background: white; }")
                return str(basic_theme)
            
            return str(qss_path)
        except Exception as e:
            print(f"Critical theme loading error: {e}")
            return ""  # Empty style as last resort

    def get_data_path(self, filename):
        """Versão mais robusta com fallback absoluto"""
        try:
            data_dir = self.root_path / 'data'
            path = data_dir / filename
        
            # Cria diretório se não existir
            data_dir.mkdir(parents=True, exist_ok=True)
        
            # Cria arquivo vazio se não existir
            if not path.exists():
                if filename.endswith('.json'):
                    path.write_text('{}')  # Cria JSON vazio
                else:
                    path.touch()
                
            return path
        except Exception as e:
            print(f"Erro crítico em get_data_path: {e}")
            return self.root_path / 'data' / 'fallback.json'
    
    def reload_calendar_data(self):
        """Força o recarregamento dos dados do calendário"""
        print("🔁 Recarregando dados do calendário...")
        try:
            self._load_core_data_config()
            if hasattr(self, 'calendario'):
                self.calendario._carregar_dados()
            self.data_loaded.emit()
            return True
        except Exception as e:
            print(f"⚠️ Falha ao recarregar dados: {e}")
            return False
            
    # Fix date handling in _calculate_tzolkin_day_number
    def _calculate_tzolkin_day_number(self, date):
        try:
            if isinstance(date, QDate):
                date = date.toPyDate()
            elif isinstance(date, (int, float)):
                date = datetime.fromtimestamp(date).date()
            elif not isinstance(date, datetime_date):
                raise ValueError("Invalid date type")
            
            maya_epoch = datetime_date(3114, 8, 11)
            delta = (date - maya_epoch).days
            return (delta % 260) + 1
        except Exception as e:
            self.logger.error(f"Tzolk'in calculation error: {e}")
            return 1

    def get_prophecy_data(self, date=None):
        """Retorna dados de profecia garantindo o formato correto"""
        test_data = [{
            'year': '2020',  # Mantém como string para compatibilidade
            'title': 'Evento de Teste',
            'description': 'Descrição do evento',
            'category': 'Teste',
            'cosmic_data': {  # Adiciona dados cósmicos de exemplo
                'baktun': 13.0,
                'venus_phase': 180.0,
                'earth_angle': 0.0
            }
        }]
        return test_data

    def _generate_prophecy_fallback_data(self, date):
        """Gera dados de profecia de fallback incluindo o ano 2020"""
        year = date.year if date else 2020
        return [{
            'year': year,
            'title': f'Transição Cósmica {year}',
            'description': 'Evento de transição galáctica',
            'category': 'Astronômico',
            'cosmic_data': {
                'baktun': (year + 3114) / 144000,
                'venus_phase': (year * 584) % 360,
                'galactic_progress': ((year + 3114) % 26000) / 260,
                'earth_angle': (year * 365) % 360
            }
        }]

    def generate_basic_prophecies(self):
        """Gera profecias básicas para o novo ciclo"""
        return [{
            'title': 'Fim do 13º Baktun',
            'year': 2012,
            'description': 'Transição para o novo ciclo galáctico',
            'alignment': True,
            'cosmic_data': {
                'baktun': 13.0,
                'venus_phase': 0.0,
                'galactic_progress': 0.0,
                'earth_angle': 0.0
            }
        }]

    # Adicione este novo método para carregamento seguro de eventos:
    def get_timeline_events(self) -> list:
        """Carrega eventos com múltiplos fallbacks e tratamento robusto"""
        fallback_events = [
            {
                'year': -3114,
                'title': 'Início da Conta Longa Maia',
                'description': 'Data de início do calendário maia',
                'category': 'Fundação',
                'cosmic_data': {
                    'baktun': 0.0,
                    'venus_phase': 0.0,
                    'galactic_progress': 0.0,
                    'earth_angle': 0.0
                }
            },
            {
                'year': 2012,
                'title': 'Fim do 13º Baktun',
                'description': 'Transição para novo ciclo galáctico',
                'category': 'Astronômico',
                'cosmic_data': {
                    'baktun': 13.0,
                    'venus_phase': 180.0,
                    'galactic_progress': 100.0,
                    'earth_angle': 0.0
                }
            }
        ]
    
        try:
            # Tenta carregar do arquivo principal
            events_path = self.get_data_path('timeline_events.json')
            if events_path.exists():
                with open(events_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                    # Verifica estrutura do arquivo
                    if isinstance(data, list):
                        return self._process_events(data)
                    elif isinstance(data, dict) and 'events' in data:
                        return self._process_events(data['events'])
                    
            # Fallback para módulo histórico
            if hasattr(self, '_utils_modules') and 'historical' in self._utils_modules:
                historical = self._utils_modules['historical']
                if hasattr(historical, 'get_default_events'):
                    return self._process_events(historical.get_default_events())
                
        except Exception as e:
            print(f"Erro ao carregar eventos: {e}")
        
        return fallback_events

    def _process_events(self, events: list) -> list:
        """Processa e valida eventos, adicionando dados cósmicos"""
        processed = []
        for event in events:
            try:
                if not isinstance(event, dict):
                    continue
                
                # Validação básica
                if 'year' not in event or not str(event['year']).strip('-').isdigit():
                    continue
                    
                # Adiciona dados cósmicos se não existirem
                if 'cosmic_data' not in event:
                    event['cosmic_data'] = self._calculate_cosmic_data(
                        int(event['year']),
                        event.get('month'),
                        event.get('day')
                    )
                
                processed.append(event)
            except Exception as e:
                print(f"Erro ao processar evento: {e}")
            
        return processed

    def _calculate_cosmic_data(self, year: int, month=None, day=None) -> dict:
        """Cálculo seguro de dados cósmicos com fallback"""
        try:
            # Para datas muito antigas, retorna valores básicos
            if year < -3000:
                return {
                    'baktun': 0.0,
                    'venus_phase': 0.0,
                    'galactic_year': 0.0,
                    'earth_angle': 0.0,
                    'is_aligned': False
                }
        
            date = datetime(
                year,
                month if month else 6,  # Padrão: meio do ano
                day if day else 15
            ).date()
    
            if hasattr(self, 'astronomy') and self.astronomy:
                return {
                    'baktun': self.astronomy.calculate_baktun(date),
                    'venus_phase': self.astronomy.venus_phase_angle(date),
                    'galactic_year': self.astronomy.galactic_year_progress(date),
                    'earth_angle': self.astronomy.earth_heliocentric_position(date).get('longitude', 0),
                    'is_aligned': self.astronomy.check_galactic_alignment(date)
                }
        except Exception as e:
            print(f"Erro ao calcular dados cósmicos para ano {year}: {e}")
    
        # Fallback básico
        return {
            'baktun': (year + 3114) / 144000,
            'venus_phase': ((year * 584) % 360),
            'galactic_year': ((year + 3114) % 26000) / 260,
            'earth_angle': (year * 365) % 360,
            'is_aligned': False
        }
           
    def _get_default_data_path(self):
        """Determina o caminho padrão para os dados"""
        return Path(__file__).parent / "data"

    def _load_and_validate_json(self, filename, required_keys):
        data = self._load_json_from_root(filename)
    
        if not data:
            data = {}
    
        if filename == 'tzolk.json':
            if 'constantes' not in data:
                data['constantes'] = {
                    'ciclo_sagrado': 260,
                    'kin_por_uinal': 20,
                    'uinales_por_tun': 18,
                    'dias_por_tun': 360
                }
            if 'nahuales' not in data:
                data['nahuales'] = []
    
        return data

    def _initialize_graph_service(self):
        """Inicialização segura do serviço de gráficos"""
        try:
            # Tenta carregar o serviço real
            from services.graph_service import GraphService
            service = GraphService()
            service._has_charts = True
            return service
        except (ImportError, AttributeError) as e:
            print(f"⚠️ GraphService não disponível - Modo básico: {str(e)}")
        
            # Fallback mínimo que não quebra o sistema
            class DummyService:
                _has_charts = False
                def __getattr__(self, name):
                    return lambda *args, **kwargs: None
                
            return DummyService()
            
    def _load_json_from_root(self, filename: str, optional: bool = False) -> Optional[Dict]:
        # Converte a string de caminho para um objeto Path
        path_obj = Path(self.root_path) / 'data' / filename

        # Agora a verificação funciona corretamente
        if not path_obj.exists():
            if not optional:
                self.logger.error(f"Arquivo JSON obrigatório não encontrado: {path_obj}")
            return None

        try:
            with open(path_obj, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao ler JSON de {path_obj}: {e}")
            return None

    def _load_json_data(self, filename):
        """Carrega arquivos JSON com tratamento robusto"""
        try:
            path = self._get_data_path(filename)
            if not path.exists():
                return self._generate_fallback_data(filename)
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Adiciona cálculos de ciclo aos dados carregados
            if 'events' in data:
                for event in data['events']:
                    event['cycles'] = self._calculate_event_cycles(event)
                
            return data
        
        except Exception as e:
            print(f"Erro ao carregar {filename}: {e}")
            return self._generate_fallback_data(filename)
        
    def _calculate_event_cycles(self, event):
        """Calcula ciclos para um evento histórico"""
        try:
            date_str = event.get('date')
            if not date_str:
                return {}
            
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return {
                'tzolkin': (date_obj.timetuple().tm_yday + 120) % 260,
                'fibonacci': self._generate_fibonacci_position(date_obj)
            }
        except:
            return {}
        
    def _load_glyph_data(self):
        """Carrega dados de glifos com fallback robusto"""
        try:
            glyph_path = self.get_data_path('tzolk.json')
            with open(glyph_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Valida estrutura mínima
            if 'nahuales' not in data or len(data['nahuales']) < 20:
                raise ValueError("Estrutura inválida de nahuales")
            
            return data
        except Exception as e:
            print(f"Erro ao carregar glifos: {e}")
            # Fallback básico
            return {
                'nahuales': [
                    {
                        'nome': f'Nahual {i+1}',
                        'glifo': '',
                        'significado_tradicional': '',
                        'significado_local': ''
                    } for i in range(20)
                ],
                'constantes': {
                    'ciclo_sagrado': 260,
                    'kin_por_uinal': 20
                }
            }
        
    def load_timeline_events(self):
        try:
            from core.config import get_timeline_events_path
            path = get_timeline_events_path()
            if not path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        
            with open(path, 'r', encoding='utf-8') as f:
                self.timeline_events = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar eventos: {e}")
            self.timeline_events = []

    # No arquivo do Connector
    def _load_astronomy_module(self):
        """Carrega módulo de astronomia com fallback"""
        try:
            from calendario_maya.utils.mayan_astronomy import MayanAstronomy
            self.astronomy = MayanAstronomy()
        except ImportError:
            from utils.cosmos_view import CosmosViewBase as FallbackAstro
            self.astronomy = FallbackAstro()
            logging.warning("Usando fallback astronômico")

    def get_astronomical_data(self, date):
        """Retorna dados astronômicos com tratamento robusto de erros"""
        try:
            if hasattr(date, 'toPyDate'):
                py_date = date.toPyDate()
            else:
                py_date = date

            epoch = datetime(2012, 12, 21).date()
            days_since_epoch = (py_date - epoch).days
            
            base_data = {
                'date': py_date.isoformat(),
                'days_since_epoch': days_since_epoch,
                'tzolkin_day': (days_since_epoch % 260) + 1
            }
            
            if hasattr(self, 'astronomy') and self.astronomy:
                astronomical_data = self.astronomy.get_planetary_positions(py_date)
            else:
                astronomical_data = self._get_basic_planetary_data(py_date)
                
            return {**base_data, **astronomical_data}
            
        except Exception as e:
            logging.error(f"Erro ao calcular dados astronômicos: {e}")
            return self._get_fallback_astronomical_data()

    def _calculate_astronomical_positions(self, days_since_epoch):
        """Usar MayanAstronomy para cálculos precisos"""
        try:
            date_obj = self.REFERENCE_DATE + timedelta(days=days_since_epoch)
            astronomy = MayanAstronomy()
            return astronomy.get_planetary_positions(date_obj)
        except Exception as e:
            logging.error(f"Erro em _calculate_astronomical_positions: {str(e)}")
            return self._get_fallback_astronomical_data()
        
    def _get_basic_planetary_data(self, date):
        """Dados planetários básicos como fallback"""
        if hasattr(date, 'toPyDate'):
            date = date.toPyDate()
        days_since_epoch = (date - date(2012, 12, 21)).days
        
        return {
            'sun': {
                'position': (days_since_epoch % 365) / 365 * 360,
                'cycle': '365 dias',
                'phase': (days_since_epoch % 365) / 365
            },
            'venus': {
                'position': (days_since_epoch % 584) / 584 * 360,
                'cycle': '584 dias',
                'phase': (days_since_epoch % 584) / 584
            }
        }

    def _get_cultural_interpretations(self, date):
        """Retorna significados culturais dos corpos celestes"""
        from utils.mayan_math import get_mayan_interpretation
    
        return {
            'interpretations': {
                'sun': get_mayan_interpretation('sun', date),
                'moon': get_mayan_interpretation('moon', date),
                'venus': get_mayan_interpretation('venus', date),
                'mars': get_mayan_interpretation('mars', date)
            }
        }

    def _get_fallback_astronomical_data(self):
        """Dados mínimos quando os cálculos falham"""
        return {
            'sun': {'position': 0, 'cycle': 365.25, 'phase': 0},
            'moon': {'position': 0, 'cycle': 27.3, 'phase': 0},
            'venus': {'position': 0, 'cycle': 584, 'phase': 0},
            'error': 'Modo simplificado ativado'
        }

    def get_tzolkin_for_date(self, date):
        """Versão robusta com tratamento de erros completo"""
        # Verifica e recarrega dados se necessário
        if not hasattr(self, 'tzolk_data') or not self.tzolk_data or 'nahuales' not in self.tzolk_data:
            self._load_core_data_config()
        
            # Se ainda não tiver dados válidos após recarregar
            if not self.tzolk_data or 'nahuales' not in self.tzolk_data:
                logging.error("Dados Tzolk'in não disponíveis mesmo após recarregar")
                return None

        try:
            day_number = self._calculate_tzolkin_day_number(date)
            nahual_index = (day_number - 1) % 20
        
            # Verificação completa dos dados
            if not isinstance(self.tzolk_data['nahuales'], list) or len(self.tzolk_data['nahuales']) < 20:
                raise ValueError("Dados de nahuales incompletos ou formato inválido")
            
            nahual = self.tzolk_data['nahuales'][nahual_index]
        
            # Garante que todos os campos essenciais existam
            return {
                'nahual': {
                    'nome': nahual.get('nome', f'Nahual {nahual_index + 1}'),
                    'glifo': nahual.get('glifo', ''),
                    'significado_tradicional': nahual.get('significado_tradicional', 'Significado não disponível'),
                    'significado_quantico': nahual.get('significado_quantico', ''),
                    'energia': str((day_number - 1) % 13 + 1),
                    'frequencia': self._calculate_frequency(day_number),
                    'cor': nahual.get('cor', '#6a3093')
                },
                'numero_tzolkin': day_number
            }
        
        except Exception as e:
            logging.error(f"Erro grave no cálculo Tzolk'in para {date}: {str(e)}", exc_info=True)
            return {
                'nahual': {
                    'nome': 'Erro',
                    'glifo': '',
                    'significado_tradicional': 'Dados temporariamente indisponíveis',
                    'significado_quantico': '',
                    'energia': '0',
                    'frequencia': '0Hz',
                    'cor': '#FF0000'
                },
                'numero_tzolkin': 0
            }

    def _calculate_frequency(self, day_number):
        """Calcula frequência baseada no número do dia"""
        base_freq = 136.1  # Hz - Frequência base
        return f"{base_freq * ((day_number % 20) + 1):.2f}Hz"

    def get_tonalpohualli_for_date(self, py_date: datetime.date) -> Dict[str, Any]:
        """Retorna informações do Tonalpohualli para uma data gregoriana."""
        if hasattr(self.calendario_cosmico, 'get_tonalpohualli_details'):
            return self.calendario_cosmico.get_tonalpohualli_details(py_date)
        # print("AVISO: get_tonalpohualli_for_date não totalmente implementado no Connector.")
        return {'signo': {'nome': 'Placeholder Tonal Signo'}, 'trecena': 'Y'}

    def gregorian_to_long_count(self, py_date: datetime.date) -> str:
        """Converte uma data gregoriana para a representação da Conta Longa."""
        if hasattr(self.calendario_cosmico, 'convert_gregorian_to_long_count_str'):
            return self.calendario_cosmico.convert_gregorian_to_long_count_str(py_date)
        # print("AVISO: gregorian_to_long_count não totalmente implementado no Connector.")
        return f"{py_date.year}.{py_date.month}.{py_date.day} (LC Placeholder)"
        
    def get_celestial_data(self, date):
        return {
            'sun': {'position': 0, 'energy': 0, 'significance': 'Kinich Ahau'},
            'venus': {'phase': 0, 'angular_dist': 0, 'significance': 'Kukulkán'},
            'earth': {'position': 0, 'cycle': 0, 'significance': 'Hunab Ku'},
            'tzolkin': self._calculate_tzolkin(date),  # Adicionado
            'new_cycle': date.year >= 2012
        }

    def _get_fallback_celestial_data(self):
        """Fallback sem parâmetros"""
        return {
            'sun': {'position': 0, 'energy': 0, 'significance': 'Kinich Ahau'},
            'venus': {'phase': 0, 'angular_dist': 0, 'significance': 'Kukulkán'},
            'earth': {'position': 0, 'cycle': 0, 'significance': 'Hunab Ku'},
            'new_cycle': False
        }

    def _get_basic_celestial_data(self, date):
        """Fallback básico quando os cálculos complexos falham"""
        day_number = (date.toordinal() % 260) + 1  # Simula um ciclo Tzolk'in básico
        return {
            'sun': {
                'distance': 0,
                'azimuth': (day_number % 20) * 18,
                'significance': 'Kinich Ahau (Sol)',
                'energy': (day_number % 13) * 7.7
            },
            'venus': {
                'distance': 0.7,
                'azimuth': (day_number % 8) * 45,
                'significance': 'Kukulkán (Vênus)',
                'energy': (day_number % 20) * 5
            },
            'moon': {
                'distance': 0.5,
                'azimuth': (day_number % 28) * 12.8,
                'significance': 'Ixchel (Lua)',
                'phase': (day_number % 28) / 28 * 100
            }
        }

    def _get_celestial_significance(self, body_name):
        """Retorna o significado ancestral do corpo celeste"""
        significances = {
            'sun': 'Kinich Ahau - O Deus Sol',
            'moon': 'Ixchel - A Deusa Lua',
            'venus': 'Kukulkán - A Serpente Emplumada', 
            'earth': 'Hunab Ku - O Doador de Movimento',
            'mars': 'Guerreiro Vermelho'
        }
        return significances.get(body_name.lower(), '')
        
    def get_historical_events(self, start_year: int, end_year: int) -> list:
        """Obtém eventos históricos com fallback robusto"""
        # Verifica cache primeiro
        if hasattr(self, '_historical_events'):
            cached_events = [e for e in self._historical_events 
                            if start_year <= e.get('year', 0) <= end_year]
            if cached_events:
                return cached_events

        # Tenta carregar de diferentes fontes
        sources = [
            self._load_from_historical_module,
            self._load_from_timeline_file,
            self._get_essential_events
        ]
    
        for source in sources:
            try:
                events = source()
                if events:
                    self._historical_events = events
                    return [e for e in events 
                           if start_year <= e.get('year', 0) <= end_year]
            except Exception as e:
                logging.warning(f"Fonte {source.__name__} falhou: {str(e)}")
    
        return []

    def _load_from_historical_module(self) -> list:
        """Tenta carregar via módulo histórico"""
        historical_module = self._utils_modules.get('historical')
        if historical_module and hasattr(historical_module, 'load_events_from_file'):
            events_path = self.get_data_path('timeline_events.json')
            return historical_module.load_events_from_file(events_path)
        return []

    def _load_from_timeline_file(self) -> list:
        """Tenta carregar diretamente do arquivo"""
        try:
            with open(self.get_data_path('timeline_events.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _get_essential_events(self) -> list:
        """Retorna eventos essenciais como fallback"""
        return [
            {'year': 1325, 'title': 'Fundação de Tenochtitlán', 'description': 'Fundação da capital asteca'},
            {'year': 1519, 'title': 'Chegada dos Espanhóis', 'description': 'Chegada de Hernán Cortés'},
            {'year': 1521, 'title': 'Queda de Tenochtitlán', 'description': 'Fim do Império Asteca'},
        ]

    # --- Factory de Widgets (se mantido) ---
    def create_widget(self, widget_type: str, *args: Any, **kwargs: Any) -> Optional[QWidget]: # Adicionado QWidget
        """Factory method para criar widgets dinamicamente."""
        from PyQt6.QtWidgets import QWidget # Import local para anotação de tipo
        
        if widget_type not in self._widget_classes:
            self._load_widget_class(widget_type)
            
        widget_class = self._widget_classes.get(widget_type)
        if widget_class:
            try:
                # Adiciona 'self' (o connector) automaticamente se o construtor do widget o aceitar
                import inspect
                sig = inspect.signature(widget_class.__init__)
                if 'connector' in sig.parameters and 'connector' not in kwargs:
                    kwargs['connector'] = self
                
                widget = widget_class(*args, **kwargs)
                self.tempo_alterado.emit({'tipo': 'widget_criado', 'nome': widget_type}) # Exemplo de sinal
                return widget
            except Exception as e:
                print(f"⚠️ Erro ao criar widget '{widget_type}': {e}")
                return None
        else:
            print(f"AVISO: Tipo de widget desconhecido no factory: {widget_type}")
            return None
            
    def _load_widget_class(self, widget_type: str):
        """Carrega classes de widget dinamicamente."""
        # Este método de carregamento dinâmico pode ser complexo de manter.
        # Importações diretas no início do módulo são geralmente mais simples.
        try:
            if widget_type == 'CalendarWidget':
                from interface.widgets.calendar_widget import CalendarWidget
                self._widget_classes[widget_type] = CalendarWidget
            elif widget_type == 'GlyphViewer':
                from interface.widgets.glyph_viewer import GlyphViewer
                self._widget_classes[widget_type] = GlyphViewer
                
            else:
                print(f"Definição de carregamento para widget '{widget_type}' não encontrada.")
                self._widget_classes[widget_type] = None
        except ImportError as e:
            print(f"⚠️ Falha na importação ao carregar classe de widget '{widget_type}': {e}")
            self._widget_classes[widget_type] = None
            
    def _calculate_tzolkin(self, date):
        """Calcula o dia no calendário Tzolk'in"""
        days_since_epoch = (date - datetime_date(2012, 12, 21)).days
        return (days_since_epoch % 260) + 1

    # --- Outros Métodos (adaptados ou placeholders) ---
    def calcular_ciclo_temporal(self, q_date: QDate, parametros: Optional[Dict[str, Any]] = None):
        """Calcula ciclos temporais (placeholder, delegar ao calendario_cosmico)."""
        py_date = q_date.toPyDate()
        if hasattr(self.calendario_cosmico, 'calcular_ciclo_para_data'):
            resultado = self.calendario_cosmico.calcular_ciclo_para_data(py_date, parametros)
            self.ciclo_completo.emit({
                'data_gregoriana': py_date.isoformat(),
                'resultado_ciclo': resultado,
                'parametros': parametros
            })
            return resultado
        print(f"AVISO: calcular_ciclo_temporal não totalmente implementado para {py_date}")
        return None
    
    def save_state(self):
        """Salva o estado atual da aplicação (placeholder)."""
        print("Connector: save_state chamado. Implementação pendente.")
        # Ex: salvar self.current_qdate, configurações, etc.

    # Método para atualizar a data corrente no connector, chamado pela MainWindow
    def set_current_date(self, q_date: QDate):
        if q_date.isValid():
            self.current_qdate = q_date
            # print(f"Connector: Data atual definida para {self.current_qdate.toString()}.")
            # Você pode querer emitir um sinal aqui se outros componentes precisam saber
            # self.tempo_alterado.emit({'tipo': 'data_alterada', 'data': self.current_qdate})
   
    @property
    def initialized(self):
        return self._initialized
    
    @property
    def current_date(self):
        return self._current_date
        
    @current_date.setter
    def current_date(self, date):
        if date != self._current_date:
            self._current_date = date
            self.date_changed.emit(date)
            
class DataBridge:
    def __init__(self):
        self._handlers = {}
        self.tzolk_data = {}
        self.tonal_data = {}
        
    def register_handler(self, message_type, handler):
        """Registra handler com verificação de tipo"""
        if not callable(handler):
            raise ValueError("Handler deve ser chamável")
        self._handlers[message_type] = handler
        
    def send_message(self, message_type, payload):
        """Envia mensagem com tratamento de erros"""
        try:
            if message_type in self._handlers:
                self._handlers[message_type](payload)
        except Exception as e:
            print(f"⚠️ Erro no handler para {message_type}: {e}")
            
    def load_data(self, data_type, data):
        """Carrega dados com verificação de estrutura"""
        if data_type == 'tzolk':
            if not isinstance(data, dict) or 'nahuales' not in data:
                raise ValueError("Dados Tzolk'in inválidos")
            self.tzolk_data = data
        elif data_type == 'tonalpohualli':
            if not isinstance(data, dict) or 'signos' not in data:
                raise ValueError("Dados Tonalpohualli inválidos")
            self.tonal_data = data
        else:
            raise ValueError(f"Tipo de dados desconhecido: {data_type}")
            
        self.send_message('data_loaded', {
            data_type: True,
            'timestamp': datetime.now().isoformat()
        })
            
class QuantumCalculator(QThread):
    calculation_done = pyqtSignal(dict)
    
    def __init__(self, date):
        super().__init__()
        self.date = date

    def run(self):
        try:
            result = QuantumMayanMathPlaceholder.calculate_venus_quantum_cycle(self.date)
            self.calculation_done.emit(result)
        except Exception as e:
            print(f"Erro no cálculo quântico: {e}")
            self.calculation_done.emit({'error': str(e)})

class QuantumIntegrationSystem:
    def __init__(self, connector):
        self.connector = connector
        self.quantum_state = {
            'tzolkin_phase': 0.0,
            'venus_phase': 0.0,
            'galactic_alignment': 0.0,
            'harmonic_convergence': 0.0
        }

    def update_quantum_state(self, date):
        """Atualiza o estado quântico com fallback seguro"""
        try:
            if hasattr(self.connector, 'astronomy') and self.connector.astronomy:
                astronomy_data = self.connector.astronomy.get_cosmic_calendar(date)
                venus_data = self.connector.astronomy.calculate_galactic_venus_cycles(date)
                
                self.quantum_state.update({
                    'tzolkin_phase': astronomy_data.get('kin', 1) / 260,
                    'venus_phase': venus_data.get('venus_phase', 0),
                    'galactic_alignment': astronomy_data.get('galactic_alignment', 0),
                    'harmonic_convergence': astronomy_data.get('harmonic_convergence', 0)
                })
            else:
                days_since_epoch = (date - datetime(2012, 12, 21).date()).days
                self.quantum_state.update({
                    'tzolkin_phase': (days_since_epoch % 260) / 260,
                    'venus_phase': (days_since_epoch % 584) / 584,
                    'galactic_alignment': 0.5,
                    'harmonic_convergence': 0.5
                })
                
            return self.quantum_state
            
        except Exception as e:
            self.connector.logger.error(f"Erro ao atualizar estado quântico: {str(e)}")
            return self.quantum_state  # Retorna o último estado válido