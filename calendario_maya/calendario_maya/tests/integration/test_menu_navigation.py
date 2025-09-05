# tests/integration/test_menu_navigation.py
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QDate
from unittest.mock import MagicMock
import sys
import os

# Adiciona o diretório raiz ao path para imports absolutos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from calendario_maya.interface.main_window import MainWindow
from calendario_maya.core.connector import Connector
from calendario_maya.constants.matematicas import NEW_CYCLE_START, OLD_CYCLE_END

@pytest.fixture
def app(qtbot):
    """Fixture para a aplicação Qt"""
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    return application

@pytest.fixture
def connector():
    """Fixture para o connector com mocks básicos"""
    conn = Connector()
    conn.get_data_path = MagicMock(return_value=os.path.abspath('data'))
    conn.date_changed = MagicMock()
    return conn

@pytest.fixture
def main_window(connector, qtbot):
    """Fixture para a janela principal com tratamento de erros"""
    window = MainWindow(connector)
    qtbot.addWidget(window)
    
    # Configuração inicial segura
    QTimer.singleShot(100, lambda: window.show())
    qtbot.wait(150)  # Espera a inicialização
    
    return window

def test_menu_navigation_flow(main_window, qtbot):
    """Testa o fluxo completo de navegação pelos menus"""
    # 1. Verifica se todos os menus principais existem
    expected_menus = ['calendar', 'glyphs', 'timeline', 'cosmos', 'math', 'prophecy']
    for menu in expected_menus:
        assert menu in main_window._component_map, f"Menu {menu} não encontrado"
    
    # 2. Testa navegação para cada menu
    for menu_id in expected_menus:
        # Simula clique no menu
        qtbot.mouseClick(
            getattr(main_window.maya_sidebar, f'{menu_id}_btn'),
            Qt.MouseButton.LeftButton
        )
        
        # Verifica se o widget correto foi ativado
        qtbot.wait(100)  # Espera a transição
        current_widget = main_window.content_stack.currentWidget()
        assert current_widget is not None, f"Nenhum widget ativo após clicar em {menu_id}"
        
        # Verifica propriedades básicas do widget
        assert current_widget.isVisible(), f"Widget de {menu_id} não está visível"
        assert current_widget.isEnabled(), f"Widget de {menu_id} está desabilitado"

def test_prophecy_data_loading(main_window, qtbot):
    test_data = [{
        'id': 1,  # Adicionar ID único
        'year': '2020',
        'title': 'Evento de Teste',
        'description': 'Descrição do evento',
        'category': 'Teste',
        'date': '2020-06-15'  # Adicionar campo date
    }]
    
    # Atualize tanto o connector quanto o manager
    main_window.connector.prophecy_data = test_data
    if hasattr(main_window, 'prophecy_viewer'):
        main_window.prophecy_viewer.manager.events = test_data

def test_cosmic_calculations(main_window, qtbot):
    """Testa os cálculos cósmicos com a nova referência pós-2012"""
    # Verifica se a view foi inicializada corretamente
    assert hasattr(main_window, 'cosmos_view'), "CosmosView não foi inicializada"
    assert main_window.cosmos_view is not None, "CosmosView é None"
    
    from calendario_maya.utils.approximate_date import ApproximateDate
    
    # Datas de teste considerando o novo ciclo (pós-2012)
    test_cases = [
        (2012, "21/12/2012"),  # Fim do último baktun
        (2013, "21/12/2013"),  # Primeiro ano do novo ciclo
        (2024, "21/12/2024"),  # Novo marco importante
        (2025, "21/12/2025")   # Ano atual do novo ciclo
    ]
    
    qtbot.mouseClick(
        main_window.maya_sidebar.cosmos_btn,
        Qt.MouseButton.LeftButton
    )
    qtbot.wait(1500)  # Tempo adicional para carregamento
    
    for year, expected_date in test_cases:
        approx_date = ApproximateDate(year)
        try:
            cosmic_data = main_window.cosmos_view.calculate_cosmic_data(approx_date.to_date())
            assert cosmic_data is not None, f"Falha no cálculo para {year}"
            
            assert isinstance(cosmic_data, dict), "Dados cósmicos não retornados"
            
            # Verificações específicas para o novo ciclo
            if year >= 2012:
                assert 'new_cycle' in cosmic_data, f"Dados do novo ciclo faltando para {year}"
                assert cosmic_data['new_cycle'] is True, f"O ano {year} deveria estar no novo ciclo"
            
            # Verificações gerais
            assert 'baktun' in cosmic_data, f"Sem dados de baktun para {year}"
            assert isinstance(cosmic_data['baktun'], (int, float)), f"Baktun inválido para {year}"
            
        except Exception as e:
            pytest.fail(f"Erro nos cálculos para {year}: {str(e)}")

def test_cycle_transition():
    """Testa a transição entre os ciclos"""
    from datetime import datetime
    new_cycle = datetime.strptime(NEW_CYCLE_START, '%Y-%m-%d').date()
    old_cycle = datetime.strptime(OLD_CYCLE_END, '%Y-%m-%d').date()
    
    assert new_cycle > old_cycle, "A data do novo ciclo deve ser após o ciclo antigo"
    
def test_theme_switching(main_window, qtbot):
    """Testa a troca de temas entre Maya e Asteca"""
    # 1. Verifica tema inicial
    assert main_window.current_theme == 'maya', "Tema inicial incorreto"
    
    # 2. Troca para tema Asteca
    main_window.toggle_civilization('aztec')
    qtbot.wait(100)
    assert main_window.current_theme == 'aztec', "Falha ao trocar para tema Asteca"
    assert main_window.sidebar_stack.currentWidget() == main_window.aztec_sidebar
    
    # 3. Volta para tema Maya
    main_window.toggle_civilization('maya')
    qtbot.wait(100)
    assert main_window.current_theme == 'maya', "Falha ao voltar para tema Maya"
    assert main_window.sidebar_stack.currentWidget() == main_window.maya_sidebar

def test_error_handling(main_window, qtbot, monkeypatch):
    """Testa o tratamento de erros em componentes"""
    # 1. Simula falha no carregamento de profecias
    monkeypatch.setattr(
        'calendario_maya.interface.widgets.prophecy_viewer.ProphecyManager.load_events',
        lambda *args, **kwargs: exec('raise ValueError("Erro simulado")')
    )

    # 2. Tenta navegar para profecias em modo silencioso
    main_window._handle_missing_component('prophecy', silent=True)
    
    # 3. Verifica que nenhuma mensagem foi mostrada
    with qtbot.assertNotEmitted(main_window.status_bar.messageChanged, wait=100):
        qtbot.mouseClick(
            main_window.maya_sidebar.prophecy_btn,
            Qt.MouseButton.LeftButton
        )