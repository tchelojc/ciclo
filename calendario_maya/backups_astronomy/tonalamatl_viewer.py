from PyQt6.QtWidgets import QWidget, QLabel

class TonalamatlViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QLabel("Tonalamatl Viewer")
        self.label.setStyleSheet("color: #d4af37;")
        
    def update_tonalli(self, date):
        self.label.setText(f"Energia do dia: {date.dayOfWeek()}")