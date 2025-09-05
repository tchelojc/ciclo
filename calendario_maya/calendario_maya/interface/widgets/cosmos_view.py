# Stdlib imports
import sys
import math
import logging
import os
import random
from datetime import date
from typing import Dict, Any, Optional
from math import acos, sin, cos, radians, degrees

# Third-party imports
import numpy as np
from PyQt6.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QTextEdit, 
                            QLabel, QGroupBox, QComboBox, QPushButton, 
                            QHBoxLayout, QCalendarWidget)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QSurfaceFormat, QPixmap

# Local imports
from calendario_maya.utils.mayan_astronomy import MayanAstronomy
from calendario_maya.core.star_map import StarMap
from calendario_maya.constants.astronomia import (
    EARTH_ORBITAL_PERIOD,
    VENUS_ORBITAL_PERIOD,
    GALACTIC_YEAR_DAYS,
    GALACTIC_EPOCH_JD,
    REFERENCE_DATE
)

# Constantes para o sistema solar
SUN_ORBIT_RADIUS_GL = 0.8
SUN_SIZE_GL = 0.1
EARTH_SIZE_GL = 0.05
VENUS_SIZE_GL = 0.04
EARTH_ORBIT_RADIUS_AROUND_SUN_GL = 0.3
VENUS_ORBIT_RADIUS_AROUND_SUN_GL = 0.2

HAS_OPENGL = False
try:
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    from OpenGL.GL import *
    HAS_OPENGL = True
except ImportError as e:
    logging.warning(f"OpenGL não disponível - {e}")

class CosmosViewBase:
    """Classe base com cálculos astronômicos compartilhados."""
    
    def __init__(self, connector=None):
        self.connector = connector
        self.astronomy = MayanAstronomy(connector)
        self.celestial_data = {}
        self.astronomical_calculations: Dict[str, Any] = {}
        self.current_q_date = QDate.currentDate()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._cache = {
            'venus': {},
            'cosmic': {},
            'galactic': {}
        }
        
    def calculate_cosmic_data(self, date_py: date) -> Dict[str, Any]:
        try:
            galactic_data = self._calculate_galactic_position(date_py)
            baktun = self.astronomy.calculate_baktun(date_py)
        
            return {
                **galactic_data,
                'baktun': baktun,
                'new_cycle': date_py >= date(2012, 12, 21)
            }
        except Exception as e:
            return {'error': str(e)}

    def _check_alignment(self, date_py: date) -> bool:
        """Verifica alinhamentos importantes"""
        try:
            jd = self.astronomy.date_to_julian(date_py)
            sun_angle = self._calculate_sun_galactic_angle(jd)
            return abs(sun_angle % 90) < 5  # 5 graus de margem
        except:
            return False

    def _calculate_sun_galactic_angle(self, current_jd: float) -> float:
        """Calcula o ângulo do Sol em relação ao centro galáctico"""
        try:
            # Baseado no ano galáctico de ~26000 anos
            galactic_year_days = 26000 * 365.25
            days_since_epoch = current_jd - 2456293.5  # JD do 21/12/2012
        
            # Ângulo baseado no movimento do sistema solar em torno da galáxia
            angle = (days_since_epoch / galactic_year_days) * 360
        
            # Ajuste para o ângulo atual do centro galáctico (266.4°)
            return (angle + 266.4) % 360
        except Exception as e:
            self.logger.error(f"Erro cálculo ângulo galáctico: {e}")
            return 0.0

    def _calculate_galactic_position(self, date_py: date) -> Dict[str, Any]:
        """Calcula posições galácticas com tratamento de erros."""
        try:
            jd = self.astronomy.date_to_julian(date_py)
            days_since_2012 = (date_py - REFERENCE_DATE).days
        
            # Ângulo solar galáctico com base no movimento do sistema solar
            sun_angle = self._calculate_sun_galactic_angle(jd)
        
            # Progresso no ciclo galáctico (26000 anos)
            galactic_progress = (days_since_2012 / (26000 * 365.25)) * 100
        
            return {
                'date': date_py.isoformat(),
                'julian_date': jd,
                'days_since_2012': days_since_2012,
                'sun_angle_galactic': sun_angle,
                'galactic_progress': galactic_progress,
                'tzolkin_day': (days_since_2012 % 260) + 1,
                **self.astronomy.get_planetary_positions(date_py)
            }
        except Exception as e:
            self.logger.error(f"Erro cálculo posição galáctica: {str(e)}")
            return {
                'date': date_py.isoformat(),
                'error': str(e)
            }

    def update_position(self, q_date: Optional[QDate] = None) -> None:
        """Atualiza as posições para a data especificada."""
        if not q_date or not q_date.isValid():
            q_date = QDate.currentDate()
        
        self.current_q_date = q_date
        
        try:
            py_date = q_date.toPyDate()
            self.astronomical_calculations = self._calculate_galactic_position(py_date)
            
            if hasattr(self.connector, 'get_astronomical_data'):
                cel_data = self.connector.get_astronomical_data(q_date)
                self.celestial_data = cel_data if cel_data else {}
            
            if hasattr(self, 'update_display'):
                self.update_display()
            elif hasattr(self, 'update_data') and not HAS_OPENGL:
                self.update_data(q_date)

        except Exception as e:
            self.logger.error(f"Erro ao atualizar posição: {str(e)}")

class AstronomicalDataDisplay(QWidget):
    """Widget para exibição de dados astronômicos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #6a3093;
                border-radius: 5px;
                padding: 10px;
                font-family: Arial;
            }
        """)
        self.layout.addWidget(self.data_display)
    
    def update_data(self, calculations: Dict, celestial_data: Dict) -> None:
        """Atualiza os dados exibidos."""
        try:
            html = self._format_data_html(calculations, celestial_data)
            self.data_display.setHtml(html)
        except Exception as e:
            logging.error(f"Erro ao atualizar dados: {str(e)}")
            self.data_display.setPlainText("Erro ao carregar dados astronômicos")

    def _format_data_html(self, calculations: Dict, celestial_data: Dict) -> str:
        """Formata os dados como HTML com informações corretas"""
        try:
            earth_angle = calculations.get('earth_angle', 0) % 360
            venus_angle = calculations.get('venus_angle', 0) % 360
        
            # Verifica alinhamentos
            alignment = ""
            if abs(earth_angle - venus_angle) < 10 or abs(earth_angle - venus_angle - 180) < 10:
                alignment += "Terra e Vênus alinhados (Conjunção/Oposição).<br>"
            
            sun_angle = calculations.get('sun_angle_galactic', 0)
            if any(abs(sun_angle - x) < 5 for x in [0, 90, 180, 270]):
                alignment += f"Sol em um eixo galáctico principal ({sun_angle:.1f}°)."
            
            return f"""
            <html>
                {self._get_html_styles()}
                <body>
                <h2>Alinhamento Cósmico Completo</h2>
            
                <h3>Sistema Solar (Heliocêntrico)</h3>
                <p><b>Data:</b> {calculations.get('date', 'N/A')}</p>
                <p><b>Posição Terra (aprox.):</b> {earth_angle:.1f}°</p>
                <p><b>Posição Vênus (aprox.):</b> {venus_angle:.1f}°</p>
            
                <h3>Sistema Galáctico (Rel. ao Centro Galáctico)</h3>
                <p><b>Ângulo Solar Galáctico (modelo):</b> {sun_angle:.4f}°</p>
                <p><b>Progresso no Ciclo Galáctico (desde 21/12/2012):</b> {calculations.get('galactic_progress', 0):.10f}%</p>
            
                <h3>Alinhamentos Notáveis</h3>
                <p>{alignment if alignment else "Nenhum alinhamento significativo hoje."}</p>
                </body>
            </html>
            """
        except Exception as e:
            logging.error(f"Erro ao formatar HTML: {str(e)}")
            return "<h2>Erro ao formatar dados</h2>"

    def _get_html_styles(self) -> str:
        """Retorna os estilos CSS para a exibição."""
        return """
            <style>
                body { background-color: #000033; color: #e0e0ff; font-family: Arial; padding: 15px; }
                h2 { color: #64f5ff; border-bottom: 1px solid #4466ff; margin-top: 0; }
                h3 { color: #ffa500; }
                .highlight { color: #ffeeaa; font-weight: bold; }
                ul { padding-left: 20px; }
            </style>
        """

if HAS_OPENGL:
    class CosmosView(QOpenGLWidget, CosmosViewBase):
        """Visualização 3D do cosmos usando OpenGL."""
        
        def __init__(self, connector=None, parent=None):
            super().__init__(parent)
            CosmosViewBase.__init__(self, connector)
            self.setMinimumSize(800, 600)
            self._setup_opengl()
            self._setup_ui()

        def _setup_opengl(self):
            fmt = QSurfaceFormat()
            fmt.setSamples(4)
            fmt.setDepthBufferSize(24)
            self.setFormat(fmt)
            
            self.rotation_angle = 0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._animate)
            self.timer.start(30)

        def _setup_ui(self):
            self.overlay = QWidget(self)
            self.overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.overlay_layout = QVBoxLayout(self.overlay)
            
            self.data_display = AstronomicalDataDisplay()
            self.overlay_layout.addWidget(self.data_display)
            self.overlay.setGeometry(10, 10, 350, 400)

        def initializeGL(self):
            glClearColor(0.02, 0.0, 0.08, 1.0)
            glEnable(GL_DEPTH_TEST)
            if self.format().samples() > 0:
                glEnable(GL_MULTISAMPLE)

        def paintGL(self):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
    
            # Configura a perspectiva
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(-1.5, 1.5, -1.5, 1.5, -1.5, 1.5)
            glMatrixMode(GL_MODELVIEW)
    
            self._draw_black_hole()

            if not self.astronomical_calculations:
                return

            # Posição do Sol em relação ao centro galáctico
            sun_angle_rad = math.radians(self.astronomical_calculations.get('sun_angle_galactic', 0))
            sun_x = SUN_ORBIT_RADIUS_GL * math.cos(sun_angle_rad)
            sun_y = SUN_ORBIT_RADIUS_GL * math.sin(sun_angle_rad)

            # Desenha órbita do Sol
            glColor3f(0.7, 0.7, 0.2)
            self._draw_orbit_at_center(0, 0, SUN_ORBIT_RADIUS_GL, 100)

            # Desenha Sol
            glColor3f(1.0, 1.0, 0.0)
            self._draw_circle(sun_x, sun_y, SUN_SIZE_GL, 20)

            # Sistema planetário
            self._draw_planetary_system(sun_x, sun_y)

        def _draw_planetary_system(self, sun_x: float, sun_y: float) -> None:
            """Desenha o sistema planetário."""
            if not self.astronomical_calculations:
                return

            # Terra
            earth_angle_rad = math.radians(self.astronomical_calculations.get('earth_angle', 0))
            earth_x = sun_x + EARTH_ORBIT_RADIUS_AROUND_SUN_GL * math.cos(earth_angle_rad)
            earth_y = sun_y + EARTH_ORBIT_RADIUS_AROUND_SUN_GL * math.sin(earth_angle_rad)
            
            glColor3f(0.2, 0.2, 0.8)
            self._draw_orbit_at_center(sun_x, sun_y, EARTH_ORBIT_RADIUS_AROUND_SUN_GL, 60)
            
            glColor3f(0.2, 0.5, 1.0)
            self._draw_circle(earth_x, earth_y, EARTH_SIZE_GL, 20)

            # Vênus
            venus_angle_rad = math.radians(self.astronomical_calculations.get('venus_angle', 0))
            venus_x = sun_x + VENUS_ORBIT_RADIUS_AROUND_SUN_GL * math.cos(venus_angle_rad)
            venus_y = sun_y + VENUS_ORBIT_RADIUS_AROUND_SUN_GL * math.sin(venus_angle_rad)
            
            glColor3f(0.8, 0.5, 0.2)
            self._draw_orbit_at_center(sun_x, sun_y, VENUS_ORBIT_RADIUS_AROUND_SUN_GL, 50)
            
            glColor3f(0.9, 0.7, 0.3)
            self._draw_circle(venus_x, venus_y, VENUS_SIZE_GL, 20)

        def _draw_orbit_at_center(self, cx: float, cy: float, radius: float, segments: int = 100) -> None:
            """Desenha uma órbita circular."""
            glBegin(GL_LINE_LOOP)
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                glVertex2f(cx + math.cos(theta) * radius, 
                          cy + math.sin(theta) * radius)
            glEnd()

        def _draw_circle(self, cx: float, cy: float, r: float, segments: int) -> None:
            """Desenha um círculo preenchido."""
            glBegin(GL_POLYGON)
            for i in range(segments):
                theta = 2.0 * math.pi * i / segments
                glVertex2f(cx + r * math.cos(theta), cy + r * math.sin(theta))
            glEnd()

        def _draw_black_hole(self) -> None:
            """Desenha o centro galáctico."""
            glColor3f(0.1, 0.1, 0.1)
            self._draw_circle(0, 0, 0.1, 32)
            glColor3f(0.3, 0, 0)
            self._draw_circle(0, 0, 0.08, 32)
            glColor3f(0.8, 0, 0)
            self._draw_circle(0, 0, 0.05, 32)

        def _animate(self) -> None:
            """Anima a rotação da visualização."""
            self.rotation_angle = (self.rotation_angle + 0.5) % 360
            self.update()

        def update_display(self) -> None:
            """Atualiza a exibição de dados."""
            if hasattr(self, 'data_display'):
                self.data_display.update_data(self.astronomical_calculations, self.celestial_data)

else:
    class CosmosView(QWidget, CosmosViewBase):
        """Visualização 2D de fallback quando OpenGL não está disponível."""
        
        def __init__(self, connector=None, parent=None):
            super().__init__(parent)
            CosmosViewBase.__init__(self, connector)
            self._update_lock = False
            self._setup_ui()

        def _setup_ui(self):
            self.layout = QVBoxLayout(self)
            self.data_display = AstronomicalDataDisplay()
            self.layout.addWidget(self.data_display)
            self.setStyleSheet("background-color: #000020;")

        def update_data(self, date: QDate) -> None:
            """Atualiza os dados exibidos."""
            if self._update_lock or not date.isValid():
                return
            
            self._update_lock = True
            try:
                self.data_display.update_data(
                    self.astronomical_calculations,
                    self.celestial_data
                )
            except Exception as e:
                logging.error(f"Erro ao atualizar dados 2D: {str(e)}")
            finally:
                self._update_lock = False