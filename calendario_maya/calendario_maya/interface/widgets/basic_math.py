from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class BasicMathViewer(QWidget):
    def __init__(self, parent=None, connector=None):
        super().__init__(parent)
        self.connector = connector
        layout = QVBoxLayout()
        self.label = QLabel("Cálculos Matemáticos Básicos\n\nInstale PyQt6-Charts para recursos avançados")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def update_calculations(self, date):
        try:
            if not hasattr(self, 'connector') or not self.connector:
                raise AttributeError("Connector não disponível")
            
            calculations = f"""
            <div style='color:#e4d3ff; text-align:center;'>
                <h3>Cálculos para {date.toString('dd/MM/yyyy')}</h3>
                <p>Instale PyQt6-Charts para gráficos quânticos</p>
            </div>
            """
            self.label.setText(calculations)
        except Exception as e:
            print(f"Erro no MathViewer: {e}")
            self.label.setText("Cálculos indisponíveis")