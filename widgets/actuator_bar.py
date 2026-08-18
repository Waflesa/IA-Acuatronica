from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

FILL = "#00E676"


class ActuatorBar(QWidget):
    def __init__(self, title, fill=FILL):
        super().__init__()
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(5)

        row = QHBoxLayout()
        name = QLabel(title)
        name.setStyleSheet("color:#E6EAEF; font-weight:700; font-size:13px;")
        self.pct = QLabel("0%")
        self.pct.setStyleSheet("color:#E6EAEF; font-weight:700; font-size:14px;")
        row.addWidget(name)
        row.addStretch()
        row.addWidget(self.pct)
        v.addLayout(row)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setFixedHeight(6)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(
            "QProgressBar { background:#202A34; border:none; border-radius:3px; }"
            f"QProgressBar::chunk {{ border-radius:3px; background:{fill}; }}"
        )
        v.addWidget(self.bar)

    def set_value(self, pct):
        self.bar.setValue(int(round(pct)))
        self.pct.setText(f"{pct:.0f}%")