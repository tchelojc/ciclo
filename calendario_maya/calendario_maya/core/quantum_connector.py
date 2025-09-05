# core/quantum_connector.py
import sys
from pathlib import Path
import importlib

class QuantumConnector:
    def __init__(self):
        self._entangled_modules = {}
        self._superposition_paths = [
            Path(__file__).parent.parent,
            Path.cwd()
        ]
        self._observe_paths()

    def _observe_paths(self):
        """Colapsa os caminhos possíveis"""
        for path in self._superposition_paths:
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))

    def entangle(self, module_name, class_name):
        """Cria um entrelaçamento quântico com um módulo"""
        try:
            module = importlib.import_module(module_name)
            self._entangled_modules[class_name] = getattr(module, class_name)
            return True
        except Exception as e:
            print(f"⚛️ Colapso quântico em {module_name}.{class_name}: {e}")
            return False

    def get(self, class_name):
        """Obtém a classe em estado de superposição"""
        return self._entangled_modules.get(class_name)

# Entrelaçamento inicial
qc = QuantumConnector()
qc.entangle("core.data_manager", "DataManager")
qc.entangle("interface.widgets.glyph_viewer", "GlyphViewer")