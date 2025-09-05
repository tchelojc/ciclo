# tests/conftest.py
import pytest
from PyQt6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Fixture para criar uma QApplication"""
    app = QApplication([])
    yield app
    app.quit()