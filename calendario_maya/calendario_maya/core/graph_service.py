# core/graph_service.py
import importlib
from typing import Optional, Any
from PyQt6.QtWidgets import QWidget

class GraphService:
    def __init__(self):
        self._has_charts = self._check_charts_availability()
        
    def _check_charts_availability(self) -> bool:
        try:
            importlib.import_module('PyQt6.QtChart')
            return True
        except ImportError:
            return False
    
    def create_chart_widget(self, parent: QWidget = None) -> Optional[Any]:
        if not self._has_charts:
            return None
        
        try:
            from PyQt6.QtChart import QChart, QChartView
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QPainter
        
            chart = QChart()
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            return chart_view
        except Exception as e:
            print(f"Erro ao criar widget de gráfico: {e}")
            return None

    graph_service = GraphService()