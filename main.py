import sys
from PySide6.QtWidgets import QApplication
from gui import MainWindow

def run_app():
    """Runs the PySide6 application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()