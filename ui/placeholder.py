from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class Placeholder(QWidget):
    """Stands in for a native screen that hasn't been built yet."""

    def __init__(self, title: str):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(self)
        label = QLabel(f"{title} isn't built yet.\nPress Esc to go back.")
        label.setObjectName("placeholder")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
