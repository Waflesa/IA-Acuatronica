import ctypes
import os

from PySide6.QtCore import QSettings

from paths import base_dir

DARK = "dark"
LIGHT = "light"

ROOT = base_dir()

PALETTE = {
    DARK: {
        "app": "#0E141B",
        "surface": "#0A0F15",
        "card": "#111A24",
        "border": "#22303F",
        "text": "#E8EEF4",
        "sub": "#8B98A7",
        "accent": "#3D9BFF",
        "warn": "#E6A23C",
        "crit": "#E35B5B",
        "grid": "#1E2A38",
        "track": "#22303F",
    },
    LIGHT: {
        "app": "#EEF2F6",
        "surface": "#FFFFFF",
        "card": "#FFFFFF",
        "border": "#D7DEE6",
        "text": "#1B2632",
        "sub": "#67737F",
        "accent": "#2E86DE",
        "warn": "#D98324",
        "crit": "#D64545",
        "grid": "#E2E8EF",
        "track": "#D7DEE6",
    },
}


def palette(mode):
    return PALETTE.get(mode, PALETTE[DARK])


def qss(mode):
    path = os.path.join(ROOT, f"styles_{mode}.qss")
    if not os.path.exists(path):
        path = os.path.join(ROOT, "styles_dark.qss")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def apply(app, mode):
    app.setStyleSheet(qss(mode))


def current():
    return QSettings("H2-OBSERVER", "H2-OBSERVER").value("theme", DARK)


def save(mode):
    QSettings("H2-OBSERVER", "H2-OBSERVER").setValue("theme", mode)


def toggle(mode):
    return LIGHT if mode == DARK else DARK


def apply_titlebar(hwnd, mode):
    """Pinta la barra de título nativa de Windows con el color del tema (DWM)."""
    try:
        dwm = ctypes.windll.dwmapi
        dark = mode == DARK
        on = ctypes.c_int(1 if dark else 0)
        dwm.DwmSetWindowAttribute(ctypes.c_void_p(hwnd), 20,
                                  ctypes.byref(on), ctypes.sizeof(on))
        col = palette(mode)["surface"]
        r = int(col[1:3], 16)
        g = int(col[3:5], 16)
        b = int(col[5:7], 16)
        cref = ctypes.c_uint32(b | (g << 8) | (r << 16))  # COLORREF 0x00BBGGRR
        dwm.DwmSetWindowAttribute(ctypes.c_void_p(hwnd), 35,
                                  ctypes.byref(cref), ctypes.sizeof(cref))
    except Exception:
        pass
