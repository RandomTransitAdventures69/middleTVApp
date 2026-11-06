"""Native YouTube app — search screen.

Lets the user type a query, then shows matching videos in a grid.
Keyboard/remote friendly: arrow keys navigate, Enter plays, Esc goes back.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy,
)

from core import theme
from ui.instruments import IlluminatedButton, PanelLineEdit, StatusLED
from ui.youtube.api import YouTubeApi, Video, SearchResult
from ui.youtube.home import _ApiWorker, HOME_COLS, VIDEO_MIN_SIZE


class YouTubeSearch(QWidget):
    """YouTube search: type a query, browse results, play a video."""

    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.config = shell.config
        self.api = YouTubeApi(self.config.youtube_api_key)
        self.setFocusPolicy(Qt.StrongFocus)

        self.videos: list[Video] = []
        self.tiles: list[IlluminatedButton] = []
        self.selected = 0
        self.loading = False
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 28, 32, 32)
        outer.setSpacing(20)

        header = QHBoxLayout()
        header.setSpacing(10)
        header.addWidget(StatusLED(theme.RED, lit=True))
        title = QLabel("SEARCH")
        title.setObjectName("heading")
        header.addWidget(title)
        header.addStretch()

        back_btn = IlluminatedButton("BACK")
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.clicked.connect(self.shell.pop)
        header.addWidget(back_btn)
        outer.addLayout(header)

        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(QLabel("QUERY"))
        self.query_field = PanelLineEdit()
        self.query_field.setMinimumWidth(420)
        self.query_field.returnPressed.connect(self._run_search)
        row.addWidget(self.query_field, stretch=1)

        go_btn = IlluminatedButton("GO")
        go_btn.setFocusPolicy(Qt.StrongFocus)
        go_btn.setFixedWidth(100)
        go_btn.clicked.connect(self._run_search)
        row.addWidget(go_btn)
        outer.addLayout(row)

        self.status = QLabel("")
        self.status.setObjectName("equipmentLabel")
        outer.addWidget(self.status)

        grid = QGridLayout()
        grid.setSpacing(18)
        self.grid = grid
        outer.addLayout(grid)
        outer.addStretch()

        hint = QLabel("ARROWS NAVIGATE  •  ENTER PLAYS  •  ESC BACK")
        hint.setObjectName("equipmentLabel")
        hint.setAlignment(Qt.AlignCenter)
        outer.addWidget(hint)

        self.query_field.setFocus()

    def on_shown(self):
        self.query_field.setFocus()

    def _run_search(self):
        query = self.query_field.text().strip()
        if not query:
            return
        self.loading = True
        self.status.setText("SEARCHING...")
        self._worker = _ApiWorker(lambda: self.api.search(query))
        self._worker.done.connect(self._on_search_done)
        self._worker.start()

    def _on_search_done(self, result: SearchResult):
        self.loading = False
        self.videos = result.videos
        self.status.setText(f"{len(self.videos)} RESULTS" if self.videos else "NO RESULTS")
        self._rebuild_grid()

    def _rebuild_grid(self):
        for btn in self.tiles:
            self.grid.removeWidget(btn)
            btn.deleteLater()
        self.tiles = []

        for i, video in enumerate(self.videos):
            btn = IlluminatedButton(video.title[:32])
            btn.setMinimumSize(*VIDEO_MIN_SIZE)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.clicked.connect(lambda checked=False, v=video: self._play(v))
            self.grid.addWidget(btn, i // HOME_COLS, i % HOME_COLS)
            self.tiles.append(btn)

        self.selected = 0
        self._highlight()

    def _highlight(self):
        for i, t in enumerate(self.tiles):
            t.set_selected(i == self.selected)

    def _play(self, video: Video):
        from ui.youtube.playback import YouTubePlayback
        self.shell.push(YouTubePlayback(self.shell, video))

    def keyPressEvent(self, event):
        key = event.key()
        n = len(self.tiles)
        if key == Qt.Key_Right and n:
            if self.selected < n - 1:
                self.selected += 1
                self._highlight()
            return
        if key == Qt.Key_Left and n:
            if self.selected > 0:
                self.selected -= 1
                self._highlight()
            return
        if key == Qt.Key_Down and n:
            if self.selected + HOME_COLS < n:
                self.selected += HOME_COLS
                self._highlight()
            return
        if key == Qt.Key_Up and n:
            if self.selected - HOME_COLS >= 0:
                self.selected -= HOME_COLS
                self._highlight()
            return
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if 0 <= self.selected < n:
                self._play(self.videos[self.selected])
            return
        super().keyPressEvent(event)
