#!/usr/bin/env python

import sys
import os
import cv2
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QScrollArea, QFileDialog,
                             QInputDialog, QComboBox)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from gui.util.draggable_text_edit import DraggableTextEdit
from gui.util.thumbnail_label import ThumbnailLabel
from util.font import Fonts
from util.colors import Colors
from util.video_transcriber import VideoTranscriber

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            print("MainWindow init start...")
            super().__init__()
            self.setWindowTitle("Initializing MainWindow")
            self.setGeometry(100, 100, 800, 600)
            self.setMinimumSize(300, 400)  # Set reasonable minimum window size

            self.opt_video_path = ""
            self.opt_maxcap = 4
            self.opt_font_size = 0.8
            self.opt_font = "simplex"
            self.opt_color = "white"
            
            print("Setting up resize timer...")
            # Create resize timer correctly
            self.resize_timer = QTimer(self)
            self.resize_timer.setSingleShot(True)
            self.resize_timer.timeout.connect(self.handleResizeTimeout)
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

            self.vidname_label = QLabel()
            self.vidname_label.setAlignment(Qt.AlignCenter)
            self.vidname_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #333;
                    padding: 5px;
                }
            """)
            self.vidname = "Not Selected"
            self.vidname_label.setText(f"Current video: {self.vidname}")
            
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
            self.prev_button.clicked.connect(self.showPreviousFrame)
            self.next_button.clicked.connect(self.showNextFrame)
            
            # Create thumbnail navigation layout
            self.nav_layout = QHBoxLayout()
            self.nav_container = QWidget()
            self.nav_container.setLayout(self.nav_layout)
            self.nav_layout.addWidget(self.prev_button)
            self.nav_layout.addWidget(self.scroll_area)
            self.nav_layout.addWidget(self.next_button)
            
            print("Setting up text box...")
 
            self.text = "Drag me!"
            self.text_box = DraggableTextEdit(self.image_label)
            self.text_box.setFixedSize(150, 50)
            self.text_box.setText(self.text)
            self.text_box.move(50, 50)
            self.text_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # File browser
            self.fileSelectButton = QPushButton("Open File", self)
            self.fileSelectButton.clicked.connect(self.openFileDialogue)

            # maximum words per caption
            self.maxcap = QInputDialog()
            self.maxcap.setOption(QInputDialog.InputDialogOption.NoButtons)
            self.maxcap.setInputMode(QInputDialog.InputMode.IntInput)
            self.maxcap.setLabelText("maximum words per caption:")
            self.maxcap.setIntValue(self.opt_maxcap)

            # font type
            self.fontLabel = QLabel("font:")

            self.fontInputField = QComboBox()
            self.fontInputField.setEditable(False)
            self.fontInputField.setEditText(self.opt_font)
            self.fontInputField.addItems([s for s in Fonts.keys()])
            self.fontInputField.currentTextChanged.connect(self.updateFont)

            self.font_container = QWidget()
            self.font_layout = QVBoxLayout()
            self.font_container.setLayout(self.font_layout)
            self.font_layout.addWidget(self.fontLabel)
            self.font_layout.addWidget(self.fontInputField)

            # font size * point to scale
            self.font_size = QInputDialog()
            self.font_size.setOption(QInputDialog.InputDialogOption.NoButtons)
            self.font_size.setInputMode(QInputDialog.InputMode.DoubleInput)
            self.font_size.setLabelText("font size:")
            self.font_size.setDoubleValue(self.opt_font_size)
            self.font_size.doubleValueChanged.connect(self.updateFontSize)

            # color
            self.colorLabel = QLabel("color:")

            self.colorInputField = QComboBox()
            self.colorInputField.setEditable(False)
            self.colorInputField.setEditText(self.opt_color)
            self.colorInputField.addItems([s for s in Colors.keys()])
            self.colorInputField.currentTextChanged.connect(self.updateColor)

            self.color_container = QWidget()
            self.color_layout = QVBoxLayout()
            self.color_container.setLayout(self.color_layout)
            self.color_layout.addWidget(self.colorLabel)
            self.color_layout.addWidget(self.colorInputField)

            # rotation
            self.rotationButton = QPushButton("rotate")

            # layout main.py options and set defaults
            self.opt_layout = QHBoxLayout()
            self.opt_container = QWidget()
            self.opt_container.setLayout(self.opt_layout)
            self.opt_layout.addWidget(self.maxcap)
            self.opt_layout.addWidget(self.font_size)
            self.opt_layout.addWidget(self.font_container)
            self.opt_layout.addWidget(self.color_container)
            self.opt_layout.addWidget(self.rotationButton)
            
            print("Adding widgets to layout...")

            self.layout.addWidget(self.image_label)
            self.layout.addWidget(self.filename_label)
            self.layout.addWidget(self.nav_container)
            self.layout.addWidget(self.vidname_label)
            self.layout.addWidget(self.fileSelectButton)
            self.layout.addWidget(self.opt_container)
            
            print("Loading frames...")
            # Load frames and show first frame
            self.frames = []
            self.frame_files = []  # Store filenames
            self.current_frame_index = 0
            self.loadFrames()
            print("Showing first frame...")
            self.showFrame(0)
            print("MainWindow init complete.")
        except Exception as e:
            print(f"Error in MainWindow initialization: {e}")
            import traceback
            traceback.print_exc()

    def runGenerator(self):
        transcriber = VideoTranscriber(file, maxcap, font, font_size, color, yaxis, rotate)
        transcriber.extract_audio()
        transcriber.transcribe_video()
        output_path = os.path.join('outputFiles/', 'output_' + os.path.basename(file))
        transcriber.create_video(output_path)
        
    def extract_frames_ui(self, output_folder):
        if self.opt_video_path:
            print('Extracting frames ui')
            cap = cv2.VideoCapture(self.opt_video_path)
            N_frames = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
                N_frames += 1
            
            cap.release()
            print('Frames ui extracted')
        else:
            print('opt_video_path not yet defined', file=sys.stderr)
            
    def set_frames_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            for file in os.listdir(folder):
                path = os.path.join(folder, path)
                try:
                    if os.path.isfile(path):
                        os.unlink(path)
                except Exception as e:
                    print(f'Error deleting {path}: {e}')
    
    def create_frames_ui(self):
        obs_folder = os.path.join("outputFiles/", "ui_frames")
        self.set_frames_folder(obs_folder)
        self.extract_frames_ui(obs_folder)

    def openFileDialogue(self):
        file_dialogue = QFileDialog(self)
        file_path, _ = file_dialogue.getOpenFileName(self, "Select File")
        if file_path:
            print(f"Selected file: {file_path}")
            self.opt_video_path = file_path
            self.create_frames_ui()
            self.loadFrames()
            self.showFrame(0)
        else:
            print("No file selected")

    def loadFrames(self):
        cur_file_path = os.path.abspath(__file__)
        cur_dir = os.path.dirname(cur_file_path)
        #parent_dir = os.path.dirname(cur_dir)
        frames_dir = os.path.join(cur_dir, "outputFiles/ui_frames")
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
                thumbnail.clicked.connect(lambda idx=0: self.showFrame(idx))
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
            
            blank_pixmap = QPixmap(400, 300)
            blank_pixmap.fill(Qt.white)
            self.frames.append(blank_pixmap)
            self.frame_files.append("blank.jpg")
            self.showFrame(0)
            return
            
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
                    
                    thumbnail = ThumbnailLabel()
                    thumbnail_pixmap = pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail.setPixmap(thumbnail_pixmap)
                    thumbnail.clicked.connect(lambda idx=len(self.frames)-1: self.showFrame(idx))
                    self.thumbnail_layout.addWidget(thumbnail)
                    
        if not self.frames:
            print("Error: Failed to load any valid frames.")
            self.filename_label.setText("Error: Failed to load any valid frames")
            
            blank_pixmap = QPixmap(400, 300)
            blank_pixmap.fill(Qt.white)
            self.frames.append(blank_pixmap)
            self.frame_files.append("blank.jpg")
            
            thumbnail = ThumbnailLabel()
            thumbnail_pixmap = blank_pixmap.scaled(80, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumbnail.setPixmap(thumbnail_pixmap)
            thumbnail.clicked.connect(lambda idx=0: self.showFrame(idx))
            self.thumbnail_layout.addWidget(thumbnail)

    def showFrame(self, index):
        if not self.frames:  # Check if frames list is empty
            print("No frames loaded.")
            return
            
        if 0 <= index < len(self.frames):
            self.current_frame_index = index
            self.original_pixmap = self.frames[index]
            self.updateImageSize()
            
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

    def showPreviousFrame(self):
        if not self.frames:  # Check if frames list is empty
            return
        new_index = (self.current_frame_index - 1) % len(self.frames)
        self.showFrame(new_index)
        # Scroll to the previous thumbnail
        if new_index > 0:
            prev_widget = self.thumbnail_layout.itemAt(new_index - 1).widget()
            self.scroll_area.ensureWidgetVisible(prev_widget)

    def showNextFrame(self):
        if not self.frames:  # Check if frames list is empty
            return
        new_index = (self.current_frame_index + 1) % len(self.frames)
        self.showFrame(new_index)
        # Scroll to the next thumbnail
        if new_index < len(self.frames) - 1:
            next_widget = self.thumbnail_layout.itemAt(new_index + 1).widget()
            self.scroll_area.ensureWidgetVisible(next_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Start or restart the timer on resize
        self.resize_timer.start(150)  # 150ms debounce

    def handleResizeTimeout(self):
        self.updateImageSize()

    def updateImageSize(self):
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
            #image_height = scaled_pixmap.height()
            
            # Calculate the actual image position within the label (for centering)
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            
            # Calculate image offset (for centered images)
            x_offset = (label_width - image_width) // 2
            #y_offset = (label_height - image_height) // 2
            
            # Set text box size to be approximately 20% of image width and 15% of image height
            text_width = int(image_width * self.text_box.par_img_w_ratio)
            text_height = int(label_height * self.text_box.par_img_h_ratio)
            self.text_box.setFixedSize(text_width, text_height)
            
            # Ensure cursor settings are preserved
            self.text_box.setCursor(Qt.CursorShape.OpenHandCursor)
            self.text_box.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            
            # Update text box position - constrain to the actual image area
            text_box_pos = self.text_box.pos()
            
            # Calculate the bounds of the actual image within the label
            min_x = x_offset
            min_y = 0
            max_x = x_offset + image_width - self.text_box.width()
            max_y = label_height - self.text_box.height()
            
            # Ensure text box stays within image bounds
            new_x = min(max(min_x, text_box_pos.x()), max_x)
            new_y = min(max(min_y, text_box_pos.y()), max_y)
            
            self.text_box.move(new_x, new_y)
        
    def updateColor(self):
        print("COLOR CHANGE")
        self.opt_color = self.colorInputField.currentText()
        self.text_box.setTextColor(self.opt_color)

    def updateFont(self):
        print("FONT CHANGE")
        self.opt_font = self.fontInputField.currentText()
        self.text_box.setCurrentFont(self.opt_font)

    def updateFontSize(self):
        print("FONT SIZE CHANGE")
        self.opt_font_size = self.font_size.doubleValue()
        (_, height), _ = cv2.getTextSize(
            text = "M",
            fontFace = Fonts[self.opt_font],
            fontScale = 1,
            thickness = 1
        )
        base_font_px = height
        point_size = (self.opt_font_size * base_font_px * 72) / 96 # 96 == DPI --dots per inch
        self.text_box.setFontPointSize(point_size)

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