import app_theme
from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget


class LineChartWidget(QWidget):
    """Gráfico de líneas QtCharts con tema claro/oscuro y eje temporal."""

    def __init__(self, specs, ymin, ymax, title, parent=None):
        super().__init__(parent)
        self._specs = specs  # [(nombre, color_hex, clave), ...]
        self._ymin = ymin
        self._ymax = ymax
        self._rows = []
        self._pal = app_theme.palette(app_theme.current())

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)

        self._chart = QChart()
        self._chart.setBackgroundBrush(QColor(self._pal["card"]))
        self._chart.setTitle(title)
        self._chart.setTitleBrush(QColor(self._pal["text"]))
        self._chart.setTitleFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        legend = self._chart.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend.setLabelColor(QColor(self._pal["sub"]))

        self._view = QChartView(self._chart)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setBackgroundBrush(QColor(self._pal["card"]))
        self._view.setMinimumHeight(270)
        v.addWidget(self._view)

    def set_theme(self, mode):
        self._pal = app_theme.palette(mode)
        self._chart.setBackgroundBrush(QColor(self._pal["card"]))
        self._chart.setTitleBrush(QColor(self._pal["text"]))
        self._chart.legend().setLabelColor(QColor(self._pal["sub"]))
        self._view.setBackgroundBrush(QColor(self._pal["card"]))
        if self._rows:
            self.update_data(self._rows)

    def update_data(self, rows):
        self._rows = rows
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
        axis_x.setLabelsColor(QColor(self._pal["sub"]))
        axis_x.setGridLineColor(QColor(self._pal["grid"]))
        axis_x.setLinePen(QPen(QColor(self._pal["grid"])))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QValueAxis()
        axis_y.setRange(self._ymin, self._ymax)
        axis_y.setLabelFormat("%.1f")
        axis_y.setLabelsColor(QColor(self._pal["sub"]))
        axis_y.setGridLineColor(QColor(self._pal["grid"]))
        axis_y.setLinePen(QPen(QColor(self._pal["grid"])))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        for line in series:
            line.attachAxis(axis_x)
            line.attachAxis(axis_y)