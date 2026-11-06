"""Loads and saves MiddleTV's on-disk configuration: the home-screen app
grid, the list of profiles, and which profile is active.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class App:
    id: str
    name: str
    kind: str  # "native" (a built-in screen) or "url" (embedded web view)
    screen: str = ""  # which built-in screen to show, when kind == "native"
    url: str = ""  # address to open, when kind == "url"


@dataclass
class Profile:
    id: str
    name: str
    color: str = "#4ECDC4"  # hex color used for the profile's avatar


@dataclass
class MediaServer:
    url: str = ""
    kind: str = "unknown"  # "jellyfin", "plex", or "unknown" until tested
    name: str = ""         # the server's own reported name, once detected


@dataclass
class Config:
    apps: list[App] = field(default_factory=list)
    profiles: list[Profile] = field(default_factory=list)
    active_profile: str = "default"
    media_server: MediaServer = field(default_factory=MediaServer)
    notifications_enabled: bool = True
    youtube_api_key: str = ""
    ui_theme: str = "modern"

    _path: Path = field(default=None, repr=False, compare=False)

    def active_profile_obj(self) -> Profile:
        for p in self.profiles:
            if p.id == self.active_profile:
                return p
        if self.profiles:
            return self.profiles[0]
        return Profile(id="default", name="Default", color="#4ECDC4")

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "apps": [asdict(a) for a in self.apps],
            "profiles": [asdict(p) for p in self.profiles],
            "active_profile": self.active_profile,
            "media_server": asdict(self.media_server),
            "notifications_enabled": self.notifications_enabled,
            "youtube_api_key": self.youtube_api_key,
            "ui_theme": self.ui_theme,
        }
        self._path.write_text(json.dumps(data, indent=2))


def _default_config(path: Path) -> Config:
    cfg = Config(
        apps=[
            App(id="jellyfin", name="Jellyfin", kind="url", url="http://localhost:8096"),
            App(id="youtube", name="YouTube", kind="native", screen="youtube_home"),
            App(id="flight_tracker", name="Flight Tracker", kind="url", url="https://www.flightradar24.com"),
            App(id="clock", name="Clock", kind="native", screen="clock"),
            App(id="files", name="Files", kind="native", screen="files"),
            App(id="settings", name="Settings", kind="native", screen="settings"),
            App(id="about", name="About", kind="native", screen="about"),
        ],
        profiles=[Profile(id="default", name="Default", color="#4ECDC4")],
        active_profile="default",
        youtube_api_key="",
        ui_theme="modern",
    )
    cfg._path = path
    return cfg


def load(path: str | Path) -> Config:
    """Reads the config file at path, creating it with sensible defaults
    if it doesn't exist yet, so the app always has something to show."""
    path = Path(path)
    if not path.exists():
        cfg = _default_config(path)
        cfg.save()
        return cfg

    raw = json.loads(path.read_text())
    apps = [App(**a) for a in raw.get("apps", [])]
    # Migrate: switch the YouTube tile from an embedded WebView to the native app.
    for app in apps:
        if app.id == "youtube" and app.kind == "url":
            app.kind = "native"
            app.screen = "youtube_home"
            app.url = ""
    cfg = Config(
        apps=apps,
        profiles=[Profile(**p) for p in raw.get("profiles", [])],
        active_profile=raw.get("active_profile", "default"),
        media_server=MediaServer(**raw["media_server"]) if raw.get("media_server") else MediaServer(),
        notifications_enabled=raw.get("notifications_enabled", True),
        youtube_api_key=raw.get("youtube_api_key", ""),
        ui_theme=raw.get("ui_theme", "modern"),
    )
    cfg._path = path
    return cfg
