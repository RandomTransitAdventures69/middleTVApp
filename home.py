from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy,
)

from core import theme
from ui.instruments import IlluminatedButton, StatusLED

HOME_COLS = 4
PROFILE_SELECTION = -1


class Home(QWidget):
    """The tile grid screen: the first thing MiddleTV shows after picking a
    profile -- the control panel's main face. Everything here -- the grid
    and the profile button -- is reachable with just the arrow keys,
    Enter, and Esc, since there's no mouse on a TV remote.
    """

    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.tiles: list[IlluminatedButton] = []
        self.selected = 0
        self.setFocusPolicy(Qt.StrongFocus)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 28)
        outer.setSpacing(20)

        header = QHBoxLayout()
        header.setSpacing(10)
        self._power_led = StatusLED(theme.GREEN, lit=True)
        header.addWidget(self._power_led)
        heading = QLabel("MIDDLETV")
        heading.setObjectName("heading")
        header.addWidget(heading)
        header.addStretch()

        self.profile_btn = IlluminatedButton("PROFILE: " + self.shell.config.active_profile_obj().name.upper())
        self.profile_btn.clicked.connect(self._open_profiles)
        header.addWidget(self.profile_btn)
        outer.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(18)
        self.tiles = []
        for i, app in enumerate(self.shell.config.apps):
            btn = IlluminatedButton(app.name.upper())
            btn.setMinimumSize(220, 140)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.clicked.connect(lambda checked=False, a=app: self._activate(a))
            grid.addWidget(btn, i // HOME_COLS, i % HOME_COLS)
            self.tiles.append(btn)
        outer.addLayout(grid)
        outer.addStretch()

        self._highlight()

    def on_shown(self):
        # the profile name may have changed since this screen was built
        self.profile_btn.setText("PROFILE: " + self.shell.config.active_profile_obj().name.upper())

    def _highlight(self):
        # Buttons use Qt.NoFocus: keyboard focus stays on this Home widget
        # so keyPressEvent below is the single source of truth for
        # navigation; set_selected() just drives the glow.
        for i, t in enumerate(self.tiles):
            t.set_selected(i == self.selected)
        self.profile_btn.set_selected(self.selected == PROFILE_SELECTION)

    def _open_profiles(self):
        from ui.profiles import ProfileSwitcher
        self.shell.push(ProfileSwitcher(self.shell, is_initial=False))

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right and self.selected != PROFILE_SELECTION:
            if self.selected < len(self.tiles) - 1:
                self.selected += 1
                self._highlight()
            return
        if key == Qt.Key_Left and self.selected != PROFILE_SELECTION:
            if self.selected > 0:
                self.selected -= 1
                self._highlight()
            return
        if key == Qt.Key_Down:
            if self.selected == PROFILE_SELECTION:
                if self.tiles:
                    self.selected = 0
                    self._highlight()
            elif self.selected + HOME_COLS < len(self.tiles):
                self.selected += HOME_COLS
                self._highlight()
            return
        if key == Qt.Key_Up:
            if self.selected != PROFILE_SELECTION:
                if self.selected < HOME_COLS:
                    self.selected = PROFILE_SELECTION
                    self._highlight()
                elif self.selected - HOME_COLS >= 0:
                    self.selected -= HOME_COLS
                    self._highlight()
            return
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if self.selected == PROFILE_SELECTION:
                self._open_profiles()
            elif 0 <= self.selected < len(self.tiles):
                self._activate(self.shell.config.apps[self.selected])
            return
        super().keyPressEvent(event)

    def _activate(self, app):
        if app.screen == "clock":
            from ui.clock_screen import ClockScreen
            self.shell.push(ClockScreen())
        elif app.kind == "url":
            from ui.webscreen import WebScreen
            self.shell.push(WebScreen(app.url, on_escape=self.shell.pop))
        elif app.kind == "native":
            from ui.placeholder import Placeholder
            self.shell.push(Placeholder(app.name))
