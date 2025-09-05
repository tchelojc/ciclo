from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon

class AztecSidebar(QWidget):
    theme_changed = pyqtSignal(str) 
    menu_changed = pyqtSignal(int)
    civilization_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_aztec_style()
        self.active_button = None
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setSpacing(10)
        
        # Cabeçalho
        header = QLabel("CÓDICES\nASTECAS")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #ff6b6b; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Menu principal
        icons = ["🌋", "📜", "🖌️", "🌌", "⚔️"]
        menu_items = [
            ("Tonalpohualli", 0),
            ("Xiuhpohualli", 1), 
            ("Glifos Sagrados", 2),
            ("Cosmovisão", 3),
            ("Rituais", 4)
        ]
        
        for (text, index), icon in zip(menu_items, icons):
            btn = QPushButton(f"{icon}  {text}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=index: self.menu_changed.emit(i))
            layout.addWidget(btn)
        
        # Espaçador
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Botão de alternância
        switch_btn = QPushButton("⇄ Alternar para Maya")
        switch_btn.setIcon(QIcon("assets/maya_icon.png"))
        switch_btn.clicked.connect(lambda: self.civilization_changed.emit("maya"))
        switch_btn.setObjectName("themeButton")
        layout.addWidget(switch_btn)
        
        self.setLayout(layout)
        self.setFixedWidth(200)

    def set_active_button(self, mode):
        """Mantido para consistência, mas não usado no modo Asteca"""
        pass
        
    def apply_aztec_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #2a0000;
                border-right: 1px solid #5a0000;
            }
            QPushButton {
                color: #ff9e9e;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 12px 8px;
                text-align: left;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #3a0000;
                color: #ff6b6b;
            }
            QPushButton:pressed {
                background: #4a0000;
            }
            QPushButton.active {
                background-color: #5a0000;
                border-left: 4px solid #ff6b6b;
            }
            #themeButton {
                background: #5a0000;
                margin-top: 15px;
                text-align: center;
            }
        """)