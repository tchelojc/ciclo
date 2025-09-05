# dependencies.py
import sys
from PyQt6.QtWidgets import QComboBox, QApplication

def verify_qt_dependencies():
    """Verifica se todos os componentes Qt necessários estão disponíveis"""
    required_widgets = [QComboBox]
    missing = []
    
    for widget in required_widgets:
        if not hasattr(widget, '__module__'):
            missing.append(widget.__name__)
    
    if missing:
        raise ImportError(
            f"Componentes Qt ausentes: {', '.join(missing)}\n"
            f"PyQt6 versão: {QApplication.instance().applicationVersion() if QApplication.instance() else 'Não inicializado'}"
        )

def verify_python_version():
    """Verifica a versão do Python"""
    if sys.version_info < (3, 8):
        raise RuntimeError("Requer Python 3.8 ou superior")

def verify_all_dependencies():
    """Verifica todas as dependências do sistema"""
    verify_python_version()
    verify_qt_dependencies()