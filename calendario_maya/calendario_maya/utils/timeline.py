# timeline.py (parte inicial)
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QRectF, QTimer, QPoint, QDate
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem,
                            QGraphicsSimpleTextItem, QMenu, QGraphicsItem, QScrollArea, 
                            QGraphicsEllipseItem, QLabel, QVBoxLayout, QWidget,
                            QGraphicsTextItem, QDialog, QVBoxLayout, QTextEdit,
                            QHBoxLayout, QPushButton, QScrollBar, QComboBox)
from PyQt6.QtGui import (QPen, QBrush, QColor, QAction, QFont, QLinearGradient,
                        QPainter, QFontMetrics, QRadialGradient, QTextCursor,
                        QMouseEvent)
from calendario_maya.utils.base_viewer import BaseViewer
from calendario_maya.utils.mayan_astronomy import MayanAstronomy
from core.config import get_timeline_events_path, get_data_path 
import math
from datetime import datetime
import json
from pathlib import Path

GALACTIC_EPOCH_JD = 2456293.5
GALACTIC_YEAR_DAYS = 25772  # ~71 anos

class TimelineViewer(BaseViewer):
    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.title_label = QLabel("Linha do Tempo Maia")
        self.content_label = QLabel()
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.content_label)
        self.setLayout(self.layout)
    
    def _update_display(self):
        events = self.connector.get_timeline_events() if self.connector else []
        date_str = self.current_date.toString('yyyy-MM-dd')
        
        relevant_events = [e for e in events if e.get('date') == date_str]
        self.content_label.setText(f"Eventos em {date_str}:\n" + 
                                 "\n".join(e['title'] for e in relevant_events))

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Busca Profética")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #0a043c;
                color: white;
            }
            QLabel {
                color: #4ecca3;
            }
            QLineEdit, QComboBox {
                background-color: #1a1a5a;
                color: white;
                border: 1px solid #4466ff;
                padding: 5px;
            }
            QPushButton {
                background-color: #6a3093;
                color: white;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8a50b3;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setSpacing(10)
    
        header = QLabel("SABEDORIA\nMAIA")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #4ecca3; margin-bottom: 20px;")
        layout.addWidget(header)
    
        # Definindo a ordem explícita dos botões
        self.menu_order = [
            ('calendar', "📅 Tzolk'in", 0),
            ('glyphs', "🌀 Glifos Sagrados", 1),
            ('timeline', "⏳ Linha do Tempo", 2, True, False),  # is_timeline
            ('math', "🧮 Matemática", 3),
            ('cosmos', "🔭 Astronomia", 4),
            ('prophecy', "🔮 Profecia 2012", 5, False, True)    # is_prophecy
        ]
    
        self.buttons = {}
        for item in self.menu_order:
            if len(item) == 3:
                key, text, index = item
                self.buttons[key] = self._create_menu_button(text, index)
            else:
                key, text, index, is_timeline, is_prophecy = item
                self.buttons[key] = self._create_menu_button(text, index, is_timeline, is_prophecy)
            layout.addWidget(self.buttons[key])
    
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
        switch_btn = QPushButton("⇄ Alternar para Asteca")
        switch_btn.setIcon(QIcon("assets/aztec_icon.png"))
        switch_btn.clicked.connect(self._emit_switch_signals)
        switch_btn.setObjectName("themeButton")
        layout.addWidget(switch_btn)
    
        self.setLayout(layout)
        self.setFixedWidth(200)
        self._apply_styles()
        self.set_active_button('calendar')  # Definir o botão inicial como calendário
    
    def validate_search(self):
        try:
            frequency = float(self.frequency_input.text()) if self.frequency_input.text() else None
            sign_idx = self.sign_combo.currentIndex() - 1 if self.sign_combo.currentIndex() > 0 else None
            angle = {
                1: 0, 2: 90, 3: 180, 4: 270, 5: 360
            }.get(self.angle_combo.currentIndex(), None)
            energy = int(self.energy_combo.currentText()) if self.energy_combo.currentIndex() > 0 else None
            
            self.parent().search_cyclic_patterns(
                frequency=frequency,
                sign_idx=sign_idx,
                angle=angle,
                energy=energy,
                callback=self.display_results
            )
        except ValueError:
            self.results_area.setText("Por favor, insira uma frequência válida")
    
    def display_results(self, results):
        if not results:
            self.results_area.setText("Nenhum padrão cíclico encontrado")
            return
            
        html = "<h3>Padrões Cíclicos Encontrados</h3><ul>"
        for event in results[:10]:  # Limita a 10 resultados
            html += f"""
            <li>
                <b>{event['title']}</b> ({event['year']})<br>
                Frequência: {event.get('frequency', 'N/A')}Hz | 
                Signo: {event.get('sign', 'N/A')}<br>
                Vênus: {event.get('venus_angle', 0):.1f}° | 
                Terra: {event.get('earth_angle', 0):.1f}°
            </li>
            """
        html += "</ul>"
        
        self.results_area.setHtml(html)

class TimelineWidget(QGraphicsView):
    year_selected = pyqtSignal(int)
    event_clicked = pyqtSignal(dict)
    cosmic_analysis_requested = pyqtSignal(dict)
    show_prophecy = pyqtSignal(dict) 
    
    def __init__(self, connector=None, parent=None):
        super().__init__(parent)
        self.connector = connector
        self._verify_connector()  # Novo método de verificação
        self._init_settings()
        self._setup_ui()
        self._load_data()

    def _verify_connector(self):
        """Garante que o connector tenha os métodos necessários"""
        if not self.connector or not hasattr(self.connector, 'get_timeline_events'):
            raise ValueError("Connector inválido ou sem método get_timeline_events")

    # Substitua o método create_event_tooltip por:
    def create_event_tooltip(self, event):
        """Versão robusta com verificação de tipos"""
        try:
            cosmic = event.get('cosmic_data', {})
            if not isinstance(cosmic, dict):
                cosmic = {}
            
            return f"""
            <b>{event.get('title', 'Evento')}</b><br>
            Ano: {event.get('year', 'N/A')}<br>
            Baktun: {float(cosmic.get('baktun', 0)):.2f}<br>
            Vênus: {float(cosmic.get('venus_phase', 0)):.1f}°
            """
        except Exception as e:
            return f"Erro no tooltip: {str(e)}"

    # Adicione este novo método para cálculo de velocidade temporal:
    def calculate_time_velocity(self, distance_km):
        """Calcula velocidade proporcional à distância com tratamento de erros"""
        try:
            # Constantes fundamentais
            C = 299792.458  # Velocidade da luz em km/s
            PLANCK_LENGTH = 1.616255e-35  # Comprimento de Planck em metros
            GALACTIC_YEAR = 225e6  # Ano galáctico em anos terrestres
        
            # Fator de escala baseado em ciclos maias
            mayan_factor = 13.0 / 20.0  # Relação 13:20 do Tzolk'in
        
            # Cálculo da velocidade proporcional
            velocity = (distance_km / C) * mayan_factor
        
            # Ajuste quântico (simplificado)
            quantum_adjustment = 1 + (PLANCK_LENGTH * 1e12)  # Fator mínima escala
        
            # Limitação para não exceder 10% da velocidade da luz
            return min(velocity * quantum_adjustment, 0.1 * C)
        except Exception as e:
            print(f"Erro no cálculo de velocidade temporal: {e}")
            return 1.0  # Valor padrão seguro
    
    def _init_settings(self):
        """Configurações iniciais"""
        self.min_year = -3114
        self.max_year = datetime.now().year + 50
        self.zoom_level = 1.0
        self.selected_event = None
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def _setup_ui(self):
        """Configura a interface"""
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setup_tooltip()
        self.setup_navigation()
        self.setSceneRect(0, 0, 2000, 400)
        
    def _render_timeline(self):
        print("DEBUG: Timeline sendo renderizada")  # Log de debug
        """Renderiza a linha do tempo inicial"""
        try:
            self.setup_scene()
            self.load_eras()
            self.load_events()
            self.display_events()
        except Exception as e:
            print(f"Erro ao renderizar timeline: {e}")
            self._show_error_message(str(e))
            
    def setup_scene(self):
        """Configura o conteúdo inicial da cena"""
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
    
        # Gradiente escuro para o fundo
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(10, 4, 60))  # Azul muito escuro
        gradient.setColorAt(1, QColor(30, 15, 80))  # Roxo escuro
        self.setBackgroundBrush(QBrush(gradient))

        # Calcula o tamanho necessário baseado nos anos
        scene_width = self.year_to_x(self.max_year) + 200  # Margem
        self.scene.setSceneRect(0, 0, scene_width, 400)

        # Desenha o eixo da timeline com cores temáticas
        self.draw_timeline_axis()

    def _load_data(self):
        """Carrega dados de forma segura"""
        try:
            if not hasattr(self, 'events'):
                self.events = []
            
            if self.connector:
                self.events = self.connector.get_timeline_events() or []
        
            if not hasattr(self, '_render_timeline'):
                self._render_timeline = self._default_render_timeline
            
            self._render_timeline()
        except Exception as e:
            print(f"Erro ao carregar timeline: {e}")
            self._show_error_message(str(e))

    def _default_render_timeline(self):
        """Fallback para renderização básica"""
        self.scene.clear()
        self.scene.addText("Linha do tempo não pôde ser carregada")

    def _show_error_message(self, message):
        """Mostra mensagem de erro na timeline"""
        error_text = QGraphicsTextItem(f"Erro: {message}")
        error_text.setDefaultTextColor(QColor(255, 100, 100))
        self.scene.addItem(error_text)

    def setup_tooltip(self):
        """Configura o tooltip para exibir detalhes dos eventos"""
        self.tooltip = QLabel(self)
        self.tooltip.setStyleSheet("""
            QLabel {
                background: rgba(30, 30, 50, 220);
                color: #e0e0e0;
                padding: 12px;
                border-radius: 6px;
                border: 2px solid #6a3093;
                font-family: Arial;
                font-size: 12px;
            }
            QLabel h3 {
                color: #4ecca3;
                margin: 0;
                font-size: 14px;
            }
            QLabel p {
                margin: 5px 0;
            }
            QLabel hr {
                border-color: #6a3093;
                margin: 8px 0;
            }
        """)
        self.tooltip.hide()
        self.tooltip.setWordWrap(True)
        self.tooltip.setFixedWidth(350)
        self.tooltip.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
    
    def setup_navigation(self):
        """Configura a navegação da timeline"""
        self.setup_navigation_controls()
    
        # Garante que os valores sejam inteiros
        min_x = int(self.year_to_x(self.min_year))
        max_x = int(self.year_to_x(self.max_year))
    
        self.scroll_bar = QScrollBar(Qt.Orientation.Horizontal)
        self.scroll_bar.setRange(min_x, max_x)
        self.scroll_bar.valueChanged.connect(self.on_scroll)
    
        if hasattr(self, 'layout') and isinstance(self.layout, QVBoxLayout):
            self.layout.addWidget(self.scroll_bar)
        
    def setup_navigation_controls(self):
        """Configura os botões de navegação e zoom"""
        # Widget container
        self.nav_widget = QWidget(self)
        self.nav_widget.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.5); 
                border-radius: 5px;
                padding: 2px;
            }
            QPushButton {
                background: rgba(70, 70, 100, 150);
                border: 1px solid #6a3093;
                border-radius: 3px;
                color: white;
            }
            QPushButton:hover {
                background: rgba(100, 100, 150, 200);
            }
        """)
    
        # Layout dos botões
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(2, 2, 2, 2)
        nav_layout.setSpacing(2)
    
        # Botões
        self.zoom_in_btn = self.create_nav_button("+", "Aumentar zoom")
        self.zoom_out_btn = self.create_nav_button("-", "Diminuir zoom")
        self.reset_btn = self.create_nav_button("⟲", "Resetar zoom")
    
        # Adiciona botões ao layout
        for btn in [self.zoom_in_btn, self.zoom_out_btn, self.reset_btn]:
            nav_layout.addWidget(btn)
    
        self.nav_widget.setLayout(nav_layout)
        self.nav_widget.move(10, 10)
    
        # Conexões dos botões com tratamento de erro
        self.zoom_in_btn.clicked.connect(self.safe_zoom_in)
        self.zoom_out_btn.clicked.connect(self.safe_zoom_out)
        self.reset_btn.clicked.connect(self.safe_reset_zoom)
        
    def update_cosmic_data(self, date):
        """Atualiza dados cósmicos com fallback seguro"""
        try:
            if hasattr(self.connector, 'astronomy'):
                data = self.connector.astronomy.get_timeline_data(date)
            else:
                days_since = (date - date(2012, 12, 21)).days
                data = {
                    'baktun': 13 + (days_since / 144000),
                    'venus_phase': (days_since % 584) / 584 * 360,
                    'galactic_year': (days_since % 26000) / 26000 * 100
                }
            
            self.ui.lblBaktun.setText(f"{data.get('baktun', 0):.2f}")
            self.ui.lblVenusPhase.setText(f"{data.get('venus_phase', 0):.1f}°")
            self.ui.lblGalacticYear.setText(f"{data.get('galactic_year', 0):.1f}%")
        except Exception as e:
            print(f"Erro ao atualizar dados cósmicos: {e}")

    def show_search_dialog(self):
        """Mostra o diálogo de busca profética"""
        self.search_dialog.show()
    
    def create_nav_button(self, text, tooltip):
        """Cria um botão de navegação padronizado"""
        btn = QPushButton(text)
        btn.setFixedSize(30, 30)
        btn.setToolTip(tooltip)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def safe_zoom_in(self):
        """Aplica zoom com tratamento seguro de erros"""
        try:
            center_year = self.get_center_year()
            self.set_zoom(1.2, center_year)
        except Exception as e:
            print(f"Erro no zoom in: {str(e)}")
            self.set_zoom(1.2)

    def safe_zoom_out(self):
        """Reduz zoom com tratamento seguro de erros"""
        try:
            center_year = self.get_center_year()
            self.set_zoom(0.8, center_year)
        except Exception as e:
            print(f"Erro no zoom out: {str(e)}")
            self.set_zoom(0.8)

    def safe_reset_zoom(self):
        """Reseta o zoom com tratamento seguro de erros"""
        try:
            center_year = self.get_center_year()
            self.set_zoom(1.0, center_year)
        except Exception as e:
            print(f"Erro ao resetar zoom: {str(e)}")
            self.set_zoom(1.0)

    def get_center_year(self):
        """Obtém o ano atualmente no centro da viewport de forma segura"""
        try:
            view_center = int(self.viewport().width() / 2)
            scene_point = self.mapToScene(QPoint(view_center, 0))
            return self.x_to_year(scene_point.x())
        except Exception as e:
            print(f"Erro ao calcular centro: {str(e)}")
            return (self.min_year + self.max_year) // 2  # Retorna o ano médio como fallback

    def set_zoom(self, factor, center_year=None):
        """Aplica zoom mantendo o foco no ano especificado"""
        old_zoom = self.zoom_level
        self.zoom_level = max(0.3, min(self.zoom_level * factor, 5.0))
    
        if center_year is not None:
            try:
                # Calcula a posição do ano central antes e depois do zoom
                old_x = self.year_to_x(center_year, old_zoom)
                new_x = self.year_to_x(center_year, self.zoom_level)
            
                # Ajusta a posição de rolagem para manter o ano no centro
                scroll_bar = self.horizontalScrollBar()
                scroll_bar.setValue(int(scroll_bar.value() + (old_x - new_x)))
            except Exception as e:
                print(f"Erro ao ajustar scroll durante zoom: {str(e)}")
    
        self.display_events()
        
    def on_scroll(self, value):
        """Manipula eventos de scroll na timeline"""
        try:
            year = self.x_to_year(value)
            self.update_display(year)
        except Exception as e:
            self.logger.error(f"Erro no scroll: {str(e)}")
        
    def draw_timeline_axis(self):
        """Desenha o eixo da timeline de forma dinâmica"""
        # Cria gradiente para a linha
        line_gradient = QLinearGradient(0, 0, self.width(), 0)
        line_gradient.setColorAt(0, QColor(100, 200, 255))  # Azul claro
        line_gradient.setColorAt(0.5, QColor(200, 100, 255))  # Roxo
        line_gradient.setColorAt(1, QColor(255, 150, 100))  # Laranja

        # Desenha a linha principal
        start_x = self.year_to_x(self.min_year)
        end_x = self.year_to_x(self.max_year)
        self.main_line = self.scene.addLine(
            start_x, 100, end_x, 100, 
            QPen(QBrush(line_gradient), 4))

        # Configuração de fonte para os marcadores
        font = QFont("Arial", 9)
        font.setBold(True)
    
        # Adiciona marcadores de tempo principais
        for year in range(-3000, self.max_year + 500, 500):
            x_pos = self.year_to_x(year)
            # Linha do marcador
            marker = self.scene.addLine(
                x_pos, 95, x_pos, 105, 
                QPen(QColor(200, 200, 255), 2))
    
            # Texto do ano
            year_text = self.scene.addSimpleText(str(year))
            year_text.setPos(x_pos - 20, 110)
            year_text.setBrush(QBrush(QColor(200, 200, 255)))
            year_text.setFont(font)
    
    def year_to_x(self, year, zoom_level=None):
        """Conversão segura para anos AEC/EC"""
        zoom = zoom_level if zoom_level is not None else self.zoom_level
        try:
            year = int(year)
            min_year = -3114
            max_year = datetime.now().year + 100
        
            # Normaliza para escala logarítmica
            offset = abs(min_year) + 1
            adjusted_year = year + offset
            if adjusted_year <= 0:
                adjusted_year = 0.1
            
            log_min = math.log(offset)
            log_max = math.log(max_year + offset)
            log_val = math.log(adjusted_year)
        
            normalized = (log_val - log_min) / (log_max - log_min)
            base_width = 1800
            return 50 + normalized * (base_width * zoom)
        
        except Exception as e:
            print(f"Erro em year_to_x: {e}")
            # Fallback linear
            return 50 + ((year - self.min_year) / (self.max_year - self.min_year)) * 1800 * zoom
    
    def load_eras(self):
        """Carrega eras de arquivo JSON com fallback"""
        try:
            eras_file = Path(__file__).parent.parent / "data" / "timeline_eras.json"
            with open(eras_file, 'r', encoding='utf-8') as f:
                self.eras = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar eras: {e}")
            self.eras = [
                {"name": "Pré-Clássico", "start": -3114, "end": 250, "color": "#64c8ff"},
                {"name": "Clássico", "start": 250, "end": 900, "color": "#ffc864"},
                {"name": "Pós-Clássico", "start": 900, "end": 1521, "color": "#c864ff"},
                {"name": "Colonial/Moderno", "start": 1521, "end": self.max_year, "color": "#64ffc8"}
            ]
    
    def load_events(self):
        """Carrega eventos de forma robusta com fallbacks"""
        self.events = []
        data_files = [
            ('historical_events.json', True),
            ('timeline_events.json', True),
            ('backup_events.json', False)
        ]

        for file_name, required in data_files:
            try:
                file_path = self.connector.get_data_path(file_name)  # Usando o connector
                if not file_path.exists():
                    if required:
                        raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {file_path}")
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'events' in data:
                        events = data['events']
                    elif isinstance(data, list):
                        events = data
                    else:
                        raise ValueError("Formato de arquivo inválido")

                    # Processa cada evento
                    for event in events:
                        if self.validate_event(event):
                            event['cosmic_data'] = self.calculate_cosmic_data(
                                int(event.get('year', 0)),
                                event.get('month'),
                                event.get('day')
                            )
                            self.events.append(event)

            except Exception as e:
                error_type = "Erro crítico" if required else "Aviso"
                print(f"{error_type} ao carregar {file_name}: {str(e)}")
                if required and file_name == "timeline_events.json":
                    # Tenta carregar fallback básico
                    self._load_basic_events()
                    break

    def validate_event(self, event):
        """Validação robusta de eventos"""
        required = ['year', 'title', 'description']
        if not all(field in event for field in required):
            return False
    
        try:
            year = int(str(event['year']).lstrip('-'))
            return year >= -3114 and year <= datetime.now().year + 100
        except (ValueError, TypeError):
            return False
    
    def process_events(self, events):
        """Adiciona dados cósmicos aos eventos"""
        processed = []
        for event in events:
            event['cosmic_data'] = self.calculate_cosmic_data(event.get('year'))
            processed.append(event)
        return processed
    
    def calculate_cosmic_data(self, year, month=None, day=None):
        """Versão robusta para lidar com qualquer data"""
        try:
            astronomy = MayanAstronomy()
    
            # Para datas muito antigas, retorna dados básicos sem cálculo astronômico
            if year < -3000:
                return {
                    'baktun': 0.0,
                    'venus_phase': 0.0,
                    'galactic_year': 0.0,
                    'earth_angle': 0.0
                }
        
            # Cria a data de forma segura
            if month is None or day is None:
                date = datetime(year, 6, 15).date()  # Meio do ano como padrão
            else:
                date = datetime(year, month, day).date()
    
            return {
                'baktun': astronomy.calculate_baktun(date),
                'venus_phase': astronomy.venus_phase_angle(date),
                'galactic_year': astronomy.galactic_year_progress(date),
                'earth_angle': astronomy.earth_heliocentric_position(date).get('longitude', 0)
            }
    
        except Exception as e:
            print(f"Erro em calculate_cosmic_data para ano {year}: {e}")
            return {
                'baktun': 0.0,
                'venus_phase': 0.0,
                'galactic_year': 0.0,
                'earth_angle': 0.0
            }
            
    def _load_basic_events(self):
        """Carrega eventos básicos como fallback"""
        self.events = [
            {
                'year': -3114,
                'title': 'Início da Conta Longa Maia',
                'description': 'Data de início do calendário maia',
                'category': 'Fundação'
            },
            {
                'year': 2024,
                'title': 'Fim do 13º Baktun',
                'description': 'Transição para novo ciclo galáctico',
                'category': 'Astronômico'
            },
            {
                'year': 1521,
                'title': 'Queda de Tenochtitlán',
                'description': 'Fim do império asteca',
                'category': 'Guerra'
            }
        ]
    
    def display_events(self):
        """Exibe eventos na timeline com espaçamento inteligente"""
        self.scene.clear()
        self.draw_timeline_axis()
    
        # Agrupa eventos por ano para evitar sobreposição
        events_by_year = {}
        for event in self.events:
            year = int(event.get('year', 0))
            if year not in events_by_year:
                events_by_year[year] = []
            events_by_year[year].append(event)
    
        # Desenha eventos com espaçamento vertical
        category_base = {
            "Cultural": 120,
            "Religioso": 160,
            "Guerra": 200,
            "Astronômico": 240,
            "Fundação": 280,
            "Outros": 320
        }
    
        for year, year_events in events_by_year.items():
            # Para anos com muitos eventos, distribui verticalmente
            if len(year_events) > 3:
                for i, event in enumerate(year_events):
                    y_pos = 120 + (i % 8) * 40  # Máximo 8 eventos por coluna
                    self.draw_event(event, y_pos)
            else:
                # Para poucos eventos, usa a posição padrão por categoria
                for event in year_events:
                    category = event.get('category', 'Outros')
                    y_pos = category_base.get(category, 320)
                    self.draw_event(event, y_pos)
                    
        zoom_text = f"Zoom: {self.zoom_level:.1f}x"
        zoom_indicator = self.scene.addSimpleText(zoom_text)
        zoom_indicator.setPos(1600, 380)
        zoom_indicator.setBrush(QBrush(QColor(255, 255, 255, 180)))
        zoom_indicator.setZValue(100)
    
    def draw_event(self, event, y_pos):
        """Desenha um evento com visual rico"""
        year = event.get('year', 0)
        x_pos = self.year_to_x(year)
        color = self.get_category_color(event.get('category', 'Outros'))
        
        # Círculo do evento com efeito de brilho
        gradient = QRadialGradient(x_pos, y_pos, 10)
        gradient.setColorAt(0, color.lighter(150))
        gradient.setColorAt(1, color.darker(120))
        
        circle = QGraphicsEllipseItem(x_pos-8, y_pos-8, 16, 16)
        circle.setPen(QPen(color.darker(), 1.5))
        circle.setBrush(QBrush(gradient))
        circle.setData(0, event)  # Armazena o evento
        circle.setCursor(Qt.CursorShape.PointingHandCursor)
        circle.setToolTip(self.create_event_tooltip(event))
        self.scene.addItem(circle)
        
        # Linha de conexão
        line = self.scene.addLine(x_pos, y_pos, x_pos, 100, 
                                QPen(color, 1, Qt.PenStyle.DashLine))
        line.setZValue(-1)
        
        # Texto do evento
        text = f"{event.get('year', '')}: {event.get('title', 'Evento')}"
        text_item = self.scene.addSimpleText(text)
        text_item.setPos(x_pos + 15, y_pos - 10)
        text_item.setBrush(QBrush(color.lighter(200)))
        text_item.setFont(QFont("Segoe UI", 9))
        
        # Se texto muito longo, ajusta a posição
        if QFontMetrics(text_item.font()).horizontalAdvance(text) > 200:
            text_item.setPos(x_pos - 220, y_pos - 10)
            text_item.setText(f"{event.get('title', 'Evento')} ({event.get('year', '')})")
    
    def get_category_color(self, category):
        """Retorna cor baseada na categoria"""
        colors = {
            "Cultural": QColor(100, 200, 255),
            "Religioso": QColor(255, 150, 200),
            "Guerra": QColor(255, 100, 100),
            "Astronômico": QColor(200, 255, 100),
            "Fundação": QColor(100, 255, 200),
            "Outros": QColor(150, 150, 150)
        }
        return colors.get(category, QColor(150, 150, 150))
    
    def setup_connections(self):
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def on_selection_changed(self):
        selected = self.scene.selectedItems()
        if selected and isinstance(selected[0], QGraphicsEllipseItem):
            self.selected_event = selected[0].data(0)
            self.show_event_detail(self.selected_event)
            
    def ensure_timeline_visible(self):
        """Garante que a linha do tempo esteja sempre visível"""
        view_rect = self.viewport().rect()
        scene_rect = self.mapToScene(view_rect).boundingRect()
    
        # Se a linha está saindo da viewport, ajusta o scroll
        timeline_bottom = 110  # Aproximadamente onde está a linha
        if scene_rect.bottom() < timeline_bottom:
            self.centerOn(self.year_to_x(self.get_center_year()), timeline_bottom)
    
    def show_event_detail(self, event_data):
        """Exibe detalhes do evento em um diálogo"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Evento: {event_data.get('title', 'Desconhecido')}")
        dialog.resize(600, 400)

        layout = QVBoxLayout()

        # Cabeçalho
        header = QLabel(f"""
            <h2>{event_data.get('title', 'Evento Desconhecido')}</h2>
            <p><b>Ano:</b> {event_data.get('year', 'N/A')}</p>
            <hr>
        """)
        header.setTextFormat(Qt.TextFormat.RichText)

        # Descrição
        scroll = QScrollArea()
        content = QLabel(event_data.get('description', 'Descrição não disponível'))
        content.setWordWrap(True)
        scroll.setWidget(content)

        # Dados cósmicos - Garantindo que existam no dicionário
        cosmic_data = event_data.get('cosmic_data', {})
        baktun = cosmic_data.get('baktun', 0)
        venus_phase = cosmic_data.get('venus_phase', 0)
        galactic_year = cosmic_data.get('galactic_year', 0)

        cosmic_info = QLabel(f"""
            <h3>Dados Cósmicos</h3>
            <p><b>Baktun:</b> {baktun:.2f}</p>
            <p><b>Fase de Vênus:</b> {venus_phase:.1f}°</p>
            <p><b>Ano Galáctico:</b> {galactic_year:.1f}%</p>
        """)
        cosmic_info.setTextFormat(Qt.TextFormat.RichText)

        layout.addWidget(header)
        layout.addWidget(scroll)
        layout.addWidget(cosmic_info)
        dialog.setLayout(layout)

        prophecy_btn = QPushButton("Ver Análise Profética")
        prophecy_btn.clicked.connect(lambda: self.show_prophecy.emit(event_data))
        layout.addWidget(prophecy_btn)
    
        dialog.exec()
    
    def show_context_menu(self, pos):
        menu = QMenu(self)
    
        # Ações básicas
        zoom_in = QAction("Ampliar (+)", self)
        zoom_in.triggered.connect(lambda: self.set_zoom(1.2, self.get_center_year()))
    
        zoom_out = QAction("Reduzir (-)", self)
        zoom_out.triggered.connect(lambda: self.set_zoom(0.8, self.get_center_year()))
    
        reset_zoom = QAction("Resetar Zoom", self)
        reset_zoom.triggered.connect(lambda: self.set_zoom(1.0, self.get_center_year()))
        
        menu.addAction(zoom_in)
        menu.addAction(zoom_out)
        menu.addAction(reset_zoom)
        menu.addSeparator()
        
        # Análise cósmica
        if self.selected_event:
            cosmic_action = QAction("Análise Cósmica Detalhada", self)
            cosmic_action.triggered.connect(self.show_cosmic_analysis)
            menu.addAction(cosmic_action)
        
        # Filtros por era
        era_menu = menu.addMenu("Filtrar por Era")
        for era in self.eras:
            era_action = QAction(era["name"], self)
            era_action.triggered.connect(
                lambda _, e=era: self.filter_by_era(e["start"], e["end"]))
            era_menu.addAction(era_action)
            
        search_action = QAction("Busca Profética", self)
        search_action.triggered.connect(self.show_search_dialog)
        menu.addAction(search_action)
    
        if self.selected_event:
            predict_action = QAction("Prever Próximo Ciclo Similar", self)
            predict_action.triggered.connect(lambda: self.show_prediction(self.selected_event))
            menu.addAction(predict_action)
    
        menu.exec(self.mapToGlobal(pos))
    
    def show_cosmic_analysis(self):
        """Mostra análise detalhada do evento"""
        if not self.selected_event:
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Análise Cósmica")
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel(f"<h2>{self.selected_event.get('title', 'Evento')}</h2>")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)
        
        # Texto de análise
        analysis = QTextEdit()
        analysis.setReadOnly(True)
        analysis.setHtml(self.generate_cosmic_analysis())
        layout.addWidget(analysis)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def generate_cosmic_analysis(self):
        """Gera HTML com análise cósmica detalhada"""
        event = self.selected_event
        cosmic = event.get('cosmic_data', {})
    
        # Previsão de próximos ciclos
        next_cycles = self.predict_next_cycle(event, years_to_look=5200)  # ~1/5 do ano galáctico
    
        prediction_html = ""
        if next_cycles:
            prediction_html = "<h3 style='color: #64c8ff'>Próximos Ciclos Similares</h3><ul>"
            for e in sorted(next_cycles, key=lambda x: int(x['year']))[:3]:  # Mostra apenas os 3 mais próximos
                years_diff = int(e['year']) - int(event['year'])
                prediction_html += f"<li><b>{e['year']}</b> (em {years_diff} anos): {e['title']}</li>"
            prediction_html += "</ul>"
    
        return f"""
        <html>
        <body style='font-family: Arial; color: white; background: #1a1a2e'>
            <div style='padding: 20px;'>
                <!-- Código existente... -->
            
                {prediction_html}
            </div>
        </body>
        </html>
        """
    
    def get_baktun_interpretation(self, baktun):
        """Retorna interpretação do ciclo Baktun"""
        phase = baktun % 1
        if phase < 0.2:
            return "Início de um novo ciclo Baktun (energia de renovação)"
        elif phase < 0.45:
            return "Fase de crescimento do ciclo Baktun (expansão)"
        elif phase < 0.55:
            return "Pico do ciclo Baktun (máxima energia)"
        elif phase < 0.8:
            return "Fase de declínio do ciclo Baktun (consolidação)"
        else:
            return "Final do ciclo Baktun (transição e liberação)"
    
    def get_venus_interpretation(self, venus_phase):
        """Retorna interpretação da fase de Vênus"""
        if venus_phase < 90:
            return "Vênus como Estrela da Manhã (energia de ação)"
        elif venus_phase < 180:
            return "Conjunção Superior de Vênus (energia interior)"
        elif venus_phase < 270:
            return "Vênus como Estrela da Tarde (energia de reflexão)"
        else:
            return "Conjunção Inferior de Vênus (energia de transformação)"
    
    def find_similar_events(self, year):
        """Encontra eventos em posições cósmicas similares"""
        try:
            year = int(year)
            similar = []
            for event in self.events:
                if event.get('year') and abs(int(event['year']) - year) > 50:
                    if abs(int(event['year']) - year) % 5200 < 100:  # ~1/5 de ano galáctico
                        similar.append(event)
            
            if similar:
                return f"Eventos em alinhamento similar: {', '.join(e['title'] for e in similar[:3])}"
            return "Nenhum evento em alinhamento similar encontrado"
        except:
            return "Não foi possível determinar eventos similares"
    
    def filter_by_era(self, start, end):
        filtered = [e for e in self.events if start <= int(e.get('year', 0)) <= end]
        self.temp_display_events(filtered)
    
    def temp_display_events(self, events):
        self.scene.clear()
        self.draw_timeline_axis()
        
        for event in events:
            self.draw_event(event, 120)
            
    def update_display(self, date):
        """Atualiza a exibição baseada na data"""
        try:
            year = date.year() if hasattr(date, 'year') else int(date)
            self.highlight_year(year)
        except Exception as e:
            print(f"Erro ao atualizar timeline: {e}")
    
    def sync_with_date(self, date):
        try:
            year = date.year() if hasattr(date, 'year') else int(date)
            self.highlight_year(year)
            self.centerOn(self.year_to_x(year), 100)
        except Exception as e:
            print(f"Erro ao sincronizar data: {e}")
    
    def highlight_year(self, year):
        if hasattr(self, 'highlight_item'):
            self.scene.removeItem(self.highlight_item)
        
        x_pos = self.year_to_x(year)
        
        self.highlight_item = self.scene.addRect(
            x_pos - 10, 80, 20, 40,
            QPen(QColor(255, 255, 0), 2),
            QBrush(QColor(255, 255, 0, 60))
        )
        
        self.year_selected.emit(year)
  
    def search_cyclic_patterns(self, frequency=None, sign_name_search=None, 
                               angle_key=None, energy_search=None, callback=None):
        results = []
        # Os eventos já devem ter 'cosmic_data' do process_events
        
        # Recuperar o nome do signo se um índice foi passado pelo SearchDialog
        target_sign_name = None
        if sign_name_search is not None: # Supondo que sign_name_search é o nome do signo
            target_sign_name = sign_name_search 

        for event in self.events:
            data = event.get('cosmic_data', {})
            match = True

            if frequency is not None and data.get('associated_frequency') is not None:
                if abs(data['associated_frequency'] - frequency) > 0.1: # Tolerância para float
                    match = False
            
            if target_sign_name and data.get('sign_name') != target_sign_name:
                match = False
            
            if energy_search is not None and data.get('tone') != energy_search:
                match = False

            if angle_key is not None and data.get('sun_angle_galactic') is not None:
                # angle_key é o ângulo buscado (0, 90, 180, 270)
                event_sun_angle = data['sun_angle_galactic'] # já é 0-360
                threshold = 7.0 # Tolerância em graus
                
                # Verifica se o ângulo do evento está próximo ao ângulo chave ou seus simétricos
                is_match_angle = False
                for i in range(4): # 0, 90, 180, 270
                    ref_angle = angle_key + (i * 90) 
                    # Compara a diferença angular (lidando com a natureza circular)
                    diff = abs(event_sun_angle - (ref_angle % 360.0))
                    if min(diff, 360.0 - diff) < threshold:
                        is_match_angle = True
                        break
                if not is_match_angle:
                    match = False
            
            if match:
                # Adicionar dados relevantes para exibição no SearchDialog
                result_event = {
                    'title': event.get('title'),
                    'year': event.get('year'),
                    'frequency': data.get('associated_frequency'),
                    'sign': data.get('sign_name'),
                    'tone': data.get('tone'),
                    'venus_angle': data.get('venus_angle_heliocentric'),
                    'earth_angle': data.get('earth_angle_heliocentric'),
                    'sun_angle_galactic': data.get('sun_angle_galactic')
                }
                results.append(result_event)
        
        if callback:
            callback(results) # Envia os resultados para o SearchDialog
        
    def apply_time_dilation(self, velocity):
        """Aplica efeitos de dilatação temporal na visualização"""
        try:
            # Fator de dilatação relativística (simplificado)
            lorentz_factor = 1 / math.sqrt(1 - (velocity**2 / (299792.458**2)))
        
            # Ajusta a escala de tempo
            self.time_scale = min(max(1.0 / lorentz_factor, 0.1), 10.0)
        
            # Atualiza a exibição
            self.display_events()
        
        except Exception as e:
            print(f"Erro na dilatação temporal: {e}")
            self.time_scale = 1.0

    def wheelEvent(self, event):
        """Extensão para suportar zoom temporal"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom normal com Ctrl
            delta = event.angleDelta().y()
            self.set_zoom(1.1 if delta > 0 else 0.9, self.get_center_year())
        elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            # Ajuste de velocidade temporal com Shift
            delta = event.angleDelta().y()
            distance = 10000 * (1 if delta > 0 else -1)  # 10.000 km por passo
            velocity = self.calculate_time_velocity(abs(distance))
            self.apply_time_dilation(velocity)
        else:
            super().wheelEvent(event)
    
    def keyPressEvent(self, event):
        """Adiciona navegação por teclado"""
        scroll_bar = self.horizontalScrollBar()
        step = 100  # Passo padrão
    
        if event.key() == Qt.Key.Key_Left:
            scroll_bar.setValue(scroll_bar.value() - step)
        elif event.key() == Qt.Key.Key_Right:
            scroll_bar.setValue(scroll_bar.value() + step)
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.set_zoom(1.2, self.get_center_year())
        elif event.key() == Qt.Key.Key_Minus:
            self.set_zoom(0.8, self.get_center_year())
        else:
            super().keyPressEvent(event)

    def x_to_year(self, x):
        """Converte posição X para ano (inverso de year_to_x)"""
        try:
            x = float(x)  # Garante que x é um número
            x_norm = (x - 50) / (1800 * self.zoom_level)
            log_min = math.log1p(abs(self.min_year) + 1)
            log_max = math.log1p(self.max_year + abs(self.min_year) + 1)
            log_val = log_min + x_norm * (log_max - log_min)
            adjusted_year = math.expm1(log_val)
            year = int(round(adjusted_year - abs(self.min_year) - 1))
            return max(self.min_year, min(year, self.max_year))  # Garante que está dentro dos limites
        except Exception as e:
            print(f"Erro ao converter posição X para ano: {e}")
            # Fallback linear em caso de erro
            total_years = self.max_year - self.min_year
            year = int(self.min_year + (x - 50) / (1800 * self.zoom_level) * total_years)
            return max(self.min_year, min(year, self.max_year))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
        # Verifica se clicou em um evento
            item = self.itemAt(event.pos())
            if item and isinstance(item, QGraphicsEllipseItem):
                event_data = item.data(0)
                if event_data:
                    self.event_clicked.emit(event_data)
                    self.show_event_detail(event_data)
                    return
    
        # Pan com o mouse
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            fake_event = QMouseEvent(
                event.type(), event.pos(), Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton, event.modifiers()
            )
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)
        
    def predict_next_cycle(self, current_event, years_to_look=5000):
        """Preve o próximo ciclo similar"""
        current_year = int(current_event['year'])
        similar_events = []
    
        # Padrões de ciclo para verificar
        cycles_to_check = [
            260,    # Ciclo Tzolk'in
            584,    # Ciclo de Vênus
            1898,   # Ciclo de Marte
            5200,   # 1/5 do ano galáctico
            26000   # Ano galáctico completo
        ]
    
        for cycle in cycles_to_check:
            next_year = current_year + cycle
            if next_year <= datetime.now().year + years_to_look:
                similar = [e for e in self.events if abs(int(e['year']) - next_year) < cycle * 0.1]  # 10% de tolerância
                similar_events.extend(similar)
    
        return similar_events
    
    def show_prediction(self, event):
        """Mostra previsão do próximo ciclo similar"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Previsão para {event['title']}")
        dialog.resize(600, 400)
    
        layout = QVBoxLayout()
    
        title = QLabel(f"<h2>Próximos ciclos similares a {event['title']} ({event['year']})</h2>")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)
    
        results = self.predict_next_cycle(event)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
    
        if not results:
            text_edit.setText("Nenhum ciclo similar previsto nos próximos 5000 anos")
        else:
            html = "<ul>"
            for e in sorted(results, key=lambda x: int(x['year'])):
                html += f"""
                <li>
                    <b>{e['year']}:</b> {e['title']}<br>
                    <small>Diferença: {int(e['year']) - int(event['year'])} anos</small>
                </li>
                """
            html += "</ul>"
            text_edit.setHtml(html)
    
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec()