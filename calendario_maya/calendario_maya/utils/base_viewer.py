# utils/base_viewer.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QDate

class BaseViewer(QWidget):
    """
    Classe base abstrata para todos os visualizadores
    Implementa funcionalidades comuns e interface padrão
    """
    
    def __init__(self, connector=None, parent=None):
        super().__init__(parent)
        self.connector = connector
        self.current_date = QDate.currentDate()
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa a interface do usuário"""
        raise NotImplementedError("Método _init_ui deve ser implementado pelas subclasses")
    
    def update_for_date(self, date):
        """
        Atualiza a visualização para uma data específica
        :param date: QDate contendo a data para atualização
        """
        self.current_date = date
        self._update_display()
    
    def _update_display(self):
        """Atualiza todos os elementos visuais (método interno)"""
        raise NotImplementedError("Método _update_display deve ser implementado pelas subclasses")
    
    def get_current_data(self):
        """Retorna os dados atualmente exibidos"""
        return {
            'date': self.current_date.toString('yyyy-MM-dd'),
            'viewer_type': self.__class__.__name__
        }