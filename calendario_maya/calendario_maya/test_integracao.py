import sys
import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDate, QTimer

# Configuração do path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Imports absolutos
from calendario_maya.core.connector import Connector
from calendario_maya.interface.main_window import MainWindow
from calendario_maya.interface.widgets.calendar_widget import CalendarWidget
from calendario_maya.interface.widgets.glyph_viewer import GlyphViewer
from calendario_maya.utils.timeline import TimelineWidget

class TestIntegracao:
    @classmethod
    def setup_class(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.connector = Connector()
        cls.window = MainWindow(cls.connector)
        cls.window.show()  # Garante que a janela esteja visível

    @classmethod
    def teardown_class(cls):
        cls.window.close()
        QTimer.singleShot(100, cls.app.quit)  # Fecha a aplicação após os testes

    def test_01_arquivos_essenciais(self):
        required_files = ['tzolk.json', 'tonalpohualli.json']
        for file in required_files:
            path = BASE_DIR / 'calendario_maya' / 'data' / file  # Caminho corrigido
            assert path.exists(), f"Arquivo {file} não encontrado em {path}"
            
    def test_02_connector(self):
        """Testa a inicialização do Connector"""
        assert self.connector.initialized, "Connector não inicializado"
        assert hasattr(self.connector, 'tzolk_data'), "Dados Tzolk'in não carregados"
        assert len(self.connector.tzolk_data['nahuales']) == 20, "Deve ter 20 nahuales"

    def test_03_calendar_widget(self):
        """Testa se o CalendarWidget está funcionando corretamente"""
        try:
            # Testa criação com parent None
            calendar = CalendarWidget(connector=self.connector, parent=None)
            assert hasattr(calendar, 'date_changed'), "Sinal date_changed faltando"
        
            # Testa criação com parent
            calendar_with_parent = CalendarWidget(connector=self.connector, parent=self.window)
            assert calendar_with_parent.parent() == self.window, "Parent não configurado"
        
        except Exception as e:
            pytest.fail(f"Falha no CalendarWidget: {str(e)}")
        
    def test_04_timeline_widget(self):
        timeline = TimelineWidget(self.connector)
        assert timeline.scene is not None, "Cena da timeline não criada"  # Atributo, não método

    def test_05_main_window(self):
        """Testa a janela principal"""
        assert self.window.isVisible(), "Janela principal não visível"
        assert hasattr(self.window, 'content_stack'), "Stack de conteúdo não existe"
        assert self.window.content_stack.count() > 0, "Nenhum widget adicionado"

    def test_06_navegacao(self):
        """Testa a navegação entre componentes"""
        # Verifica inicialização dos componentes
        assert hasattr(self.window, 'calendar_widget'), "CalendarWidget não inicializado"
        assert hasattr(self.window, 'glyph_viewer'), "GlyphViewer não inicializado"
    
        # Verifica se os widgets foram adicionados ao content_stack
        assert self.window.content_stack.count() >= 2, "Poucos widgets no content_stack"

        # Testa navegação para cada componente
        components = [
            ('calendar', 'calendar_widget'),
            ('glyphs', 'glyph_viewer')
        ]
    
        for component_id, widget_name in components:
            # Emite sinal de mudança
            self.window.maya_sidebar.menu_changed.emit(component_id)
        
            # Processa eventos pendentes
            QApplication.processEvents()
        
            # Pequeno delay para garantir a renderização
            import time
            time.sleep(0.1)
        
            # Verifica se o widget correto está ativo
            current_widget = self.window.content_stack.currentWidget()
            expected_widget = getattr(self.window, widget_name)
        
            assert current_widget is not None, "Nenhum widget ativo"
            assert expected_widget is not None, f"Widget {widget_name} não encontrado"
            assert current_widget == expected_widget, (
                f"Widget {component_id} não ativado. "
                f"Esperado: {type(expected_widget).__name__}, "
                f"Obtido: {type(current_widget).__name__}"
            )
        
    def test_07_mudanca_tema(self):
        # Teste com timeout para evitar travamentos
        import time
        start_time = time.time()
    
        try:
            # Testa mudança para tema aztec
            assert self.window.toggle_civilization('aztec'), "Falha ao mudar para tema aztec"
            assert self.window.current_theme == 'aztec', "Tema não foi alterado para aztec"
        
            # Testa mudança de volta para maya
            assert self.window.toggle_civilization('maya'), "Falha ao voltar para tema maya"
            assert self.window.current_theme == 'maya', "Tema não foi alterado para maya"
        
            # Verifica se não excedeu o tempo limite
            assert time.time() - start_time < 5, "Teste excedeu o tempo limite"
        except Exception as e:
            pytest.fail(f"Teste de tema falhou: {str(e)}")
    
        @classmethod
        def teardown_class(cls):
            """Limpeza após os testes"""
            cls.window.close()
            del cls.window
            del cls.connector
            del cls.app
        
    def test_08_glyph_viewer(self):
        """Testa o visualizador de glifos com diferentes configurações"""
        # Teste com parent None
        viewer1 = GlyphViewer(connector=self.connector, parent=None)
        assert viewer1.connector == self.connector, "Connector não configurado"
    
        # Teste com parent definido
        viewer2 = GlyphViewer(connector=self.connector, parent=self.window)
        assert viewer2.parent() == self.window, "Parent não configurado"
    
        # Teste de atualização
        test_date = QDate.currentDate()
        viewer1.update_glyphs(test_date)
        assert hasattr(viewer1, 'glyph_label'), "Componente de glifo não criado"
    
    def test_navigation_with_delay(self):
        """Teste com delay para eventos UI"""
        self.window.maya_sidebar.menu_changed.emit('calendar')
    
        # Usa QTimer para esperar a mudança
        timer = QTimer(self.window)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: None)  # Continua após processar eventos
    
        # Espera até 1 segundo
        timer.start(1000)
        while timer.isActive():
            QApplication.processEvents()

if __name__ == "__main__":
    pytest.main(["-v", str(Path(__file__))])