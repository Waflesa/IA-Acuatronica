from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget


class LineChartWidget(QWidget):
    """Gráfico de líneas QtCharts con tema oscuro y eje temporal."""

    def __init__(self, specs, ymin, ymax, title, parent=None):
        super().__init__(parent)
        self._specs = specs  # [(nombre, color_hex, clave), ...]
        self._ymin = ymin
        self._ymax = ymax

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)

        self._chart = QChart()
        self._chart.setBackgroundBrush(QColor("#141A21"))
        self._chart.setTitle(title)
        self._chart.setTitleBrush(QColor("#E6EAEF"))
        self._chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        legend = self._chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setLabelColor(QColor("#B9C2CB"))

        self._view = QChartView(self._chart)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setMinimumHeight(270)
        v.addWidget(self._view)

    def update_data(self, rows):
        chart = self._chart
        for s in list(chart.series()):
            chart.removeSeries(s)
        for ax in list(chart.axes()):
            chart.removeAxis(ax)
        if not rows:
            return

        series = []
        for name, color, key in self._specs:
            line = QLineSeries()
            line.setName(name)
            line.setColor(QColor(color))
            line.setPen(QPen(QColor(color), 2))
            for r in rows:
                line.append(r["dt"].toMSecsSinceEpoch(), float(r[key]))
            chart.addSeries(line)
            series.append(line)

        t0 = rows[0]["dt"].toMSecsSinceEpoch()
        t1 = rows[-1]["dt"].toMSecsSinceEpoch()
        if t1 - t0 < 1000:
            t1 = t0 + 1000

        axis_x = QDateTimeAxis()
        axis_x.setFormat("HH:mm:ss")
        axis_x.setTickCount(min(6, len(rows) + 1))
        axis_x.setRange(QDateTime.fromMSecsSinceEpoch(t0), QDateTime.fromMSecsSinceEpoch(t1))
        axis_x.setLabelsColor(QColor("#7E8B9A"))
        axis_x.setGridLineColor(QColor("#202A34"))
        axis_x.setLinePen(QPen(QColor("#202A34")))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QValueAxis()
        axis_y.setRange(self._ymin, self._ymax)
        axis_y.setLabelFormat("%.1f")
        axis_y.setLabelsColor(QColor("#7E8B9A"))
        axis_y.setGridLineColor(QColor("#202A34"))
        axis_y.setLinePen(QPen(QColor("#202A34")))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        for line in series:
            line.attachAxis(axis_x)
            line.attachAxis(axis_y)