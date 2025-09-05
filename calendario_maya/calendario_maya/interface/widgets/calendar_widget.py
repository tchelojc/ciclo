from shared_imports import QLineEdit
from typing import Dict, Any # <--- IMPORTAÇÃO ADICIONADA/VERIFICADA
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QWidget,
    QCalendarWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit
)
from PyQt6.QtGui import QPixmap # QPixmap é usado
from pathlib import Path
import json

# Supondo que estes imports estão corretos para sua estrutura
from core.data_bridge import data_bridge
from config.paths import path_manager
from config.styles import load_styles  # Importa diretamente do módulo
from config import style_loader

# --- Placeholder para conversor_temporal ---
class ConversorTemporalPlaceholder:
    def quantico_para_terrestre(self, valor, unidade):
        return float(valor) * 24.0 

    def calcular_ciclo_solar(self, date_obj):
        year = date_obj.year if hasattr(date_obj, 'year') else 2023
        month = date_obj.month if hasattr(date_obj, 'month') else 1
        day = date_obj.day if hasattr(date_obj, 'day') else 1
        return (year + month / 12.0 + day / 365.0) % 11.0

conversor_temporal = ConversorTemporalPlaceholder() # Substitua pelo seu import real
# --- Fim do Placeholder ---

# --- Implementações das Abas ---
class TzolkinTab(QWidget):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.data = data # Pode ser usado para configuração inicial se necessário
        layout = QVBoxLayout(self)
        self.info_label = QLabel("Tzolk'in (Selecione uma data no calendário)")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def update_data(self, day_info: Dict[str, Any]):
        nahual_data = day_info.get('nahual', {})
        numero = day_info.get('numero_tzolkin', '')
        text = (f"<b>Tzolk'in:</b><br>"
                f"Nahual: {nahual_data.get('nome', 'N/A')} {nahual_data.get('glifo', '')}<br>"
                f"Número: {numero}<br>"
                f"Significado Tradicional: {nahual_data.get('significado_tradicional', 'N/A')}<br>"
                f"Significado Quântico: {nahual_data.get('significado_quantico', 'N/A')}")
        self.info_label.setText(text)

class TonalTab(QWidget):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.data = data
        layout = QVBoxLayout(self)
        self.info_label = QLabel("Tonalpohualli (Selecione uma data no calendário)")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def update_data(self, day_info: Dict[str, Any]):
        signo_data = day_info.get('signo', {})
        trecena_info = day_info.get('trecena_info', 'N/A')
        text = (f"<b>Tonalpohualli:</b><br>"
                f"Signo: {signo_data.get('nome', 'N/A')} {signo_data.get('glifo', '')}<br>"
                f"Trecena: {trecena_info}<br>"
                f"Energia: {signo_data.get('energia', 'N/A')}")
        self.info_label.setText(text)

class LongCountTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.info_label = QLabel("Conta Longa (Implementação Pendente)")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def update_data(self, long_count_str: str):
        self.info_label.setText(f"<b>Conta Longa:</b><br>{long_count_str}")

class CalendarWidget(QWidget):
    date_changed = pyqtSignal(QDate)
    
    def __init__(self, connector=None, parent=None): 
        super().__init__(parent)
        self.connector = connector
        self.current_date = QDate.currentDate()
        self.tzolk_data: Dict[str, Any] = {}
        self.tonal_data: Dict[str, Any] = {}

        self._load_initial_data()
        self._init_ui()
        self._setup_connections()
        self.load_styles()

        self.calendar.setSelectedDate(QDate.currentDate()) # Define data atual
        self._on_date_changed() # Dispara a primeira atualização

    def _load_initial_data(self):
        print("🌀 CalendarWidget: Carregando dados calendáricos...")
        try:
            # Prioritiza data_bridge se ele já tem os dados populados externamente
            tzolk_loaded_from_bridge = hasattr(data_bridge, 'tzolk_data') and data_bridge.tzolk_data
            tonal_loaded_from_bridge = hasattr(data_bridge, 'tonal_data') and data_bridge.tonal_data

            if tzolk_loaded_from_bridge:
                self.tzolk_data = data_bridge.tzolk_data
                print("  Dados Tzolk'in encontrados via data_bridge.")
            else:
                # Usa path_manager.ESSENTIAL_FILES (conforme seu paths.py)
                tzolk_path = path_manager.get('tzolk.json')  # Adicione a extensão .json
                self.tzolk_data = self._load_json_file(tzolk_path)
                if self.tzolk_data: data_bridge.tzolk_data = self.tzolk_data # Atualiza o bridge

            if tonal_loaded_from_bridge:
                self.tonal_data = data_bridge.tonal_data
                print("  Dados Tonalpohualli encontrados via data_bridge.")
            else:
                tonal_path = path_manager.ESSENTIAL_FILES.get('tonalpohualli')
                self.tonal_data = self._load_json_file(tonal_path)
                if self.tonal_data: data_bridge.tonal_data = self.tonal_data # Atualiza o bridge

        except AttributeError as ae:
            print(f"⚠️ Erro de atributo em path_manager ou data_bridge: {ae}. Verifique config/paths.py e core/data_bridge.py.")
            self._load_fallback_data()
        except Exception as e:
            print(f"⚠️ Falha crítica ao carregar dados principais: {e}")
            self._load_fallback_data()
        finally:
            self._verify_data_structure()

    def _load_json_file(self, filepath: Path | None) -> Dict[str, Any]:
        """Carrega arquivo JSON com verificações adicionais"""
        if not filepath:
            return {}
        
        try:
            if not filepath.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
                # Verificação básica de estrutura
                if not isinstance(data, dict):
                    raise ValueError("JSON inválido - Esperado um objeto")
                
                return data
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar {filepath.name}: {str(e)}")
            return {}

    def _load_fallback_data(self):
        print("⚡ Ativando dados de fallback devido a erro de carregamento.")
        self.tzolk_data = {
            'nahuales': [{'nome': 'Fallback Nahual', 'glifo': '⚛', 'significado_tradicional': 'N/A', 'significado_quantico': 'Estado de Superposição'}],
            'constantes': {'ciclo_sagrado': 260}
        }
        self.tonal_data = {
            'signos': [{'nome': 'Fallback Signo', 'glifo': '🌀', 'energia': 'KIN X'}],
            'trecenas': []
        }

    def _verify_data_structure(self):
        """Verificação completa da estrutura de dados com fallback robusto"""
        # Função auxiliar para garantir listas
        def ensure_list(data, key, default_item):
            if key not in data or not isinstance(data[key], list):
                data[key] = [default_item]
            elif not data[key]:  # Lista vazia
                data[key].append(default_item)

        # 1. Verificação Tzolk'in
        if not isinstance(self.tzolk_data, dict):
            self.tzolk_data = {}
    
        # Garante nahuales
        ensure_list(self.tzolk_data, 'nahuales', {
            'nome': 'Nahual Padrão',
            'glifo': '🌀', 
            'significado_tradicional': 'Significado padrão',
            'significado_quantico': 'Estado quântico padrão'
        })
    
        # Garante constantes
        required_constants = {
            'ciclo_sagrado': 260,
            'kin_por_uinal': 20,
            'uinales_por_tun': 18,
            'dias_por_tun': 360
        }
    
        if 'constantes' not in self.tzolk_data:
            self.tzolk_data['constantes'] = {}
    
        for const, default_val in required_constants.items():
            if const not in self.tzolk_data['constantes']:
                self.tzolk_data['constantes'][const] = default_val

        # 2. Verificação Tonalpohualli
        if not isinstance(self.tonal_data, dict):
            self.tonal_data = {}
    
        ensure_list(self.tonal_data, 'signos', {
            'nome': 'Signo Padrão',
            'glifo': '✨',
            'energia': 'Energia padrão'
        })
    
        # 3. Log de verificação
        print("✅ Estrutura de dados verificada com sucesso")
        print(f"- Nahuales: {len(self.tzolk_data['nahuales'])}")
        print(f"- Constantes: {self.tzolk_data['constantes']}")
        print(f"- Signos: {len(self.tonal_data.get('signos', []))}")
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        main_layout.addWidget(self.calendar)

        self.tab_widget = QTabWidget()
        # Passa os dados já carregados (ou fallback) para as abas
        self.tzolkin_tab = TzolkinTab(self.tzolk_data)
        self.tonal_tab = TonalTab(self.tonal_data)
        self.long_count_tab = LongCountTab()

        self.tab_widget.addTab(self.tzolkin_tab, "Tzolk'in")
        self.tab_widget.addTab(self.tonal_tab, "Tonalpohualli")
        self.tab_widget.addTab(self.long_count_tab, "Conta Longa")
        main_layout.addWidget(self.tab_widget)

        self.time_conversion_label = QLabel("Conversões temporais aparecerão aqui.")
        self.time_conversion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_conversion_label.setWordWrap(True)
        main_layout.addWidget(self.time_conversion_label)
        self.setLayout(main_layout)

    def _setup_connections(self):
        self.calendar.selectionChanged.connect(self._on_date_changed)

    def _on_date_changed(self):
        selected_qdate = self.calendar.selectedDate()
        self.date_changed.emit(selected_qdate)
        
        if self.connector:
            self.connector.current_date = selected_qdate 
    
        # Obtém dados formatados
        py_date = selected_qdate.toPyDate()
        tzolkin_info = {}
        tonal_info = {}
        long_count_str = "N/A"
    
        if self.connector:
            try:
                tzolkin_info = self.connector.get_tzolkin_for_date(py_date) or {}
                tonal_info = self.connector.get_tonalpohualli_for_date(py_date) or {}
                long_count_str = self.connector.gregorian_to_long_count(py_date) or "N/A"
            except Exception as e:
                print(f"Erro ao obter dados do connector: {str(e)}")
    
        # Atualiza abas
        self.tzolkin_tab.update_data(tzolkin_info)
        self.tonal_tab.update_data(tonal_info)
        self.long_count_tab.update_data(long_count_str)
    
        self._update_time_conversion_display(py_date)

    def _update_time_conversion_display(self, selected_py_date):
        horas_terrestres = conversor_temporal.quantico_para_terrestre(1, 'dias')
        ciclo_solar = conversor_temporal.calcular_ciclo_solar(selected_py_date)
        self.time_conversion_label.setText(
            f"<b>Conversão Temporal (Exemplo):</b>\n"
            f"1 unidade quântica (dia) = {horas_terrestres:.2f} horas terrestres\n"
            f"Ciclo solar atual (Exemplo): {ciclo_solar:.4f}"
        )

    def update_tab_data(self, date):
        """Atualiza todas as abas com dados consistentes"""
        try:
            # Tzolk'in
            tzolkin_data = self.connector.get_tzolkin_for_date(date)
            self.tzolkin_tab.update_data(tzolkin_data)
        
            # Tonalpohualli
            tonal_data = self.connector.get_tonalpohualli_for_date(date)
            self.tonal_tab.update_data(tonal_data)
        
            # Long Count
            long_count = self.connector.gregorian_to_long_count(date)
            self.long_count_tab.update_data(long_count)
        
        except Exception as e:
            print(f"Erro ao atualizar abas: {e}")
        
    def load_styles(self):
        """Estilo do calendário com melhor contraste"""
        calendar_style = """
        /* Fundo geral */
        QCalendarWidget {
            background-color: #000033;
        }
    
        /* Cabeçalho (mês/ano) */
        QCalendarWidget QToolButton {
            color: #64f5ff;
            font-size: 14px;
            font-weight: bold;
            background-color: #1a1a5a;
            padding: 5px;
            border-radius: 4px;
        }
    
        /* Dias da semana */
        QCalendarWidget QWidget#qt_calendar_navigationbar {
            background-color: #1a1a5a;
        }
    
        QCalendarWidget QAbstractItemView {
            outline: 0; /* Remove borda de foco */
        }
    
        /* Dias normais */
        QCalendarWidget QAbstractItemView:enabled {
            color: #ffffff;
            background-color: #000044;
            font-size: 12px;
        }
    
        /* Dia selecionado */
        QCalendarWidget QAbstractItemView:enabled:selected {
            background-color: #4466ff;
            color: #ffffff;
            font-weight: bold;
        }
    
        /* Dias de outros meses */
        QCalendarWidget QAbstractItemView:disabled {
            color: #666699;
        }
    
        /* Grade do calendário */
        QCalendarWidget QTableView {
            alternate-background-color: #000033;
            gridline-color: #4466ff;
        }
        """
        self.setStyleSheet(calendar_style)

    def update_display(self, date):
        """Atualiza o widget com uma nova data (interface requerida pelo Connector)"""
        if isinstance(date, QDate):
            self.calendar.setSelectedDate(date)
        elif hasattr(date, 'toPyDate'):  # Para objetos QDate
            self.calendar.setSelectedDate(date)
        else:
            try:
                qdate = QDate(date.year, date.month, date.day)
                if qdate.isValid():
                    self.calendar.setSelectedDate(qdate)
            except (AttributeError, TypeError):
                print(f"Formato de data não suportado: {type(date)}")
            
    def selectedDate(self) -> QDate:
        return self.calendar.selectedDate()

    def set_selected_date(self, date_input: Any):
        # Lógica de conversão e validação de data
        q_date_to_set = None
        if isinstance(date_input, QDate) and date_input.isValid():
            q_date_to_set = date_input
        elif hasattr(date_input, 'year') and hasattr(date_input, 'month') and hasattr(date_input, 'day'): # datetime.date or similar
            try:
                q_date_to_set = QDate(date_input.year, date_input.month, date_input.day)
                if not q_date_to_set.isValid(): q_date_to_set = None
            except ValueError: q_date_to_set = None # Ex: ano fora do range do QDate
        elif isinstance(date_input, str):
            q_date_to_set = QDate.fromString(date_input, Qt.DateFormat.ISODate) # YYYY-MM-DD
            if not q_date_to_set.isValid(): q_date_to_set = None
        
        if q_date_to_set:
            self.calendar.setSelectedDate(q_date_to_set)
        else:
            print(f"Formato de data não suportado ou data inválida para set_selected_date: {date_input}")


    def set_era(self, era_info: Any):
        print(f"CalendarWidget: set_era chamado com {era_info}. Implementação pendente.")
        # Se 'era_info' for uma data (QDate ou datetime.date), tente definir o calendário para essa data.
        if isinstance(era_info, (QDate, type(datetime.now().date()))):
            self.set_selected_date(era_info)
        elif isinstance(era_info, str): # Tenta converter string para data
            self.set_selected_date(era_info)