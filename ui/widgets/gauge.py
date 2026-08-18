from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

_COLORS = {"ok": "#3D9BFF", "warn": "#E6A23C", "crit": "#E35B5B"}


class Gauge(QWidget):
    """Gauge semicircular minimalista: un único arco por fracción y color según estado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frac = 0.0
        self._status = "ok"
        self.setMinimumSize(120, 74)
        self.setMaximumHeight(96)

    def set_value(self, frac, status):
        self._frac = min(max(frac, 0.0), 1.0)
        self._status = status
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h * 0.92
        r = min(w, h) * 0.42
        rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)

        p.setPen(QPen(QColor("#22303F"), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(rect, 0 * 16, 180 * 16)

        color = QColor(_COLORS.get(self._status, "#3D9BFF"))
        sweep = int(180 * self._frac) * 16
        p.setPen(QPen(color, 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(rect, 180 * 16, -sweep)
        p.end()