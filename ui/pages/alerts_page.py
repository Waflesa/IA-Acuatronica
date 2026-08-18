import datetime

from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from ui.logic import expert
from ui.widgets.header import PageHeader


class AlertsPage(QWidget):
    def __init__(self, sensors):
        super().__init__()
        self._sensors = sensors
        self._log = []

        v = QVBoxLayout(self)
        v.setContentsMargins(26, 18, 26, 18)
        v.setSpacing(12)

        v.addWidget(PageHeader(
            "Centro de Alertas",
            "Toxicidad, fallas mecánicas y protocolos de mitigación"))

        metrics = QHBoxLayout()
        metrics.setSpacing(14)
        self.m_crit = self._metric_card("ALERTAS CRÍTICAS")
        self.m_warn = self._metric_card("ADVERTENCIAS")
        self.m_total = self._metric_card("TOTAL REGISTRADAS")
        metrics.addWidget(self.m_crit[0])
        metrics.addWidget(self.m_warn[0])
        metrics.addWidget(self.m_total[0])
        v.addLayout(metrics)

        self.clear_btn = QPushButton("Limpiar historial de alertas")
        self.clear_btn.clicked.connect(self._clear)
        v.addWidget(self.clear_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea{ background:transparent; border:none; }")
        self.content = QWidget()
        self.content.setStyleSheet("background:transparent;")
        self.content_lay = QVBoxLayout(self.content)
        self.content_lay.setContentsMargins(0, 0, 8, 0)
        self.content_lay.setSpacing(10)
        self.scroll.setWidget(self.content)
        v.addWidget(self.scroll, 1)

        sensors.data_changed.connect(self._update)
        self._update()

    @staticmethod
    def _metric_card(title):
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("cardRange")
        val = QLabel("0")
        val.setObjectName("metricValue")
        v.addWidget(t)
        v.addWidget(val)
        return frame, val

    def _clear(self):
        self._log.clear()
        self._rebuild()

    def _update(self):
        res = expert.diagnosis(self._sensors.values())
        now = datetime.datetime.now().strftime("%H:%M")
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        added = False
        for h in res["hallazgos"]:
            if h["severity"] == "ok":
                continue
            if not any(a["title"] == h["title"] and a.get("_t") == now for a in self._log):
                self._log.append({"_t": now, "time": stamp, **h})
                added = True
        del self._log[:-40]
        if added:
            self._rebuild()
        self._rebuild_metrics()

    def _clear_layout(self):
        while self.content_lay.count():
            item = self.content_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _rebuild(self):
        self._clear_layout()
        if not self._log:
            lbl = QLabel("No hay alertas registradas. El sistema opera en rango seguro.")
            lbl.setObjectName("dxBody")
            lbl.setWordWrap(True)
            self.content_lay.addWidget(lbl)
        else:
            for a in reversed(self._log):
                self.content_lay.addWidget(_alert_card(a))
        self.content_lay.addStretch()
        self._rebuild_metrics()

    def _rebuild_metrics(self):
        crit = sum(1 for a in self._log if a["severity"] == "crit")
        warn = sum(1 for a in self._log if a["severity"] == "warn")
        self.m_crit[1].setText(str(crit))
        self.m_warn[1].setText(str(warn))
        self.m_total[1].setText(str(len(self._log)))


def _alert_card(a):
    sev = a["severity"]
    frame = QFrame()
    frame.setObjectName(f"dx{sev.capitalize()}")
    v = QVBoxLayout(frame)
    v.setContentsMargins(14, 12, 14, 12)
    v.setSpacing(6)

    head = QHBoxLayout()
    head.setSpacing(8)
    title = QLabel(a["title"])
    title.setObjectName("dxTitle")
    time_lbl = QLabel(a.get("time", ""))
    time_lbl.setObjectName("cardRange")
    pill = QLabel(" " + {"warn": "Advertencia", "crit": "Crítico"}[sev] + " ")
    pill.setObjectName(f"pill{sev.capitalize()}")
    head.addWidget(title)
    head.addStretch()
    head.addWidget(time_lbl)
    head.addWidget(pill)
    v.addLayout(head)

    body = QLabel(a.get("message", ""))
    body.setObjectName("dxBody")
    body.setWordWrap(True)
    v.addWidget(body)

    for i, step in enumerate(a.get("protocol", []), 1):
        step_lbl = QLabel(f"{i}. {step}")
        step_lbl.setObjectName("protoStep")
        step_lbl.setWordWrap(True)
        v.addWidget(step_lbl)

    return frame