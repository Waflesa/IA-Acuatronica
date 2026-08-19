"""Medidor semicircular de una variable (solo lectura).

Muestra el valor que envía el backend como un arco semicircular coloreado
según el estado (ÓPTIMO / ADVERTENCIA / CRÍTICO). Sin backend se ve vacío
con la etiqueta "SIN DATOS". No permite edición manual.
"""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui import app_theme
from ui.logic.sensors import STATUS_LABEL
from ui.widgets.util import repolish

STATUS_COLORS = {
    "ok": "#2ECC71",
    "warn": "#E6A23C",
    "crit": "#E35B5B",
}


class _Arc(QWidget):
    """Pinta el semicírculo (pista + arco de valor + texto)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pct = 0.0
        self._color = None
        self._text = "—"
        self._mode = app_theme.current()
        self.setFixedSize(120, 78)

    def set_state(self, pct, color, text):
        self._pct = pct
        self._color = color
        self._text = text
        self.update()

    def set_theme(self, mode):
        self._mode = mode
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        pal = app_theme.palette(self._mode)
        w, h = self.width(), self.height()

        pen_w = 12
        margin = pen_w / 2
        # Elipse CUADRADA: su mitad superior es un semicírculo perfecto.
        side = min(w - pen_w, 2 * h - pen_w)
        ellipse = QRectF((w - side) / 2.0, margin, side, side)

        track = QPen(QColor(pal["track"]), pen_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(track)
        p.drawArc(ellipse, 180 * 16, 180 * 16)

        if self._color is not None:
            span = int(180 * 16 * max(min(self._pct, 1.0), 0.0))
            if span > 0:
                valpen = QPen(QColor(self._color), pen_w,
                              Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                p.setPen(valpen)
                p.drawArc(ellipse, 180 * 16, -span)

        p.setPen(QColor(pal["text"] if self._color else pal["sub"]))
        f = QFont("Segoe UI", 13, QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(QRectF(0, (h - 34) / 2.0, w, 34),
                   Qt.AlignmentFlag.AlignCenter, self._text)
        p.end()


class SemiGauge(QWidget):
    """Medidor de una variable; los valores los escribe únicamente el backend."""

    def __init__(self, sid, meta, parent=None):
        super().__init__(parent)
        self._sid = sid
        self._meta = meta
        self._mode = app_theme.current()
        self.setFixedWidth(132)

        v = QVBoxLayout(self)
        v.setContentsMargins(6, 8, 6, 6)
        v.setSpacing(5)

        self._arc = _Arc()
        v.addWidget(self._arc, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.name_lbl = QLabel(meta["name"].upper())
        self.name_lbl.setObjectName("gaugeName")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.name_lbl)

        self.pill = QLabel("")
        self.pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.pill)

        self.set_disconnected()

    def apply_theme(self, mode):
        self._mode = mode
        self._arc.set_theme(mode)

    def set_disconnected(self):
        """Estado sin backend: medidor vacío y sin valor."""
        self._arc.set_state(0.0, None, "—")
        self.pill.setText("SIN DATOS")
        self.pill.setObjectName("pillOff")
        repolish(self.pill)

    def set_reading(self, value, status):
        """Actualiza el medidor con el valor recibido del backend."""
        m = self._meta
        pct = (value - m["low"]) / (m["high"] - m["low"])
        self._arc.set_state(pct, STATUS_COLORS.get(status), f"{value:.2f}")
        self.pill.setText(" " + STATUS_LABEL[status] + " ")
        self.pill.setObjectName(f"pill{status.capitalize()}")
        repolish(self.pill)