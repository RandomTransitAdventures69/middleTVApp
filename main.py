"""MiddleTV: a fullscreen, remote-friendly TV launcher."""
import sys
import traceback
from pathlib import Path


def _excepthook(exc_type, exc_value, exc_tb):
    # PySide6 silently swallows exceptions raised inside Qt callbacks
    # (keyPressEvent, signal handlers, etc.) unless we do this: without it,
    # a bug in there just does nothing instead of showing an error.
    traceback.print_exception(exc_type, exc_value, exc_tb)
    sys.exit(1)


sys.excepthook = _excepthook

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# QtWebEngine (used by the embedded Jellyfin/Flight Tracker screens)
# has to be imported, and this attribute set, before QApplication is
# constructed -- doing it later, even on first use of a web screen, makes
# Chromium's startup hang instead of working.
from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from core import config, theme
from ui.shell import Shell


def main():
    app_dir = Path(sys.argv[0]).resolve().parent
    config_path = app_dir / "config" / "middletv.json"
    cfg = config.load(config_path)

    app = QApplication(sys.argv)
    theme.apply_theme(cfg.ui_theme)
    app.setStyleSheet(theme.STYLESHEET)

    shell = Shell(cfg)
    shell.resize(1280, 720)
    shell.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
