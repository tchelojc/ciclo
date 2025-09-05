import numpy as np
import matplotlib
from datetime import datetime
# matplotlib.use('Qt5Agg') # Se PyQt6 é o seu primário, considere 'QtAgg' ou deixe Matplotlib escolher.
# Se 'Qt5Agg' funciona com suas importações PyQt6, pode manter, mas é uma fonte potencial de conflito sutil.
matplotlib.use('QtAgg') # Tentativa com backend mais genérico para Qt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg # Para QtAgg
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # Se voltar para Qt5Agg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QTextEdit, QTabWidget, QHBoxLayout)
from PyQt6.QtCore import Qt, QDate
import matplotlib.pyplot as plt

# ================= CONSTANTES GLOBAIS PARA CÁLCULOS GALÁCTICOS =================
GALACTIC_EPOCH_JD = 2456283.0 
GALACTIC_YEAR_DAYS = 250e6 * 365.256 # Período orbital do Sol em dias
# ==============================================================================

class MathCalculator(QWidget):
    def __init__(self, connector=None, parent=None):
        super().__init__(parent)
        self.connector = connector
        if self.connector:
            self.connector.date_changed.connect(self.update_calculations)
        self.current_date = QDate.currentDate()
        
        self._ax_solar_inset = None # Para o eixo do gráfico "inset"

        self.setup_ui()
        # Inicializa os gráficos com um placeholder APÓS a UI estar montada
        self.init_math_graph()
        self.init_unified_cosmic_graph()
        
    def setup_ui(self):
        self.tabs = QTabWidget()
        
        self.tab_math = QWidget()
        self.setup_math_tab() # Configura os widgets desta aba
        
        self.tab_cosmic = QWidget()
        self.setup_cosmic_tab() # Configura os widgets desta aba
        
        self.tabs.addTab(self.tab_math, "Matemática Sagrada")
        self.tabs.addTab(self.tab_cosmic, "Alinhamento Cósmico")
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
        
    def setup_math_tab(self):
        layout_math = QVBoxLayout(self.tab_math)
        
        title = QLabel("Matemática Sagrada Maia")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #64f5ff; font-size: 18px; font-weight: bold; padding: 10px;")
        layout_math.addWidget(title)
        
        try:
            self.math_figure = Figure(figsize=(5, 3), facecolor='#000033', dpi=100)
            self.math_canvas = FigureCanvasQTAgg(self.math_figure)
            self.math_canvas.setStyleSheet("background-color: #000033; border: 1px solid #4466ff; border-radius: 5px;")
            layout_math.addWidget(self.math_canvas)
        except Exception as e:
            print(f"Erro ao criar gráfico matemático: {e}")
            layout_math.addWidget(QLabel("Gráfico matemático não disponível"))
        
        self.calculation_area = QTextEdit()
        self.calculation_area.setReadOnly(True)
        self.calculation_area.setStyleSheet("""
            QTextEdit {
                background-color: #000033; color: #ffffff; border: 1px solid #4466ff;
                border-radius: 5px; padding: 10px; font-family: 'Courier New';
            }""")
        layout_math.addWidget(self.calculation_area)
    
    def setup_cosmic_tab(self):
        layout_cosmic = QVBoxLayout(self.tab_cosmic)
        
        title = QLabel("Visualização Cósmica Unificada: Galáxia e Sistema Solar")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #64f5ff; font-size: 16px; font-weight: bold; padding: 5px;")
        layout_cosmic.addWidget(title)

        try:
            self.galactic_figure = Figure(figsize=(8, 7), facecolor='#000033', dpi=100)
            self.galactic_canvas = FigureCanvasQTAgg(self.galactic_figure)
            self.galactic_canvas.setStyleSheet("background-color: #000033; border: 1px solid #4466ff; border-radius: 5px;")
            layout_cosmic.addWidget(self.galactic_canvas)
        except Exception as e:
            print(f"Erro ao criar canvas galáctico: {e}")
            layout_cosmic.addWidget(QLabel("Canvas galáctico não disponível."))

        self.cosmic_info = QTextEdit()
        self.cosmic_info.setReadOnly(True)
        self.cosmic_info.setStyleSheet("""
            QTextEdit {
                background-color: #000033; color: #ffffff; border: 1px solid #4466ff;
                border-radius: 5px; padding: 10px; font-family: Arial;
            }""")
        layout_cosmic.addWidget(self.cosmic_info)

    def init_math_graph(self):
        if not hasattr(self, 'math_figure') or self.math_figure is None:
            print("[AVISO] math_figure não existe para init_math_graph.")
            return
        try:
            self.math_figure.clf()
            ax = self.math_figure.add_subplot(111)
            ax.set_title("Aguardando dados...", color='white')
            ax.set_facecolor('#000033')
            ax.axis('off')
            if hasattr(self, 'math_canvas'): self.math_canvas.draw_idle()
        except Exception as e:
            print(f"[ERRO INIT MATH GRAPH] {str(e)}")

    def init_unified_cosmic_graph(self):
        if not hasattr(self, 'galactic_figure') or self.galactic_figure is None:
            print("[AVISO] galactic_figure não existe para init_unified_cosmic_graph.")
            return
        try:
            self.galactic_figure.clf()
            ax = self.galactic_figure.add_subplot(111) # Adiciona um subplot principal
            ax.set_facecolor('#000033')
            ax.text(0.5, 0.5, "Aguardando dados...", 
                    ha='center', va='center', color='white', transform=ax.transAxes)
            ax.axis('off')
            if hasattr(self, 'galactic_canvas'): self.galactic_canvas.draw_idle()
        except Exception as e:
            print(f"[ERRO INIT UNIFIED COSMIC] {str(e)}")
            
    def _calculate_sun_galactic_angle(self, current_jd):
        days_since_galactic_epoch = current_jd - GALACTIC_EPOCH_JD
        
        if GALACTIC_YEAR_DAYS == 0:
            print("[SUN ANGLE ERROR] GALACTIC_YEAR_DAYS é zero.")
            return 0.0

        fraction_of_orbit = days_since_galactic_epoch / GALACTIC_YEAR_DAYS
        angle_degrees = fraction_of_orbit * 360.0
        
        # print(f"[SUN ANGLE DEBUG] Date: {self.current_date.toString('dd/MM/yyyy')}, JD: {current_jd}")
        # print(f"  Days since Gal Epoch: {days_since_galactic_epoch:.2f}, Frac Orbit: {fraction_of_orbit:.10e}, Raw Angle: {angle_degrees:.4f}°")
            
        if np.isnan(angle_degrees) or np.isinf(angle_degrees):
            print(f"[SUN ANGLE WARNING] Ângulo solar NaN/Inf para JD {current_jd}. Retornando 0.")
            return 0.0
            
        return angle_degrees

    def _calculate_days_for_mayan_cycles(self, date_qdate):
        try:
            mayan_creation_epoch = datetime(2012, 12, 21) 
            current_py_date = date_qdate.toPyDate() # datetime(date_qdate.year(), date_qdate.month(), date_qdate.day())
            delta = (current_py_date - mayan_creation_epoch).days
            return delta % (365 * 25000) 
        except Exception as e:
            print(f"[ERRO DIAS MAYAN CYCLE] {str(e)}")
            return 0
            
    def update_calculations(self, date_qdate):
        try:
            if not date_qdate.isValid():
                print(f"[AVISO] Data inválida: {date_qdate}. Usando data atual.")
                date_qdate = QDate.currentDate()
    
            year = date_qdate.year()
            if not (-10000 <= year <= 10000): # Limite prático
                print(f"[AVISO] Ano {year} muito extremo. Ajustando para data atual.")
                date_qdate = QDate.currentDate()
            
            self.current_date = date_qdate
            
            print(f"[DEBUG] update_calculations para data: {self.current_date.toString('dd/MM/yyyy')}")

            self.update_math_tab(self.current_date)
            self.update_cosmic_tab(self.current_date)
        
        except Exception as e:
            print(f"[ERRO ATUALIZAÇÃO GERAL] {str(e)} para data {date_qdate.toString('dd/MM/yyyy')}")
            self.init_math_graph() 
            self.init_unified_cosmic_graph()

    def update_math_tab(self, date_qdate):
        if not (hasattr(self, 'math_figure') and self.math_figure and \
                hasattr(self, 'calculation_area') and self.calculation_area and \
                hasattr(self, 'math_canvas') and self.math_canvas):
            print("[ERRO MATH_TAB] Componentes da UI não inicializados.")
            return
        try:
            self.math_figure.clf()
            ax = self.math_figure.add_subplot(111)
            
            kin = self._calculate_kin_number(date_qdate)
            fib = self._fibonacci_position(date_qdate)
            days_since_ref = self._calculate_days_since_reference(date_qdate)
            
            x_vals = np.linspace(0, 13, 100)
            cycle_pos = (days_since_ref % 260) / 260.0 if 260 != 0 else 0
            y_vals = np.sin(x_vals + cycle_pos * 4 * np.pi)
            
            ax.plot(x_vals, y_vals, color='#64f5ff', linewidth=2)
            ax.set_facecolor('#000033')
            ax.grid(color='#4466ff', alpha=0.1)
            ax.tick_params(axis='both', colors='#e0e0ff')
            for spine in ax.spines.values():
                spine.set_color('#64f5ff')
            ax.set_title(f"Padrão Sagrado - Kin {kin}", color='#64f5ff')
            
            info_text = f"""
            <html><body style='font-family:Arial; color:#e0e0ff; background-color:#000033;'>
                <h3 style='color:#64f5ff;'>Matemática Sagrada</h3>
                <div style='border:1px solid #4466ff; border-radius:5px; padding:10px;'>
                    <p><b>Data:</b> {date_qdate.toString('dd/MM/yyyy')}</p>
                    <p><b>Kin:</b> {kin}/260</p>
                    <p><b>Fibonacci:</b> {fib}</p>
                    <p><b>Padrão:</b> Ciclo de 260 dias do Tzolk'in</p>
                </div></body></html>"""
            self.calculation_area.setHtml(info_text)
            self.math_canvas.draw_idle()
            
        except Exception as e:
            print(f"[ERRO MATEMÁTICO TAB] {str(e)}")
            if hasattr(self, 'math_figure') and self.math_figure:
                 try:
                     self.math_figure.clf()
                     ax_err = self.math_figure.add_subplot(111)
                     ax_err.set_facecolor('#000033')
                     ax_err.text(0.5,0.5, f"Erro ao gerar gráfico:\n{e}", color="red", ha="center", va="center", transform=ax_err.transAxes, wrap=True)
                     ax_err.axis('off')
                     if hasattr(self, 'math_canvas'): self.math_canvas.draw_idle()
                 except Exception as e_draw:
                     print(f"Erro ao desenhar msg de erro no math_tab: {e_draw}")

    def update_cosmic_tab(self, date_qdate):
        if not (hasattr(self, 'galactic_figure') and self.galactic_figure and \
                hasattr(self, 'cosmic_info') and self.cosmic_info and \
                hasattr(self, 'galactic_canvas') and self.galactic_canvas):
            print("[ERRO COSMIC_TAB] Componentes da UI não inicializados.")
            return
        try:
            print(f"[DEBUG COSMIC TAB] Atualizando para: {date_qdate.toString('dd/MM/yyyy')}")
            self._update_cosmic_system(date_qdate)
            self._update_cosmic_info(date_qdate)
        except Exception as e:
            print(f"[ERRO CRÍTICO UPDATE COSMIC TAB] {str(e)} para data {date_qdate.toString('dd/MM/yyyy')}")
            self._draw_error_on_cosmic_graph(f"Erro em Cosmic Tab:\n{str(e)}")

    def _update_cosmic_system(self, date_qdate):
        current_jd = date_qdate.toJulianDay() + 0.5 
        print(f"[COSMIC SYS DEBUG] Iniciando _update_cosmic_system para JD: {current_jd}")

        if not (hasattr(self, 'galactic_figure') and self.galactic_figure):
            print("[ERRO COSMIC SYS] galactic_figure não disponível.")
            return
        try:
            self.galactic_figure.clf() 
            ax_galactic = self.galactic_figure.add_subplot(111, facecolor='#000010')
            ax_galactic.set_aspect('equal')
            ax_galactic.axis('off')

            ax_galactic.plot(0, 0, 'o', color='#ff00ff', markersize=20, zorder=10, label="Centro Galáctico (Sgr A*)")
            ax_galactic.text(0, -0.15, 'Sgr A*', ha='center', va='top', color='#ff00ff', fontsize=10)

            sun_orbital_angle_deg_raw = self._calculate_sun_galactic_angle(current_jd)
            if np.isnan(sun_orbital_angle_deg_raw) or np.isinf(sun_orbital_angle_deg_raw):
                raise ValueError(f"Ângulo solar inválido (NaN/Inf): {sun_orbital_angle_deg_raw:.4e}")

            sun_dist_galactic_plot = 0.8 # Raio visual da órbita do Sol no gráfico
            self._draw_orbit(ax_galactic, 0, 0, sun_dist_galactic_plot, '#ffff00', linewidth=1, alpha=0.5)

            sun_angle_for_plot = sun_orbital_angle_deg_raw % 360.0
            sun_x_galactic = sun_dist_galactic_plot * np.cos(np.radians(sun_angle_for_plot))
            sun_y_galactic = sun_dist_galactic_plot * np.sin(np.radians(sun_angle_for_plot))
            
            if np.isnan(sun_x_galactic) or np.isnan(sun_y_galactic):
                raise ValueError(f"Coordenadas do Sol NaN: ({sun_x_galactic:.4e}, {sun_y_galactic:.4e})")

            ax_galactic.plot(sun_x_galactic, sun_y_galactic, 'o', color='#ffff00', markersize=10, zorder=5, label="Sol")
            
            lim = 1.2 * sun_dist_galactic_plot
            ax_galactic.set_xlim(-lim, lim)
            ax_galactic.set_ylim(-lim, lim)
            ax_galactic.set_title(f"Visão Galáctica - {date_qdate.toString('dd/MM/yyyy')}", color='white', pad=15)

            # --- INSET SOLAR ---
            inset_pos = [0.68, 0.02, 0.3, 0.3] 
            # Após clf(), o _ax_solar_inset antigo é destruído. Sempre recriamos.
            self._ax_solar_inset = self.galactic_figure.add_axes(inset_pos, facecolor='#000022')
            ax_solar = self._ax_solar_inset # Use a variável local para clareza nesta função
            
            ax_solar.set_aspect('equal')
            ax_solar.axis('off')
            ax_solar.patch.set_alpha(0.8) # Para o fundo do inset

            venus_orbit_r_plot = 0.4 
            earth_orbit_r_plot = 0.6
            self._draw_orbit(ax_solar, 0,0, venus_orbit_r_plot, '#64f5ff', linewidth=0.8, alpha=0.7)
            self._draw_orbit(ax_solar, 0,0, earth_orbit_r_plot, '#ff5555', linewidth=0.8, alpha=0.7)
            ax_solar.plot(0, 0, 'o', color='#ffff00', markersize=12, label="Sol (Inset)") 

            day_in_year = date_qdate.dayOfYear()
            earth_angle_deg = ((day_in_year - 1) / 365.256) * 360.0 
            venus_angle_deg = ((day_in_year - 1) / 224.701) * 360.0
            
            venus_x_plot = venus_orbit_r_plot * np.cos(np.radians(venus_angle_deg))
            venus_y_plot = venus_orbit_r_plot * np.sin(np.radians(venus_angle_deg))
            ax_solar.plot(venus_x_plot, venus_y_plot, 'o', color='#64f5ff', markersize=5, label="Vênus")

            earth_x_plot = earth_orbit_r_plot * np.cos(np.radians(earth_angle_deg))
            earth_y_plot = earth_orbit_r_plot * np.sin(np.radians(earth_angle_deg))
            ax_solar.plot(earth_x_plot, earth_y_plot, 'o', color='#ff5555', markersize=6, label="Terra")

            inset_lim_plot = earth_orbit_r_plot * 1.15
            ax_solar.set_xlim(-inset_lim_plot, inset_lim_plot)
            ax_solar.set_ylim(-inset_lim_plot, inset_lim_plot)
            ax_solar.annotate("Sistema Solar", xy=(0.03, 0.97), xycoords='axes fraction',
                              fontsize=9, color='white', ha='left', va='top')
            
            if hasattr(self, 'galactic_canvas'):
                self.galactic_canvas.draw_idle()
            print(f"[COSMIC SYS DEBUG] Gráfico atualizado para JD: {current_jd}")

        except ValueError as ve:
            print(f"[ERRO VALOR COSMIC SYS] {str(ve)} ao processar data {date_qdate.toString('dd/MM/yyyy')}")
            self._draw_error_on_cosmic_graph(f"Erro de valor nos cálculos:\n{str(ve)}")
        except Exception as e:
            print(f"[ERRO CRÍTICO COSMIC SYS] {str(e)} ao processar data {date_qdate.toString('dd/MM/yyyy')}")
            self._draw_error_on_cosmic_graph(f"Erro inesperado no sistema cósmico:\n{str(e)}")

    def _draw_error_on_cosmic_graph(self, error_message):
        if not (hasattr(self, 'galactic_figure') and self.galactic_figure):
            print(f"Tentativa de desenhar erro, mas galactic_figure não existe. Erro: {error_message}")
            return
        try:
            self.galactic_figure.clf()
            ax = self.galactic_figure.add_subplot(111)
            ax.set_facecolor('#000033')
            ax.text(0.5, 0.5, error_message, color='red', ha='center', va='center', 
                    fontsize=10, wrap=True, transform=ax.transAxes)
            ax.axis('off')
            if hasattr(self, 'galactic_canvas'):
                self.galactic_canvas.draw_idle()
        except Exception as e_draw:
            print(f"Erro ao tentar desenhar mensagem de erro no gráfico: {e_draw}")

    def _draw_orbit(self, ax, center_x, center_y, radius, color, linewidth=1.0, alpha=0.5):
        # Adicionar verificação se ax é um objeto Axes válido
        if not isinstance(ax, plt.Axes):
            print(f"[DRAW ORBIT WARNING] Objeto 'ax' não é um Axes válido.")
            return
        try:
            orbit = plt.Circle((center_x, center_y), radius, fill=False,
                               color=color, linewidth=linewidth, alpha=alpha, zorder=1)
            ax.add_patch(orbit)
        except Exception as e:
            print(f"[DRAW ORBIT ERROR] Erro ao desenhar órbita: {e}")


    def _update_cosmic_info(self, date_qdate):
        if not (hasattr(self, 'cosmic_info') and self.cosmic_info):
            print("[AVISO] cosmic_info (QTextEdit) não encontrado.")
            return
        try:
            current_jd = date_qdate.toJulianDay() + 0.5
            
            # Ângulos heliocêntricos para Terra e Vênus (baseado no dia do ano)
            day_of_year = date_qdate.dayOfYear() # 1 a 366
            earth_angle_heliocentric_info = ((day_of_year - 1) / 365.256) * 360.0
            venus_angle_heliocentric_info = ((day_of_year - 1) / 224.701) * 360.0
            
            sun_galactic_angle_raw = self._calculate_sun_galactic_angle(current_jd) 
            sun_galactic_angle_display = sun_galactic_angle_raw % 360.0
            
            days_elapsed_galactic = current_jd - GALACTIC_EPOCH_JD
            galactic_year_progress_info = 0.0
            if GALACTIC_YEAR_DAYS != 0: # Evitar divisão por zero
                galactic_year_progress_info = (days_elapsed_galactic / GALACTIC_YEAR_DAYS) * 100

            alignment_str = self._check_cosmic_alignments(date_qdate, 
                                                          earth_angle_heliocentric_info, 
                                                          venus_angle_heliocentric_info, 
                                                          sun_galactic_angle_display) # Passa o ângulo solar 0-360 para display

            epoch_date_qdate = QDate.fromJulianDay(int(GALACTIC_EPOCH_JD))
            epoch_date_str = epoch_date_qdate.toString('dd/MM/yyyy') if epoch_date_qdate.isValid() else "Data de Época Inválida"


            info_text = f"""
            <html><body style='font-family:Arial; color:#e0e0ff; background-color:#000033;'>
                <h2 style='color:#64f5ff;'>Alinhamento Cósmico Completo</h2>
                <div style='border:1px solid #4466ff; border-radius:5px; padding:10px; margin-bottom:10px;'>
                    <h3 style='color:#ffff00;'>Sistema Solar (Heliocêntrico)</h3>
                    <p><b>Data:</b> {date_qdate.toString('dd/MM/yyyy')}</p>
                    <p><b>Posição Terra (aprox.):</b> {earth_angle_heliocentric_info:.1f}°</p>
                    <p><b>Posição Vênus (aprox.):</b> {venus_angle_heliocentric_info:.1f}°</p>
                </div>
                <div style='border:1px solid #4466ff; border-radius:5px; padding:10px; margin-bottom:10px;'>
                    <h3 style='color:#ffff00;'>Sistema Galáctico (Rel. ao Centro Galáctico)</h3>
                    <p><b>Ângulo Solar Galáctico (modelo):</b> {sun_galactic_angle_display:.4f}°</p>
                    <p><b>Progresso no Ciclo Galáctico (desde {epoch_date_str}):</b> {galactic_year_progress_info:.10f}%</p>
                </div>
                <div style='border:1px solid #ff5555; border-radius:5px; padding:10px;'>
                    <h3 style='color:#ff5555;'>Alinhamentos Notáveis</h3>
                    <p>{alignment_str}</p>
                </div></body></html>"""
            self.cosmic_info.setHtml(info_text)
        except Exception as e:
            print(f"[ERRO UPDATE COSMIC INFO] {str(e)}")
            self.cosmic_info.setHtml(f"<p style='color:red;'>Erro ao gerar informações cósmicas: {e}</p>")

    def _check_cosmic_alignments(self, current_qdate, earth_angle_heliocentric, venus_angle_heliocentric, sun_angle_galactic_display):
        threshold = 7.0 
        alignment_messages = []

        is_alignment_target_date = (current_qdate.year() == 2012 and 
                                    current_qdate.month() == 12 and 
                                    current_qdate.day() == 21)

        if is_alignment_target_date:
            # sun_angle_galactic_display já é % 360.0
            sun_on_ref_axis = abs(sun_angle_galactic_display) < threshold or \
                              abs(sun_angle_galactic_display - 360.0) < threshold # Redundante com o módulo, mas seguro
            
            if sun_on_ref_axis:
                # Simplificação: consideramos alinhamento se os planetas estiverem em oposição/conjunção com o eixo Sol-BH.
                # Se Sol está a 0 graus galácticos, planetas a 0/180 graus heliocêntricos (rel. ao mesmo eixo 0) estão alinhados.
                earth_aligned_bh_line = abs(earth_angle_heliocentric % 180.0) < threshold
                venus_aligned_bh_line = abs(venus_angle_heliocentric % 180.0) < threshold
                
                if earth_aligned_bh_line and venus_aligned_bh_line:
                    alignment_messages.append("⭐ ALINHAMENTO CÓSMICO 21/12/2024 (BH-Sol-Terra-Vênus no Eixo Ref.)")
                elif earth_aligned_bh_line:
                    alignment_messages.append("21/12/2024: Sol e Terra no eixo de referência galáctico.")
                elif venus_aligned_bh_line:
                    alignment_messages.append("21/12/2024: Sol e Vênus no eixo de referência galáctico.")
                else:
                    alignment_messages.append("21/12/2024: Sol no eixo de referência galáctico.")
            else:
                alignment_messages.append(f"21/12/2024: Sol a {sun_angle_galactic_display:.2f}° (Alinhamento Principal não como esperado).")
        
        # Alinhamentos gerais
        sun_on_major_axis = False
        for axis_angle in [0.0, 90.0, 180.0, 270.0]: # Usar floats
            if abs(sun_angle_galactic_display - axis_angle) < threshold or \
               abs(sun_angle_galactic_display - (axis_angle + 360.0)) < threshold: # Lida com o caso perto de 360 e 0
                sun_on_major_axis = True
                break
        if sun_on_major_axis and not (is_alignment_target_date and sun_on_ref_axis):
            alignment_messages.append("Sol em um eixo galáctico principal (0°, 90°, 180° ou 270°).")

        angle_diff_ev = abs(earth_angle_heliocentric - venus_angle_heliocentric)
        # Normaliza a diferença para estar entre 0 e 180 para checar conjunção (0) ou oposição (180)
        normalized_diff_ev = angle_diff_ev % 360.0
        if normalized_diff_ev > 180.0:
            normalized_diff_ev = 360.0 - normalized_diff_ev
        
        if normalized_diff_ev < threshold or abs(normalized_diff_ev - 180.0) < threshold:
             alignment_messages.append("Terra e Vênus alinhados (Conjunção/Oposição).")

        if not alignment_messages:
            return "Sem alinhamentos notáveis para esta data."
        return " | ".join(alignment_messages)

    def _fibonacci_position(self, date_qdate):
        try:
            kin = self._calculate_kin_number(date_qdate)
            n = kin % 30 
            if n < 0: n += 30 # Garante n positivo para fibonacci
            if n == 0: return 0
            if n == 1: return 1
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
        except Exception as e:
            print(f"[ERRO FIBONACCI] {str(e)}")
            return 0

    def _calculate_kin_number(self, date_qdate):
        try:

            kin_epoch_jd = 2456283.0 
            kin_at_epoch = 63       # Kin 4 Ahau

            current_jd = date_qdate.toJulianDay() # QDate.toJulianDay já é o início do dia.
            
            days_diff = int(current_jd - kin_epoch_jd)
            kin = (kin_at_epoch -1 + days_diff) % 260 + 1 # -1 e +1 para base 1-260
            return kin
        except Exception as e:
            print(f"[ERRO CÁLCULO KIN] {str(e)}")
            return 1 

    def _calculate_days_since_reference(self, date_qdate):
        try:
            ref_date_py = datetime(2012, 12, 21).date() 
            current_date_py = date_qdate.toPyDate()
            return (current_date_py - ref_date_py).days
        except Exception as e:
            print(f"[ERRO DAYS SINCE REFERENCE] {str(e)}")
            return 0