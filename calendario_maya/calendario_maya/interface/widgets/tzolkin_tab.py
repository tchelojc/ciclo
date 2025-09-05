from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QGroupBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction 

class TzolkinTab(QWidget):
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
        """)
        
        # 1. Cabeçalho com informações gerais
        header = QLabel(f"Calendário Sagrado Tzolk'in - Ciclo de {self.dados['constantes']['ciclo_sagrado']} dias")
        header.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #6a3093; margin-bottom: 15px;")
        layout.addWidget(header)
        
        # 2. Tabela de Nahuales
        self.add_nahuales_section(layout)
        
        # 3. Tabela de Energias
        self.add_energias_section(layout)
        
        # 4. Informações do Ciclo
        self.add_ciclo_section(layout)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
    
    def add_nahuales_section(self, layout):
        """Adiciona seção de Nahuales com tabela detalhada"""
        group = QGroupBox("Os 20 Nahuales do Tzolk'in")
        group_layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setRowCount(len(self.dados['nahuales']))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Nahual", "Nome", "Significado"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, nahual in enumerate(self.dados['nahuales']):
            # Ícone/glifo (simplificado - poderia ser uma imagem)
            glyph_item = QTableWidgetItem(chr(0x1F700 + i))  # Usando caracteres Unicode como placeholder
            glyph_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_item = QTableWidgetItem(nahual['nome'])
            meaning_item = QTableWidgetItem(nahual['significado'])
            
            table.setItem(i, 0, glyph_item)
            table.setItem(i, 1, name_item)
            table.setItem(i, 2, meaning_item)
        
        group_layout.addWidget(table)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_energias_section(self, layout):
        """Adiciona seção de Energias Tonais"""
        group = QGroupBox("As 13 Energias Tonais")
        group_layout = QVBoxLayout()
        
        table = QTableWidget()
        table.setRowCount(len(self.dados['energias']))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Número", "Nome Maia", "Significado"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        for i, energia in enumerate(self.dados['energias']):
            num_item = QTableWidgetItem(str(i+1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_item = QTableWidgetItem(energia['nome'])
            meaning_item = QTableWidgetItem(energia['significado'])
            
            table.setItem(i, 0, num_item)
            table.setItem(i, 1, name_item)
            table.setItem(i, 2, meaning_item)
        
        group_layout.addWidget(table)
        
        # Explicação adicional
        info = QLabel("Cada dia no Tzolk'in combina um Nahual (de 1 a 20) com uma Energia (de 1 a 13),\n"
                     "criando um ciclo único de 260 dias (20 x 13).")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-style: italic; margin-top: 10px;")
        
        group_layout.addWidget(info)
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def add_ciclo_section(self, layout):
        """Adiciona informações sobre o ciclo sagrado"""
        group = QGroupBox("O Ciclo Sagrado de 260 Dias")
        group_layout = QVBoxLayout()
        
        # Tabela de constantes
        table = QTableWidget()
        table.setRowCount(4)
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Unidade", "Valor"])
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        constants = self.dados['constantes']
        rows = [
            ("Dias em um ciclo sagrado (Tzolk'in)", constants['ciclo_sagrado']),
            ("Kins (dias) em um Uinal", constants['kin_por_uinal']),
            ("Uinales em um Tun", constants['uinales_por_tun']),
            ("Dias em um Tun", constants['dias_por_tun'])
        ]
        
        for i, (label, value) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(label))
            table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        group_layout.addWidget(table)
        
        # Explicação matemática
        math_info = QLabel(
            "Matematicamente: 1 Tun = {uinales} Uinales × {kins} Kins = {dias} dias\n"
            "O ciclo de 260 dias não se alinha com o ano solar, mas sincroniza com:\n"
            "- O ciclo gestacional humano\n"
            "- O período orbital de Vênus\n"
            "- O ciclo de manchas solares".format(
                uinales=constants['uinales_por_tun'],
                kins=constants['kin_por_uinal'],
                dias=constants['dias_por_tun']
            )
        )
        math_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        math_info.setWordWrap(True)
        math_info.setStyleSheet("margin-top: 15px;")
        
        group_layout.addWidget(math_info)
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        # Espaçamento final
        layout.addStretch()