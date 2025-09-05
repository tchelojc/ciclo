from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class GraphGenerator(QWidget):
    def __init__(self, celestial_data, parent=None):
        super().__init__(parent)
        self.celestial_data = celestial_data
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # Cria figura do matplotlib
        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.generate_graphs()
        
    def generate_graphs(self):
        """Gera gráficos dos dados astronômicos"""
        self.figure.clear()
        
        # Exemplo: Gráfico de energia dos corpos celestes
        bodies = []
        energies = []
        for body, data in self.celestial_data.items():
            if isinstance(data, dict) and 'energy' in data:
                bodies.append(body.capitalize())
                energies.append(data['energy'])
        
        if bodies:
            ax1 = self.figure.add_subplot(211)
            ax1.bar(bodies, energies, color=['gold', 'orange', 'silver'])
            ax1.set_title('Energia dos Corpos Celestes')
            ax1.set_ylabel('Energia')
            
        # Exemplo: Posições azimutais
        ax2 = self.figure.add_subplot(212, projection='polar')
        for body, data in self.celestial_data.items():
            if isinstance(data, dict) and 'azimuth' in data:
                theta = math.radians(data['azimuth'])
                r = data.get('distance', 1)
                ax2.plot(theta, r, 'o', label=body.capitalize())
        ax2.set_title('Posições Azimutais')
        ax2.legend()
        
        self.canvas.draw()