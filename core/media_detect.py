"""Figures out whether a media server URL is Jellyfin or Plex, so the home
screen tile can show the right name without the person having to say so.
Uses only the standard library's urllib -- one more dependency wasn't
worth it for two GET requests.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error

from core.config import MediaServer

_TIMEOUT = 3.0


def detect(url: str) -> MediaServer:
    url = url.rstrip("/")
    if not url:
        return MediaServer(url=url, kind="unknown", name="")

    jellyfin = _try_jellyfin(url)
    if jellyfin:
        return jellyfin

    plex = _try_plex(url)
    if plex:
        return plex

    return MediaServer(url=url, kind="unreachable", name="")


def _get_json(url: str, headers: dict) -> dict | None:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            body = resp.read()
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def _try_jellyfin(url: str) -> MediaServer | None:
    data = _get_json(f"{url}/System/Info/Public", {"Accept": "application/json"})
    if data and "ServerName" in data:
        return MediaServer(url=url, kind="jellyfin", name=data.get("ServerName", "Jellyfin"))
    return None


def _try_plex(url: str) -> MediaServer | None:
    data = _get_json(f"{url}/identity", {"Accept": "application/json"})
    if data and "MediaContainer" in data:
        name = data["MediaContainer"].get("friendlyName", "Plex")
        return MediaServer(url=url, kind="plex", name=name)
    return None
