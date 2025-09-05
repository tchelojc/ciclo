from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QGraphicsView)
from PyQt6.QtCore import QDate, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont, QPainter, QPen, QColor
from PyQt6.QtChart import QChart, QChartView, QLineSeries
import math
import random
from core.connector import connector
from utils.style_utils import sanitize_stylesheet

try:
    from PyQt6.QtChart import QChart, QChartView, QLineSeries
    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False

class MathViewerBase(QWidget):
    """Classe base comum"""
    def __init__(self, connector=None):
        super().__init__()
        self.connector = connector

if HAS_CHARTS:
    class QuantumMathViewer(MathViewerBase):
        """Versão completa com gráficos"""
        def __init__(self, connector=None):
            super().__init__(connector)
            self.setup_chart_view()
            self.connector = connector or connector
            self.has_charts = self._check_chart_availability()
            self.quantum_mode = False
            self.current_date = QDate.currentDate()
            self.setup_ui()

        def setup_chart_view(self):
            self.chart = QChart()
            self.chart_view = QChartView(self.chart)
                    
        def _check_chart_availability(self):
            try:
                from PyQt6.QtCharts import QChart, QChartView
                return True
            except ImportError:
                return False
    
        def setup_ui(self):
            self.layout = QVBoxLayout()
        
            # Título dinâmico
            self.title = QLabel("MATEMÁTICA SAGRADA MAIA-QUÂNTICA")
            self.title.setStyleSheet("font-size: 18px; color: #4ecca3; font-weight: bold;")
            self.layout.addWidget(self.title)
        
            # Configura a área de visualização baseada na disponibilidade de gráficos
            if hasattr(self.connector, 'graph_service') and self.connector.graph_service._has_charts:
                self.setup_full_view()
            else:
                self.setup_fallback_view()
        
            self.setLayout(self.layout)
    
    def setup_full_view(self):
        """Configura a visualização completa com gráficos"""
        from PyQt6.QtGui import QPainter
    
        # Área de gráfico quântico
        self.quantum_chart = QChartView()
        self.quantum_chart.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.layout.addWidget(self.quantum_chart)

        # Área de texto
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setStyleSheet("""
            background: #16213e;
            color: #ffffff;
            border: 1px solid #4ecca3;
            border-radius: 5px;
            padding: 10px;
        """)
        self.layout.addWidget(self.info_display)

        # Controle quântico
        self.toggle_btn = QPushButton("🌀 ATIVAR VISUALIZAÇÃO QUÂNTICA")
        self.toggle_btn.setStyleSheet(self.get_button_style())
        self.toggle_btn.clicked.connect(self.toggle_quantum_view)
        self.layout.addWidget(self.toggle_btn)

        # Configura animações
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_quantum_animation)
        self.animation_timer.start(100)
    
        def setup_fallback_view(self):
            """Configura a visualização simplificada sem gráficos"""
            self.info_label = QLabel("""
                <center>
                <h3 style='color:#4ecca3'>MATEMÁTICA SAGRADA</h3>
                <p style='color:#e94560'>Modo Simplificado Ativado</p>
                <p>Instale PyQt6-Charts para visualizações quânticas completas</p>
                </center>
            """)
            self.info_label.setWordWrap(True)
            self.layout.addWidget(self.info_label)
        
            # Botão desativado
            self.toggle_btn = QPushButton("🔒 MODO QUÂNTICO INDISPONÍVEL")
            self.toggle_btn.setEnabled(False)
            self.toggle_btn.setStyleSheet("""
                QPushButton {
                    background: #555555;
                    color: #aaaaaa;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)
            self.layout.addWidget(self.toggle_btn)
    
        def get_button_style(self):
            return """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #e94560, stop:1 #4ecca3);
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #d4344f, stop:1 #3eb893);
                }
            """
    
        def toggle_quantum_view(self):
            """Alterna entre visualizações com tratamento seguro"""
            if not hasattr(self, 'quantum_chart'):  # Se não tem gráficos disponíveis
                return
            
            self.quantum_mode = not self.quantum_mode
        
            if self.quantum_mode:
                self.toggle_btn.setText("▢ SAIR DO MODO QUÂNTICO")
                self.title.setStyleSheet("""
                    font-size: 18px;
                    color: #e94560;
                    font-weight: bold;
                    border-bottom: 2px solid #4ecca3;
                """)
                self.start_quantum_effects()
            else:
                self.toggle_btn.setText("🌀 ATIVAR MODO QUÂNTICO")
                self.title.setStyleSheet("""
                    font-size: 18px;
                    color: #4ecca3;
                    font-weight: bold;
                    border-bottom: 2px solid #e94560;
                """)
                self.stop_quantum_effects()
        
            self.update_calculations(self.current_date)
    
        # math_viewer.py
        def update_calculations(self, date):
            """Atualiza os cálculos matemáticos"""
            try:
                # Cálculos básicos de calendário
                kin = self.connector.get_kin_number(date)
                self.display_kin_circle(kin)
        
                # Adiciona informações textuais
                info = f"""
                Cálculos para {date.toString('dd/MM/yyyy')}:
                - Kin: {kin}
                - Número Harmônico: {(kin % 13) + 1}
                - Onda Encantada: {((kin - 1) // 13) + 1}
                """
                self.info_label.setText(info)
        
            except Exception as e:
                print(f"Erro nos cálculos matemáticos: {e}")
    
        def _update_text_view(self, date):
            """Atualiza a visualização de texto simplificada"""
            kin = (date.toJulianDay() % 260) + 1
            self.info_label.setText(f"""
                <center>
                <h3 style='color:#4ecca3'>CÁLCULOS PARA {date.toString('dd/MM/yyyy')}</h3>
                <p><b>Kin:</b> {kin}</p>
                <p><b>Nahual:</b> {(kin-1)%20 + 1}</p>
                <p style='color:#e94560'>Instale PyQt6-Charts para recursos quânticos</p>
                </center>
            """)
    
        def _update_classic_view(self, date):
            """Atualiza a visualização clássica"""
            kin = (date.toJulianDay() % 260) + 1
            self.info_display.setHtml(f"""
                <h2 style='color:#4ecca3'>Ciclo Tzolk'in</h2>
                <p><b>Kin:</b> {kin}</p>
                <p><b>Nahual:</b> {(kin-1)%20 + 1}</p>
                <p><b>Energia:</b> {(kin-1)%13 + 1}</p>
            """)
            self._update_basic_chart(kin)
    
        def _update_quantum_view(self, date):
            """Atualiza a visualização quântica"""
            days = date.toJulianDay()
            kin = (days % 260) + 1
        
            self.info_display.setHtml(f"""
                <h2 style='color:#e94560'>ESTADO QUÂNTICO</h2>
                <p><b>Kin:</b> {kin} | Ψ⟩ = {math.sin(kin/260*math.pi*2):.2f}|0⟩ + {math.cos(kin/260*math.pi*2):.2f}|1⟩</p>
                <p><b>Ressonância:</b> {math.sin(days/365.25*math.pi):.4f}</p>
            """)
            self._update_quantum_chart(kin)
    
        def _update_basic_chart(self, kin):
            """Atualiza o gráfico básico"""
            chart = QChart()
            series = QLineSeries()
        
            for x in range(0, 20):
                y = math.sin(x + kin/260*math.pi*2)
                series.append(x, y)
        
            chart.addSeries(series)
            chart.createDefaultAxes()
            self.quantum_chart.setChart(chart)
    
        def _update_quantum_chart(self, kin):
            """Atualiza o gráfico quântico"""
            chart = QChart()
            series = QLineSeries()
        
            for x in range(0, 100):
                y = math.sin(x/10 + kin/260*math.pi*4) * math.cos(x/5)
                series.append(x, y)
        
            chart.addSeries(series)
            chart.createDefaultAxes()
            self.quantum_chart.setChart(chart)
    
        def start_quantum_effects(self):
            """Inicia efeitos visuais quânticos"""
            if not hasattr(self, 'info_display'):
                return
            
            self.quantum_animation = QPropertyAnimation(self.info_display, b"styleSheet")
            self.quantum_animation.setDuration(2000)
            self.quantum_animation.setLoopCount(100)
        
            self.quantum_animation.setStartValue("""
                background: #16213e;
                border: 2px solid #4ecca3;
            """)
            self.quantum_animation.setEndValue("""
                background: #1a1a2e;
                border: 2px solid #e94560;
            """)
            self.quantum_animation.start()
    
        def stop_quantum_effects(self):
            """Para os efeitos quânticos"""
            if hasattr(self, 'quantum_animation'):
                self.quantum_animation.stop()
            if hasattr(self, 'info_display'):
                self.info_display.setStyleSheet("""
                    background: #16213e;
                    color: #ffffff;
                    border: 1px solid #4ecca3;
                    border-radius: 5px;
                    padding: 10px;
                """)
    
        def update_quantum_animation(self):
            """Atualiza animações em tempo real"""
            if hasattr(self, 'quantum_mode') and self.quantum_mode:
                if random.random() > 0.7:
                    self.create_quantum_particle()
    
        def create_quantum_particle(self):
            """Cria efeito visual de partícula quântica"""
            if not hasattr(self, 'quantum_chart'):
                return
            
            particle = QLabel("•", self)
            particle.setStyleSheet("color: #4ecca3; font-size: 24px;")
            particle.move(
                random.randint(0, self.width()-30),
                random.randint(0, self.height()-30)
            )
            particle.show()
        
            # Animação de desaparecimento
            QTimer.singleShot(500, lambda: particle.deleteLater())
        
else:
    class QuantumMathViewer(MathViewerBase):
        """Versão simplificada sem gráficos"""
        def __init__(self, connector=None):
            super().__init__(connector)
            self.setup_basic_view()
        
        def setup_basic_view(self):
            self.label = QLabel("Visualização matemática básica\n(PyQt6-Charts não disponível)")