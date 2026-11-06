from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame

from core import config, theme
from core.media_detect import detect
from ui.instruments import IlluminatedButton, PanelLineEdit, StatusLED


def _module_frame() -> QFrame:
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {theme.PANEL};
            border: 1px solid {theme.BORDER};
            border-radius: 8px;
        }}
    """)
    return frame


def _module_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("equipmentLabel")
    return label


class _DetectWorker(QThread):
    """Runs the media-server detection off the UI thread, since it makes
    real network calls that can take a couple of seconds."""
    done = Signal(object)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        self.done.emit(detect(self.url))


class SettingsScreen(QWidget):
    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.setFocusPolicy(Qt.StrongFocus)
        self._worker: _DetectWorker | None = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 28, 32, 28)
        outer.setSpacing(20)

        header = QHBoxLayout()
        header.addWidget(StatusLED(theme.AMBER, lit=True))
        title = QLabel("SETTINGS")
        title.setObjectName("heading")
        header.addWidget(title)
        header.addStretch()
        outer.addLayout(header)

        outer.addWidget(self._build_media_server_module())
        outer.addWidget(self._build_notifications_module())
        outer.addWidget(self._build_ui_theme_module())
        outer.addStretch()

        hint = QLabel("PRESS ESC TO RETURN")
        hint.setObjectName("equipmentLabel")
        hint.setAlignment(Qt.AlignCenter)
        outer.addWidget(hint)

        self.setTabOrder(self.url_field, self.test_btn)
        self.setTabOrder(self.test_btn, self.notif_toggle)

    def _build_media_server_module(self) -> QFrame:
        frame = _module_frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(_module_label("MEDIA SERVER"))

        row = QHBoxLayout()
        self.url_field = PanelLineEdit("http://localhost:8096")
        self.url_field.setText(self.shell.config.media_server.url)
        row.addWidget(self.url_field, stretch=1)

        self.test_btn = IlluminatedButton("TEST")
        self.test_btn.setFocusPolicy(Qt.StrongFocus)
        self.test_btn.setFixedWidth(110)
        self.test_btn.clicked.connect(self._test_connection)
        row.addWidget(self.test_btn)
        layout.addLayout(row)

        status_row = QHBoxLayout()
        self.server_led = StatusLED(theme.GREEN, lit=False)
        status_row.addWidget(self.server_led)
        self.server_status = QLabel(self._server_status_text())
        self.server_status.setObjectName("equipmentLabel")
        status_row.addWidget(self.server_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        self._refresh_server_led()
        return frame

    def _server_status_text(self) -> str:
        ms = self.shell.config.media_server
        if ms.kind in ("jellyfin", "plex") and ms.name:
            return f"{ms.kind.upper()} -- {ms.name}"
        if ms.kind == "unreachable":
            return "NOT REACHABLE"
        return "NOT CONFIGURED"

    def _refresh_server_led(self):
        ms = self.shell.config.media_server
        self.server_led.set_lit(ms.kind in ("jellyfin", "plex"))

    def _test_connection(self):
        url = self.url_field.text().strip()
        if not url:
            return
        self.test_btn.setEnabled(False)
        self.test_btn.setText("TESTING...")
        self._worker = _DetectWorker(url)
        self._worker.done.connect(self._on_detect_done)
        self._worker.start()

    def _on_detect_done(self, media_server):
        self.shell.config.media_server = media_server
        self.shell.config.save()
        self.server_status.setText(self._server_status_text())
        self.server_led.set_lit(media_server.kind in ("jellyfin", "plex"))
        self.test_btn.setEnabled(True)
        self.test_btn.setText("TEST")
        self.shell.notify(
            f"Media server: {media_server.kind}" if media_server.kind in ("jellyfin", "plex")
            else "Media server not reachable",
            level="ok" if media_server.kind in ("jellyfin", "plex") else "error",
        )

    def _build_notifications_module(self) -> QFrame:
        frame = _module_frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(_module_label("NOTIFICATIONS"))

        row = QHBoxLayout()
        row.addWidget(QLabel("Show in-app notifications"))
        row.addStretch()
        self.notif_toggle = IlluminatedButton()
        self.notif_toggle.setFocusPolicy(Qt.StrongFocus)
        self.notif_toggle.setFixedWidth(90)
        self.notif_toggle.clicked.connect(self._toggle_notifications)
        row.addWidget(self.notif_toggle)
        layout.addLayout(row)
        self._refresh_notif_toggle()
        return frame

    def _refresh_notif_toggle(self):
        on = self.shell.config.notifications_enabled
        self.notif_toggle.setText("ON" if on else "OFF")

    def _toggle_notifications(self):
        self.shell.config.notifications_enabled = not self.shell.config.notifications_enabled
        self.shell.config.save()
        self._refresh_notif_toggle()
        self.shell.notify("Notifications enabled" if self.shell.config.notifications_enabled
                           else "Notifications disabled")

    def _build_ui_theme_module(self) -> QFrame:
        frame = _module_frame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(_module_label("USER INTERFACE"))

        row = QHBoxLayout()
        row.addWidget(QLabel("Interface style"))
        row.addStretch()

        self.theme_btn = IlluminatedButton(self.shell.config.ui_theme.upper())
        self.theme_btn.setFocusPolicy(Qt.StrongFocus)
        self.theme_btn.setFixedWidth(140)
        self.theme_btn.clicked.connect(self._cycle_theme)
        row.addWidget(self.theme_btn)
        layout.addLayout(row)

        hint = QLabel("MODERN / AERO / TERMINAL — SAVES AUTOMATICALLY")
        hint.setObjectName("equipmentLabel")
        layout.addWidget(hint)

        # YouTube API key
        key_row = QHBoxLayout()
        key_row.setSpacing(12)
        key_row.addWidget(QLabel("YouTube API key"))
        self.api_key_field = PanelLineEdit()
        self.api_key_field.setPlaceholderText("AIza…")
        self.api_key_field.setText(self.shell.config.youtube_api_key)
        self.api_key_field.textChanged.connect(self._on_api_key_changed)
        key_row.addWidget(self.api_key_field, stretch=1)
        layout.addLayout(key_row)

        key_hint = QLabel("GET ONE AT console.cloud.google.com — REQUIRED FOR SEARCH/BROWSE")
        key_hint.setObjectName("equipmentLabel")
        layout.addWidget(key_hint)
        return frame

    def _cycle_theme(self):
        themes = ["modern", "aero", "terminal"]
        current = self.shell.config.ui_theme
        idx = themes.index(current) if current in themes else 0
        next_theme = themes[(idx + 1) % len(themes)]
        self.shell.config.ui_theme = next_theme
        self.shell.config.save()
        theme.apply_theme(next_theme)
        self.theme_btn.setText(next_theme.upper())
        # Re-apply the stylesheet so all screens pick up the new theme
        app = self.shell.app()
        if app:
            app.setStyleSheet(theme.STYLESHEET)
        self.shell.notify(f"UI: {next_theme.upper()}")

    def _on_api_key_changed(self, text: str):
        self.shell.config.youtube_api_key = text.strip()
        self.shell.config.save()

    def on_shown(self):
        self.url_field.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.focusNextChild()
            return
        if event.key() == Qt.Key_Up:
            self.focusPreviousChild()
            return
        super().keyPressEvent(event)
