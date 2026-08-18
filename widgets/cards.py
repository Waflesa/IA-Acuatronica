from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


def section_card(title):
    """Contenedor tipo tarjeta con encabezado. Devuelve (frame, layout_interior)."""
    frame = QFrame()
    frame.setObjectName("card")
    v = QVBoxLayout(frame)
    v.setContentsMargins(16, 14, 16, 14)
    v.setSpacing(10)
    h = QLabel(title)
    h.setStyleSheet("color:#8794A3; font-size:12px; font-weight:700;")
    v.addWidget(h)
    return frame, v