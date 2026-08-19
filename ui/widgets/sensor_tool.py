from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QSlider, QVBoxLayout

from ui.logic.sensors import STATUS_LABEL
from ui.widgets.util import repolish


class SensorTool(QFrame):
    """Lectura de sensor compacta (estilo herramienta de panel superior)."""

    def __init__(self, sid, meta, sensors):
        super().__init__()
        self.setObjectName("toolGroup")
        self._sid = sid
        self._meta = meta
        self._sensors = sensors

        v = QVBoxLayout(self)
        v.setContentsMargins(6, 5, 6, 5)
        v.setSpacing(2)

        head = QHBoxLayout()
        head.setSpacing(6)
        name = QLabel(meta["name"].upper())
        name.setObjectName("toolCap")
        self.pill = QLabel()
        head.addWidget(name)
        head.addStretch()
        head.addWidget(self.pill)
        v.addLayout(head)

        val_row = QHBoxLayout()
        val_row.setSpacing(4)
        self.value_lbl = QLabel()
        self.value_lbl.setObjectName("toolValue")
        unit = QLabel(meta["unit"])
        unit.setObjectName("cardUnit")
        val_row.addWidget(self.value_lbl)
        val_row.addWidget(unit, alignment=Qt.AlignmentFlag.AlignBottom)
        v.addLayout(val_row)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(meta["low"] * 100), int(meta["high"] * 100))
        self.slider.setFixedHeight(14)
        v.addWidget(self.slider)

        self.drift_chk = QCheckBox("Simular deriva")
        v.addWidget(self.drift_chk)

        self.drift_chk.toggled.connect(self._on_drift)
        self.slider.valueChanged.connect(self._on_slider)
        self.refresh()

    def _on_drift(self, on):
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

        self.value_lbl.setText(f"{v:.2f}")
        self.pill.setText(" " + STATUS_LABEL[st] + " ")
        self.pill.setObjectName(f"pill{st.capitalize()}")
        repolish(self.pill)

        drift = self._sensors.is_drift(self._sid)
        live = self._sensors.is_live()
        self.drift_chk.blockSignals(True)
        self.drift_chk.setChecked(drift)
        self.drift_chk.blockSignals(False)
        self.drift_chk.setEnabled(not live)
        self.slider.setEnabled(drift and not live)
        self.slider.blockSignals(True)
        self.slider.setValue(int(v * 100))
        self.slider.blockSignals(False)