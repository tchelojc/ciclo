from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class LongCountTab(QWidget):
    def __init__(self, calendario):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("Long Count Calendar"))