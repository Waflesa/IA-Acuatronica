from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PageHeader(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 6, 2, 14)
        lay.setSpacing(2)
        t = QLabel(title)
        t.setObjectName("heading")
        sub = QLabel(subtitle)
        sub.setObjectName("sub")
        sub.setWordWrap(True)
        lay.addWidget(t)
        lay.addWidget(sub)