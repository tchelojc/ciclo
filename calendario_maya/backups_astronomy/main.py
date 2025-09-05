import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
import warnings
from erfa import ErfaWarning

# Suprimir avisos específicos do ERFA
warnings.filterwarnings("ignore", category=ErfaWarning)

# Configura caminhos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from calendario_maya.core.connector import Connector
from calendario_maya.interface.main_window import MainWindow

def load_stylesheet():
    try:
        base_path = Path(__file__).parent
        style_path = base_path / "interface" / "assets" / "styles" / "maya_theme.qss"
        
        if not style_path.exists():
            raise FileNotFoundError(f"Arquivo de estilo não encontrado: {style_path}")
            
        with open(style_path, "r", encoding="utf-8") as f:
            stylesheet = f.read()
            
        # Verificação básica do conteúdo
        if not stylesheet.strip() or "QWidget" not in stylesheet:
            raise ValueError("Stylesheet inválido ou vazio")
            
        return stylesheet
        
    except Exception as e:
        print(f"Erro ao carregar stylesheet: {e}")
        return "QWidget { background-color: #0a043c; color: white; }"  # Fallback mínimo

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())  # ← aplica o tema

    data_path = project_root / "data"
    connector = Connector(data_path=data_path)

    window = MainWindow(connector)
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
