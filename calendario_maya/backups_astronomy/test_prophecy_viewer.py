# tests/test_prophecy_viewer.py
import unittest
from unittest.mock import MagicMock
from calendario_maya.interface.widgets.prophecy_viewer import (
    ProphecyViewer, 
    EventListWidget,
    EventDetailsWidget
)

class TestProphecyComponents(unittest.TestCase):
    def setUp(self):
        self.connector = MagicMock()
        self.connector.get_data_path.return_value = "fake/path"
        
    def test_prophecy_viewer_creation(self):
        viewer = ProphecyViewer(self.connector)
        self.assertIsInstance(viewer, ProphecyViewer)
        
    def test_event_list_widget(self):
        # Criar um mock do prophecy_manager
        prophecy_manager = MagicMock()
        widget = EventListWidget(prophecy_manager)
        # resto do teste
        
    def test_event_detail_widget(self):
        widget = EventDetailsWidget()
        self.assertTrue(hasattr(widget, 'set_event_detail'))