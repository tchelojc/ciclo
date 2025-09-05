from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QGroupBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QAction

class TonalTab(QWidget):
    def __init__(self, calendario, dados):
        super().__init__()
        self.dados = dados
        self.init_ui()
        
    def init_ui(self):
        # Layout principal com rolagem
        main_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Estilo
        self.setStyleSheet("""
            QLabel {
                color: #e4d3ff;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #6a3093;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #f8f8ff;
                font-size: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTableWidget {
                background: rgba(26, 10, 94, 0.7);
                gridline-color: #3a2a5a;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #3d2a8e;
                color: white;
                padding: 4px;
                border: none;
            }
            .signo-card {
                background: rgba(58, 42, 90, 0.6);
                border-radius: 8px;
                padding: 10px;
                border: 1px solid #6a3093;
            }
        """)
        
        # 1. Cabeçalho com informações gerais
        header = QLabel("Tonalpohualli - O Calendário Sagrado Asteca")
        header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #6a3093; margin-bottom: 15px;")
        layout.addWidget(header)
        
        # 2. Seção de Signos
        self.add_signos_section(layout)
        
        # 3. Seção de Trecenas
        self.add_trecenas_section(layout)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def add_signos_section(self, layout):
        """Adiciona seção dos 20 Signos do Tonalpohualli"""
        group = QGroupBox("Os 20 Signos do Tonalpohualli")
        group_layout = QVBoxLayout()
        
        # Tabela de signos
        table = QTableWidget()
        table.setRowCount(len(self.dados['signos']))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Signo", "Nome", "Significado"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, signo in enumerate(self.dados['signos']):
            # Ícone (usando número como placeholder)
            icon_item = QTableWidgetItem(str(signo['id']))
            icon_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_item = QTableWidgetItem(signo['nome'])
            meaning_item = QTableWidgetItem(signo['significado'])
            
            table.setItem(i, 0, icon_item)
            table.setItem(i, 1, name_item)
            table.setItem(i, 2, meaning_item)
        
        group_layout.addWidget(table)
        
        # Explicação adicional
        info = QLabel(
            "Cada dia no Tonalpohualli é governado por um desses 20 signos,\n"
            "que se combinam com números de 1 a 13 para formar um ciclo de 260 dias."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-style: italic; margin-top: 10px;")
        
        group_layout.addWidget(info)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_trecenas_section(self, layout):
        """Adiciona seção das 20 Trezenas (períodos de 13 dias)"""
        group = QGroupBox("As 20 Trezenas (Ciclos de 13 Dias)")
        group_layout = QVBoxLayout()
        
        # Container com rolagem horizontal para as trecenas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        hbox = QHBoxLayout(content)
        
        # Cria um card para cada trecena
        for trecena in self.dados['trecenas']:
            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet(".QFrame { background: rgba(58, 42, 90, 0.6); border-radius: 8px; }")
            frame_layout = QVBoxLayout(frame)
            
            # Título da trecena
            title = QLabel(f"Trecena {trecena['id']}: {trecena['significado'].split(' - ')[0]}")
            title.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title.setStyleSheet("color: #e4d3ff; margin-bottom: 5px;")
            frame_layout.addWidget(title)
            
            # Signos da trecena
            signos_label = QLabel("Signos:")
            signos_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
            frame_layout.addWidget(signos_label)
            
            for signo_id in trecena['signos']:
                signo = next(s for s in self.dados['signos'] if s['id'] == signo_id)
                signo_text = QLabel(f"{signo_id}. {signo['nome']} - {signo['significado']}")
                signo_text.setStyleSheet("margin-left: 10px;")
                frame_layout.addWidget(signo_text)
            
            # Significado completo
            significado = QLabel(trecena['significado'].split(' - ')[1])
            significado.setStyleSheet("font-style: italic; margin-top: 10px; color: #c9b2ff;")
            significado.setWordWrap(True)
            frame_layout.addWidget(significado)
            
            frame.setFixedWidth(250)
            hbox.addWidget(frame)
        
        scroll.setWidget(content)
        group_layout.addWidget(scroll)
        
        # Explicação adicional
        info = QLabel(
            "Cada trecena representa um período de 13 dias com um tema espiritual específico.\n"
            "O ciclo completo de 20 trecenas forma os 260 dias do Tonalpohualli."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-style: italic; margin-top: 10px;")
        
        group_layout.addWidget(info)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Espaçamento final
        layout.addStretch()