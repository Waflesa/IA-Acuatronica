import datetime
import math

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QStackedWidget, QTabBar,
                               QVBoxLayout, QWidget)

import app_theme
from logic.sensors import META
from pages.alerts_page import AlertsPage
from pages.dashboard_page import DashboardPage
from pages.diagnosis_page import DiagnosisPage
from pages.fuzzy_page import FuzzyPage
from widgets.logo import logo_icon, logo_pixmap
from widgets.sensor_tool import SensorTool


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
        status_lbl = QLabel("SISTEMA OPERATIVO")
        status_lbl.setObjectName("sideStatus")
        self.led = led
        app_row.addWidget(led)
        app_row.addWidget(status_lbl)
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
        t.addLayout(app_row)

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
        sens_row.setSpacing(6)
        self.tools = []
        for sid, m in META.items():
            tool = SensorTool(sid, m, sensors)
            self.tools.append(tool)
            sens_row.addWidget(tool)
        sens_row.addStretch()
        rib.addLayout(_ribbon_group("SENSORES", sens_row))

        rib.addSpacing(14)
        rib.addWidget(_vdiv())
        rib.addSpacing(14)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        lbl = QLabel("Cada")
        lbl.setObjectName("cardRange")
        self.combo = QComboBox()
        self.combo.addItems(["1 s", "3 s", "5 s"])
        self.combo.currentIndexChanged.connect(self._on_interval)
        ctrl.addWidget(lbl)
        ctrl.addWidget(self.combo)
        rib.addLayout(_ribbon_group("ACTUALIZACIÓN", ctrl))

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
            FuzzyPage(sensors),
            DiagnosisPage(sensors),
            AlertsPage(sensors),
        ]
        for pg in self.pages:
            self.stack.addWidget(pg)
        self.tabs.currentChanged.connect(self.stack.setCurrentIndex)
        self.tabs.setCurrentIndex(0)

        lay.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        sensors.data_changed.connect(self._refresh_tools)
        self._refresh_tools()
        self._apply_theme(self._theme)
        self._update_collapse_btn()

    def _app(self):
        return QApplication.instance()

    def showEvent(self, event):
        super().showEvent(event)
        hwnd = int(self.winId())
        QTimer.singleShot(0, lambda: app_theme.apply_titlebar(hwnd, self._theme))

    def _on_interval(self):
        ms = {"1 s": 1000, "3 s": 3000, "5 s": 5000}[self.combo.currentText()]
        self._sensors.set_interval(ms)

    def _refresh_tools(self):
        for tool in self.tools:
            tool.refresh()
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

    def _toggle_theme(self):
        mode = app_theme.toggle(self._theme)
        app_theme.apply(self._app(), mode)
        app_theme.save(mode)
        self._apply_theme(mode)
        if self.isVisible():
            app_theme.apply_titlebar(int(self.winId()), mode)

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