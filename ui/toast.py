from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

from core import theme

_LEVEL_COLORS = {
    "info": theme.BLUE,
    "ok": theme.GREEN,
    "error": theme.RED,
}


class Toast(QWidget):
    """A small illuminated status panel that appears over whatever screen
    is showing, then dismisses itself -- like an equipment rack's message
    display, not a phone-style popup."""

    def __init__(self, parent_window: QWidget):
        super().__init__(parent_window)
        self._parent_window = parent_window
        self.setStyleSheet(f"""
            Toast {{
                background-color: {theme.PANEL_RAISED};
                border: 2px solid {theme.BORDER};
                border-radius: 6px;
            }}
        """)
        glow = QGraphicsDropShadowEffect(self)
        glow.setColor(QColor("#000000"))
        glow.setOffset(0, 4)
        glow.setBlurRadius(20)
        self.setGraphicsEffect(glow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 18, 10)
        layout.setSpacing(10)

        self._dot = QLabel("\u25cf")
        layout.addWidget(self._dot)
        self._label = QLabel()
        self._label.setObjectName("equipmentLabel")
        layout.addWidget(self._label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

        self.hide()

    def show_message(self, message: str, level: str = "info", duration_ms: int = 3000):
        color = _LEVEL_COLORS.get(level, theme.BLUE)
        self._dot.setStyleSheet(f"color: {color}; font-size: 14pt;")
        self._label.setText(message.upper())
        self.adjustSize()
        self._reposition()
        self.show()
        self.raise_()
        self._timer.start(duration_ms)

    def _reposition(self):
        pw = self._parent_window.width()
        self.move(pw - self.width() - 24, 24)
