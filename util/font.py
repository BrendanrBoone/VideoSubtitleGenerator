import cv2
import os
from PySide6.QtGui import QFontDatabase
from PIL import ImageFont

Fonts = {
    'simplex': cv2.FONT_HERSHEY_SIMPLEX,
    'plain': cv2.FONT_HERSHEY_PLAIN,
    'duplex': cv2.FONT_HERSHEY_DUPLEX,
    'complex': cv2.FONT_HERSHEY_COMPLEX,
    'triplex': cv2.FONT_HERSHEY_TRIPLEX,
    'complex_small': cv2.FONT_HERSHEY_COMPLEX_SMALL,
    'script_simplex': cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    'script_complex': cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
    'italic': cv2.FONT_ITALIC
}

# {<font-name> : <font-path>}
cssFonts = {
    "Arial": os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts/Arial.ttf"),
    "Times New Roman": os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts/TimesNewRoman.ttf"),
    "Comic Sans": os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts/ComicSans.ttf")
}

