class GraphService:
    def __init__(self):
        try:
            from PyQt6.QtCharts import QChart
            self._has_charts = True
        except ImportError:
            self._has_charts = False
            
    def plot_data(self, data):
        """Implementação básica para fallback"""
        print("Gráfico simulado:", data)
        return {"status": "simulated"}