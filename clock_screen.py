from __future__ import annotations

import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from core import theme
from ui.instruments import SegmentedDisplay, StatusLED


class ClockScreen(QWidget):
    """A big illuminated segmented-display clock -- the kind you'd find on
    a rack of broadcast gear, not a phone lock screen."""

    def __init__(self):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 40, 40, 40)

        label_row = QHBoxLayout()
        label_row.addWidget(StatusLED(theme.GREEN, lit=True))
        caption = QLabel("MASTER CLOCK")
        caption.setObjectName("equipmentLabel")
        label_row.addWidget(caption)
        label_row.addStretch()
        outer.addLayout(label_row)

        outer.addStretch()
        self.time_display = SegmentedDisplay("00:00:00", color=theme.AMBER, dim_color=theme.AMBER_DIM)
        self.time_display.setFixedHeight(220)
        outer.addWidget(self.time_display)

        self.date_display = SegmentedDisplay("00-00-0000", color=theme.GREEN, dim_color=theme.GREEN_DIM)
        self.date_display.setFixedHeight(70)
        outer.addWidget(self.date_display)
        outer.addStretch()

        hint = QLabel("PRESS ESC TO RETURN")
        hint.setObjectName("equipmentLabel")
        hint.setAlignment(Qt.AlignCenter)
        outer.addWidget(hint)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

    def _tick(self):
        now = datetime.datetime.now()
        self.time_display.setText(now.strftime("%H:%M:%S"))
        self.date_display.setText(now.strftime("%m-%d-%Y"))

    def on_shown(self):
        self._tick()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
