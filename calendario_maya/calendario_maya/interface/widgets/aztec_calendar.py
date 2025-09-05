# interface/widgets/aztec_calendar.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QDate, pyqtSignal

class AztecCalendarWidget(QWidget):
    date_changed = pyqtSignal(QDate)  # Sinal para notificar mudanças de data

    def __init__(self, parent=None, connector=None):
        super().__init__(parent)
        self.connector = connector
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Calendário Asteca")
        self.label.setStyleSheet("""
            font-size: 16px; 
            color: #d4af37;
            padding: 10px;
            background: #1a0a0a;
            border: 1px solid #5a0000;
            border-radius: 5px;
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
    def update_xiuhpohualli(self, date):
        """Atualiza a exibição para a data especificada"""
        # Exemplo básico - implemente a lógica real do Xiuhpohualli aqui
        day_name = self._get_aztec_day_name(date)
        self.label.setText(
            f"<b>Calendário Asteca</b><br>"
            f"Data: {date.toString('dd/MM/yyyy')}<br>"
            f"Dia: {day_name}"
        )
    
    def _get_aztec_day_name(self, date):
        """Lógica para determinar o nome do dia asteca"""
        # Implementação temporária - substitua pela lógica real
        aztec_days = ["Cipactli", "Ehecatl", "Calli", "Cuetzpalin", "Coatl",
                     "Miquiztli", "Mazatl", "Tochtli", "Atl", "Itzcuintli",
                     "Ozomahtli", "Malinalli", "Acatl", "Ocelotl", "Cuauhtli",
                     "Cozcaquauhtli", "Ollin", "Tecpatl", "Quiahuitl", "Xochitl"]
        return aztec_days[date.day() % 20]