import math
from datetime import date
from typing import Union  # Para type hints
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from datetime import datetime
from calendario_maya.utils.astronomy import get_constellation_positions
from calendario_maya.utils.mayan_astronomy import MayanAstronomy
from calendario_maya.utils.astronomy_utils import AstronomyUtils
mayan_astro = MayanAstronomy()
venus_pos = mayan_astro.get_planetary_positions(date.today())['venus']

class StarMap(QGraphicsView):
    def __init__(self, hemisphere="Norte", parent=None):
        super().__init__(parent)
        from PyQt6.QtGui import QPainter
        
        self.hemisphere = hemisphere
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setup_ui()
        
    def setup_ui(self):
        # Configurações básicas
        self.setMinimumSize(600, 600)
        self.setStyleSheet("background: #0a0a1a; border: 1px solid #4466ff;")
        
        # Título
        title = self.scene.addText(f"Mapa Estelar - Hemisfério {self.hemisphere}")
        title.setDefaultTextColor(QColor("#ffffff"))
        title.setPos(10, 10)
        
        # Configurações de visualização
        self.setSceneRect(QRectF(0, 0, 800, 800))
        self.centerOn(400, 400)
        
    def update_positions(self, date, planetary_positions=None):
        """Atualiza o mapa estelar para uma data específica"""
        self.scene.clear()
        self.setup_ui()  # Re-adiciona o título
        
        # Obtém as posições das constelações
        constellations = get_constellation_positions(date, self.hemisphere)
        
        # Desenha as constelações
        for constellation in constellations:
            self.draw_constellation(constellation)
            
        # Desenha os planetas se fornecidos
        if planetary_positions:
            self.draw_planets(planetary_positions)
            
        # Adiciona legenda
        self.add_legend()

    def draw_constellation(self, constellation):
        """Desenha uma constelação no mapa"""
        color = QColor("#4ecca3") if constellation["name"] in ["Ursa Maior", "Orion"] else QColor("#64c8ff")
        
        # Desenha as estrelas
        for star in constellation["stars"]:
            x, y = self.projection(star["ra"], star["dec"])
            size = max(2, 8 - star["magnitude"])  # Estrelas mais brilhantes são maiores
            
            self.scene.addEllipse(x, y, size, size, 
                                QPen(color), 
                                QBrush(color))
        
        # Desenha as linhas de conexão
        for i, j in constellation["lines"]:
            if i < len(constellation["stars"]) and j < len(constellation["stars"]):
                star1 = constellation["stars"][i]
                star2 = constellation["stars"][j]
                x1, y1 = self.projection(star1["ra"], star1["dec"])
                x2, y2 = self.projection(star2["ra"], star2["dec"])
                
                self.scene.addLine(x1 + 2, y1 + 2, x2 + 2, y2 + 2, 
                                 QPen(color, 1, Qt.PenStyle.DashLine))

    def draw_planets(self, positions):
        """Desenha os planetas no mapa"""
        planet_colors = {
            "sun": QColor("#FFD700"),
            "moon": QColor("#C0C0C0"),
            "mercury": QColor("#A9A9A9"),
            "venus": QColor("#FFA07A"),
            "mars": QColor("#FF4500"),
            "jupiter": QColor("#F4A460"),
            "saturn": QColor("#DAA520")
        }
        
        for planet, data in positions.items():
            if planet in planet_colors:
                x, y = self.projection(data["ra"], data["dec"])
                size = 10 if planet == "sun" else 8
                
                self.scene.addEllipse(x - size/2, y - size/2, size, size,
                                    QPen(planet_colors[planet], 2),
                                    QBrush(planet_colors[planet]))
                
                # Adiciona rótulo
                label = self.scene.addText(planet.capitalize())
                label.setDefaultTextColor(planet_colors[planet])
                label.setPos(x + size, y)

    def projection(self, ra, dec):
        """Projeção esférica para coordenadas 2D"""
        # Ajusta para o hemisfério correto
        if self.hemisphere == "Sul":
            dec = -dec
            
        # Coordenadas polares para cartesianas
        r = (90 - abs(dec)) * 4  # Escala
        theta = math.radians(ra)
        
        x = 400 + r * math.cos(theta)
        y = 400 + r * math.sin(theta)
        
        return x, y

    def add_legend(self):
        """Adiciona legenda ao mapa"""
        legend = self.scene.addRect(600, 20, 180, 150, 
                                  QPen(QColor("#4466ff")), 
                                  QBrush(QColor("#0a0a1a")))
        
        # Texto da legenda
        text = self.scene.addText("Legenda:")
        text.setDefaultTextColor(QColor("#ffffff"))
        text.setPos(610, 30)
        
        # Exemplo de itens da legenda
        items = [
            ("Estrelas", "#64c8ff"),
            ("Planetas", "#FFD700"),
            ("Constelações", "#4ecca3")
        ]
        
        for i, (name, color) in enumerate(items):
            self.scene.addEllipse(615, 60 + i*30, 10, 10, 
                                QPen(QColor(color)), 
                                QBrush(QColor(color)))
            label = self.scene.addText(name)
            label.setDefaultTextColor(QColor("#ffffff"))
            label.setPos(630, 55 + i*30)