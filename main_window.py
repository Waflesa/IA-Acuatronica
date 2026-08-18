import datetime

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QMainWindow,
                               QStackedWidget, QTabBar, QVBoxLayout, QWidget)

from logic.sensors import META
from pages.alerts_page import AlertsPage
from pages.dashboard_page import DashboardPage
from pages.diagnosis_page import DiagnosisPage
from pages.fuzzy_page import FuzzyPage
from widgets.logo import logo_icon, logo_pixmap
from widgets.sensor_tool import SensorTool


class _StatusDot(QWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#00E676")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())
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
        logo_lbl = QLabel()
        logo_lbl.setPixmap(logo_pixmap(30))
        logo_lbl.setFixedSize(30, 30)
        name_lbl = QLabel("H2-OBSERVER")
        name_lbl.setObjectName("sideName")
        app_row.addWidget(logo_lbl)
        app_row.addWidget(name_lbl)
        app_row.addStretch()
        led = _StatusDot()
        led.setFixedSize(10, 10)
        status_lbl = QLabel("SISTEMA OPERATIVO")
        status_lbl.setObjectName("sideStatus")
        app_row.addWidget(led)
        app_row.addWidget(status_lbl)
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
        rib.setContentsMargins(12, 8, 12, 8)
        rib.setSpacing(0)

        sens_row = QHBoxLayout()
        sens_row.setSpacing(8)
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

    def _on_interval(self):
        ms = {"1 s": 1000, "3 s": 3000, "5 s": 5000}[self.combo.currentText()]
        self._sensors.set_interval(ms)

    def _refresh_tools(self):
        for tool in self.tools:
            tool.refresh()
        self.time_lbl.setText(datetime.datetime.now().strftime("%H:%M:%S"))