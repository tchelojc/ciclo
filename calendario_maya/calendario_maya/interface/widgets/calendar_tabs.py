from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

class TzolkinTab(QWidget):
    def __init__(self, calendario, dados):
        super().__init__()
        self.calendario = calendario
        self.dados = dados
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabela de nahuales
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nahual", "Significado"])
        
        nahuales = self.dados.get('nahuales', [])
        self.table.setRowCount(len(nahuales))
        
        for i, nahual in enumerate(nahuales):
            self.table.setItem(i, 0, QTableWidgetItem(nahual.get('nome', '')))
            self.table.setItem(i, 1, QTableWidgetItem(nahual.get('significado', '')))
        
        layout.addWidget(self.table)
        self.setLayout(layout)
        
    def update_data(self, day_number: int):
        nahual = symbol_connector.get_nahual(day_number)
        if nahual:
            self.label.setText(f"{nahual['nome']} - Frequência: {nahual['frequencia']}Hz")

class TonalTab(QWidget):
    def __init__(self, calendario, dados):
        super().__init__()
        self.calendario = calendario
        self.dados = dados
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        signos = self.dados.get('signos', [])
        self.info_label.setText(f"Tonalpohualli - {len(signos)} signos carregados")
        
        layout.addWidget(self.info_label)
        self.setLayout(layout)

class LongCountTab(QWidget):
    def __init__(self, calendario):
        super().__init__()
        self.calendario = calendario
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Calculadora de Long Count")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.label)
        self.setLayout(layout)