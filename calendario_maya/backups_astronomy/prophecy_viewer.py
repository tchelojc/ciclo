import os
import sys
from datetime import datetime, date
from shared_imports import QLineEdit
import json
from typing import Union 
from pathlib import Path
from shared_imports import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QGroupBox, QLineEdit, QComboBox, QFormLayout, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QObject
from PyQt6.QtWidgets import QDateEdit
from calendario_maya.utils.prophecy_manager import ProphecyManager, ApproximateDate
from calendario_maya.utils.astronomy_utils import AstronomyUtils

class ProphecyViewer(QWidget):
    def __init__(self, connector=None):  # Tornar connector opcional
        super().__init__()
        self.connector = connector
        
        # Configura astronomia - usa connector se disponível, senão usa MayanAstronomy diretamente
        if connector and hasattr(connector, 'astronomy_utils'):
            self.astronomy = connector.astronomy_utils
            self.manager = ProphecyManager(connector)
        else:
            from utils.mayan_astronomy import MayanAstronomy
            self.astronomy = MayanAstronomy()
            self.manager = ProphecyManager()  # Sem connector
            
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Filtros
        filter_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.end_date = QDateEdit()
        filter_btn = QPushButton("Filtrar")
        filter_btn.clicked.connect(self._on_filter)
        filter_layout.addWidget(QLabel("De:"))
        filter_layout.addWidget(self.start_date)
        filter_layout.addWidget(QLabel("Até:"))
        filter_layout.addWidget(self.end_date)
        filter_layout.addWidget(filter_btn)
        main_layout.addLayout(filter_layout)
        
        # Corpo principal
        body_layout = QHBoxLayout()
        self.event_list = EventListWidget(self.manager)
        self.event_details = EventDetailsWidget()  # Note o nome correto
        body_layout.addWidget(self.event_list)
        body_layout.addWidget(self.event_details)
        main_layout.addLayout(body_layout)
        analysis_btn = QPushButton("Analisar Padrão 2012")
        analysis_btn.clicked.connect(self.analyze_2012_pattern)
        filter_layout.addWidget(analysis_btn)
        
        # Conexões
        self.event_list.event_selected.connect(self.event_details.show_event)
        
    def calculate_prophecy_cycles(self, event_data):
        """Enriquece os dados da profecia com cálculos de ciclo"""
        try:
            # Mantém os dados originais
            event_date = self._parse_date(event_data['date'])
        
            # Adiciona cálculos cíclicos
            cycles = astronomy_utils.calculate_cycles(event_date)
            event_data.update({
                'cycles': cycles,
                'alignment_score': self._calculate_alignment_score(cycles)
            })
        
            return event_data
        
        except Exception as e:
            print(f"Erro no cálculo de profecia: {e}")
            return event_data
    
    def filter_events_by_date(self):
        """Filtra eventos pelo intervalo de datas selecionado"""
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        self.event_list.filter_events_by_date(start.year, end.year)

    def setup_connections(self):
        """Configura todas as conexões entre componentes"""
        # Conecta o sinal da lista de eventos ao widget de detalhes
        self.event_list.event_selected.connect(self.event_detail.show_event)
        
        # Conecta também ao sinal da classe para uso externo
        self.event_list.event_selected.connect(self.event_selected)

    def load_data_async(self):
        """Carrega dados assincronamente se necessário"""
        # Implementação do carregamento assíncrono aqui
        pass

    def _setup_fallback_ui(self):
        """Cria uma interface simplificada em caso de erro"""
        fallback = QLabel("""
            <div style='text-align: center; padding: 50px; color: #ff5555;'>
                <h2>Prophecy Viewer Indisponível</h2>
                <p>Não foi possível carregar os dados de profecias</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        layout = QVBoxLayout()
        layout.addWidget(fallback)
        self.setLayout(layout)
        
    def on_events_loaded(self, events):
        """Lida com o carregamento completo dos eventos"""
        self.event_list.load_events()
        
    def on_load_error(self, error_msg):
        """Lida com erros no carregamento"""
        error_label = QLabel(f"Erro ao carregar eventos: {error_msg}")
        error_label.setStyleSheet("color: red;")
        self.layout().addWidget(error_label)
        
    def _on_filter(self):
        """Filtra eventos por data com tratamento robusto"""
        try:
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
        
            if start_date > end_date:
                start_date, end_date = end_date, start_date

            filtered = []
            for event in self.manager.events:
                event_date = self._parse_date(event.get('date'))
                if event_date and start_date <= event_date <= end_date:
                    filtered.append(event)
                
            self.event_list.update_events(filtered)
        except Exception as e:
            print(f"Erro ao filtrar: {e}")
            self.event_list.update_events(self.manager.events)
        
    def analyze_2012_pattern(self):
        """Analisa e exibe alinhamentos similares ao de 2012"""
        reference_date = datetime(2012, 12, 21)
        similar_dates = self.manager.find_similar_alignments(reference_date)
        
        if similar_dates:
            message = "Próximos alinhamentos similares a 2012:\n"
            message += "\n".join([d.strftime("%d/%m/%Y") for d in similar_dates])
        else:
            message = "Nenhum alinhamento similar encontrado nos próximos 100 anos"
            
        # Mostra os resultados (pode ser um QMessageBox ou na interface)
        self.event_details.show_message("Análise Cósmica", message)

class EventListWidget(QWidget):
    # Adicione isto:
    event_selected = pyqtSignal(dict)  # Sinal para comunicação com a main window
    
    def __init__(self, prophecy_manager, connector=None):
        super().__init__()
        self.prophecy_manager = prophecy_manager
        self.connector = connector
        self.setup_ui()
        
    def emit_event(self, event_id):
        details = self.prophecy_manager.get_event_detail(event_id)
        if details:
            self.event_selected.emit(details)  # Emitindo o sinal corretamente
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("📜 Eventos Históricos")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFA500;")
        layout.addWidget(title)
        
        # Barra de busca (opcional)
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Buscar eventos...")
        search_bar.textChanged.connect(self.filter_events)
        layout.addWidget(search_bar)
        
        # Área rolável de eventos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.event_container = QWidget()
        self.event_layout = QVBoxLayout(self.event_container)
        self.event_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.load_events()
        
        scroll.setWidget(self.event_container)
        layout.addWidget(scroll)
        
    def load_events(self):
        """Carrega eventos do prophecy_manager com tratamento robusto"""
        self.clear_events()
    
        try:
            # Verificar se o manager tem os dados necessários
            if not hasattr(self.prophecy_manager, 'load_events'):
                raise AttributeError("ProphecyManager não possui método load_events")
            
            events = self.prophecy_manager.load_events()
        
            if not isinstance(events, list):
                raise TypeError("Dados de eventos devem ser uma lista")
            
            for event in events:
                btn = QPushButton(f"{event.get('year', 'N/A')} - {event.get('title', 'Sem título')}")
                btn.setProperty('event_id', event.get('id', 0))
                btn.setProperty('event_year', event.get('year', 0))
                btn.clicked.connect(lambda _, e=event: self.emit_event(e.get('id')))
                self.event_layout.addWidget(btn)
        
        except Exception as e:
            error_label = QLabel(f"Erro ao carregar eventos: {str(e)}")
            error_label.setStyleSheet("color: red;")
            self.event_layout.addWidget(error_label)

    def _setup_fallback_ui(self):
        """Cria uma UI de fallback básica"""
        fallback = QLabel("""
            <div style='text-align: center; padding: 30px;'>
                <h3 style='color: #ff5555'>Visualizador de Profecias Indisponível</h3>
                <p>O componente não pôde ser carregado</p>
                <p>Verifique os logs para detalhes</p>
            </div>
        """)
        fallback.setTextFormat(Qt.TextFormat.RichText)
        layout = QVBoxLayout(self)
        layout.addWidget(fallback)
        self.setLayout(layout)
            
    def filter_events_by_year(self, start_year, end_year):
        """Filtra eventos por range de anos"""
        try:
            start = int(start_year)
            end = int(end_year)
            for i in range(self.event_layout.count()):
                widget = self.event_layout.itemAt(i).widget()
                if isinstance(widget, QPushButton):
                    event_year = int(widget.property('event_year'))
                    widget.setVisible(start <= event_year <= end)
        except:
            pass
    
    def filter_events(self, text):
        for i in range(self.event_layout.count()):
            widget = self.event_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setVisible(text.lower() in widget.text().lower())
    
    def update_events(self, events):
        """Atualiza a lista de eventos exibidos"""
        self.clear_events()
        for event in events:
            btn = QPushButton(f"{event.get('year', 'N/A')} - {event.get('title', 'Sem título')}")
            btn.setProperty('event_id', event.get('id', 0))
            btn.clicked.connect(lambda _, e=event: self.emit_event(e.get('id')))
            self.event_layout.addWidget(btn)
            
    def clear_events(self):
        for i in reversed(range(self.event_layout.count())):
            self.event_layout.itemAt(i).widget().setParent(None)


class EventDetailsWidget(QWidget):
    def __init__(self, astronomy_utils=None):
        super().__init__()
        self.astronomy_utils = astronomy_utils
        self.setup_ui()
        self.analysis_results = None
        self.placeholder = QLabel("Selecione um evento...")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details_layout.addWidget(self.placeholder)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Grupo de detalhes (existente)
        self.details_group = QGroupBox("Detalhes do Evento")
        self.details_layout = QVBoxLayout()
        
        # Grupo de análise cíclica (novo)
        self.analysis_group = QGroupBox("Análise Cíclica")
        self.analysis_layout = QVBoxLayout()
        
        # Botão para análise profética
        self.analyze_btn = QPushButton("Análise Profética")
        self.analyze_btn.clicked.connect(self.show_prophetic_analysis)
        
        # Adiciona os componentes
        self.details_group.setLayout(self.details_layout)
        self.analysis_group.setLayout(self.analysis_layout)
        
        layout.addWidget(self.details_group)
        layout.addWidget(self.analyze_btn)
        layout.addWidget(self.analysis_group)
        
    def show_event(self, event_data):
        self.clear_details()
        self.current_event = event_data
        
        # Mostra os detalhes básicos (existente)
        title = QLabel(f"<h2>{event_data['title']}</h2>")
        title.setTextFormat(Qt.TextFormat.RichText)
        self.details_layout.addWidget(title)
        
        # Adiciona análise cíclica básica
        self.add_cyclic_analysis(event_data)
    
    def add_cyclic_analysis(self, event_data):
        """Versão alternativa que usa MayanAstronomy diretamente"""
        try:
            event_date = self._parse_date(event_data.get('date'))
            if not event_date:
                return
                
            # Usa self.astronomy que pode ser tanto do connector quanto MayanAstronomy
            baktun = self.astronomy.calculate_baktun(event_date)
            venus_phase = self.astronomy.venus_phase_angle(event_date)
            galactic_year = self.astronomy.galactic_year_progress(event_date)
            
            html = f"""
            <div style='margin-top: 15px; border-top: 1px solid #6a3093; padding-top: 10px;'>
                <h3 style='color: #64c8ff'>Ciclos Astronômicos</h3>
                <table width='100%'>
                    <tr><td>🌀 Baktun:</td><td>{baktun:.2f}</td></tr>
                    <tr><td>♀ Fase de Vênus:</td><td>{venus_phase:.1f}°</td></tr>
                    <tr><td>🌌 Ano Galáctico:</td><td>{galactic_year:.1f}%</td></tr>
                </table>
            </div>
            """
            cosmic_label = QLabel(html)
            cosmic_label.setTextFormat(Qt.TextFormat.RichText)
            self.details_layout.addWidget(cosmic_label)
            
        except Exception as e:
            print(f"Erro na análise cíclica: {e}")
    
    def _parse_date(self, date_str):
        """Método auxiliar para parse de datas"""
        try:
            if isinstance(date_str, str):
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            elif isinstance(date_str, date):
                return date_str
            return None
        except:
            return None
    
    def set_event_detail(self, event):
        """Exibe os detalhes de um evento"""
        self.event = event
        self.update_display()
        
    def update_display(self):
        """Atualiza a exibição com base no evento atual"""
        if not hasattr(self, 'event') or not self.event:
            self.clear_details()
            return
            
        try:
            # Limpa os widgets anteriores
            self.clear_details()
            
            # Adiciona os novos widgets com os dados do evento
            title = QLabel(f"<h2>{self.event.get('title', 'Evento sem título')}</h2>")
            title.setTextFormat(Qt.TextFormat.RichText)
            self.details_layout.addWidget(title)
            
            # Restante da implementação de exibição...
            # (pode reutilizar o código do método show_event existente)
            
        except Exception as e:
            print(f"Erro ao atualizar exibição: {e}")
            error_label = QLabel("Erro ao exibir detalhes do evento")
            error_label.setStyleSheet("color: red;")
            self.details_layout.addWidget(error_label)
            
    def update_energy_graph(self, energy_level):
        # Simulação simples de gráfico - pode ser substituído por matplotlib ou outro
        width = 300
        filled = int(width * (energy_level / 100))
        
        html = f"""
        <div style='margin-top: 20px; text-align: center;'>
            <h4 style='color: #64c8ff'>Nível de Energia Cósmica</h4>
            <div style='background: #333; height: 20px; width: {width}px; margin: 0 auto;'>
                <div style='background: linear-gradient(to right, #6a3093, #a044ff); 
                             height: 100%; width: {filled}px;'></div>
            </div>
            <p style='color: white'>{energy_level}% do potencial máximo</p>
        </div>
        """
        self.energy_graph.setText(html)
    
    def clear_details(self):
        for i in reversed(range(self.details_layout.count())):
            widget = self.details_layout.itemAt(i).widget()
            if widget != self.placeholder:
                widget.setParent(None)
        
        if self.details_layout.count() == 0:
            self.details_layout.addWidget(self.placeholder)
            
    def show_message(self, title, message):
        """Exibe uma mensagem no widget de detalhes"""
        self.clear_details()
        title_label = QLabel(f"<h2>{title}</h2>")
        title_label.setTextFormat(Qt.TextFormat.RichText)
        self.details_layout.addWidget(title_label)
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        self.details_layout.addWidget(msg_label)
        
    def show_prophetic_analysis(self):
        """Mostra análise profética para o evento atual"""
        if not hasattr(self, 'current_event'):
            return
    
        try:
            event = self.current_event
            date_str = event.get('date')
            if not date_str:
                return
        
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
            if hasattr(self, 'astronomy_utils') and self.astronomy_utils:
                astronomy = self.astronomy_utils
            else:
                from calendario_maya.utils.mayan_astronomy import MayanAstronomy
                astronomy = MayanAstronomy()
    
            analysis = {
                'baktun': astronomy.calculate_baktun(date_obj),
                'venus_phase': astronomy.venus_phase_angle(date_obj),
                'galactic_year': astronomy.galactic_year_progress(date_obj),
                'alignment': astronomy._check_galactic_alignment(date_obj)
            }
    
            message = f"""
            <h3>Análise Profética</h3>
            <p><b>Data:</b> {date_obj.strftime('%d/%m/%Y')}</p>
            <p><b>Baktun:</b> {analysis['baktun']:.2f}</p>
            <p><b>Fase de Vênus:</b> {analysis['venus_phase']:.1f}°</p>
            <p><b>Ano Galáctico:</b> {analysis['galactic_year']:.1f}%</p>
            <p><b>Alinhamento:</b> {'Sim' if analysis['alignment'] else 'Não'}</p>
            """
            self.show_message("Análise Profética", message)
    
        except Exception as e:
            print(f"Erro na análise profética: {e}")
            self.show_message("Erro", "Não foi possível gerar a análise")
        