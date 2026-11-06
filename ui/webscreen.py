from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWebEngineCore import QWebEngineScript
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout

# A plain Qt shortcut isn't reliable here: the embedded browser engine
# handles its own keyboard input and doesn't consistently let Esc bubble
# back up to Qt. Instead, inject a listener that -- on Escape -- sets the
# page title to a sentinel value; Python watches for that sentinel via
# QWebEnginePage.titleChanged, which needs no extra resources to load and
# always works. The real title is restored immediately after, so nothing
# else ever sees the sentinel.
_SENTINEL = "__middletv_escape__"

_ESC_SCRIPT = f"""
(function () {{
    document.addEventListener('keydown', function (e) {{
        if (e.key === 'Escape') {{
            document.title = {_SENTINEL!r};
        }}
    }}, true);
}})();
"""


class WebScreen(QWidget):
    """Shows a URL inside the app itself -- a real embedded browser engine,
    not a popped-out window. This is the only place MiddleTV uses any kind
    of web rendering, and it's confined to this one screen: everything
    else in the app is plain native Qt widgets.

    Cookies and local storage persist on their own: QWebEngineView keeps
    its own on-disk profile for this app by default, the same way a real
    browser does, so staying logged into YouTube or Jellyfin survives
    closing and reopening the tile.
    """

    def __init__(self, url: str, on_escape=None):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._on_escape = on_escape or (lambda: None)
        self._real_title = ""

        self.view = QWebEngineView()

        script = QWebEngineScript()
        script.setName("mtv-esc-watch")
        script.setSourceCode(_ESC_SCRIPT)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setRunsOnSubFrames(True)
        self.view.page().scripts().insert(script)
        self.view.page().titleChanged.connect(self._on_title_changed)

        self.view.setUrl(url)
        layout.addWidget(self.view)

    def _on_title_changed(self, title: str):
        if title == _SENTINEL:
            self._on_escape()
        else:
            self._real_title = title

    def on_shown(self):
        self.view.setFocus()
