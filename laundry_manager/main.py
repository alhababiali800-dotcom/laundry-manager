"""
International Laundries — Desktop Management System
Entry point: python main.py
"""
import sys
import os
import traceback
import logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from database.schema import initialize_database
from utils.i18n import init_language, tr
from views.login_window import LoginWindow
from PyQt6.QtGui import QPalette, QColor
from views.main_window import MainWindow


# Global references - prevents garbage collection
_login_win = None
_main_win = None

def show_login():
    global _login_win, _main_win
    _main_win = None  # release old window
    _login_win = LoginWindow()
    _login_win.login_successful.connect(on_login)
    # Center on screen
    screen = QApplication.primaryScreen().geometry()
    _login_win.move(
        (screen.width()  - _login_win.width())  // 2,
        (screen.height() - _login_win.height()) // 2,
    )
    _login_win.show()

def on_login(user):
    global _login_win, _main_win
    _login_win.hide()
    _main_win = MainWindow(user, on_logout=show_login)
    _main_win.showMaximized()

def setup_crash_logger():
    """Write all unhandled exceptions to a log file next to the app."""
    if os.name == 'nt':
        log_dir = Path(os.environ.get('APPDATA', Path.home())) / 'InternationalLaundries'
    else:
        log_dir = Path.home() / '.international_laundries'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'crash.log'

    logging.basicConfig(
        filename=str(log_file),
        level=logging.ERROR,
        format='%(asctime)s  %(levelname)s\n%(message)s\n' + '-'*60,
    )

    def handle_exception(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logging.error("Unhandled exception:\n%s", error_msg)
        # Also show a dialog so the user knows what happened
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(tr("unexpected_error"))
        msg.setText(tr("unexpected_error_message"))
        msg.setDetailedText(error_msg)
        msg.setInformativeText(tr("details_saved", path=log_file))
        msg.exec()

    sys.excepthook = handle_exception
    return log_file


def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")          # ← السطر الجديد
    app.setApplicationName("International Laundries")

    log_file = setup_crash_logger()
    init_language()

    try:
        initialize_database()
    except Exception as e:
        QMessageBox.critical(None, tr("database_error"), tr("database_init_failed", error=e))
        sys.exit(1)

    show_login()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
