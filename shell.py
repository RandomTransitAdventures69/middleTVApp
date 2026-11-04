"""The shell owns the window, the screen back-stack, and global key
handling. Esc always goes back, no matter what screen is showing --
every screen gets that for free and none of them can override it.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from core.config import Config


class Shell(QMainWindow):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.setWindowTitle("MiddleTV")

        # A screen pushed on top must not destroy the one underneath it --
        # QMainWindow.setCentralWidget() would do exactly that, since it
        # deletes whatever it replaces. QStackedWidget instead keeps every
        # screen alive and just switches which one is visible, which is
        # what a back-stack needs.
        self._stacked = QStackedWidget()
        super().setCentralWidget(self._stacked)
        self._stack: list = []

        # Application-wide context: Esc must go back even when an embedded
        # web view (Jellyfin, YouTube...) has keyboard focus, not just when
        # one of our own widgets does.
        back_shortcut = QShortcut(QKeySequence("Esc"), self)
        back_shortcut.setContext(Qt.ApplicationShortcut)
        back_shortcut.activated.connect(self.pop)

        # Shown first, every launch: "who's watching?" before the home screen.
        from ui.profiles import ProfileSwitcher
        self.push(ProfileSwitcher(self, is_initial=True))

    def push(self, screen) -> None:
        self._stack.append(screen)
        self._stacked.addWidget(screen)
        self._render()

    def pop(self) -> None:
        if len(self._stack) <= 1:
            return
        old = self._stack.pop()
        self._render()
        self._stacked.removeWidget(old)
        old.deleteLater()

    def _render(self) -> None:
        screen = self._stack[-1]
        self._stacked.setCurrentWidget(screen)
        screen.setFocus()
        if hasattr(screen, "on_shown"):
            screen.on_shown()
