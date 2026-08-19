import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ui.app_theme import apply, current
from ui.logic.sensors import Sensors
# Importa la clase que maneja la conexión WebSocket con FastAPI
from ui.logic.backend_client import BackendClient 
from ui.main_window import MainWindow
from ui.splash import SplashScreen


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("H2-OBSERVER")
    app.setStyle("Fusion")    
    # 1. Crear el contenedor de sensores
    sensors = Sensors()
    # Instanciar el cliente del backend
    backend_client = BackendClient(sensors)

    window = MainWindow(sensors)
    
    # GUARDAR REFERENCIA EXPLICITA (Evita que Python destruya el socket)
    window.backend_client = backend_client
    apply(app, current())

    # 2. Instanciar el cliente del backend (se conecta solo en el __init__)
    backend_client = BackendClient(sensors)

    # 3. Crear la ventana principal y vincular el cliente para evitar que el Garbage Collector lo elimine
    window = MainWindow(sensors)
    window.backend_client = backend_client

    splash = SplashScreen()

    def on_splash_done():
        window.show()
        splash.close()

    splash.finished.connect(on_splash_done)
    QTimer.singleShot(0, splash.start)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()