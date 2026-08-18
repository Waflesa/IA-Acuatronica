from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QSlider, QVBoxLayout

from ui.logic.sensors import STATUS_LABEL
from ui.widgets.gauge import Gauge
from ui.widgets.util import repolish


class SensorCard(QFrame):
    """Tarjeta de sensor: gauge, valor, estado y controles de simulación."""

    def __init__(self, sid, meta, sensors):
        super().__init__()
        self.setObjectName("card")
        self._sid = sid
        self._meta = meta
        self._sensors = sensors

        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(6)

        head = QHBoxLayout()
        head.setSpacing(8)
        self.name_lbl = QLabel(meta["name"])
        self.name_lbl.setObjectName("cardName")
        self.pill = QLabel()
        head.addWidget(self.name_lbl)
        head.addStretch()
        head.addWidget(self.pill)
        v.addLayout(head)

        self.gauge = Gauge()
        v.addWidget(self.gauge, alignment=Qt.AlignmentFlag.AlignHCenter)

        val_row = QHBoxLayout()
        val_row.setSpacing(6)
        self.value_lbl = QLabel()
        self.value_lbl.setObjectName("cardValue")
        unit_lbl = QLabel(meta["unit"])
        unit_lbl.setObjectName("cardUnit")
        val_row.addWidget(self.value_lbl)
        val_row.addWidget(unit_lbl, alignment=Qt.AlignmentFlag.AlignBottom)
        v.addLayout(val_row)

        rng = QLabel(f"Óptimo: {meta['opt'][0]:g}–{meta['opt'][1]:g} {meta['unit']}")
        rng.setObjectName("cardRange")
        v.addWidget(rng)

        self.drift_chk = QCheckBox("Simular deriva")
        v.addWidget(self.drift_chk)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(meta["low"] * 100), int(meta["high"] * 100))
        v.addWidget(self.slider)

        self.drift_chk.toggled.connect(self._on_drift_toggled)
        self.slider.valueChanged.connect(self._on_slider)

        self.refresh()

    def _on_drift_toggled(self, on):
        self._sensors.set_drift(self._sid, on)
        self.slider.setEnabled(on)
        self.slider.blockSignals(True)
        self.slider.setValue(int(self._sensors.value(self._sid) * 100))
        self.slider.blockSignals(False)

    def _on_slider(self, v):
        self._sensors.set_value(self._sid, v / 100.0)
        self._sensors.set_drift(self._sid, False)
        self.drift_chk.blockSignals(True)
        self.drift_chk.setChecked(False)
        self.drift_chk.blockSignals(False)
        self.refresh()

    def refresh(self):
        v = self._sensors.value(self._sid)
        st = self._sensors.status(self._sid)
        m = self._meta
        frac = (v - m["low"]) / (m["high"] - m["low"])

        self.gauge.set_value(frac, st)
        self.value_lbl.setText(f"{v:.2f}")

        self.pill.setText(" " + STATUS_LABEL[st] + " ")
        self.pill.setObjectName(f"pill{st.capitalize()}")
        repolish(self.pill)

        drift = self._sensors.is_drift(self._sid)
        self.drift_chk.blockSignals(True)
        self.drift_chk.setChecked(drift)
        self.drift_chk.blockSignals(False)
        self.slider.setEnabled(drift)
        self.slider.blockSignals(True)
        self.slider.setValue(int(v * 100))
        self.slider.blockSignals(False)