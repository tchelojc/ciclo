from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QDate

class VenusTracker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Rastreador de Vênus")
        self.label.setStyleSheet("font-size: 14px; color: #ff6b6b;")
        layout.addWidget(self.label)
        self.setLayout(layout)
        
    def update_venus_phase(self, date):
        self.label.setText(f"Fase de Vênus em {date.toString('dd/MM/yyyy')}")