from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser

class EventDetailWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setup_ui()
    
    def setup_ui(self):
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        self.year_label = QLabel()
        self.year_label.setStyleSheet("color: #aaaaaa;")
        self.layout.addWidget(self.year_label)
        
        self.description_browser = QTextBrowser()
        self.description_browser.setStyleSheet("background: #333344;")
        self.layout.addWidget(self.description_browser)
        
        self.sources_label = QLabel("Fontes:")
        self.sources_label.setStyleSheet("font-style: italic;")
        self.layout.addWidget(self.sources_label)
    
    def load_event(self, event_data):
        self.title_label.setText(event_data['title'])
        self.year_label.setText(f"Ano: {event_data['year']} {self.get_era(event_data['year'])}")
        self.description_browser.setText(event_data['description'])
        self.sources_label.setText("Fontes: " + ", ".join(event_data['sources']))
    
    def get_era(self, year):
        return "a.C." if year < 0 else "d.C."