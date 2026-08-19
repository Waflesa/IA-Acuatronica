import ctypes
import ctypes.wintypes
import datetime
import math

from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout, QLabel,
                               QMainWindow, QPushButton, QStackedWidget, QTabBar,
                               QVBoxLayout, QWidget)

from ui import app_theme
from ui.logic.backend_client import BackendClient
from ui.logic.sensors import META
from ui.pages.alerts_page import AlertsPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.diagnosis_page import DiagnosisPage
from ui.pages.fuzzy_page import FuzzyPage
from ui.widgets.logo import logo_icon, logo_pixmap
from ui.widgets.sensor_tool import SensorTool

WM_NCHITTEST = 0x0084
WM_GETMINMAXINFO = 0x0024
HTCLIENT = 1
HTCAPTION = 2
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17


class _MINMAXINFO(ctypes.Structure):
    _fields_ = [
        ("ptReserved", ctypes.wintypes.POINT),
        ("ptMaxSize", ctypes.wintypes.POINT),
        ("ptMaxPosition", ctypes.wintypes.POINT),
        ("ptMinTrackSize", ctypes.wintypes.POINT),
        ("ptMaxTrackSize", ctypes.wintypes.POINT),
    ]


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


class _WinBtn(QPushButton):
    """Botón de ventana: minimizar, maximizar/restaurar o cerrar (iconos vectoriales)."""

    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self._kind = kind  # "min" | "max" | "close"
        self._maximized = False
        self._hover = False
        self._color = QColor("#8B98A7")
        self.setFixedSize(46, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def set_maximized(self, maximized):
        if self._maximized != maximized:
            self._maximized = maximized
            self.update()

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        if self._hover:
            if self._kind == "close":
                p.fillRect(0, 0, w, h, QColor("#E81123"))
            else:
                bg = QColor(self._color)
                bg.setAlpha(36)
                p.fillRect(0, 0, w, h, bg)

        icon = QColor("#FFFFFF") if (self._hover and self._kind == "close") else self._color
        pen = QPen(icon, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        cx, cy = w / 2.0, h / 2.0

        if self._kind == "min":
            p.drawLine(QPointF(cx - 4.5, cy), QPointF(cx + 4.5, cy))
        elif self._kind == "max":
            if self._maximized:
                p.drawRect(QRectF(cx - 3.2, cy - 3.6, 7.0, 7.0))
                p.drawRect(QRectF(cx - 4.6, cy - 1.6, 7.0, 7.0))
            else:
                p.drawRect(QRectF(cx - 4.4, cy - 4.0, 8.8, 8.8))
        else:
            p.drawLine(QPointF(cx - 4, cy - 4), QPointF(cx + 4, cy + 4))
            p.drawLine(QPointF(cx - 4, cy + 4), QPointF(cx + 4, cy - 4))
        p.end()


class _BackendBtn(QPushButton):
    """Botón de conexión con el motor IA del backend (off / connecting / on / error)."""

    _TEXTO = {
        "off": "Conectar IA",
        "connecting": "Conectando…",
        "on": "IA conectada",
        "error": "Error de conexión",
    }
    _DOT = {
        "off": "#5B6672",
        "connecting": "#E6A23C",
        "on": "#2ECC71",
        "error": "#E35B5B",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = "off"
        self._color = QColor("#8B98A7")
        self.setObjectName("backendBtn")
        self.setFixedSize(120, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_state(self, state):
        self._state = state
        self.update()

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        dot = QColor(self._DOT[self._state])
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(dot))
        p.drawEllipse(QRectF(8, 9, 8, 8))
        f = p.font()
        f.setPointSize(8)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QPen(self._color))
        p.drawText(QRect(21, 0, self.width() - 25, self.height()),
                   Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                   self._TEXTO[self._state])
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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
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
        status_lbl = QLabel("SISTEMA OPERATIVO")
        status_lbl.setObjectName("sideStatus")
        self.led = led
        self.status_lbl = status_lbl
        app_row.addWidget(led)
        app_row.addWidget(status_lbl)
        self.backend_btn = _BackendBtn()
        self.backend_btn.setToolTip(f"Conectar con el motor IA del backend ({self._client.url()})")
        self.backend_btn.clicked.connect(self._on_backend_btn)
        self._client.status_changed.connect(self._backend_state)
        app_row.addSpacing(8)
        app_row.addWidget(self.backend_btn)
        app_row.addSpacing(8)
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
        self.min_btn = _WinBtn("min")
        self.max_btn = _WinBtn("max")
        self.close_btn = _WinBtn("close")
        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self._toggle_max)
        self.close_btn.clicked.connect(self.close)
        app_row.addSpacing(6)
        app_row.addWidget(self.min_btn)
        app_row.addWidget(self.max_btn)
        app_row.addWidget(self.close_btn)
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
        self._refresh_tools()
        self._apply_theme(self._theme)
        self._update_collapse_btn()

    def _app(self):
        return QApplication.instance()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._update_win_buttons)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            QTimer.singleShot(0, self._update_win_buttons)
        super().changeEvent(event)

    def nativeEvent(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            try:
                addr = int(message)
            except (TypeError, ValueError, OverflowError):
                addr = message.__int__()
            msg = ctypes.wintypes.MSG.from_address(addr)
            if msg.message == WM_NCHITTEST:
                l = int(msg.lParam)
                x = ctypes.c_short(l & 0xFFFF).value
                y = ctypes.c_short((l >> 16) & 0xFFFF).value
                dpr = self.devicePixelRatioF() or 1.0
                res = self._hit_test(QPoint(int(x / dpr), int(y / dpr)))
                return True, res
            if msg.message == WM_GETMINMAXINFO:
                return self._wm_getminmaxinfo(msg)
        return super().nativeEvent(eventType, message)

    def _hit_test(self, gpos):
        """Devuelve la zona de Windows (HTCAPTION para arrastrar, HT* para redimensionar)."""
        if not self.isMaximized():
            win = self.geometry()
            m = 6
            left = gpos.x() - win.left()
            top = gpos.y() - win.top()
            right = win.right() - gpos.x()
            bottom = win.bottom() - gpos.y()
            if left <= m and top <= m:
                return HTTOPLEFT
            if right <= m and top <= m:
                return HTTOPRIGHT
            if left <= m and bottom <= m:
                return HTBOTTOMLEFT
            if right <= m and bottom <= m:
                return HTBOTTOMRIGHT
            if left <= m:
                return HTLEFT
            if right <= m:
                return HTRIGHT
            if top <= m:
                return HTTOP
            if bottom <= m:
                return HTBOTTOM

        bar = self._titlebar
        if bar.isVisible():
            win = self.geometry()
            bar_bottom = bar.mapToGlobal(QPoint(0, bar.height())).y()
            if win.top() <= gpos.y() <= bar_bottom and win.left() <= gpos.x() <= win.right():
                for btn in (self.min_btn, self.max_btn, self.close_btn,
                            self.theme_btn, self.collapse_btn, self.backend_btn):
                    btl = btn.mapToGlobal(QPoint(0, 0))
                    if QRect(btl, btn.size()).contains(gpos):
                        return HTCLIENT
                return HTCAPTION
        return HTCLIENT

    def _wm_getminmaxinfo(self, msg):
        info = _MINMAXINFO.from_address(int(msg.lParam))
        screen = self.screen() or QGuiApplication.primaryScreen()
        wa = screen.availableGeometry()
        dpr = self.devicePixelRatioF() or 1.0
        info.ptMaxPosition.x = int(wa.x() * dpr)
        info.ptMaxPosition.y = int(wa.y() * dpr)
        info.ptMaxSize.x = int(wa.width() * dpr)
        info.ptMaxSize.y = int(wa.height() * dpr)
        info.ptMinTrackSize.x = self.minimumWidth()
        info.ptMinTrackSize.y = self.minimumHeight()
        return True, 0

    def _toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self._update_win_buttons()

    def _update_win_buttons(self):
        self.max_btn.set_maximized(self.isMaximized())

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
        self.backend_btn.set_color(pal["text"])
        dark_logo = mode == app_theme.LIGHT
        self.logo_lbl.setPixmap(logo_pixmap(30, dark=dark_logo))
        self.setWindowIcon(logo_icon(64, dark=dark_logo))
        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.set_color(pal["text"])
        for pg in self.pages:
            if hasattr(pg, "apply_theme"):
                pg.apply_theme(mode)
        self._backend_state(self._client.state())

    def _on_backend_btn(self):
        self._client.toggle()

    def _backend_state(self, state):
        self.backend_btn.set_state(state)
        self.combo.setEnabled(state != "on")
        if state == "on":
            self.led.set_color("#2ECC71")
            self.status_lbl.setText("MOTOR IA CONECTADO")
        elif state == "error":
            self.led.set_color("#E35B5B")
            self.status_lbl.setText("ERROR DE CONEXIÓN")
        else:
            self.led.set_color(app_theme.palette(self._theme)["accent"])
            self.status_lbl.setText("SISTEMA OPERATIVO")

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