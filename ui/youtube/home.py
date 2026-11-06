"""Native YouTube app — home / browse screen.

Shows trending/popular videos in a grid, navigable with arrow keys, plus a
"Search" entry. Selecting a video pushes the playback screen. Fully native
Qt widgets — no WebView. Adapts to whichever middleTV UI theme is active.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy,
)

from core import theme
from core.config import Config
from ui.instruments import IlluminatedButton, StatusLED
from ui.youtube.api import YouTubeApi, Video, SearchResult


HOME_COLS = 4
VIDEO_MIN_SIZE = (260, 180)


class _ThumbnailLoader(QThread):
    """Downloads a thumbnail image off the UI thread so the grid stays snappy."""
    done = Signal(object, QPixmap)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        import urllib.request
        try:
            with urllib.request.urlopen(self.url, timeout=10.0) as resp:
                data = resp.read()
            pix = QPixmap()
            pix.loadFromData(data)
        except Exception:
            pix = QPixmap()
        self.done.emit(self.url, pix)


class YouTubeHome(QWidget):
    """YouTube home screen: trending videos grid + search entry."""

    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.config: Config = shell.config
        self.api = YouTubeApi(self.config.youtube_api_key)
        self.setFocusPolicy(Qt.StrongFocus)

        self.videos: list[Video] = []
        self.tiles: list[IlluminatedButton] = []
        self.thumbs: dict[str, QPixmap] = {}
        self.selected = 0
        self.loading = False
        self._search_idx = -1  # search tile lives at index -1 (top-left)

        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 28, 32, 32)
        outer.setSpacing(20)

        header = QHBoxLayout()
        header.setSpacing(10)
        header.addWidget(StatusLED(theme.RED, lit=True))
        title = QLabel("YOUTUBE")
        title.setObjectName("heading")
        header.addWidget(title)
        header.addStretch()

        back_btn = IlluminatedButton("BACK")
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.clicked.connect(self.shell.pop)
        header.addWidget(back_btn)
        outer.addLayout(header)

        # Search entry row
        search_row = QHBoxLayout()
        self.search_btn = IlluminatedButton("SEARCH YOUTUBE")
        self.search_btn.setMinimumSize(260, 70)
        self.search_btn.setFocusPolicy(Qt.NoFocus)
        self.search_btn.clicked.connect(self._open_search)
        search_row.addWidget(self.search_btn)
        search_row.addStretch()
        outer.addLayout(search_row)

        grid = QGridLayout()
        grid.setSpacing(18)
        self.grid = grid
        outer.addLayout(grid)
        outer.addStretch()

        self._highlight()

    def on_shown(self):
        self._refresh_labels()
        if not self.config.youtube_api_key:
            self.status = QLabel("NO YOUTUBE API KEY CONFIGURED — OPEN SETTINGS TO ADD ONE")
            self.status.setObjectName("equipmentLabel")
            self.status.setAlignment(Qt.AlignCenter)
            # find the outer layout and insert status
            self.layout().addWidget(self.status)
            return
        if not self.videos and not self.loading:
            self._load_trending()

    def _refresh_labels(self):
        self.search_btn.setText("SEARCH YOUTUBE")

    def _load_trending(self):
        self.loading = True
        self._worker = _ApiWorker(self.api.trending)
        self.worker_done = self._worker.done
        self._worker.done.connect(self._on_trending_done)
        self._worker.start()

    def _on_trending_done(self, result: SearchResult):
        self.loading = False
        self.videos = result.videos
        self._rebuild_grid()

    def _rebuild_grid(self):
        # Clear existing tiles
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
            self._load_thumb(video)

        self._highlight()

    def _load_thumb(self, video: Video):
        if not video.thumbnail_url:
            return
        loader = _ThumbnailLoader(video.thumbnail_url)
        loader.done.connect(lambda url, pix, v=video: self._on_thumb_loaded(v, pix))
        loader.start()

    def _on_thumb_loaded(self, video: Video, pix: QPixmap):
        self.thumbs[video.id] = pix
        # Re-highlight to potentially redraw with thumbnail context
        self._highlight()

    def _highlight(self):
        for i, t in enumerate(self.tiles):
            t.set_selected(i == self.selected)

    def _open_search(self):
        from ui.youtube.search import YouTubeSearch
        self.shell.push(YouTubeSearch(self.shell))

    def _play(self, video: Video):
        from ui.youtube.playback import YouTubePlayback
        self.shell.push(YouTubePlayback(self.shell, video))

    def keyPressEvent(self, event):
        key = event.key()
        n = len(self.tiles)
        if key == Qt.Key_Right:
            if self.selected < n - 1:
                self.selected += 1
                self._highlight()
            return
        if key == Qt.Key_Left:
            if self.selected > 0:
                self.selected -= 1
                self._highlight()
            return
        if key == Qt.Key_Down:
            if self.selected + HOME_COLS < n:
                self.selected += HOME_COLS
                self._highlight()
            return
        if key == Qt.Key_Up:
            if self.selected - HOME_COLS >= 0:
                self.selected -= HOME_COLS
                self._highlight()
            return
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if 0 <= self.selected < n:
                self._play(self.videos[self.selected])
            return
        super().keyPressEvent(event)


class _ApiWorker(QThread):
    """Runs an arbitrary zero-arg API call off the UI thread."""
    done = Signal(object)

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def run(self):
        self.done.emit(self.fn())
