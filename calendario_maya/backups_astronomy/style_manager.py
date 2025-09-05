from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont
import os
from PyQt6.QtCore import QFile, QTextStream
from pathlib import Path

class StyleManager:
    THEMES = {
        'maya': {
            'primary': '#1a0a5a',
            'secondary': '#4ecca3',
            'text': '#e0e0e0',
            'css_file': 'maya_theme.css',
            'background': 'images/maya_bg.jpg'
        },
        'aztec': {
            'primary': '#5a0000',
            'secondary': '#d4af37',
            'text': '#ff9e9e',
            'css_file': 'aztec_theme.css',
            'background': 'images/aztec_bg.jpg'
        }
    }
    
    def __init__(self, app: QApplication):
        self.app = app
        self.current_theme = 'maya'
        self.themes_dir = Path(__file__).parent / 'styles'
        self.styles_dir = os.path.join(os.path.dirname(__file__), '..', 'interface', 'assets', 'styles')

    def apply_theme(self, theme_name: str, window=None) -> None:
        """Aplica um tema CSS à aplicação"""
        theme = self.THEMES.get(theme_name, self.THEMES['maya'])
        
        # 1. Carrega o arquivo CSS
        css_path = os.path.join(self.styles_dir, theme['css_file'])
        
        if not os.path.exists(css_path):
            print(f"⚠️ Arquivo CSS não encontrado: {css_path}")
            return

        # 2. Lê e processa o CSS
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        
        # 3. Substitui as variáveis de tema
        css = self._replace_theme_variables(css, theme)
        
        # 4. Aplica o CSS
        if window:
            window.setStyleSheet(css)
        else:
            self.app.setStyleSheet(css)

    def _replace_theme_variables(self, css: str, theme: dict) -> str:
        """Substitui as variáveis CSS pelos valores do tema"""
        replacements = {
            'var(--primary)': theme['primary'],
            'var(--secondary)': theme['secondary'],
            'var(--text)': theme['text'],
            '../images/': ':/images/'  # Adapta caminhos para recursos Qt
        }
        
        for var, value in replacements.items():
            css = css.replace(var, value)
        
        return css

    def _apply_base_palette(self, theme_name: str) -> None:
        """Configura a paleta de cores base do tema"""
        palette = QPalette()
        
        if theme_name == 'aztec':
            # Paleta Asteca
            palette.setColor(QPalette.ColorRole.Window, QColor('#2E1B0E'))
            palette.setColor(QPalette.ColorRole.WindowText, QColor('#F0E5D8'))
            palette.setColor(QPalette.ColorRole.Base, QColor('#4A2B13'))
            palette.setColor(QPalette.ColorRole.Text, QColor('#F8F8F8'))
            palette.setColor(QPalette.ColorRole.Highlight, QColor('#8B6914'))
        else:
            # Paleta Maya (padrão)
            palette.setColor(QPalette.ColorRole.Window, QColor('#0a043c'))
            palette.setColor(QPalette.ColorRole.WindowText, QColor('#e4d3ff'))
            palette.setColor(QPalette.ColorRole.Base, QColor('#1a0a5e'))
            palette.setColor(QPalette.ColorRole.Text, QColor('#f8f8ff'))
            palette.setColor(QPalette.ColorRole.Highlight, QColor('#6a3093'))
        
        self.app.setPalette(palette)
        self.app.setStyle('Fusion')
        
        # Configuração de fonte
        font = QFont('Segoe UI', 10)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.app.setFont(font)

    def _apply_fallback_stylesheet(self, theme_name: str) -> None:
        """Aplica um estilo básico quando o QSS não está disponível"""
        theme = self.THEMES.get(theme_name, self.THEMES['maya'])
        stylesheet = f"""
        QWidget {{
            color: {theme['text']};
            font-family: 'Segoe UI';
        }}
        QPushButton {{
            background-color: {theme['primary']};
            color: {theme['text']};
            border: 1px solid {theme['secondary']};
            padding: 5px;
            border-radius: 4px;
        }}
        QLabel {{
            color: {theme['text']};
        }}
        """
        self.app.setStyleSheet(stylesheet)

    def _apply_fallback_theme(self) -> None:
        """Tema de fallback completo para quando ocorrem erros"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#2d2d2d'))
        palette.setColor(QPalette.ColorRole.WindowText, QColor('#ffffff'))
        self.app.setPalette(palette)
        self.app.setStyle('Fusion')
        
        stylesheet = """
        QWidget {
            font-family: 'Segoe UI';
            color: #ffffff;
        }
        """
        self.app.setStyleSheet(stylesheet)

    @classmethod
    def get_theme_colors(cls, theme_name: str) -> dict:
        """Obtém as cores de um tema específico"""
        return cls.THEMES.get(theme_name, cls.THEMES['maya'])