from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect,
)

from core import theme


class ProfileSwitcher(QWidget):
    """Lets the person pick which profile is active -- shown first on
    every launch (is_initial=True: picking a profile pushes Home), and
    also reachable from Home's profile button (is_initial=False: picking
    a profile just pops back).
    """

    def __init__(self, shell, is_initial: bool):
        super().__init__()
        self.shell = shell
        self.is_initial = is_initial
        self.cards: list[QPushButton] = []
        self.selected = 0
        self.setFocusPolicy(Qt.StrongFocus)
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 40, 28, 28)
        outer.setSpacing(36)

        title = QLabel("SELECT OPERATOR")
        title.setObjectName("heading")
        title.setAlignment(Qt.AlignCenter)
        outer.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(28)
        row.addStretch()

        self.cards = []
        profiles = self.shell.config.profiles
        for i, prof in enumerate(profiles):
            card = QVBoxLayout()
            card.setSpacing(10)

            avatar = QPushButton((prof.name or "?")[0].upper())
            avatar.setFocusPolicy(Qt.NoFocus)
            avatar.setFixedSize(140, 140)
            avatar.clicked.connect(lambda checked=False, idx=i: self._pick(idx))
            glow = QGraphicsDropShadowEffect(avatar)
            glow.setColor(QColor(theme.AMBER))
            glow.setOffset(0, 0)
            glow.setBlurRadius(0)
            avatar.setGraphicsEffect(glow)
            avatar.glow_effect = glow
            card.addWidget(avatar, alignment=Qt.AlignCenter)

            name = QLabel(prof.name.upper())
            name.setObjectName("equipmentLabel")
            name.setAlignment(Qt.AlignCenter)
            card.addWidget(name)

            row.addLayout(card)
            self.cards.append(avatar)
            if prof.id == self.shell.config.active_profile:
                self.selected = i

        row.addStretch()
        outer.addLayout(row)
        outer.addStretch()

        self._highlight()

    def on_shown(self):
        pass

    def _highlight(self):
        for i, c in enumerate(self.cards):
            selected = i == self.selected
            bg = theme.AMBER if selected else theme.PANEL_RAISED
            fg = "#1a1208" if selected else theme.TEXT
            border = theme.AMBER if selected else theme.BORDER
            c.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {fg};
                    border: 3px solid {border};
                    border-radius: 70px;
                    font-size: 28pt;
                    font-weight: bold;
                }}
            """)
            c.glow_effect.setBlurRadius(32 if selected else 0)

    def _pick(self, idx: int):
        if not self.cards:
            return
        self.shell.config.active_profile = self.shell.config.profiles[idx].id
        self.shell.config.save()
        if self.is_initial:
            from ui.home import Home
            self.shell.push(Home(self.shell))
        else:
            self.shell.pop()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Right and self.selected < len(self.cards) - 1:
            self.selected += 1
            self._highlight()
            return
        if key == Qt.Key_Left and self.selected > 0:
            self.selected -= 1
            self._highlight()
            return
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._pick(self.selected)
            return
        super().keyPressEvent(event)
