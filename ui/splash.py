import os

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (QBrush, QColor, QFont, QFontDatabase, QFontMetrics,
                           QGuiApplication, QImage, QLinearGradient, QPainter, QPen, QPixmap)
from PySide6.QtWidgets import QWidget

from ui.paths import base_dir

_STEPS = [
    ("Inicializando módulos de control…", 8),
    ("Conectando sensores simulados…", 26),
    ("Calibrando controlador difuso…", 52),
    ("Cargando sistema experto…", 78),
    ("Preparando dashboard de H2-OBSERVER…", 92),
    ("Listo", 100),
]

_CARD_W, _CARD_H = 760, 480

_METAL_STOPS = [
    (0.00, "#262F39"),
    (0.12, "#1A2129"),
    (0.30, "#202831"),
    (0.55, "#161C23"),
    (0.80, "#1D242D"),
    (1.00, "#12171D"),
]


class SplashScreen(QWidget):
    """Pantalla de inicio: tarjeta rectangular sobre el escritorio.

    Si existe ``resources/splash_bg.png`` se usa como fondo de la tarjeta;
    si no, se dibuja el fondo metálico por defecto.
    """

    finished = Signal()

    def __init__(self):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(_CARD_W, _CARD_H)

        res_dir = os.path.join(base_dir(), "resources")
        font_path = os.path.join(res_dir, "GuggenheimSans-Bold.ttf")
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)

        self._bg = None
        for name in ("splash_bg.png", "splash_bg.jpg", "splash_bg.jpeg"):
            path = os.path.join(res_dir, name)
            if os.path.exists(path):
                self._bg = QPixmap(path)
                if not self._bg.isNull():
                    break
                self._bg = None

        self._logo = None
        self._logo_src = None
        for name in ("logo.png", "logo.jpg", "logo.jpeg"):
            path = os.path.join(res_dir, name)
            if os.path.exists(path):
                self._logo = QPixmap(path)
                if not self._logo.isNull():
                    img = self._logo.toImage().convertToFormat(QImage.Format.Format_ARGB32)
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
                        self._logo_src = (minx, miny, maxx - minx + 1, maxy - miny + 1)
                    break
                self._logo = None

        screen = QGuiApplication.primaryScreen()
        geo = screen.availableGeometry() if screen else None
        if geo:
            self.move(int(geo.x() + (geo.width() - _CARD_W) / 2),
                      int(geo.y() + (geo.height() - _CARD_H) / 2))

        self._index = 0
        self._msg, self._pct = _STEPS[0]
        self._timer = QTimer(self)
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self._advance)

    def start(self):
        self.show()
        self._timer.start()

    def _advance(self):
        self._index += 1
        if self._index >= len(_STEPS):
            self._timer.stop()
            self.finished.emit()
            self.close()
            return
        self._msg, self._pct = _STEPS[self._index]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        card = QRectF(r).adjusted(1, 1, -1, -1)

        if self._bg is not None and not self._bg.isNull():
            cw, ch = card.width(), card.height()
            sw = cw / self._bg.width()
            sh = ch / self._bg.height()
            s = max(sw, sh)
            w = int(self._bg.width() * s)
            h = int(self._bg.height() * s)
            x = int(card.center().x() - w / 2)
            y = int(card.center().y() - h / 2)
            p.drawPixmap(x, y, w, h, self._bg)
        else:
            metal = QLinearGradient(0, card.top(), 0, card.bottom())
            for pos, hexc in _METAL_STOPS:
                metal.setColorAt(pos, QColor(hexc))
            p.setBrush(QBrush(metal))
            p.fillRect(card, metal)

            sheen = QLinearGradient(card.topLeft(), card.bottomLeft())
            sheen.setColorAt(0.0, QColor(255, 255, 255, 18))
            sheen.setColorAt(0.4, QColor(255, 255, 255, 0))
            p.fillRect(card, sheen)

        p.setPen(QPen(QColor("#2A3440"), 1))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(card)

        font = QFont("Guggenheim Sans", 24)
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        fm = QFontMetrics(font)

        lt = "H2-"
        rt = "BSERVER"
        gap = 6

        if self._logo is not None and not self._logo.isNull():
            lh = 130
            if self._logo_src:
                sx, sy, sw, sh = self._logo_src
            else:
                sx, sy, sw, sh = 0, 0, self._logo.width(), self._logo.height()
            lw = int(lh * sw / sh)
        else:
            lh = lw = 0

        cy = card.top() + card.height() / 2
        half = lw / 2
        x0 = card.left() + 60
        cx = x0 + fm.horizontalAdvance(lt) + gap + half

        if self._logo is not None and not self._logo.isNull():
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPixmap(int(cx - lw / 2), int(cy - lh / 2), lw, lh,
                         self._logo, sx, sy, sw, sh)

        p.setPen(QColor("#FFFFFF"))
        left_rect = QRectF(x0, cy - 40, (cx - half - gap) - x0, 80)
        p.drawText(left_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, lt)
        right_rect = QRectF(cx + half + gap, cy - 40,
                            card.right() - 60 - (cx + half + gap), 80)
        p.drawText(right_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, rt)

        bar = QRectF(card.right() - 20 - 200, card.bottom() - 30, 200, 3)
        p.setPen(QColor("#A9B4BF"))
        p.setFont(QFont("Segoe UI", 10))
        p.drawText(QRectF(card.left() + 60, card.bottom() - 42, card.width() - 296, 20),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self._msg)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#202A34")))
        p.drawRoundedRect(bar, 1, 1)

        fill = QRectF(bar.left(), bar.top(), bar.width() * self._pct / 100.0, bar.height())
        p.setBrush(QBrush(QColor("#cbd2daff")))
        p.drawRoundedRect(fill, 1, 1)
        p.end()