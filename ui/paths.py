import os
import sys


def base_dir():
    """Directorio base de la app: raíz del proyecto o _MEIPASS si está empaquetada."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))