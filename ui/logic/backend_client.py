"""Cliente del backend Acuatrónica (FastAPI) vía WebSocket.

Recibe el paquete de telemetría {"sensors", "actuators", "diagnosis", "mode"}
y lo integra con el modelo de sensores del frontend para que la app use el
motor IA real del backend (RandomForest + motor de reglas).

URL por defecto: ws://127.0.0.1:8000/ws/telemetry (se puede sobreescribir con
la variable de entorno H2O_BACKEND_URL).
"""

import json
import os

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtWebSockets import QWebSocket

DEFAULT_URL = os.environ.get("H2O_BACKEND_URL", "ws://127.0.0.1:8000/ws/telemetry")

# backend (dataset limpio) -> claves del frontend (ui.logic.sensors.META)
MAPEO_SENSORES = {
    "temperature": "temp",
    "dissolved_oxygen": "od",
    "ammonia": "amonio",
    "nitrite": "nitrito",
    "ph": "ph",
}

# backend (actuadores %) -> claves del frontend (página fuzzy)
MAPEO_ACTUADORES = {
    "aeration_rate": "aireacion",
    "heating_power": "calefaccion",
    "recirculation_flow": "recirculacion",
}

_NIVEL = {"CRITICAL": "crit", "WARNING": "warn", "OPTIMAL": "ok"}
_CALIDAD = {"Buena": "ok", "Moderada": "warn", "Mala": "crit"}


def backend_diagnosis_to_hallazgos(dx):
    """Convierte el diagnóstico del backend al formato de las páginas del frontend."""
    hallazgos = []
    wq = (dx.get("water_quality") or "").split("/")[0].strip()
    if wq:
        hallazgos.append({
            "severity": _CALIDAD.get(wq, "ok"),
            "title": f"Calidad del agua (ML): {wq}",
            "message": "Clasificación del modelo de aprendizaje automático sobre las variables fisicoquímicas.",
            "protocol": [],
        })
    alerts = dx.get("alerts") or []
    protocols = dx.get("protocols") or []
    for i, al in enumerate(alerts):
        a_sev = "crit" if any(
            k in al.lower() for k in ("crit", "toxicidad", "emergencia", "amonio",
                                      "nitrito", "oxigeno", "falla")
        ) else "warn"
        hallazgos.append({
            "severity": a_sev,
            "title": al,
            "message": "",
            "protocol": protocols if i == 0 else [],
        })
    if not hallazgos:
        hallazgos.append({
            "severity": "ok",
            "title": "Sin alertas activas",
            "message": "Parámetros dentro de rango según el motor del backend.",
            "protocol": [],
        })
    nivel = _NIVEL.get(dx.get("status"), "ok")
    if any(h["severity"] == "crit" for h in hallazgos):
        nivel = "crit"
    elif any(h["severity"] == "warn" for h in hallazgos):
        nivel = "warn"
    return {"nivel_general": nivel, "hallazgos": hallazgos}


class BackendClient(QObject):
    """Conexión automática con el backend vía WebSocket.

    Se conecta al iniciar y, si el backend no está activo, reintenta cada 3 s
    para quedar conectado en cuanto esté disponible. Estados:
    off | connecting | on | error.
    """

    status_changed = Signal(str)

    def __init__(self, sensors, parent=None):
        super().__init__(parent)
        self._sensors = sensors
        self._url = DEFAULT_URL
        self._state = "off"
        self._last = None
        self._ws = QWebSocket()
        self._ws.connected.connect(self._on_connected)
        self._ws.disconnected.connect(self._on_disconnected)
        self._ws.errorOccurred.connect(self._on_error)
        self._ws.textMessageReceived.connect(self._on_message)
        self._retry = QTimer(self)
        self._retry.setInterval(3000)
        self._retry.timeout.connect(self._auto_retry)
        self.connect_backend()

    def state(self):
        return self._state

    def is_connected(self):
        return self._state == "on"

    def url(self):
        return self._url

    def toggle(self):
        if self.is_connected():
            self.disconnect_backend()
        else:
            self.connect_backend()

    def connect_backend(self):
        self._set_state("connecting")
        self._ws.open(QUrl(self._url))

    def disconnect_backend(self):
        self._ws.close()
        self._sensors.set_live(False)
        self._set_state("off")
        self._retry.start()

    def telemetry(self):
        return self._last

    def actuators(self):
        return self._last.get("actuators") if self._last else None

    def diagnosis(self):
        return self._last.get("diagnosis") if self._last else None

    # ---- internos ----
    def _set_state(self, state):
        if self._state != state:
            self._state = state
            self.status_changed.emit(state)

    def _auto_retry(self):
        if self._state != "on":
            self.connect_backend()

    def _on_connected(self):
        self._retry.stop()
        self._set_state("on")
        self._sensors.set_live(True)

    def _on_disconnected(self):
        self._sensors.set_live(False)
        if self._state == "on":
            self._set_state("off")
        if self._state != "on":
            self._retry.start()

    def _on_error(self, error):
        self._sensors.set_live(False)
        self._set_state("error")
        self._retry.start()
        self._ws.abort()

    def _on_message(self, text):
        try:
            packet = json.loads(text)
        except (ValueError, TypeError):
            return
        self._last = packet
        sens = packet.get("sensors") or {}
        for bk, fk in MAPEO_SENSORES.items():
            v = sens.get(bk)
            if v is not None:
                try:
                    self._sensors.set_value(fk, float(v))
                except (TypeError, ValueError):
                    pass
        self._sensors.record()
        self._sensors.data_changed.emit()