"""Application entry point."""
from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

    from PyQt6.QtWidgets import QApplication
    from gda_table_gen.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
