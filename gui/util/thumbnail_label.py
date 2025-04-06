from PySide6.QtWidgets import (QLabel)
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal

class ThumbnailLabel(QLabel):
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid gray;
                border-radius: 5px;
            }
            QLabel:hover {
                border: 2px solid blue;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
