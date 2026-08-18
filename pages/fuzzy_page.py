from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from logic import fuzzy
from logic.sensors import META
from widgets.actuator_bar import ActuatorBar
from widgets.cards import section_card
from widgets.header import PageHeader


class FuzzyPage(QWidget):
    def __init__(self, sensors):
        super().__init__()
        self._sensors = sensors

        v = QVBoxLayout(self)
        v.setContentsMargins(26, 18, 26, 18)
        v.setSpacing(14)

        v.addWidget(PageHeader(
            "Controlador Difuso",
            "Regulación de aireación, calefacción y recirculación · lógica difusa"))

        top = QHBoxLayout()
        top.setSpacing(14)

        cond_frame, cond_lay = section_card("CONDICIONES ACTUALES")
        self.cond_labels = {}
        for sid, m in META.items():
            lbl = QLabel()
            self.cond_labels[sid] = lbl
            cond_lay.addWidget(lbl)

        sp_frame, sp_lay = section_card("SETPOINTS OBJETIVO")
        self.sp_sliders = {}
        self.sp_labels = {}
        specs = [("temp", "Temperatura objetivo (°C)", 20.0, 30.0),
                 ("od", "OD objetivo (mg/L)", 5.0, 8.0),
                 ("ph", "pH objetivo", 6.5, 7.5)]
        inits = {"temp": 26.0, "od": 6.0, "ph": 7.0}
        for key, name, lo, hi in specs:
            row = QHBoxLayout()
            name_lbl = QLabel(name)
            name_lbl.setObjectName("cardRange")
            val_lbl = QLabel()
            val_lbl.setStyleSheet("color:#E6EAEF; font-weight:700; font-size:14px;")
            self.sp_labels[key] = val_lbl
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(int(lo * 10), int(hi * 10))
            s.setValue(int(inits[key] * 10))
            s.valueChanged.connect(self._refresh)
            self.sp_sliders[key] = s
            row.addWidget(name_lbl)
            row.addWidget(val_lbl)
            row.addWidget(s, 1)
            sp_lay.addLayout(row)

        top.addWidget(cond_frame)
        top.addWidget(sp_frame)
        v.addLayout(top)

        out_frame, out_lay = section_card("SALIDAS DEL CONTROLADOR")
        self.bars = {
            "aireacion": ActuatorBar("Aireación"),
            "calefaccion": ActuatorBar("Calefacción"),
            "recirculacion": ActuatorBar("Recirculación"),
        }
        for b in self.bars.values():
            out_lay.addWidget(b)
        v.addWidget(out_frame)

        rules_frame, rules_lay = section_card("REGLAS ACTIVAS")
        self.rules_lbl = QLabel()
        self.rules_lbl.setObjectName("dxBody")
        self.rules_lbl.setWordWrap(True)
        rules_lay.addWidget(self.rules_lbl)
        v.addWidget(rules_frame)
        v.addStretch()

        sensors.data_changed.connect(self._refresh)
        self._refresh()

    def _setpoints(self):
        return {
            "temp": self.sp_sliders["temp"].value() / 10.0,
            "od": self.sp_sliders["od"].value() / 10.0,
            "ph": self.sp_sliders["ph"].value() / 10.0,
        }

    def _refresh(self):
        vals = self._sensors.values()
        for sid, lbl in self.cond_labels.items():
            m = META[sid]
            lbl.setText(f"{m['name']}:   {vals[sid]:.2f} {m['unit']}")

        setpoints = self._setpoints()
        for key, lbl in self.sp_labels.items():
            lbl.setText(f"{self.sp_sliders[key].value() / 10.0:.1f}")

        accion = fuzzy.control_action(vals, setpoints)
        for k, bar in self.bars.items():
            bar.set_value(accion[k])

        reglas = fuzzy.active_rules(vals, setpoints)
        self.rules_lbl.setText("\n".join("• " + r for r in reglas))