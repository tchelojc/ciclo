# main_window.py (parte inicial)
def check_dependencies():
    required = {
        'PyQt6': '6.0.0',
        'numpy': '1.20.0',
        'ephem': '4.1.3'
    }
    
    missing = []
    for pkg, ver in required.items():
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Erro: Dependências faltando: {', '.join(missing)}")
        return False
    return True

if __name__ == "__main__":
    if not check_dependencies():
        exit(1)
        
import sys
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
import numpy as np
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
# Imports absolutos do PyQt6
from PyQt6.QtWidgets import (
    QMainWindow, QHBoxLayout, QWidget, QStackedWidget, 
    QLabel, QVBoxLayout, QStatusBar, QApplication,
    QComboBox, QFormLayout, QScrollBar, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QIcon, QAction

# Imports absolutos da aplicação
from calendario_maya.interface.maya_sidebar import MayanSidebar
from calendario_maya.interface.aztec_sidebar import AztecSidebar
from calendario_maya.interface.widgets.calendar_widget import CalendarWidget
from calendario_maya.interface.widgets.glyph_viewer import GlyphViewer
from calendario_maya.interface.widgets.math_calculator import MathCalculator
from calendario_maya.interface.widgets.cosmos_view import CosmosView
from calendario_maya.interface.widgets.prophecy_viewer import ProphecyViewer, EventListWidget, EventDetailsWidget, ProphecyManager
from calendario_maya.interface.widgets.aztec_calendar import AztecCalendarWidget
from calendario_maya.interface.widgets.aztec_venus_tracker import VenusTracker
from calendario_maya.interface.widgets.tonalamatl_viewer import TonalamatlViewer
from calendario_maya.utils.timeline import TimelineWidget
from calendario_maya.core.quantum_tunnel import QuantumTunnel
from calendario_maya.core.connector import QuantumMayanMathPlaceholder, Connector
from calendario_maya.config import style_loader
from calendario_maya.config.style_manager import StyleManager
from calendario_maya.core.star_map import StarMap

class MainWindow(QMainWindow):
    theme_changed = pyqtSignal(str)
    menu_changed = pyqtSignal(str)
    quantum_state_changed = pyqtSignal(dict)
    prophecy_requested = pyqtSignal(dict)

    def __init__(self, connector):
        super().__init__()
        self.connector = connector
        self.quantum_tunnel = QuantumTunnel(connector)
        self.style_manager = StyleManager(QApplication.instance())  # Inicializa o gerenciador de temas
        self._setup_quantum_connections()
        self.tab_widget = QTabWidget()
        self.content_stack = QStackedWidget()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_quantum_state = {}
        self._update_lock = False
        self._last_update = None
        self.current_theme = 'maya'  # Adiciona variável para controlar o tema atual
        self._component_map = {
            'calendar': 'calendar_widget',
            'glyphs': 'glyph_viewer',
            'timeline': 'timeline_widget',
            'cosmos': 'cosmos_view',
            'math': 'math_viewer',
            'prophecy': 'prophecy_viewer'
        }
        
        try:
            self._setup_logging()
            self._setup_ui()  # O tema será aplicado aqui
            self._verify_required_methods()
            self._verify_initialization()
            self._initialize_components()
            self._setup_connections()
            self._finalize_setup()
        except Exception as e:
            self._handle_initialization_error(e)
            raise

    def _setup_ui(self):
        """Configuração básica com tema cosmológico"""
        try:
            self.style_manager.apply_theme(self.current_theme, self)
            self.setWindowTitle("Calendário Sagrado Maya-Asteca")
            self.resize(1200, 800)
        
            # Configuração da barra de status
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
        
            # Widget central
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
        
            # Layout principal
            self.main_layout = QHBoxLayout(self.central_widget)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
        
            # Sidebar
            self.sidebar_stack = QStackedWidget()
            self.maya_sidebar = MayanSidebar()
            self.aztec_sidebar = AztecSidebar()
        
            # Aplica estilos mínimos para evitar warnings
            self.maya_sidebar.setObjectName("mayaSidebar")
            self.aztec_sidebar.setObjectName("aztecSidebar")
            """Configuração básica com tema cosmológico"""
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    /* Remove warnings de propriedades desconhecidas */
                    border: none;
                }
                /* Adicione outros estilos específicos aqui */
            """)
        
            # Adiciona sidebars ao stack
            self.sidebar_stack.addWidget(self.maya_sidebar)
            self.sidebar_stack.addWidget(self.aztec_sidebar)
            self.main_layout.addWidget(self.sidebar_stack)
        
            # Área de conteúdo
            self.content_stack = QStackedWidget()
            self.main_layout.addWidget(self.content_stack)
        
        except Exception as e:
            self.logger.error(f"Erro na configuração da UI: {str(e)}")
            raise
        
    def is_component_available(self, component_id):
        """Verifica se um componente está disponível"""
        if component_id not in self._component_map:
            return False
        
        widget_name = self._component_map[component_id]
        return hasattr(self, widget_name) and getattr(self, widget_name) is not None
        
    def debug_navigation(self, component_id):
        """Método aprimorado para debug da navegação"""
        debug_info = [
            f"\n--- DEBUG NAVEGAÇÃO ---",
            f"Componente solicitado: {component_id}",
            f"Widget mapeado: {self._component_map.get(component_id, 'NÃO MAPEADO')}",
            f"Total de widgets no stack: {self.content_stack.count()}",
            f"Widget atual: {self.content_stack.currentWidget()}",
            f"Componentes inicializados:"
        ]
    
        for comp_id, widget_name in self._component_map.items():
            widget = getattr(self, widget_name, None)
            debug_info.append(f"- {comp_id}: {'SIM' if widget else 'NÃO'}")
    
        debug_info.append("----------------------")
        print("\n".join(debug_info))
        
    def is_new_cycle_date(self, date):
        """Verifica se uma data está no novo ciclo (pós-21/12/2012)"""
        try:
            from datetime import date as date_type
            if isinstance(date, date_type):
                return date >= date_type(2012, 12, 21)
            return False
        except Exception as e:
            self.logger.error(f"Erro ao verificar ciclo: {str(e)}")
            return False

    def toggle_civilization(self, mode):
        try:
            if mode not in ['maya', 'aztec']:
                raise ValueError("Modo inválido")
        
            self.current_theme = mode
            self.style_manager.apply_theme(mode, self)
        
            # Atualiza a sidebar corretamente
            if mode == 'aztec':
                self.sidebar_stack.setCurrentWidget(self.aztec_sidebar)
            else:
                self.sidebar_stack.setCurrentWidget(self.maya_sidebar)
            
            # Força uma atualização da interface
            QApplication.processEvents()
            return True
        except Exception as e:
            self.logger.error(f"Erro ao trocar tema: {str(e)}")
            return False
    def _setup_connections(self):
        """Configura todas as conexões entre componentes"""
        try:
            # Conexão central de data
            self.connector.date_changed.connect(self.update_all_views)

            # Conexões do túnel quântico
            if hasattr(self, 'quantum_tunnel'):
                self.quantum_tunnel.culture_changed.connect(self.toggle_civilization)

            # Configura os botões da sidebar
            self._setup_sidebar_buttons()
        
            # Conexões da timeline
            if hasattr(self, 'timeline_widget'):
                self.timeline_widget.show_prophecy.connect(self.show_prophecy_view)

            # Conexões do visualizador de profecias
            if hasattr(self, 'prophecy_viewer'):
                try:
                    if hasattr(self.prophecy_viewer, 'event_selected'):
                        self.prophecy_viewer.event_selected.connect(self.handle_prophecy_event)
                except Exception as e:
                    self.logger.error(f"Erro ao conectar sinais de profecia: {str(e)}")

        except Exception as e:
            self.logger.error(f"Erro na configuração de conexões: {str(e)}")
        
    def _change_content(self, component_id):
        """Muda o conteúdo exibido de forma segura e robusta"""
        try:
            # Verifica se o componente está mapeado
            if component_id not in self._component_map:
                self.logger.warning(f"Componente {component_id} não está mapeado")
                return

            widget_name = self._component_map[component_id]

            # Debug: mostra informações de navegação
            self.debug_navigation(component_id)
        
            # Verifica se o widget existe e está inicializado
            if not hasattr(self, widget_name) or getattr(self, widget_name) is None:
                # Tenta inicializar o componente se não existir
                initializer = getattr(self, f"init_{widget_name}", None)
                if initializer and not initializer():
                    self._handle_missing_component(component_id)
                    return

            # Obtém o widget
            widget = getattr(self, widget_name)
            if widget is None:
                self._handle_missing_component(component_id)
                return
            
            # Muda para o widget
            if widget not in [self.content_stack.widget(i) for i in range(self.content_stack.count())]:
                self.content_stack.addWidget(widget)
            
            self.content_stack.setCurrentWidget(widget)
            self.logger.debug(f"Componente {component_id} ativado com sucesso")
        
        except Exception as e:
            self.logger.error(f"Erro ao mudar para {component_id}: {str(e)}")
            self._handle_missing_component(component_id)
        
    def verify_data_files():
        """Verifica se todos os arquivos necessários existem"""
        required_files = [
            'tzolk.json',
            'tonalpohualli.json',
            'historical_events.json',
            'timeline_events.json'
        ]
    
        missing = []
        for file in required_files:
            path = get_data_path() / file
            if not path.exists():
                missing.append(file)
    
        if missing:
            print(f"AVISO: Arquivos essenciais faltando: {', '.join(missing)}")
            print("Alguns recursos podem não funcionar corretamente")
        
        return len(missing) == 0
  
    def _handle_missing_component(self, component_id, silent=False):
        """Mostra uma mensagem quando um componente não está disponível"""
        if silent:
            return
        
        names = {
            'calendar': 'Calendário',
            'glyphs': 'Visualizador de Glifos',
            'timeline': 'Linha do Tempo',
            'cosmos': 'Visualização Cósmica',
            'math': 'Calculadora Matemática',
            'prophecy': 'Visualizador de Profecias'
        }
    
        friendly_name = names.get(component_id, component_id)
        self.status_bar.showMessage(f"{friendly_name} não disponível", 3000)
        self.logger.warning(f"Tentativa de acessar componente não disponível: {component_id}")
    
    def verify_dependencies():
        required = {
            'PyQt6': '6.0.0',
            'numpy': '1.20.0',
            'astropy': '4.2'
        }
    
        missing = []
        for package, version in required.items():
            try:
                mod = __import__(package)
                if hasattr(mod, '__version__') and mod.__version__ < version:
                    missing.append(f"{package} (versão {version} requerida)")
            except ImportError:
                missing.append(package)
    
        if missing:
            raise ImportError(f"Dependências faltando ou desatualizadas: {', '.join(missing)}")
   
    def verify_data_integrity(self):
        """Verifica se todos os dados necessários estão carregados"""
        required_data = {
            'nahuales': 20,
            'energias': 13,
            'glifos': 20
        }
    
        for key, expected in required_data.items():
            actual = len(self.connector.get_data(key))
            if actual != expected:
                self.logger.error(f"Dados incompletos: {key} (esperado: {expected}, obtido: {actual})")
                return False
        return True
    
    def safe_component_initialization(self, component_name, initializer):
        """Tenta inicializar um componente com múltiplas tentativas"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                result = initializer()
                if result:
                    return True
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt + 1} falhou para {component_name}: {str(e)}")
                time.sleep(1)  # Espera antes de tentar novamente
    
        self.logger.error(f"Falha ao inicializar {component_name} após {max_attempts} tentativas")
        self._show_component_error(component_name)
        return False
    
    def _setup_quantum_connections(self):
        self.quantum_tunnel.transition_started.connect(self._freeze_ui)
        self.quantum_tunnel.transition_completed.connect(self._unfreeze_ui)
        self.quantum_tunnel.culture_changed.connect(self.toggle_civilization)
     
    def _verify_required_methods(self):
        """Verificação atualizada dos métodos obrigatórios"""
        required_methods = [
            'init_calendar_widget',  # Nome consistente com a implementação existente
            'init_glyph_viewer',     # Nome do método que já existe
            'init_timeline_widget',  # Nome consistente
            'init_cosmos_view',      # Já existe
            'init_math_viewer',      # Já existe
            'init_prophecy_component'# Nome do método existente
        ]
    
        missing_methods = [m for m in required_methods if not hasattr(self, m)]
        if missing_methods:
            error_msg = f"Métodos obrigatórios não implementados: {', '.join(missing_methods)}"
            self.logger.critical(error_msg)
            raise NotImplementedError(error_msg)
    
    def _setup_logging(self):
        """Configura o sistema de logging"""
        self.logger = logging.getLogger('MainWindow')
        handler = RotatingFileHandler(
            'app.log',
            maxBytes=1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def _verify_dependencies(self):
        """Verifica dependências críticas"""
        try:
            from dependencies import verify_qt_dependencies
            verify_qt_dependencies()
        except ImportError as e:
            self.logger.critical(f"Falha na verificação de dependências: {e}")
            raise
        
    def _handle_initialization_error(self, error):
        """Trata erros durante a inicialização"""
        self.logger.critical(f"Erro na inicialização: {str(error)}")
    
        # Mensagem de erro crítica
        error_msg = QLabel(f"""
            <div style='text-align: center; padding: 50px;'>
                <h2 style='color: #ff0000;'>ERRO CRÍTICO</h2>
                <p style='font-size: 16px;'>{str(error)}</p>
                <p style='color: #aaaaaa;'>Verifique os logs para mais detalhes</p>
            </div>
        """)
        error_msg.setTextFormat(Qt.TextFormat.RichText)
    
        # Configura a janela principal para mostrar apenas o erro
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(error_msg)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
        # Garante que a janela possa ser fechada
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
    def _verify_initialization(self):
        """Verifica se todos os componentes foram inicializados"""
        required_components = [
            'calendar_widget', 'glyph_viewer', 'timeline_widget',
            'cosmos_view', 'math_viewer', 'prophecy_viewer'
        ]
    
        for comp in required_components:
            if not hasattr(self, comp) or getattr(self, comp) is None:
                self.logger.error(f"Componente {comp} não inicializado corretamente")

    def _initialize_components(self):
        """Inicialização robusta de todos os componentes"""
        # Ordem de inicialização cuidadosamente definida
        components_order = [
            ('calendar_widget', self.init_calendar_widget, "Calendário"),
            ('glyph_viewer', self.init_glyph_viewer, "Visualizador de Glifos"),
            ('timeline_widget', self.init_timeline_widget, "Linha do Tempo"),
            ('cosmos_view', self.init_cosmos_view, "Visualização Cósmica"),
            ('math_viewer', self.init_math_viewer, "Calculadora Matemática"),
            ('prophecy_viewer', self.init_prophecy_component, "Visualizador de Profecias")
        ]

        for attr_name, initializer, friendly_name in components_order:
            try:
                if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
                    if not initializer():
                        self.logger.error(f"Falha ao inicializar {friendly_name}")
                        self._show_component_error(attr_name.split('_')[0])
            except Exception as e:
                self.logger.error(f"Erro na inicialização de {friendly_name}: {str(e)}")
                self._show_component_error(attr_name.split('_')[0])
            
    def _setup_sidebar_buttons(self):
        """Configura todos os botões da sidebar"""
        try:
            # Mapeamento de botões para componentes
            self.buttons = {
                'calendar': self.maya_sidebar.calendar_btn,
                'glyphs': self.maya_sidebar.glyphs_btn,
                'timeline': self.maya_sidebar.timeline_btn,
                'cosmos': self.maya_sidebar.cosmos_btn,
                'math': self.maya_sidebar.math_btn,
                'prophecy': self.maya_sidebar.prophecy_btn
            }
        
            # Conecta cada botão
            for btn_name, button in self.buttons.items():
                button.clicked.connect(
                    lambda _, name=btn_name: self.on_button_clicked(name))
                
            # Define o botão inicial como ativo
            self.set_active_button('calendar')
        
        except Exception as e:
            self.logger.error(f"Erro ao configurar botões da sidebar: {str(e)}")
        
    def init_calendar_widget(self):
        try:
            from .widgets.calendar_widget import CalendarWidget
            self.calendar_widget = CalendarWidget(connector=self.connector, parent=self)
            self.content_stack.addWidget(self.calendar_widget)  # Adiciona ao stack
            return True
        except Exception as e:
            self.logger.error(f"Falha ao inicializar calendário: {str(e)}")
            return False

    def init_glyph_viewer(self):
        try:
            from .widgets.glyph_viewer import GlyphViewer
            self.glyph_viewer = GlyphViewer(connector=self.connector, parent=self)
            self.content_stack.addWidget(self.glyph_viewer)  # Adiciona ao stack
            return True
        except Exception as e:
            self.logger.error(f"Falha ao inicializar visualizador de glifos: {str(e)}")
            return False
            
    def init_timeline_widget(self):
        """Inicialização mais segura da timeline"""
        try:
            if not hasattr(self, 'timeline_widget'):
                from calendario_maya.utils.timeline import TimelineWidget
                self.timeline_widget = TimelineWidget(connector=self.connector)
                self.content_stack.addWidget(self.timeline_widget)
            
                # Conecta os sinais
                self.timeline_widget.event_clicked.connect(self.show_event_detail)
            
            return True
        except Exception as e:
            print(f"Falha ao inicializar timeline: {e}")
            return False

    def _setup_timeline_navigation(self):
        """Configuração segura da navegação da timeline"""
        if not hasattr(self, 'timeline_widget'):
            self.logger.error("TimelineWidget não inicializado para configuração de navegação")
            return

        try:
            # Configuração básica
            self.timeline_widget.setup_navigation_controls()
        
            # Configuração da barra de rolagem com conversão para inteiros
            min_val = int(self.timeline_widget.year_to_x(self.timeline_widget.min_year))
            max_val = int(self.timeline_widget.year_to_x(self.timeline_widget.max_year))
        
            scroll_bar = QScrollBar(Qt.Orientation.Horizontal)
            scroll_bar.setRange(min_val, max_val)
            scroll_bar.valueChanged.connect(self.timeline_widget.on_scroll)
        
            # Adição ao layout se existir
            if hasattr(self.timeline_widget, 'layout') and isinstance(self.timeline_widget.layout, QVBoxLayout):
                self.timeline_widget.layout.addWidget(scroll_bar)
            
        except Exception as e:
            self.logger.error(f"Erro na configuração de navegação: {str(e)}")
            # Fallback: apenas configuração básica
            self.timeline_widget.setup_navigation_controls()
            
    def _setup_basic_configuration(self):
        """Configuração inicial sem dependências complexas"""
        self.setWindowTitle("Calendário Sagrado Maya-Asteca")
        self.resize(1200, 800)
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

    def _init_ui_components(self):
        """Inicialização dos componentes de UI"""
        self.logger.debug("Inicializando componentes de UI")
        
        # Sidebars
        self._init_sidebars()
        
        # Área de conteúdo principal
        self._init_content_area()

    def _init_sidebars(self):
        """Inicialização robusta das sidebars com tratamento de erro"""
        try:
            self.sidebar_stack = QStackedWidget()
        
            # Maya Sidebar
            from .maya_sidebar import MayanSidebar
            from .aztec_sidebar import AztecSidebar
        
            self.maya_sidebar = MayanSidebar()
            self.maya_sidebar.setObjectName("mayaSidebar")
            self.maya_sidebar.setStyleSheet("#mayaSidebar { background-color: #0a0a1a; }")
        
            # Aztec Sidebar
            self.aztec_sidebar = AztecSidebar()
            self.aztec_sidebar.setObjectName("aztecSidebar")
            self.aztec_sidebar.setStyleSheet("#aztecSidebar { background-color: #1a0a0a; }")
        
            # Adiciona widgets
            self.sidebar_stack.addWidget(self.maya_sidebar)
            self.sidebar_stack.addWidget(self.aztec_sidebar)
            self.main_layout.addWidget(self.sidebar_stack)
        
            # Conexões de sinais
            self.maya_sidebar.menu_changed.connect(self._change_content)
            self.aztec_sidebar.menu_changed.connect(self._change_content)
        
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sidebars: {str(e)}")
            # Fallback básico
            self.sidebar_stack = QLabel("Menu Indisponível")
            self.sidebar_stack.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.sidebar_stack)

    def _init_content_area(self):
        """Inicialização controlada da área de conteúdo"""
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)
    
        # Dicionário de inicializadores com nomes amigáveis
        initializers = {
            'Calendário': self.init_calendar_widget,
            'Glifos': self.init_glyph_viewer,
            'Linha do Tempo': self.init_timeline,
            'Visualização Cósmica': self.init_cosmos_view,
            'Matemática': self.init_math_viewer,
            'Profecias': self._init_prophecy_tab
        }
    
        for name, initializer in initializers.items():
            try:
                self.logger.info(f"Iniciando {name}")
                initializer()
                self.logger.info(f"{name} inicializado com sucesso")
            except Exception as e:
                self.logger.error(f"Falha ao inicializar {name}: {str(e)}")
                self._show_component_error(name.lower().replace(' ', '_'))

    def _show_component_error(self, component_name):
        """Mostra um widget de fallback para componentes que falharam"""
        display_names = {
            'calendar': 'Calendário',
            'glyphs': 'Glifos Sagrados',
            'timeline': 'Linha do Tempo',
            'cosmos': 'Visualização Cósmica',
            'math': 'Matemática Maia',
            'prophecy': 'Profecias'
        }
    
        fallback = QLabel(f"""
            <div style='text-align: center; padding: 30px;'>
                <h3 style='color: #ff5555'>{display_names.get(component_name, component_name)} Indisponível</h3>
                <p>Recurso temporariamente desativado</p>
                <p>Verifique os logs para detalhes</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        setattr(self, f"{component_name}_fallback", fallback)
        self.content_stack.addWidget(fallback)

    def _load_styles(self):
        """Carrega estilos com fallback robusto"""
        try:
            # Tenta carregar o tema Maya completo
            maya_style_path = Path(__file__).parent.parent / "interface" / "assets" / "styles" / "maya_theme.qss"
            if maya_style_path.exists():
                with open(maya_style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
                return
        
            # Fallback básico
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #0a0a1a;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #1a3d1a;
                    color: white;
                    padding: 5px;
                }
            """)
                
        except Exception as e:
            print(f"Erro ao carregar estilos: {e}")

    def apply_aztec_theme(self):
        """Tema completo Asteca"""
        aztec_style = """
        /* Adicione aqui todos os estilos específicos */
        QMainWindow {
            background-color: #1a0a0a;
            border: 2px solid #5a0000;
        }
        """
        self.setStyleSheet(self.styleSheet() + aztec_style)

    def apply_maya_theme(self):
        """Tema completo Maia"""
        maya_style = """
        /* Adicione aqui todos os estilos específicos */
        QMainWindow {
            background-color: #0a0a1a;
            border: 2px solid #00005a;
        }
        """
        self.setStyleSheet(self.styleSheet() + maya_style)

    def check_opengl_support(self):
        """Verificação mais segura"""
        try:
            from PyQt6.QtOpenGL import QOpenGLWindow
            test_window = QOpenGLWindow()
            test_window.destroy()
            return True
        except:
            return False
        
    def _freeze_ui(self):
        """Congela a UI durante transição"""
        self.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        
    def _unfreeze_ui(self):
        """Descongela a UI após transição"""
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def show_critical_error(self, message):
        """Mostra uma mensagem de erro crítica"""
        error_label = QLabel(f"ERRO CRÍTICO:\n{message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("""
            QLabel {
                color: #ff0000;
                font-size: 16px;
                font-weight: bold;
                background: #300000;
                padding: 20px;
            }
        """)
        self.setCentralWidget(error_label)
    
    def setup_cosmic_theme(self):
        """Aplica o tema cósmico completo"""
        cosmic_theme = """
        /* Garante que todos os QTextEdit tenham contraste */
        QTextEdit {
            background-color: #000033;
            color: #ffffff;
            border: 1px solid #4466ff;
            padding: 10px;
        }
    
        /* Garante visibilidade nos QLabel */
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
    
        /* Estilo para as abas */
        QTabWidget::pane {
            border: 1px solid #4466ff;
            background: #000033;
        }
    
        QTabBar::tab {
            background: #1a1a5a;
            color: #a0a0ff;
            padding: 8px;
            border: 1px solid #4466ff;
        }
        """
        self.setStyleSheet(cosmic_theme)
    
    def setup_status_bar(self):
        """Configura a barra de status"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema pronto", 3000)

    def setup_main_layout(self):
        """Configura o layout principal"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
    
        # Área de conteúdo principal
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack)

    def setup_sidebar(self):
        """Configura a sidebar com temas"""
        self.sidebar_stack = QStackedWidget()
        self.sidebar_stack.setFixedWidth(200)
    
        # Adiciona as sidebars
        self.maya_sidebar = MayanSidebar()
        self.aztec_sidebar = AztecSidebar()
        self.sidebar_stack.addWidget(self.maya_sidebar)
        self.sidebar_stack.addWidget(self.aztec_sidebar)
    
        # Insere a sidebar no layout
        self.main_layout.insertWidget(0, self.sidebar_stack)
        self.sidebar_stack.setCurrentWidget(self.maya_sidebar)
 
    def apply_quantum_theme(self, theme):
        """Versão simplificada sem StyleManager"""
        try:
            if theme == "aztec":
                self.apply_aztec_theme()
            else:
                self.apply_maya_theme()
            self.current_quantum_state['theme'] = theme
            self.quantum_state_changed.emit(self.current_quantum_state)
        except Exception as e:
            logging.error(f"Erro ao aplicar tema: {str(e)}")
        
    def handle_quantum_change(self, state):
        """Lida com mudanças no estado quântico"""
        try:
            if 'theme' in state:
                self.apply_quantum_theme(state['theme'])
            if 'time_flow' in state:
                self.adjust_time_flow(state['time_flow'])
        except Exception as e:
            logging.error(f"Erro na transição quântica: {str(e)}")

    def init_timeline(self) -> bool:
        """Inicializa o componente de linha do tempo"""
        try:
            if not hasattr(self, 'timeline_widget'):
                from calendario_maya.utils.timeline import TimelineWidget
                self.timeline_widget = TimelineWidget(self.connector)
                self.tab_widget.addTab(self.timeline_widget, "Linha do Tempo")
        
            # Configuração inicial da timeline
            if hasattr(self.timeline_widget, 'initialize'):
                return self.timeline_widget.initialize()
        
            return True
        except Exception as e:
            logging.error(f"Falha ao inicializar timeline: {str(e)}")
            return False

    def _show_fallback(self, component_name, display_name):
        """Cria um widget de fallback padronizado"""
        fallback = QLabel(f"""
            <div style='text-align: center; padding: 30px;'>
                <h3 style='color: #ff5555'>{display_name} Indisponível</h3>
                <p>Recurso temporariamente desativado</p>
                <p>Verifique os logs para detalhes</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        setattr(self, f"{component_name}_fallback", fallback)
        self.content_stack.addWidget(fallback)
    
    def init_calendar_fallback(self):
        """Fallback para o widget do calendário"""
        fallback = QLabel("Calendário Sagrado (Modo Básico)")
        fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback.setStyleSheet("""
            QLabel {
                color: #e0ffe0;
                font-size: 16px;
                background: #1a3d1a;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.content_stack.addWidget(fallback)
        self.current_quantum_state['calendar'] = 'fallback'
    
    def init_content_widgets(self):
        """Inicialização com superposição quântica de estados"""
        # Widgets essenciais (sempre presentes)
        self.init_calendar_widget()
        self.init_glyph_viewer()
        self.init_timeline()
        
        # Widgets em superposição (podem colapsar para fallback)
        self.init_quantum_widgets()

    def init_glyph_fallback(self):
        """Fallback para visualização de glifos"""
        fallback = QLabel("Glifos Sagrados (Modo Básico)")
        fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback.setStyleSheet("""
            QLabel {
                color: #ffe0e0;
                font-size: 16px;
                background: #3d1a1a;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.content_stack.addWidget(fallback)
        self.current_quantum_state['glyphs'] = 'fallback'

    def init_essential_widgets(self):
        """Inicializa widgets sem duplicação"""
        try:
            logging.debug("Iniciando widgets essenciais")
        
            # Widget principal baseado na preferência
            if getattr(self.connector, 'prefer_prophecy_view', False):
                self.init_prophecy_tab()
            else:
                self.init_timeline()
            
            # Demais widgets
            self.init_calendar_widget()
            self.init_glyph_viewer()
            self.init_cosmos_view()
            self.init_math_viewer()
        
        except Exception as e:
            logging.error(f"Falha na inicialização: {str(e)}")
            self.show_critical_error(str(e))

    def _init_prophecy_tab(self):
        """Inicializa a aba de profecias"""
        try:
            # Correção no caminho de importação
            from calendario_maya.interface.widgets.prophecy_viewer import ProphecyViewer
            self.prophecy_viewer = ProphecyViewer(self.connector)
            self.content_stack.addWidget(self.prophecy_viewer)
            return True
        except Exception as e:
            self.logger.error(f"Falha ao inicializar profecias: {str(e)}")
            self._init_prophecy_fallback()
            return False

    # ADICIONE AQUI O NOVO MÉTODO
    def toggle_prophecy_mode(self, enabled):
        """Alterna entre timeline e prophecy viewer"""
        logging.debug(f"Alternando modo profecia: {'Ativado' if enabled else 'Desativado'}")
    
        # Atualiza o connector
        self.connector.prefer_prophecy_view = enabled
    
        try:
            if enabled:
                self.init_prophecy_tab()
            else:
                if hasattr(self, 'prophecy_viewer'):
                    self.content_stack.removeWidget(self.prophecy_viewer)
                    self.prophecy_viewer.deleteLater()
                    del self.prophecy_viewer
                self.init_timeline()
            
            # Atualiza a sidebar
            if hasattr(self, 'maya_sidebar'):
                self.maya_sidebar.set_active_button('prophecy' if enabled else 'timeline')
            
        except Exception as e:
            logging.error(f"Erro ao alternar modo profecia: {str(e)}")
            self.show_critical_error(f"Falha ao alternar visualização: {str(e)}")

    def init_connections(self):
        """Configura todas as conexões entre componentes"""
        logging.debug("Configurando conexões")
    
        # Conexões existentes...
        if hasattr(self, 'timeline'):
            self.timeline.show_prophecy.connect(self.show_prophecy_viewer)
        
    def show_timeline(self):
        """Mostra a timeline com tratamento seguro"""
        try:
            if hasattr(self, 'timeline'):
                self.content_stack.setCurrentWidget(self.timeline)
                self.maya_sidebar.set_active_button('timeline')
            elif hasattr(self, 'timeline_fallback'):
                self.content_stack.setCurrentWidget(self.timeline_fallback)
        except Exception as e:
            self.logger.error(f"Erro ao mostrar timeline: {str(e)}")

    def show_prophecy(self):
        """Mostra as profecias com tratamento seguro"""
        try:
            if hasattr(self, 'prophecy_viewer'):
                self.content_stack.setCurrentWidget(self.prophecy_viewer)
                self.maya_sidebar.set_active_button('prophecy')
            elif hasattr(self, 'prophecy_fallback'):
                self.content_stack.setCurrentWidget(self.prophecy_fallback)
        except Exception as e:
            self.logger.error(f"Erro ao mostrar profecia: {str(e)}")

    def set_active_button(self, mode):
        """Define qual botão deve aparecer como ativo"""
        # Verifica se os botões foram inicializados
        if not hasattr(self, 'buttons') or not self.buttons:
            self.logger.warning("Nenhum botão disponível para ativação")
            return
    
        # Remove estilo do botão ativo atual
        if hasattr(self, 'active_button') and self.active_button:
            self.active_button.setStyleSheet("")
    
        # Define o novo botão ativo
        if mode in self.buttons:
            self.active_button = self.buttons[mode]
            self.active_button.setStyleSheet("""
                background-color: #1a3a5a;
                border-left: 4px solid #4ecca3;
            """)

    def on_button_clicked(self, btn_name):
        """Lida com o clique nos botões do menu"""
        try:
            # Atualiza o botão ativo
            self.set_active_button(btn_name)
        
            # Navega para o componente correspondente
            if hasattr(self, 'content_stack'):
                self._change_content(btn_name)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar clique no botão {btn_name}: {str(e)}")
        
    def init_timeline_fallback(self):
        """Cria um fallback para a timeline"""
        fallback = QLabel("""
            <div style='text-align: center; padding: 30px;'>
                <h3 style='color: #ff5555'>Linha do Tempo Indisponível</h3>
                <p>O componente não pôde ser carregado</p>
                <p>Recarregue ou verifique os arquivos de dados</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        self.content_stack.addWidget(fallback)
        self.timeline_fallback = fallback

    def reload_timeline(self):
        """Tenta recarregar a timeline"""
        self.content_stack.removeWidget(self.content_stack.currentWidget())
        self.init_timeline()

    def init_timeline_component(self):
        """Inicializa o componente de linha do tempo"""
        self.timeline_widget = TimelineWidget(connector=self.connector, parent=self)
    
        # Configura a navegação
        self._setup_timeline_navigation()
    
        # Adiciona ao layout principal
        self.main_layout.addWidget(self.timeline_widget)
    
        # Conecta sinais
        self.timeline_widget.year_selected.connect(self._on_year_selected)
        self.timeline_widget.event_clicked.connect(self._show_event_detail)

    def init_prophecy_component(self):
        try:
            from .widgets.prophecy_viewer import ProphecyViewer
            self.prophecy_viewer = ProphecyViewer(self.connector)
            self.content_stack.addWidget(self.prophecy_viewer)
            return True
        except Exception as e:
            self._init_prophecy_fallback()
            return False

    def _init_prophecy_fallback(self):
        fallback = QLabel("""
            <div style='text-align: center; padding: 30px;'>
                <h3 style='color: #ff5555'>Profecias Indisponíveis (Erro)</h3>
                <p>O componente não pôde ser carregado devido a um erro</p>
                <p>Verifique os logs para detalhes</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        self.prophecy_fallback = fallback
        self.content_stack.addWidget(fallback)
        
    def handle_prophecy_event(self, event_data):
        """Método para lidar com eventos de profecia selecionados"""
        try:
            if hasattr(self, 'prophecy_viewer'):
                self.prophecy_viewer.show_event_detail(event_data)
            elif hasattr(self, 'event_detail_widget'):
                self.event_detail_widget.show_event(event_data)
            else:
                self.status_bar.showMessage("Visualizador de profecias não disponível", 3000)
        except Exception as e:
            self.logger.error(f"Erro ao processar evento de profecia: {str(e)}")
        
    def _init_astronomy_module(self):
        """Inicializa o módulo de astronomia maia com fallback"""
        try:
            from calendario_maya.utils.mayan_astronomy import MayanAstronomy
            self.astronomy = MayanAstronomy(self.connector)
            # Garantir que a data de referência está definida
            if not hasattr(self.astronomy, 'REFERENCE_DATE'):
                self.astronomy.REFERENCE_DATE = date(2012, 12, 21)
            self.logger.debug("Módulo astronômico avançado carregado")
        except ImportError as e:
            self.logger.warning(f"Módulo MayanAstronomy não encontrado: {str(e)}")
            from calendario_maya.utils.basic_astronomy import BasicAstronomy
            self.astronomy = BasicAstronomy(self.connector)

    def init_quantum_widgets(self):
        """Inicializa widgets com comportamento quântico"""
        # Visualização Cósmica
        self.init_cosmos_view()
        
        # Calculadora Matemática
        self.init_math_viewer()

    def init_cosmos_view(self):
        """Inicialização robusta da visualização cósmica"""
        try:
            if not hasattr(self, 'cosmos_view'):
                from PyQt6.QtGui import QPainter
                from calendario_maya.interface.widgets.cosmos_view import CosmosView
                from calendario_maya.core.star_map import StarMap
            
                # Corrige o problema do QPainter.Antialiasing
                QPainter.Antialiasing = QPainter.RenderHint.Antialiasing
            
                # Inicializa componentes
                self.star_map = StarMap()
            
                # Cria a view com tratamento de erros
                try:
                    self.cosmos_view = CosmosView(self.connector)
                    self.content_stack.addWidget(self.cosmos_view)
                
                    # Conecta sinais
                    self.connector.date_changed.connect(
                        self.cosmos_view.update_cosmic_view
                    )
                
                    return True
                except Exception as view_error:
                    self.logger.error(f"Falha ao criar CosmosView: {str(view_error)}")
                    return False
                
        except ImportError as e:
            self.logger.error(f"Erro de importação na CosmosView: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado na inicialização da CosmosView: {str(e)}")
            return False

    def calculate_cosmic_data(self, date):
        """Calcula dados cósmicos considerando o novo ciclo após 21/12/2012"""
        try:
            from datetime import datetime

            # Define a data de início do novo ciclo
            new_cycle_start = datetime(2012, 12, 21).date()
            is_new_cycle = date.date() >= new_cycle_start

            # Seleciona os métodos de acordo com o ciclo
            if is_new_cycle:
                return {
                    'cycle': 'new',
                    'baktun': self._calculate_new_cycle_baktun(date),
                    'planetary': self._calculate_planetary_positions(date),
                    'frequencies': self._calculate_new_frequencies(date)
                }
            else:
                return {
                    'cycle': 'old',
                    'baktun': self._calculate_old_cycle_baktun(date),
                    'planetary': self._calculate_planetary_positions(date),
                    'frequencies': self._calculate_old_frequencies(date)
                }

        except Exception as e:
            self.logger.error(f"Erro ao calcular dados cósmicos: {str(e)}")
            return {'error': str(e)}
    
    def update_astronomical_view(self):
        """Atualiza a visualização astronômica, se disponível"""
        try:
            now = datetime.now()
            cosmic_data = self.connector.get_cosmic_data(now)
            cycle_data = astronomy_utils.calculate_cycles(now)

            if hasattr(self, 'cosmos_view') and self.cosmos_view:
                if hasattr(self.cosmos_view, 'update_cosmic_view'):
                    self.cosmos_view.update_cosmic_view(cosmic_data)

                if hasattr(self.cosmos_view, 'update_cycle_display'):
                    self.cosmos_view.update_cycle_display(cycle_data)
            else:
                self.logger.warning("cosmos_view não inicializado para update_astronomical_view")

        except Exception as e:
            self.logger.error(f"Erro ao atualizar visualização astronômica: {str(e)}")
    
    def _init_cosmos_fallback(self):
        """Fallback para visualização cósmica"""
        fallback = QLabel("""
            <div style='text-align: center; padding: 30px;'>
                <h3 style='color: #ff5555'>Visualização Astronômica Indisponível</h3>
                <p>Recurso temporariamente desativado</p>
                <p>Verifique os logs para detalhes</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        self.content_stack.addWidget(fallback)
        self.cosmos_fallback = fallback

    def init_math_viewer(self):
        """Inicializa o visualizador matemático"""
        try:
            self.logger.debug("Inicializando visualizador matemático")
            self.math_viewer = MathCalculator(connector=self.connector)
            self.content_stack.addWidget(self.math_viewer)
        except Exception as e:
            self.logger.error(f"Falha ao inicializar matemática: {str(e)}")
            raise

    def init_math_fallback(self):
        """Fallback harmônico para matemática"""
        fallback = QLabel("Cálculos Matemáticos (Modo Sagrado)")
        fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback.setStyleSheet("""
            QLabel {
                color: #ffffe0;
                font-size: 16px;
                background: #3d3d1a;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.content_stack.addWidget(fallback)

    def update_all_views(self, date):
        """Atualiza todos os componentes com a nova data"""
        components = [
            ('calendar_widget', 'update_display'),
            ('glyph_viewer', 'update_glyphs'),
            ('math_viewer', 'update_calculations'),
            ('cosmos_view', 'update_cosmic_view'),
            ('timeline_widget', 'sync_with_date')
        ]
    
        for widget_name, method in components:
            try:
                widget = getattr(self, widget_name, None)
                if widget and hasattr(widget, method):
                    getattr(widget, method)(date)
            except Exception as e:
                print(f"Erro atualizando {widget_name}: {e}")

    def _print_debug_info(self, date):
        """Imprime informações de debug de forma organizada"""
        if hasattr(self, 'math_viewer'):
            try:
                print("[MATH DEBUG] Cálculos atualizados:")
                print(f"- Kin: {self.math_viewer._calculate_kin_number(date)}")
                print(f"- Fibonacci: {self.math_viewer._fibonacci_position(date)}")
            except Exception as e:
                print(f"[MATH ERROR] Debug falhou: {str(e)}")

        if self.current_civilization_mode == "aztec" and hasattr(self, 'aztec_calendar'):
            try:
                print("[AZTEC DEBUG] Status asteca:")
                print(f"- Dia Xiuhpohualli: {getattr(self.aztec_calendar, 'current_xiuhpohualli_day', 'N/A')}")
                if hasattr(self, 'aztec_venus_tracker'):
                    print(f"- Fase de Vênus: {getattr(self.aztec_venus_tracker, 'current_phase', 'N/A')}")
            except Exception as e:
                print(f"[AZTEC ERROR] Debug falhou: {str(e)}")
                
    def show_event_detail(self, event_data):
        """Mostra detalhes do evento em um diálogo"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
    
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Evento: {event_data.get('title', 'Desconhecido')}")
        layout = QVBoxLayout()
    
        title = QLabel(f"<h2>{event_data.get('title', 'Evento Desconhecido')}</h2>")
        desc = QLabel(event_data.get('description', 'Sem descrição disponível'))
        desc.setWordWrap(True)
    
        layout.addWidget(title)
        layout.addWidget(desc)
        dialog.setLayout(layout)
        dialog.exec()
                
    def show_timeline_view(self):
        """Mostra a linha do tempo de forma segura"""
        try:
            if not hasattr(self, 'timeline_widget'):
                self.init_timeline_widget()
            self.content_stack.setCurrentWidget(self.timeline_widget)
            self.maya_sidebar.set_active_button('timeline')
        except Exception as e:
            self.logger.error(f"Erro ao mostrar timeline: {str(e)}")
            
    def setup_views(self):
        self.views = {
            'calendar': CalendarWidget(self.connector),
            'glyphs': GlyphViewer(self.connector),
            'math': MathCalculator(self.connector),
            'cosmos': CosmosView(self.connector),  # Certifique-se que está instanciado
            'prophecy': ProphecyViewer(self.connector)
        }

    def show_prophecy_view(self):
        """Mostra as profecias de forma segura"""
        try:
            if not hasattr(self, 'prophecy_viewer'):
                self.init_prophecy_component()
            self.content_stack.setCurrentWidget(self.prophecy_viewer)
            self.maya_sidebar.set_active_button('prophecy')
        except Exception as e:
            self.logger.error(f"Erro ao mostrar profecias: {str(e)}")
            
    def show_prophecy_analysis(self, event_data):
        """Mostra a análise profética de forma robusta"""
        try:
            if not hasattr(self, 'prophecy_viewer'):
                self.init_prophecy_component()
            
            # Garante que o widget está visível
            self.content_stack.setCurrentWidget(self.prophecy_viewer)
        
            # Atualiza com os dados do evento
            if event_data:
                self.prophecy_viewer.show_prophecy_analysis(event_data)
            
        except Exception as e:
            print(f"Erro ao mostrar análise profética: {e}")
            self.status_bar.showMessage("Falha ao carregar análise profética", 3000)

    def handle_theme_change(self, theme):
        """Mudança de tema com transição quântica"""
        try:
            self.apply_quantum_theme(theme)
        
            # Atualiza o estado quântico
            self.current_quantum_state['culture'] = theme
            
            # Decisão quântica na sidebar
            if theme == "aztec":
                self.sidebar_stack.setCurrentWidget(self.aztec_sidebar)
                self.current_quantum_state['culture'] = 'aztec'
            else:
                self.sidebar_stack.setCurrentWidget(self.maya_sidebar)
                self.current_quantum_state['culture'] = 'maya'
                
        except Exception as e:
            logging.error(f"Efeito Zenão: {str(e)}")
            
    def _setup_navigation(self):
        """Configura o sistema de navegação entre componentes"""
        self.component_map = {
            'calendar': ('CalendarWidget', self.init_calendar_widget),
            'glyphs': ('GlyphViewer', self.init_glyph_viewer),
            'timeline': ('TimelineWidget', self.init_timeline_widget),
            'cosmos': ('CosmosView', self.init_cosmos_view),
            'math': ('MathCalculator', self.init_math_viewer),
            'prophecy': ('ProphecyViewer', self.init_prophecy_component)
        }
    
        # Conexão dos sinais do menu
        self.maya_sidebar.menu_changed.connect(self._handle_menu_change)
        self.aztec_sidebar.menu_changed.connect(self._handle_menu_change)

    def handle_menu_change(self, component_id):
        """Muda o componente exibido com base na seleção do menu"""
        if component_id not in self.component_map:
            print(f"Componente {component_id} não encontrado")
            return

        component_name, initializer = self.component_map[component_id]
        widget_attr = self._component_map.get(component_id)

        if widget_attr:
            existing_widget = getattr(self, widget_attr, None)
            if existing_widget:
                self.content_stack.setCurrentWidget(existing_widget)
                return

        # Se não existir, tenta inicializar
        if initializer():
            self.content_stack.setCurrentIndex(self.content_stack.count() - 1)

    def show_critical_error(self, message):
        """Mostra uma mensagem de erro crítica"""
        error_label = QLabel(f"ERRO CRÍTICO:\n{message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("""
            QLabel {
                color: #ff0000;
                font-size: 16px;
                font-weight: bold;
                background: #300000;
                padding: 20px;
            }
        """)
        self.setCentralWidget(error_label)
    
    def closeEvent(self, event):
        """Destruição segura"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        super().closeEvent(event)
    
    def adjust_time_flow(self, factor):
        """Ajusta o fluxo temporal da aplicação"""
        self.time_flow_factor = factor
        self.current_quantum_state['time_flow'] = factor

        if hasattr(self, 'cosmos_view') and hasattr(self.cosmos_view, 'set_time_factor'):
            self.cosmos_view.set_time_factor(factor)

        self.status_bar.showMessage(f"Fluxo temporal ajustado para {factor}x", 2000)

    def get_view_name(self, index):
        """Retorna nomes amigáveis para as views"""
        names = {
            0: "Calendário Sagrado",
            1: "Glifos e Símbolos",
            2: "Linha do Tempo",
            3: "Visualização Cósmica",
            4: "Cálculos Matemáticos",
            5: "Profecias 2012"  # Adicione esta linha
        }
        return names.get(index, f"Visualização {index+1}")
    
    def safe_set_current_index(self, index):
        """Muda a view com tratamento de erros robusto"""
        try:
            if hasattr(self, 'content_stack'):
                if 0 <= index < self.content_stack.count():
                    self.content_stack.setCurrentIndex(index)
                    return True
            return False
        except Exception as e:
            logging.error(f"Falha ao mudar view: {str(e)}")
            return False
        
    def post_init(self):
        """Método simples de pós-inicialização"""
        self.status_bar.showMessage("Sistema carregado com sucesso", 3000)
        self.setWindowTitle("Calendário Sagrado Maya-Asteca - Pronto")
        
    def init_aztec_components(self):
        """Inicializa componentes específicos do modo Asteca"""
        try:
            from .widgets.aztec_calendar import AztecCalendarWidget
            from .widgets.aztec_venus_tracker import VenusTracker
        
            # Remove o calendário maia se estiver visível
            if hasattr(self, 'calendar_widget'):
                self.content_stack.removeWidget(self.calendar_widget)
                self.calendar_widget.hide()
        
            # Cria calendário asteca
            self.aztec_calendar = AztecCalendarWidget(parent=self, connector=self.connector)
            self.content_stack.addWidget(self.aztec_calendar)
            self.content_stack.setCurrentWidget(self.aztec_calendar)
        
            # Outros componentes astecas
            self.aztec_venus_tracker = VenusTracker()
            self.content_stack.addWidget(self.aztec_venus_tracker)
        
        except Exception as e:
            print(f"Erro ao carregar componentes astecas: {str(e)}")
            # Fallback básico
            fallback = QLabel("Calendário Asteca (Modo Básico)")
            self.content_stack.addWidget(fallback)
            
    def apply_aztec_theme(self):
        """Aplica o tema visual asteca"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a0a0a;
                border: 2px solid #5a0000;
            }
            QLabel, QTextEdit, QPushButton {
                color: #ff9e9e;
                font-family: 'Arial';
            }
            QStatusBar {
                background-color: #2a0000;
                color: #d4af37;
            }
        """)

    def apply_maya_theme(self):
        """Aplica o tema visual maia"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a1a;
                border: 2px solid #00005a;
            }
            QLabel, QTextEdit, QPushButton {
                color: #9e9eff;
                font-family: 'Arial';
            }
            QStatusBar {
                background-color: #00002a;
                color: #afd437;
            }
        """)
        
    def get_calendar_widget(self, mode):
        if mode == "maya":
            return MayanCalendarWidget()
        else:
            return AztecCalendarWidget()
        
    def _activate_aztec_mode(self):
        """Ativação segura do modo Asteca"""
        try:
            # 1. Esconde componentes Mayas
            if hasattr(self, 'calendar_widget'):
                self.calendar_widget.hide()
        
            # 2. Garante que componentes Astecas existem
            if not hasattr(self, 'aztec_calendar'):
                self._init_aztec_components()
            
            # 3. Mostra componentes Astecas
            self.aztec_calendar.show()
            self.sidebar_stack.setCurrentWidget(self.aztec_sidebar)
            self.apply_aztec_theme()
        
            # 4. Atualiza views sem loop
            QTimer.singleShot(100, lambda: self.update_all_views(QDate.currentDate()))
        
        except Exception as e:
            logging.error(f"Falha na ativação Asteca: {str(e)}")

    def _activate_maya_mode(self):
        """Ativação segura do modo Maya"""
        try:
            # 1. Esconde componentes Astecas
            if hasattr(self, 'aztec_calendar'):
                self.aztec_calendar.hide()
        
            # 2. Mostra componentes Mayas
            if hasattr(self, 'calendar_widget'):
                self.calendar_widget.show()
            
            self.sidebar_stack.setCurrentWidget(self.maya_sidebar)
            self.apply_maya_theme()
        
            # 3. Atualiza views sem loop
            QTimer.singleShot(100, lambda: self.update_all_views(QDate.currentDate()))
        
        except Exception as e:
            logging.error(f"Falha na ativação Maya: {str(e)}")
            
    def _finalize_setup(self):
        """Finaliza a configuração da janela principal"""
        self.logger.debug("Finalizando configuração da janela")

        self.setWindowTitle("Calendário Sagrado Maya-Asteca - Pronto")
        self.status_bar.showMessage("Sistema carregado com sucesso", 3000)

        # Conectar eventos da visão de profecias
        if hasattr(self, 'prophecy_viewer'):
            try:
                if hasattr(self.prophecy_viewer, 'event_selected'):
                    self.prophecy_viewer.event_selected.connect(self.handle_prophecy_event)
            except Exception as e:
                self.logger.error(f"Erro na conexão final de eventos: {str(e)}")

        # Garante visualização cósmica carregada
        if not hasattr(self, 'cosmos_view') or self.cosmos_view is None:
            if not self.init_cosmos_view():
                self._init_cosmos_fallback()
