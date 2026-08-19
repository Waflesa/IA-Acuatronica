import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ui.app_theme import apply, current
from ui.logic.backend_server import start_backend_if_needed, stop_backend
from ui.logic.sensors import Sensors
from ui.main_window import MainWindow
from ui.splash import SplashScreen


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("H2-OBSERVER")
    app.setStyle("Fusion")

    apply(app, current())

    backend_proc = start_backend_if_needed()

    sensors = Sensors()
    window = MainWindow(sensors)
    splash = SplashScreen()

    def on_splash_done():
        window.show()
        splash.close()

    splash.finished.connect(on_splash_done)
    splash.start(ready_check=lambda: window._client.state() == "on")

    app.aboutToQuit.connect(lambda: stop_backend(backend_proc))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()