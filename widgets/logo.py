import os

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap

from paths import base_dir

_RES_DIR = os.path.join(base_dir(), "resources")

_BASE_FILES = ("logo.png", "logo.jpg", "logo.jpeg")
_DARK_FILES = ("logo_dark.png", "logo_dark.jpg", "logo_dark.jpeg")


def _load_source(base):
    """Carga un archivo de logo recortando el margen transparente. Devuelve QImage o None."""
    for name in base:
        path = os.path.join(_RES_DIR, name)
        if not os.path.exists(path):
            continue
        img = QImage(path).convertToFormat(QImage.Format.Format_ARGB32)
        if img.isNull():
            continue
        w, h = img.width(), img.height()
        minx, miny, maxx, maxy = w, h, 0, 0
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                if img.pixelColor(x, y).alpha() > 8:
                    if x < minx: minx = x
                    if x > maxx: maxx = x
                    if y < miny: miny = y
                    if y > maxy: maxy = y
        if maxx >= minx and maxy >= miny:
            img = img.copy(QRect(minx, miny, maxx - minx + 1, maxy - miny + 1))
        return img
    return None


def logo_pixmap(size=110, dark=False):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    src = _load_source(_DARK_FILES if dark else _BASE_FILES)
    if src is None:
        src = _load_source(_BASE_FILES)
    if src is None:
        return pm
    scaled = src.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.drawPixmap(int((size - scaled.width()) / 2), int((size - scaled.height()) / 2),
                 QPixmap.fromImage(scaled))
    p.end()
    return pm


def logo_icon(size=64, dark=False):
    return QIcon(logo_pixmap(size, dark))
