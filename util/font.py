import cv2
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
cssFontPath = {}

lst_of_css_fonts = [
    "Arial",
    "Times New Roman",
    "Comic Sans"
]

# uses PySide6 to find system-wide fonts and define them to cssFontPath
def initCssFonts():
    font_db = QFontDatabase()
    for font in lst_of_css_fonts:
        font_path = None
        for font_info in font_db.styles(font):
            if hasattr(font_db, 'fontFilePath'):
                font_path = font_db.fontFilePath(font, font_info)
        if font_path and font_path.lower().endswith('.ttf'):
            cssFontPath[font] = font_path
        else:
            print(f"{font} path couldn't be found.")
            cssFontPath[font] = None
