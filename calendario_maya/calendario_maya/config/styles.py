from typing import Dict  # Adicione esta linha no topo do arquivo
from pathlib import Path
from .paths import path_manager

class StyleLoader:
    """Carregador de estilos com fallback integrado"""
    
    def __init__(self):
        self._builtin_styles = self._load_builtin_styles()
        
    def _load_builtin_styles(self) -> Dict[str, str]:
        """Estilos embutidos para fallback"""
        return {
            "maya": """
                /* Tema Maya - Fallback */
                QMainWindow { background: #16213e; }
                QPushButton { color: #4ecca3; }
                QLabel { color: #ffffff; }
            """,
            "aztec": """
                /* Tema Asteca - Fallback */
                QMainWindow { background: #3d0000; }
                QPushButton { color: #950101; }
                QLabel { color: #f5d76e; }
            """
        }
    
    def load(self, theme: str) -> str:
        """Carrega estilos com fallback automático"""
        try:
            # 1. Tenta carregar do arquivo QSS temático
            qss_path = path_manager.get(f"interface/assets/styles/{theme}_theme.qss")
            if qss_path and qss_path.exists():
                with open(qss_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # 2. Fallback para estilos embutidos
            return self._builtin_styles.get(theme.lower(), "")
        except Exception as e:
            print(f"ERRO CRÍTICO no StyleLoader: {e}")
            return self._builtin_styles.get("maya", "")  # Fallback absoluto

# Instância singleton
style_loader = StyleLoader()

# Interface principal
def load_styles(theme="maya"):
    """Função principal para carregar estilos"""
    # ... implementação existente ...

def safe_load_styles(theme="maya"):
    """Versão segura com tratamento de erros"""
    try:
        return load_styles(theme)
    except Exception as e:
        print(f"AVISO: Erro ao carregar estilos - {e}")
        return ""  # Retorna string vazia como fallback