from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, 
                            QSizePolicy)
from PyQt6.QtGui import QColor, QAction 
from PyQt6.QtCore import Qt
from typing import Optional
import json
from pathlib import Path
from utils.style_utils import sanitize_stylesheet
from core.config import get_glyph_path

class GlyphViewer(QScrollArea):
    def __init__(self, connector=None, parent=None):
        super().__init__(parent)
        self.connector = connector
        if self.connector:
            self.connector.date_changed.connect(self.update_glyphs)
        self._current_glyph = None
        self.glyphs = {}
        self._setup_ui()
        self._load_glyphs()
        
    def _setup_ui(self):
        """Configuração completa da interface com melhor contraste"""
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container principal
        self.container = QWidget()
        self.container.setObjectName("container")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        # Glifo principal
        self.glyph_label = QLabel("🌀")
        self.glyph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.glyph_label.setStyleSheet("""
            QLabel {
                font-size: 140px;
                color: #ffffff;
                margin: 10px;
                background-color: rgba(26, 26, 90, 0.5);
                border-radius: 20px;
                padding: 20px;
                min-width: 200px;
                min-height: 200px;
                border: 1px solid #4466ff;
                box-shadow: 0 0 10px #4466ff;
            }
        """)

        # Área de informações
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                background-color: #1a1a5a;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #4466ff;
                line-height: 1.5;
            }
        """)

        self.layout.addWidget(self.glyph_label, 1)
        self.layout.addWidget(self.info_label, 1)
        self.setWidget(self.container)

        # Estilo do container principal
        self.setStyleSheet("""
            QScrollArea {
                background: #0a043c;
                border: 2px solid #4466ff;
                border-radius: 8px;
            }
            QWidget#container {
                background-color: #0a043c;
            }
        """)

    def _load_glyphs(self):
        """Carrega glifos com fallback seguro"""
        try:
            if not self.connector:
                raise ValueError("Connector não disponível")
            
            glyph_path = self.connector.get_data_path('tzolk.json')
            if not glyph_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {glyph_path}")
            
            with open(glyph_path, 'r', encoding='utf-8') as f:
                self.glyphs = json.load(f)
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar glifos: {e}")
            self.glyphs = {
                'nahuales': [{'nome': f'Nahual {i+1}', 'glifo': '🌀'} for i in range(20)],
                'constantes': {'ciclo_sagrado': 260}
            }
            self._show_error_state(str(e))

    def _show_error_state(self, message):
        """Mostra estado de erro com fallback seguro"""
        error_color = "#ff5555"
        self.glyph_label.setText("⚠️")
        self.glyph_label.setStyleSheet(f"""
            QLabel {{
                font-size: 140px;
                color: {error_color};
                background-color: rgba(60, 4, 4, 0.8);
                border: 2px solid {error_color};
            }}
        """)
        self.info_label.setText(f"""
        <div style='color:{error_color}; text-align:center;'>
            <h2 style='margin-bottom:10px;'>Erro</h2>
            <div style='background-color:#300000; padding:15px; border-radius:8px;'>
                <p>Não foi possível carregar os dados</p>
                <p><small>{message}</small></p>
            </div>
        </div>
        """)
        
    def _calculate_kin_number(self, date) -> int:
        """Calcula o número kin (1-260) para uma data"""
        if not date.isValid():
            return 1
            
        days_since_epoch = date.toJulianDay() - 584283 
        return (days_since_epoch % 260) + 1

    def update_glyphs(self, date) -> None:
        """Atualização com fallback robusto"""
        try:
            if not date or not date.isValid():
                raise ValueError("Data inválida")

            # Fallback local se o connector não estiver pronto
            if not getattr(self, 'connector', None) or not self.connector.initialized:
                self._show_local_glyphs(date)
                return

            py_date = date.toPyDate() if hasattr(date, 'toPyDate') else date
            kin_number = self._calculate_kin_number(date)

            # Dados padrão com fallback
            data = {
                'nome': 'Desconhecido',
                'glifo': '❓',
                'significado': 'Informação não disponível',
                'energia': '--',
                'frequencia': '-- Hz',
                'cor': '#6a3093'
            }

            # Tenta primeiro obter do connector
            if self.connector:
                try:
                    conn_data = self.connector.get_tzolkin_for_date(py_date)
                    if conn_data and 'nahual' in conn_data:
                        data.update(conn_data['nahual'])
                except Exception as e:
                    print(f"⚠️ Erro no connector: {e}")

            # Fallback para dados locais se o connector falhou
            if data['glifo'] == '❓' and self.glyphs:
                local_data = self.glyphs.get('nahuales', [{}])[kin_number % 20]
                data.update({
                    'nome': local_data.get('nome', data['nome']),
                    'glifo': local_data.get('glifo', data['glifo']),
                    'significado': local_data.get('significado_tradicional', 
                                       local_data.get('significado', data['significado'])),
                    'cor': local_data.get('cor', data['cor'])
                })

            # Aplica estilo
            glow_color = data.get('cor', '#6a3093')
            self.glyph_label.setText(data['glifo'])
            self.glyph_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 140px;
                    color: {glow_color};
                    margin: 10px;
                    background-color: rgba(10, 4, 60, 0.8);
                    border-radius: 20px;
                    padding: 20px;
                    min-width: 200px;
                    min-height: 200px;
                    border: 2px solid {glow_color};
                    box-shadow: 0 0 10px {glow_color};
                }}
            """)

            html = f"""
            <div style='text-align:center;'>
                <h2 style='color:{glow_color}; font-size:24px; margin-bottom:15px;'>
                    {data['nome']}
                </h2>
                <div style='
                    background-color: #1a1a5a;
                    color: #ffffff;
                    padding: 20px;
                    border-radius: 12px;
                    border: 1px solid {glow_color};
                '>
                    <p style='margin:8px 0;'><b>Energia:</b> <span style='color:{glow_color};'>{data['energia']}</span></p>
                    <p style='margin:8px 0;'><b>Frequência:</b> <span style='color:{glow_color};'>{data['frequencia']}</span></p>
                    <p style='margin:8px 0;'><b>Significado:</b> {data['significado']}</p>
                    <p style='margin:8px 0; font-size:12px; color:#aaaaaa;'>Kin {kin_number}/260</p>
                </div>
            </div>
            """
            self.info_label.setText(html)
    
        except Exception as e:
            self._show_error_state(str(e))
            
    def update_local_meaning(self):
        """Atualiza o significado local baseado na posição"""
        try:
            if not hasattr(self.connector, 'astronomy'):
                return
            
            location = self._get_user_location()  # Implementar esta função
            date = self.get_current_date()
        
            local_data = self.connector.astronomy.get_local_meaning(date, location)
            self.ui.lblLocalMeaning.setText(local_data.get('interpretation', 'N/A'))
            self.ui.lblEnergyFactor.setText(f"{local_data.get('energy_factor', 0):.2f}")
        except Exception as e:
            print(f"Erro ao atualizar significado local: {e}")
            
    def _show_local_glyphs(self, date):
        """Mostra glifos usando dados locais"""
        kin_number = self._calculate_kin_number(date)
        nahual = self.glyphs.get('nahuales', [{}])[kin_number % 20]
    
        self.glyph_label.setText(nahual.get('glifo', '🌀'))
        self.info_label.setText(f"""
            <div style='text-align:center; color:#ffffff;'>
                <h2>{nahual.get('nome', 'Nahual')}</h2>
                <p>{nahual.get('significado', 'Significado não disponível')}</p>
                <small>Modo local - Kin {kin_number}</small>
            </div>
        """)