# shared_imports.py
"""
Arquivo centralizado para todos os imports comuns do projeto
Organizado por módulo Qt e categorias lógicas
"""

# QtWidgets - Componentes de UI
from PyQt6.QtWidgets import (
    # Layouts
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    
    # Componentes básicos
    QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
    QSpinBox, QSlider, QProgressBar,
    
    # Containers
    QGroupBox, QTabWidget, QStackedWidget, QScrollArea, QFrame,
    
    # Janelas e diálogos
    QMainWindow, QDialog,
    
    # Gráficos
    QGraphicsView, QGraphicsScene, QGraphicsItem,
    
    # Menus
    QMenu, QMenuBar, QStatusBar, QTextBrowser,
    
    # Outros
    QCalendarWidget, QTextEdit, QApplication
)

# QtGui - Elementos gráficos
from PyQt6.QtGui import (
    QAction, QIcon, QPixmap, QFont, QFontDatabase,
    QPen, QBrush, QColor, QPainter, QPainterPath,
    QLinearGradient, QRadialGradient,
    QKeySequence, QShortcut
)

# QtCore - Funcionalidades básicas
from PyQt6.QtCore import (
    Qt, pyqtSignal, pyqtSlot, QDate, QDateTime, QTime,
    QTimer, QPoint, QPointF, QRect, QRectF, QSize,
    QUrl, QDir, QFileInfo, QSettings
)

# Tipos de dados padrão
from datetime import datetime, date, timedelta
from typing import Optional, Union, List, Dict, Tuple, Any, Callable
import os
from pathlib import Path
import json
import math

# Verificação de dependências
try:
    import ephem
    HAS_EPHEM = True
except ImportError:
    HAS_EPHEM = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Constantes personalizadas
class DisplayMetrics:
    DPI = 96
    SCALE_FACTOR = 1.0

class Colors:
    MAYA_BLUE = QColor(115, 194, 251)
    AZTEC_RED = QColor(206, 17, 38)
    THEME_DARK = QColor(53, 53, 53)