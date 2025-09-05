# diagnostico_imports.py
import os
import sys
from pathlib import Path

class SistemaDiagnostico:
    def __init__(self):
        self.project_root = self._find_project_root()
        self.data_dir = self.project_root / 'data'
        sys.path.insert(0, str(self.project_root))
        
    def _find_project_root(self):
        """Encontra a raiz do projeto de forma confiável"""
        possible_roots = [  # Nome corrigido para possible_roots
            Path(__file__).parent.parent,
            Path.cwd(),
            Path.home() / "portal" / "calendario_maya"
        ]
        
        for root in possible_roots:  # Nome corrigido aqui também
            if (root / 'main.py').exists() or (root / 'data').exists():
                return root
        return Path.cwd()

    def testar_imports(self):
        print("\n=== TESTANDO IMPORTS ===")
        
        imports = [
            ('interface.widgets.glyph_viewer', 'GlyphViewer'),
            ('interface.widgets.tonal_tab', 'TonalTab'),
            ('interface.widgets.tzolkin_tab', 'TzolkinTab'),
            ('core.data_manager', 'DataManager')
        ]
        
        for module, obj in imports:
            try:
                imported = __import__(module, fromlist=[obj])
                getattr(imported, obj)
                print(f"✅ {module}.{obj}")
            except ImportError as e:
                print(f"❌ {module}.{obj} - {str(e)}")
                self._show_import_paths()

    def _show_import_paths(self):
        print("\nCaminhos de importação (sys.path):")
        for p in sys.path:
            print(f"- {p}")

if __name__ == "__main__":
    print("=== DIAGNÓSTICO DE IMPORTAÇÕES ===")
    diagnostico = SistemaDiagnostico()
    diagnostico.testar_imports()