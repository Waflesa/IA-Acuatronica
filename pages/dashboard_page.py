from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from widgets.chart import LineChartWidget
from widgets.header import PageHeader


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
            [("Temperatura °C", "#00E676", "temp"),
             ("Oxígeno Disuelto mg/L", "#4FC3F7", "od"),
             ("pH", "#FFB300", "ph")],
            0, 35, "Parámetros físicos")
        self.chart_b = LineChartWidget(
            [("Amonio (NH₃)", "#FF5252", "amonio"),
             ("Nitritos (NO₂)", "#FFB300", "nitrito")],
            0, 1.5, "Ciclo del nitrógeno")
        charts_row.addWidget(self.chart_a)
        charts_row.addWidget(self.chart_b)
        v.addLayout(charts_row, 1)

        sensors.data_changed.connect(self._refresh)
        self._refresh()

    def _refresh(self):
        hist = self._sensors.history()
        self.chart_a.update_data(hist)
        self.chart_b.update_data(hist)