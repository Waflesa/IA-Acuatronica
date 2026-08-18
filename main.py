import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from logic.sensors import Sensors
from main_window import MainWindow
from splash import SplashScreen

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("H2-OBSERVER")
    app.setStyle("Fusion")

    qss_path = os.path.join(ROOT, "styles.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    sensors = Sensors()
    window = MainWindow(sensors)
    splash = SplashScreen()

    def on_splash_done():
        window.show()
        splash.close()

    splash.finished.connect(on_splash_done)
    QTimer.singleShot(0, splash.start)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()