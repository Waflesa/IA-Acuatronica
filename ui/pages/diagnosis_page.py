from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from ui.logic import expert
from ui.widgets.header import PageHeader
from ui.widgets.util import repolish


class DiagnosisPage(QWidget):
    def __init__(self, sensors):
        super().__init__()
        self._sensors = sensors
        self._sig = ""

        v = QVBoxLayout(self)
        v.setContentsMargins(26, 18, 26, 18)
        v.setSpacing(12)

        v.addWidget(PageHeader(
            "Sistema Experto de Diagnóstico",
            "Reglas simbólicas sobre patrones de calidad del agua · mitigación automática"))

        top = QHBoxLayout()
        top.setSpacing(12)
        self.overall = QLabel()
        self.overall.setObjectName("pillOk")
        self.caption = QLabel("")
        self.caption.setObjectName("sub")
        top.addWidget(self.overall)
        top.addWidget(self.caption)
        top.addStretch()
        v.addLayout(top)

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

        sensors.data_changed.connect(self._refresh)
        self._refresh()

    def _refresh(self):
        res = expert.diagnosis(self._sensors.values())
        sig = res["nivel_general"] + "|" + "|".join(
            f"{h['severity']}{h['title']}" for h in res["hallazgos"])
        if sig != self._sig or self.content_lay.count() == 0:
            self._sig = sig
            self._rebuild(res)

    def _clear(self):
        while self.content_lay.count():
            item = self.content_lay.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _rebuild(self, res):
        self._clear()
        nivel = res["nivel_general"]
        label = {"ok": "SISTEMA ESTABLE", "warn": "ATENCIÓN", "crit": "ACCIÓN REQUERIDA"}[nivel]
        self.overall.setText(" " + label + " ")
        self.overall.setObjectName(f"pill{nivel.capitalize()}")
        repolish(self.overall)
        self.caption.setText(f"Diagnóstico sobre {len(res['hallazgos'])} variables evaluadas")

        for h in res["hallazgos"]:
            self.content_lay.addWidget(_dx_card(h))
        self.content_lay.addStretch()


def _dx_card(h):
    sev = h["severity"]
    frame = QFrame()
    frame.setObjectName(f"dx{sev.capitalize()}")
    v = QVBoxLayout(frame)
    v.setContentsMargins(14, 12, 14, 12)
    v.setSpacing(6)

    head = QHBoxLayout()
    head.setSpacing(8)
    title = QLabel(h["title"])
    title.setObjectName("dxTitle")
    pill = QLabel(" " + {"ok": "Estable", "warn": "Advertencia", "crit": "Crítico"}[sev] + " ")
    pill.setObjectName(f"pill{sev.capitalize()}")
    head.addWidget(title)
    head.addStretch()
    head.addWidget(pill)
    v.addLayout(head)

    body = QLabel(h.get("message", ""))
    body.setObjectName("dxBody")
    body.setWordWrap(True)
    v.addWidget(body)

    for i, step in enumerate(h.get("protocol", []), 1):
        step_lbl = QLabel(f"{i}. {step}")
        step_lbl.setObjectName("protoStep")
        step_lbl.setWordWrap(True)
        v.addWidget(step_lbl)

    return frame