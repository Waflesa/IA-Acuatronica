import ctypes
import datetime
import math

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QStackedWidget, QTabBar,
                               QVBoxLayout, QWidget)

from ui import app_theme
from ui.logic.backend_client import BackendClient
from ui.logic.sensors import META
from ui.pages.alerts_page import AlertsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.diagnosis_page import DiagnosisPage
from ui.pages.fuzzy_page import FuzzyPage
from ui.widgets.gauge import SemiGauge
from ui.widgets.logo import logo_icon, logo_pixmap

# Atributos DWM para la barra de título nativa (para que combine con el tema).
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36


def _colorref(hex_color):
    """Convierte #RRGGBB a COLORREF (0x00BBGGRR) usado por DWM."""
    v = int(hex_color.lstrip("#"), 16)
    r, g, b = (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF
    return (b << 16) | (g << 8) | r


class _StatusDot(QWidget):
    def __init__(self, color="#3D9BFF", parent=None):
        super().__init__(parent)
        self._color = QColor(color)

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())
        p.end()


class _ThemeIconBtn(QPushButton):
    """Botón de tema: luna (oscuro) o sol (claro), dibujado simple, sin emojis."""

    def __init__(self, mode="dark", parent=None):
        super().__init__(parent)
        self._moon = mode == "dark"
        self._color = QColor("#8B98A7")
        self.setObjectName("cornerBtn")
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_mode(self, mode):
        self._moon = mode == "dark"
        self.update()

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = self.width() / 2.0
        p.setBrush(QBrush(self._color))
        if self._moon:
            body = QPainterPath()
            body.addEllipse(c - 5.0, c - 5.0, 10.0, 10.0)
            bite = QPainterPath()
            bite.addEllipse(c - 2.0, c - 3.6, 8.4, 8.4)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawPath(body.subtracted(bite))
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(c, c), 3.4, 3.4)
            pen = QPen(self._color, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            for i in range(8):
                a = math.radians(45 * i)
                dx, dy = math.cos(a) * 5.6, math.sin(a) * 5.6
                p.setPen(pen)
                p.drawLine(QPointF(c + dx * 0.7, c + dy * 0.7),
                           QPointF(c + dx, c + dy))
        p.end()


def _vdiv():
    d = QFrame()
    d.setObjectName("vdiv")
    d.setFixedWidth(1)
    return d


def _ribbon_group(caption, content_lay):
    g = QVBoxLayout()
    g.setSpacing(6)
    cap = QLabel(caption)
    cap.setObjectName("ribbonCap")
    g.addWidget(cap)
    g.addLayout(content_lay)
    return g


class MainWindow(QMainWindow):
    def __init__(self, sensors):
        super().__init__()
        self._sensors = sensors
        self._client = BackendClient(sensors)
        self._theme = app_theme.current()
        self._ribbon_open = True
        self.setWindowTitle("H2-OBSERVER · Control de Acuaponía")
        self.setWindowIcon(logo_icon())
        self.resize(1320, 800)
        self.setMinimumSize(1100, 680)
        self.setObjectName("appBg")

        central = QWidget()
        central.setObjectName("appBg")
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        top = QFrame()
        top.setObjectName("topBar")
        t = QVBoxLayout(top)
        t.setContentsMargins(14, 10, 14, 10)
        t.setSpacing(8)

        app_row = QHBoxLayout()
        app_row.setContentsMargins(0, 0, 0, 0)
        app_row.setSpacing(10)
        self.logo_lbl = QLabel()
        self.logo_lbl.setPixmap(logo_pixmap(30))
        self.logo_lbl.setFixedSize(30, 30)
        name_lbl = QLabel("H2-OBSERVER")
        name_lbl.setObjectName("sideName")
        app_row.addWidget(self.logo_lbl)
        app_row.addWidget(name_lbl)
        app_row.addStretch()
        led = _StatusDot(app_theme.palette(self._theme)["accent"])
        led.setFixedSize(10, 10)
        status_lbl = QLabel("BACKEND DESCONECTADO")
        status_lbl.setObjectName("sideStatus")
        self.led = led
        self.status_lbl = status_lbl
        app_row.addWidget(led)
        app_row.addWidget(status_lbl)
        self._client.status_changed.connect(self._backend_state)
        self.collapse_btn = QPushButton()
        self.collapse_btn.setObjectName("cornerBtn")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.clicked.connect(self._toggle_ribbon)
        self.theme_btn = _ThemeIconBtn(self._theme)
        self.theme_btn.clicked.connect(self._toggle_theme)
        app_row.addSpacing(12)
        app_row.addWidget(self.collapse_btn)
        app_row.addWidget(self.theme_btn)
        self._titlebar = QWidget()
        self._titlebar.setLayout(app_row)
        t.addWidget(self._titlebar)

        self.tabs = QTabBar()
        self.tabs.setObjectName("navTabs")
        self.tabs.setDrawBase(False)
        self.tabs.setExpanding(True)
        for label in ["Dashboard", "Control Difuso", "Diagnóstico", "Alertas"]:
            self.tabs.addTab(label)
        t.addWidget(self.tabs)

        ribbon = QFrame()
        ribbon.setObjectName("ribbon")
        rib = QHBoxLayout(ribbon)
        rib.setContentsMargins(8, 6, 8, 6)
        rib.setSpacing(0)

        sens_row = QHBoxLayout()
        sens_row.setSpacing(10)
        self.gauges = []
        for sid in ("ph", "temp", "od", "amonio", "nitrito"):
            gauge = SemiGauge(sid, META[sid])
            self.gauges.append(gauge)
            sens_row.addWidget(gauge)
        sens_row.addStretch()
        rib.addLayout(_ribbon_group("SENSORES", sens_row))

        rib.addSpacing(14)
        rib.addWidget(_vdiv())
        rib.addSpacing(14)

        time_lay = QVBoxLayout()
        time_lay.setSpacing(2)
        self.time_lbl = QLabel("—")
        self.time_lbl.setObjectName("toolValue")
        time_lay.addWidget(self.time_lbl)
        rib.addLayout(_ribbon_group("ÚLTIMA LECTURA", time_lay))

        rib.addStretch()
        self.ribbon = ribbon
        t.addWidget(ribbon)

        lay.addWidget(top)

        self.stack = QStackedWidget()
        self.pages = [
            DashboardPage(sensors),
            FuzzyPage(sensors, self._client),
            DiagnosisPage(sensors, self._client),
            AlertsPage(sensors, self._client),
        ]
        for pg in self.pages:
            self.stack.addWidget(pg)
        self.tabs.currentChanged.connect(self.stack.setCurrentIndex)
        self.tabs.setCurrentIndex(0)

        lay.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        sensors.data_changed.connect(self._refresh_tools)
        self.time_lbl.setText("—")
        self._apply_theme(self._theme)
        self._update_collapse_btn()

    def _app(self):
        return QApplication.instance()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._set_caption)

    def _set_caption(self):
        """Colorea la barra de título nativa según el tema (combina con el dashboard)."""
        try:
            hwnd = int(self.winId())
        except Exception:
            return
        pal = app_theme.palette(self._theme)
        dwm = ctypes.windll.dwmapi
        dark = 1 if self._theme == app_theme.DARK else 0
        mode = ctypes.c_int(dark)
        for attr in (DWMWA_USE_IMMERSIVE_DARK_MODE, 19):
            try:
                dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(mode), ctypes.sizeof(mode))
            except Exception:
                pass
        for attr, color in ((DWMWA_CAPTION_COLOR, pal["surface"]),
                            (DWMWA_TEXT_COLOR, pal["text"])):
            try:
                ref = ctypes.c_uint(_colorref(color))
                dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(ref), ctypes.sizeof(ref))
            except Exception:
                pass

    def _refresh_tools(self):
        vals = self._sensors.values()
        for gauge in self.gauges:
            gauge.set_reading(vals[gauge._sid], self._sensors.status(gauge._sid))
        self.time_lbl.setText(datetime.datetime.now().strftime("%H:%M:%S"))

    def _apply_theme(self, mode):
        self._theme = mode
        pal = app_theme.palette(mode)
        self.led.set_color(pal["accent"])
        self.theme_btn.set_mode(mode)
        self.theme_btn.setToolTip("Cambiar a modo claro" if mode == app_theme.DARK else "Cambiar a modo oscuro")
        dark_logo = mode == app_theme.LIGHT
        self.logo_lbl.setPixmap(logo_pixmap(30, dark=dark_logo))
        self.setWindowIcon(logo_icon(64, dark=dark_logo))
        for pg in self.pages:
            if hasattr(pg, "apply_theme"):
                pg.apply_theme(mode)
        for gauge in self.gauges:
            gauge.apply_theme(mode)
        self._backend_state(self._client.state())
        if self.isVisible():
            self._set_caption()

    def _backend_state(self, state):
        if state == "on":
            self.led.set_color("#2ECC71")
            self.status_lbl.setText("MOTOR IA CONECTADO")
        else:
            self.led.set_color("#E6A23C" if state == "connecting"
                               else app_theme.palette(self._theme)["accent"])
            self.status_lbl.setText(
                "CONECTANDO AL MOTOR IA…" if state == "connecting" else "BACKEND DESCONECTADO")
            for gauge in self.gauges:
                gauge.set_disconnected()

    def _toggle_theme(self):
        mode = app_theme.toggle(self._theme)
        app_theme.apply(self._app(), mode)
        app_theme.save(mode)
        self._apply_theme(mode)

    def _toggle_ribbon(self):
        self._ribbon_open = not self._ribbon_open
        self.ribbon.setVisible(self._ribbon_open)
        self._update_collapse_btn()

    def _update_collapse_btn(self):
        if self._ribbon_open:
            self.collapse_btn.setText("▾")
            self.collapse_btn.setToolTip("Ocultar la barra de herramientas")
        else:
            self.collapse_btn.setText("▸")
            self.collapse_btn.setToolTip("Mostrar la barra de herramientas")