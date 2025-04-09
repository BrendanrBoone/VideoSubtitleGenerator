
from PySide6.QtWidgets import (QTextEdit)
from PySide6.QtCore import Qt, QPoint

class DraggableTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 180);
                border: 1px solid black;
                border-radius: 5px;
            }
        """)
        self.par_img_w_ratio = 1
        self.par_img_h_ratio = 0.2
        self.dragging = False
        self.offset = QPoint()
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        
        # Store parent image label for boundary calculations
        self.image_label = parent

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Calculate new position
            direction = event.position().toPoint() - self.offset
            new_pos = self.mapToParent(direction)
            
            # Get the current pixmap from the image label
            pixmap = self.image_label.pixmap()
            if pixmap:
                # Calculate image boundaries
                image_width = pixmap.width()
                #image_height = pixmap.height()
                label_width = self.image_label.width()
                label_height = self.image_label.height()
                
                # Calculate image offset (for centered images)
                x_offset = (label_width - image_width) // 2
                #y_offset = (label_height - image_height) // 2
                
                # Calculate bounds
                min_x = x_offset
                min_y = 0
                max_x = x_offset + image_width - self.width()
                max_y = label_height - self.height()
                
                # Constrain position to image boundaries
                new_x = min(max(min_x, new_pos.x()), max_x)
                new_y = min(max(min_y, new_pos.y()), max_y)
                
                # Move to constrained position
                self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            
    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().leaveEvent(event)
