#!/usr/bin/env python

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QScrollArea, QFileDialog)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from util.draggable_text_edit import DraggableTextEdit
from util.thumbnail_label import ThumbnailLabel

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            print("MainWindow init start...")
            super().__init__()
            self.setWindowTitle("Button Test")
            self.setGeometry(100, 100, 800, 600)
            self.setMinimumSize(300, 400)  # Set reasonable minimum window size
            
            print("Setting up resize timer...")
            # Create resize timer correctly
            self.resize_timer = QTimer(self)
            self.resize_timer.setSingleShot(True)
            self.resize_timer.timeout.connect(self.handle_resize_timeout)
            self.pending_resize = False
            
            print("Creating widgets...")
            # Create central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            self.layout = QVBoxLayout(central_widget)
            
            print("Setting up image label...")
            # Create and setup image label
            self.image_label = QLabel()
            self.image_label.setAlignment(Qt.AlignCenter) 
            
            # Create filename label
            self.filename_label = QLabel()
            self.filename_label.setAlignment(Qt.AlignCenter)
            self.filename_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #333;
                    padding: 5px;
                }
            """)
            
            print("Setting up thumbnails...")
            # Create thumbnail strip
            self.thumbnail_layout = QHBoxLayout()
            self.thumbnail_widget = QWidget()
            self.thumbnail_widget.setLayout(self.thumbnail_layout)
            
            # Create scroll area for thumbnails
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidget(self.thumbnail_widget)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setFixedHeight(100)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            print("Setting up navigation buttons...")
            # Create navigation buttons
            self.prev_button = QPushButton("←")
            self.next_button = QPushButton("→")
            self.prev_button.clicked.connect(self.show_previous_frame)
            self.next_button.clicked.connect(self.show_next_frame)
            
            # Create thumbnail navigation layout
            nav_layout = QHBoxLayout()
            nav_layout.addWidget(self.prev_button)
            nav_layout.addWidget(self.scroll_area)
            nav_layout.addWidget(self.next_button)
            
            print("Setting up text box...")
            # Create draggable text box
            text = "Drag me!"
            self.text_box = DraggableTextEdit(self.image_label)
            self.text_box.setFixedSize(150, 50)
            self.text_box.setText(text)
            self.text_box.move(50, 50)

            # File browser
            self.fileSelectButton = QPushButton("Open File", self)
            self.fileSelectButton.clicked.connect(self.open_file_dialogue)
            
            print("Setting up buttons...")
            # Create buttons
            self.button1 = QPushButton("Print Hello")
            self.button2 = QPushButton("Print World")
            self.button3 = QPushButton("Print Button Clicked")
            
            # Connect buttons to functions
            self.button1.clicked.connect(self.print_hello)
            self.button2.clicked.connect(self.print_world)
            self.button3.clicked.connect(self.print_button_clicked)
            
            print("Adding widgets to layout...")
            # Add widgets to layout
            self.layout.addWidget(self.image_label)
            self.layout.addWidget(self.filename_label)  # Add filename label
            self.layout.addLayout(nav_layout)
            self.layout.addWidget(self.fileSelectButton)
            self.layout.addWidget(self.button1)
            self.layout.addWidget(self.button2)
            self.layout.addWidget(self.button3)
            
            print("Loading frames...")
            # Load frames and show first frame
            self.frames = []
            self.frame_files = []  # Store filenames
            self.current_frame_index = 0
            self.load_frames()
            print("Showing first frame...")
            self.show_frame(0)
            print("MainWindow init complete.")
        except Exception as e:
            print(f"Error in MainWindow initialization: {e}")
            import traceback
            traceback.print_exc()

    def open_file_dialogue(self):
        file_dialogue = QFileDialog(self)
        file_path, _ = file_dialogue.getOpenFileName(self, "Select File")
        if file_path:
            print(f"Selected file: {file_path}")
        else:
            print("No file selected")

        

    def load_frames(self):
        cur_file_path = os.path.abspath(__file__)
        cur_dir = os.path.dirname(cur_file_path)
        parent_dir = os.path.dirname(cur_dir)
        frames_dir = os.path.join(parent_dir, "outputFiles/frames")
        # Create frames directory if it doesn't exist
        try:
            if not os.path.exists(frames_dir):
                print(f"Creating frames directory '{frames_dir}'")
                os.makedirs(frames_dir)
                # No images yet, so create a blank default
                print("No frames directory - creating default blank image")
                self.filename_label.setText("No images found - please add images to frames directory")
                blank_pixmap = QPixmap(400, 300)
                blank_pixmap.fill(Qt.white)
                self.frames.append(blank_pixmap)
                self.frame_files.append("blank.jpg")
                
                # Create thumbnail for blank image
                thumbnail = ThumbnailLabel()
                thumbnail_pixmap = blank_pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumbnail.setPixmap(thumbnail_pixmap)
                thumbnail.clicked.connect(lambda idx=0: self.show_frame(idx))
                self.thumbnail_layout.addWidget(thumbnail)
                return
        except Exception as e:
            print(f"Error creating frames directory: {e}")
            
        # Get all jpg files and sort them numerically
        try:
            frame_files = [f for f in os.listdir(frames_dir) if f.endswith('.jpg')]
        except Exception as e:
            print(f"Error listing directory: {e}")
            frame_files = []
        
        if not frame_files:
            print(f"Error: No jpg files found in '{frames_dir}' directory.")
            self.filename_label.setText("Error: No jpg files found in frames directory")
            # Create a default blank image if no frames are available
            blank_pixmap = QPixmap(400, 300)
            blank_pixmap.fill(Qt.white)
            self.frames.append(blank_pixmap)
            self.frame_files.append("blank.jpg")
            self.show_frame(0)
            return
            
        # Sort by the numeric part of the filename
        frame_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))
        
        # Use a set to track unique filenames
        seen_files = set()
        self.frame_files = []
        
        for frame_file in frame_files:
            if frame_file not in seen_files:
                seen_files.add(frame_file)
                self.frame_files.append(frame_file)
                
                pixmap = QPixmap(os.path.join(frames_dir, frame_file))
                if not pixmap.isNull():
                    self.frames.append(pixmap)
                    
                    # Create thumbnail
                    thumbnail = ThumbnailLabel()
                    thumbnail_pixmap = pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail.setPixmap(thumbnail_pixmap)
                    thumbnail.clicked.connect(lambda idx=len(self.frames)-1: self.show_frame(idx))
                    self.thumbnail_layout.addWidget(thumbnail)
                    
        if not self.frames:
            print("Error: Failed to load any valid frames.")
            self.filename_label.setText("Error: Failed to load any valid frames")
            # Create a default blank image if no frames could be loaded
            blank_pixmap = QPixmap(400, 300)
            blank_pixmap.fill(Qt.white)
            self.frames.append(blank_pixmap)
            self.frame_files.append("blank.jpg")
            
            # Create thumbnail for blank image
            thumbnail = ThumbnailLabel()
            thumbnail_pixmap = blank_pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumbnail.setPixmap(thumbnail_pixmap)
            thumbnail.clicked.connect(lambda idx=0: self.show_frame(idx))
            self.thumbnail_layout.addWidget(thumbnail)

    def show_frame(self, index):
        if not self.frames:  # Check if frames list is empty
            print("No frames loaded.")
            return
            
        if 0 <= index < len(self.frames):
            self.current_frame_index = index
            self.original_pixmap = self.frames[index]
            self.update_image_size()
            
            # Update filename label
            if self.frame_files:
                self.filename_label.setText(f"Current Image: {self.frame_files[index]}")
            
            # Highlight current thumbnail and ensure it's visible
            for i in range(self.thumbnail_layout.count()):
                widget = self.thumbnail_layout.itemAt(i).widget()
                if i == index:
                    widget.setStyleSheet("border: 2px solid blue; border-radius: 5px;")
                    # Ensure the current thumbnail is visible in the scroll area
                    self.scroll_area.ensureWidgetVisible(widget)
                else:
                    widget.setStyleSheet("border: 2px solid gray; border-radius: 5px;")

    def show_previous_frame(self):
        if not self.frames:  # Check if frames list is empty
            return
        new_index = (self.current_frame_index - 1) % len(self.frames)
        self.show_frame(new_index)
        # Scroll to the previous thumbnail
        if new_index > 0:
            prev_widget = self.thumbnail_layout.itemAt(new_index - 1).widget()
            self.scroll_area.ensureWidgetVisible(prev_widget)

    def show_next_frame(self):
        if not self.frames:  # Check if frames list is empty
            return
        new_index = (self.current_frame_index + 1) % len(self.frames)
        self.show_frame(new_index)
        # Scroll to the next thumbnail
        if new_index < len(self.frames) - 1:
            next_widget = self.thumbnail_layout.itemAt(new_index + 1).widget()
            self.scroll_area.ensureWidgetVisible(next_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Start or restart the timer on resize
        self.resize_timer.start(150)  # 150ms debounce

    def handle_resize_timeout(self):
        self.update_image_size()

    def update_image_size(self):
        if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
            # Calculate available space with minimum thresholds
            available_width = max(200, self.width() - 20)  # Minimum 200px width
            available_height = max(100, self.height() - 250)  # Minimum 100px height
            
            scaled_pixmap = self.original_pixmap.scaled(
                available_width,
                available_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            
            # Calculate appropriate text box size relative to image size
            image_width = scaled_pixmap.width()
            image_height = scaled_pixmap.height()
            
            # Calculate the actual image position within the label (for centering)
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            
            # Calculate image offset (for centered images)
            x_offset = (label_width - image_width) // 2
            y_offset = (label_height - image_height) // 2
            
            # Set text box size to be approximately 20% of image width and 15% of image height
            text_width = max(150, int(image_width * 0.2))
            text_height = max(50, int(image_height * 0.15))
            
            # Update text box size
            self.text_box.setFixedSize(text_width, text_height)
            
            # Calculate appropriate font size based on text box size
            font_size = max(10, min(20, int(text_height / 3)))
            
            # Apply font size to text box
            self.text_box.setStyleSheet(f"""
                QTextEdit {{
                    background-color: rgba(255, 255, 255, 30 );
                    border: 1px solid black;
                    border-radius: 5px;
                    font-size: {font_size}pt;
                }}
            """)
            
            # Ensure cursor settings are preserved
            self.text_box.setCursor(Qt.CursorShape.OpenHandCursor)
            self.text_box.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            
            # Update text box position - constrain to the actual image area
            text_box_pos = self.text_box.pos()
            
            # Calculate the bounds of the actual image within the label
            min_x = x_offset
            min_y = y_offset
            max_x = x_offset + image_width - self.text_box.width()
            max_y = y_offset + image_height - self.text_box.height()
            
            # Ensure text box stays within image bounds
            new_x = min(max(min_x, text_box_pos.x()), max_x)
            new_y = min(max(min_y, text_box_pos.y()), max_y)
            
            self.text_box.move(new_x, new_y)

    def print_hello(self):
        print("Hello!")

    def print_world(self):
        print("World!")

    def print_button_clicked(self):
        print("Button was clicked!")

if __name__ == "__main__":
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        print("Creating main window...")
        window = MainWindow()
        print("Setting up window...")
        # Set window properties after initialization
        window.setWindowTitle("Video Subtitle Generator")
        window.setGeometry(100, 100, 800, 600)
        
        print("Showing window...")
        window.show()
        
        print("Entering event loop...")
        return_code = app.exec()
        print(f"Application exited with code {return_code}")
        sys.exit(return_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...") 