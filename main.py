#!/usr/bin/env python3
"""Entry point for the Bulk Email Sender application."""

import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Bulk Email Sender")
    app.setOrganizationName("ResendMailer")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
