"""Arranque y parada del backend FastAPI como subproceso de la app.

Si el puerto 8000 ya responde con nuestro backend, no se lanza otro; solo se
usa. En caso contrario se levanta ``uvicorn backend.main:app`` con el mismo
intérprete de Python (para que funcione el doble clic al acceso directo).
"""

import os
import subprocess
import sys
import urllib.request

from ui.paths import base_dir

HEALTH_URL = "http://127.0.0.1:8000/"
LOG_PATH = os.path.join(base_dir(), "backend", "server.log")


def backend_already_running():
    """True si el backend ya responde en el puerto 8000."""
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=0.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def start_backend_if_needed():
    """Lanza uvicorn si el backend no está activo. Devuelve el Popen (o None)."""
    if backend_already_running():
        return None

    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    log = open(LOG_PATH, "a", encoding="utf-8")
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app",
             "--host", "127.0.0.1", "--port", "8000"],
            cwd=base_dir(),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=flags,
        )
    except Exception:
        log.close()
        return None
    return proc


def stop_backend(proc):
    """Detiene el subproceso si sigue vivo (solo si esta instancia lo lanzó)."""
    if proc is None:
        return
    try:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    except Exception:
        pass