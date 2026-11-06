"""Native YouTube app — video playback screen.

Plays a YouTube video natively (no WebView):

1. yt-dlp extracts the actual MP4 stream URL for the video (background
   thread, never blocks the UI).
2. Qt Multimedia (QMediaPlayer + QVideoWidget) plays it directly.

Video metadata (title, channel, description) comes from the YouTube Data
API v3, so everything shown is real data, not placeholders.
"""

from __future__ import annotations

import subprocess
import threading

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
)

from core import theme
from ui.instruments import IlluminatedButton, StatusLED
from ui.youtube.api import Video


class YouTubePlayback(QWidget):
    """Fullscreen-ish video playback with transport controls."""

    def __init__(self, shell, video: Video):
        super().__init__()
        self.shell = shell
        self.config = shell.config
        self.video = video
        self.setFocusPolicy(Qt.StrongFocus)

        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        self._duration = 0
        self._position = 0
        self._seeking = False

        self._build()
        self._start_playback()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Video area
        outer.addWidget(self.video_widget, stretch=1)

        # Info panel (overlayed at bottom via a frame)
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.PANEL};
                border-top: 2px solid {theme.BORDER};
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(24, 14, 24, 14)
        info_layout.setSpacing(8)

        self.title_label = QLabel(self.video.title)
        self.title_label.setObjectName("heading")
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)

        meta = QLabel(f"{self.video.channel_title}  •  {self._fmt_duration()}")
        meta.setObjectName("equipmentLabel")
        info_layout.addWidget(meta)

        desc = QLabel(self.video.description[:200])
        desc.setObjectName("equipmentLabel")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {theme.TEXT_MUTED};")
        info_layout.addWidget(desc)

        outer.addWidget(info_frame)

        # Transport controls
        ctrl = QHBoxLayout()
        ctrl.setContentsMargins(24, 14, 24, 18)
        ctrl.setSpacing(16)

        self.play_btn = IlluminatedButton("PAUSE")
        self.play_btn.setFocusPolicy(Qt.StrongFocus)
        self.play_btn.setFixedWidth(120)
        self.play_btn.clicked.connect(self._toggle_play)
        ctrl.addWidget(self.play_btn)

        back10 = IlluminatedButton("-10s")
        back10.setFocusPolicy(Qt.StrongFocus)
        back10.setFixedWidth(90)
        back10.clicked.connect(lambda: self._seek(-10))
        ctrl.addWidget(back10)

        fwd10 = IlluminatedButton("+10s")
        fwd10.setFocusPolicy(Qt.StrongFocus)
        fwd10.setFixedWidth(90)
        fwd10.clicked.connect(lambda: self._seek(10))
        ctrl.addWidget(fwd10)

        ctrl.addStretch()

        vol_btn = IlluminatedButton("VOLUME")
        vol_btn.setFocusPolicy(Qt.StrongFocus)
        vol_btn.setFixedWidth(120)
        vol_btn.clicked.connect(self._toggle_volume)
        ctrl.addWidget(vol_btn)

        back_btn = IlluminatedButton("BACK")
        back_btn.setFocusPolicy(Qt.StrongFocus)
        back_btn.setFixedWidth(100)
        back_btn.clicked.connect(self.shell.pop)
        ctrl.addWidget(back_btn)

        outer.addLayout(ctrl)

        hint = QLabel("ARROWS NAVIGATE  •  ENTER PLAY/PAUSE  •  ESC BACK")
        hint.setObjectName("equipmentLabel")
        hint.setAlignment(Qt.AlignCenter)
        outer.addWidget(hint)

        # Position timer for the progress label
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

        # Connect player signals
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.errorOccurred.connect(self._on_error)

    def _start_playback(self):
        self.title_label.setText("LOADING…")
        self.shell.notify("Fetching stream URL…", level="info")

        def fetch():
            url = self._extract_stream_url(self.video.id)
            from PySide6.QtCore import QMetaObject, Qt as QtCon
            QMetaObject.invokeMethod(
                self, "_on_stream_url_ready",
                QtCon.QueuedConnection,
                lambda: url,
            )

        threading.Thread(target=fetch, daemon=True).start()

    def _extract_stream_url(self, video_id: str) -> str:
        """Use yt-dlp to get the best progressive MP4 stream URL."""
        try:
            out = subprocess.run(
                ["yt-dlp", "-g", "-f", "best[ext=mp4][height<=1080]",
                 f"https://www.youtube.com/watch?v={video_id}"],
                capture_output=True, text=True, timeout=30,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip().splitlines()[0]
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        # Fallback: any best format
        try:
            out = subprocess.run(
                ["yt-dlp", "-g", "-f", "best",
                 f"https://www.youtube.com/watch?v={video_id}"],
                capture_output=True, text=True, timeout=30,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip().splitlines()[0]
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return ""

    def _on_stream_url_ready(self, url: str):
        if not url:
            self.title_label.setText("PLAYBACK UNAVAILABLE")
            self.shell.notify("Could not fetch video stream", level="error")
            return
        self.title_label.setText(self.video.title)
        self.player.setSource(QUrl(url))
        self.player.play()
        self.play_btn.setText("PAUSE")

    def _toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("PLAY")
        else:
            self.player.play()
            self.play_btn.setText("PAUSE")

    def _seek(self, delta: int):
        self.player.setPosition(max(0, self.player.position() + delta * 1000))

    def _toggle_volume(self):
        muted = self.player.isMuted()
        self.player.setMuted(not muted)

    def _tick(self):
        self._position = self.player.position()

    def _on_duration_changed(self, dur: int):
        self._duration = dur

    def _on_position_changed(self, pos: int):
        self._position = pos

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setText("PAUSE")
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.play_btn.setText("PLAY")

    def _on_error(self, error, error_string):
        self.title_label.setText("PLAYBACK ERROR")
        self.shell.notify(f"Playback error: {error_string}", level="error")

    def _fmt_duration(self) -> str:
        total = self.video.duration  # ISO 8601 like PT4M32S
        return total  # show as-is for now; could parse nicely

    def on_shown(self):
        self.setFocus()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._toggle_play()
            return
        if key == Qt.Key_Left:
            self._seek(-10)
            return
        if key == Qt.Key_Right:
            self._seek(10)
            return
        if key == Qt.Key_Up:
            self._toggle_volume()
            return
        if key == Qt.Key_Down:
            self._toggle_volume()
            return
        super().keyPressEvent(event)
