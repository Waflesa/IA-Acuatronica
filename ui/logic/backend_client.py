import json
import os

from PySide6.QtCore import QObject, QTimer, QUrl, Signal
from PySide6.QtWebSockets import QWebSocket

MAPEO_SENSORES = {
    "temperature": "temp",
    "dissolved_oxygen": "od",
    "ammonia": "amonio",
    "nitrite": "nitrito",
    "ph": "ph",
}

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
    """Cliente WebSocket para la comunicación en tiempo real con FastAPI."""

    status_changed = Signal(str)

    def __init__(self, sensors, parent=None):
        super().__init__(parent)
        self._sensors = sensors
        self._url = os.environ.get("H2O_BACKEND_URL", "ws://127.0.0.1:8000/ws/telemetry")
        self._state = "off"
        self._last = None

        self._ws = QWebSocket(parent=self)
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
        if self._state != "on":
            print(f"[BackendClient] Intentando conectar a {self._url} ...")
            self._set_state("connecting")
            self._ws.open(QUrl(self._url))

    def disconnect_backend(self):
        self._ws.close()
        if hasattr(self._sensors, "set_live"):
            self._sensors.set_live(False)
        self._set_state("off")
        self._retry.start()

    def telemetry(self):
        return self._last

    def actuators(self):
        return self._last.get("actuators") if self._last else None

    def diagnosis(self):
        return self._last.get("diagnosis") if self._last else None

    # ---- Métodos Internos ----
    def _set_state(self, state):
        if self._state != state:
            self._state = state
            self.status_changed.emit(state)

    def _auto_retry(self):
        if self._state != "on":
            self.connect_backend()

    def _on_connected(self):
        print("[BackendClient] ¡Conexión WebSocket establecida con éxito!")
        self._retry.stop()
        self._set_state("on")
        if hasattr(self._sensors, "set_live"):
            self._sensors.set_live(True)

    def _on_disconnected(self):
        print("[BackendClient] WebSocket desconectado.")
        if hasattr(self._sensors, "set_live"):
            self._sensors.set_live(False)
        self._set_state("off")
        if not self._retry.isActive():
            self._retry.start()

    def _on_error(self, error):
        print(f"[BackendClient] Error en WebSocket: {error} ({self._ws.errorString()})")
        if hasattr(self._sensors, "set_live"):
            self._sensors.set_live(False)
        self._set_state("error")
        if not self._retry.isActive():
            self._retry.start()

    def _on_message(self, text):
        """Procesa los mensajes JSON que llegan continuamente del servidor."""
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

        if hasattr(self._sensors, "record"):
            self._sensors.record()
        if hasattr(self._sensors, "data_changed"):
            self._sensors.data_changed.emit()