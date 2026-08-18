from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ui.widgets.chart import LineChartWidget
from ui.widgets.header import PageHeader


class DashboardPage(QWidget):
    def __init__(self, sensors):
        super().__init__()
        self._sensors = sensors

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(12)

        v.addWidget(PageHeader(
            "Dashboard",
            "Tendencias de la calidad del agua en tiempo real"))

        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)
        self.chart_a = LineChartWidget(
            [("Temperatura °C", "#4EA8FF", "temp"),
             ("Oxígeno Disuelto mg/L", "#7AC4FF", "od"),
             ("pH", "#2E86DE", "ph")],
            0, 35, "Parámetros físicos")
        self.chart_b = LineChartWidget(
            [("Amonio (NH₃)", "#E35B5B", "amonio"),
             ("Nitritos (NO₂)", "#E6A23C", "nitrito")],
            0, 1.5, "Ciclo del nitrógeno")
        charts_row.addWidget(self.chart_a)
        charts_row.addWidget(self.chart_b)
        v.addLayout(charts_row, 1)

        sensors.data_changed.connect(self._refresh)
        self._refresh()

    def apply_theme(self, mode):
        self.chart_a.set_theme(mode)
        self.chart_b.set_theme(mode)

    def _refresh(self):
        hist = self._sensors.history()
        self.chart_a.update_data(hist)
        self.chart_b.update_data(hist)