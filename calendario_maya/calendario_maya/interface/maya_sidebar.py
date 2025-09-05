from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon

class MayanSidebar(QWidget):
    menu_changed = pyqtSignal(str)
    civilization_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    timeline_requested = pyqtSignal()
    prophecy_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.active_button = None
        self.buttons = {}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setSpacing(10)
    
        # Cabeçalho
        header = QLabel("SABEDORIA\nMAIA")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #4ecca3; margin-bottom: 20px;")
        layout.addWidget(header)
    
        # Menu principal
        self.buttons = {
            'calendar': self._create_menu_button("📅 Tzolk'in", 'calendar'),
            'glyphs': self._create_menu_button("🌀 Glifos Sagrados", 'glyphs'),
            'timeline': self._create_menu_button("⏳ Linha do Tempo", 'timeline', is_timeline=True),
            'math': self._create_menu_button("🧮 Matemática", 'math'),
            'cosmos': self._create_menu_button("🔭 Astronomia", 'cosmos'),
            'prophecy': self._create_menu_button("🔮 Profecia 2012", 'prophecy', is_prophecy=True)
        }

        self.calendar_btn = self.buttons['calendar']
        self.glyphs_btn = self.buttons['glyphs']
        self.timeline_btn = self.buttons['timeline'] 
        self.math_btn = self.buttons['math']
        self.cosmos_btn = self.buttons['cosmos']
        self.prophecy_btn = self.buttons['prophecy']
    
        # Adiciona botões na ordem correta
        for key in ['calendar', 'glyphs', 'timeline', 'math', 'cosmos', 'prophecy']:
            layout.addWidget(self.buttons[key])
    
        # Espaçador
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
        # Botão de alternância
        switch_btn = QPushButton("⇄ Alternar para Asteca")
        switch_btn.setIcon(QIcon("assets/aztec_icon.png"))
        switch_btn.clicked.connect(self._emit_switch_signals)
        switch_btn.setObjectName("themeButton")
        layout.addWidget(switch_btn)
    
        self.setLayout(layout)
        self.setFixedWidth(200)
        self._apply_styles()
        self.set_active_button('timeline')

    def _create_menu_button(self, text, index, is_timeline=False, is_prophecy=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setProperty("mode", "timeline" if is_timeline else "prophecy" if is_prophecy else None)
    
        if is_timeline:
            btn.clicked.connect(self._emit_timeline_signal)
        elif is_prophecy:
            btn.clicked.connect(self._emit_prophecy_signal)
        else:
            btn.clicked.connect(lambda: self.menu_changed.emit(index))
    
        return btn

    def _emit_timeline_signal(self):
        """Emite sinal para timeline"""
        self.set_active_button('timeline')
        self.timeline_requested.emit()

    def _emit_prophecy_signal(self):
        """Emite sinal para profecia"""
        self.set_active_button('prophecy')
        self.prophecy_requested.emit()

        
    def set_active_button(self, mode):
        """Define qual botão deve aparecer como ativo"""
        # Remove o estilo do botão ativo atual
        if self.active_button:
            self.active_button.setStyleSheet("")
        
        # Define o novo botão ativo
        if mode in self.buttons:
            self.active_button = self.buttons[mode]
            self.active_button.setStyleSheet("""
                background-color: #1a3a5a;
                border-left: 4px solid #4ecca3;
            """)

    def _emit_switch_signals(self):
        """Emite ambos os sinais para manter compatibilidade"""
        self.civilization_changed.emit("aztec")
        self.theme_changed.emit("aztec")

    def _apply_styles(self):
        """Aplica os estilos ao sidebar"""
        self.setStyleSheet("""
            QWidget {
                background: #0a1a2a;
                border-right: 1px solid #1a3a5a;
            }
            QPushButton {
                color: #a8e6cf;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 12px 8px;
                text-align: left;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #1a2a3a;
                color: #4ecca3;
            }
            QPushButton:pressed {
                background: #2a3a4a;
            }
            #themeButton {
                background: #1a3a5a;
                margin-top: 15px;
                text-align: center;
            }
        """)