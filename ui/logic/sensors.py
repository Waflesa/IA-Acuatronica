"""Modelo de sensores del módulo acuapónico.

Los valores provienen del backend real vía WebSocket (BackendClient). Este
modelo solo recibe y almacena las lecturas para que las páginas las consuman;
no genera valores aleatorios, se queda a la espera del backend.
"""

import random

from PySide6.QtCore import QDateTime, QObject, QTimer, Signal

META = {
    "ph": {
        "name": "pH", "unit": "pH",
        "low": 5.5, "high": 8.5, "opt": (6.5, 7.5), "warn": (6.0, 8.0),
        "step": 0.02, "init": 6.92,
    },
    "temp": {
        "name": "Temperatura", "unit": "°C",
        "low": 15.0, "high": 35.0, "opt": (24.0, 28.0), "warn": (20.0, 32.0),
        "step": 0.15, "init": 26.3,
    },
    "od": {
        "name": "Oxígeno Disuelto", "unit": "mg/L",
        "low": 0.0, "high": 12.0, "opt": (5.0, 8.0), "warn": (4.0, 9.0),
        "step": 0.10, "init": 6.4,
    },
    "amonio": {
        "name": "Amonio (NH₃)", "unit": "mg/L",
        "low": 0.0, "high": 3.0, "opt": (0.0, 0.5), "warn": (0.5, 1.0),
        "step": 0.02, "init": 0.28,
    },
    "nitrito": {
        "name": "Nitritos (NO₂)", "unit": "mg/L",
        "low": 0.0, "high": 3.0, "opt": (0.0, 0.5), "warn": (0.5, 1.0),
        "step": 0.02, "init": 0.22,
    },
    "flujo": {
        "name": "Flujo recirculación", "unit": "L/min",
        "low": 0.0, "high": 30.0, "opt": (8.0, 15.0), "warn": (6.0, 20.0),
        "step": 0.30, "init": 11.5,
    },
}

STATUS_LABEL = {"ok": "ÓPTIMO", "warn": "ADVERTENCIA", "crit": "CRÍTICO"}


def classify(value, opt, warn):
    if opt[0] <= value <= opt[1]:
        return "ok"
    if warn[0] <= value <= warn[1]:
        return "warn"
    return "crit"


class Sensors(QObject):
    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._values = {k: m["init"] for k, m in META.items()}
        self._drift = {k: True for k in META}
        self._history = []
        self._interval = 1000
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)

    def set_interval(self, ms):
        self._interval = max(ms, 250)

    def set_live(self, on):
        """Modo live: los valores los escribe el backend (sin simulación aleatoria)."""
        if on:
            self._timer.stop()

    def is_live(self):
        return not self._timer.isActive()

    def values(self):
        return dict(self._values)

    def value(self, sid):
        return self._values[sid]

    def set_value(self, sid, v):
        m = META[sid]
        self._values[sid] = min(max(v, m["low"]), m["high"])

    def set_drift(self, sid, on):
        self._drift[sid] = on

    def is_drift(self, sid):
        return self._drift[sid]

    def status(self, sid):
        m = META[sid]
        return classify(self._values[sid], m["opt"], m["warn"])

    def history(self):
        return list(self._history)

    def record(self):
        """Guarda una lectura en el historial (lo invoca el backend en cada telemetría)."""
        self._history.append({"dt": QDateTime.currentDateTime(), **{k: self._values[k] for k in META}})
        del self._history[:-120]

    def _step(self):
        for sid, m in META.items():
            if self._drift[sid]:
                v = self._values[sid] + random.uniform(-m["step"], m["step"])
                self.set_value(sid, v)
        self.record()
        self.data_changed.emit()