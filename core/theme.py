"""MiddleTV look-and-feel themes.

Three switchable interfaces:

* **Modern** — the original equipment-panel aesthetic: dark chassis surfaces,
  amber/green illuminated controls, warm-white text. This is the default.
* **Aero** — translucent glass surfaces, soft blur, cool blue/white accents,
  rounded panels, light text.
* **Terminal** — black background, green/amber monospace text, blocky
  command-line feel, no blur, no rounded corners.

Call `apply_theme(name)` once (typically at startup, and again whenever the
person switches UIs in Settings) to rebuild `STYLESHEET` and the per-theme
color/surface constants that screens import from `core.theme`.
"""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

# ---------------------------------------------------------------------------
# Shared surface names (every theme defines these)
# ---------------------------------------------------------------------------

BACKGROUND = "#141210"
PANEL = "#1f1c18"
PANEL_RAISED = "#29251f"
BORDER = "#3a352c"

AMBER = "#ffa726"
AMBER_DIM = "#4a3418"
GREEN = "#5fbf5f"
GREEN_DIM = "#223422"
RED = "#e5544a"
RED_DIM = "#3a211e"
BLUE = "#5b9bd5"
BLUE_DIM = "#1e2b38"

TEXT = "#f2e8d5"
TEXT_MUTED = "#9c9284"

STYLESHEET = ""

_CURRENT_THEME = "modern"


# ---------------------------------------------------------------------------
# Theme definitions
# ---------------------------------------------------------------------------

def _modern() -> None:
    """Original equipment-panel look (the default)."""
    global BACKGROUND, PANEL, PANEL_RAISED, BORDER
    global AMBER, AMBER_DIM, GREEN, GREEN_DIM, RED, RED_DIM, BLUE, BLUE_DIM
    global TEXT, TEXT_MUTED, STYLESHEET

    BACKGROUND = "#141210"
    PANEL = "#1f1c18"
    PANEL_RAISED = "#29251f"
    BORDER = "#3a352c"

    AMBER = "#ffa726"
    AMBER_DIM = "#4a3418"
    GREEN = "#5fbf5f"
    GREEN_DIM = "#223422"
    RED = "#e5544a"
    RED_DIM = "#3a211e"
    BLUE = "#5b9bd5"
    BLUE_DIM = "#1e2b38"

    TEXT = "#f2e8d5"
    TEXT_MUTED = "#9c9284"

    STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-family: "DejaVu Sans", sans-serif;
    font-size: 13pt;
}}

QLabel#heading {{
    font-size: 18pt;
    font-weight: bold;
    letter-spacing: 2px;
    color: {TEXT};
}}

QLabel#equipmentLabel {{
    color: {TEXT_MUTED};
    font-size: 9pt;
    letter-spacing: 3px;
}}

QLabel#placeholder {{
    color: {TEXT_MUTED};
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}}

QPushButton {{
    background-color: {PANEL_RAISED};
    border: 2px solid {BORDER};
    border-radius: 6px;
    color: {TEXT};
    font-weight: bold;
    font-size: 13pt;
    padding: 10px;
}}

QPushButton:hover {{
    border-color: {AMBER};
}}

QLineEdit {{
    background-color: {BACKGROUND};
    color: {TEXT};
    border: 2px solid {BORDER};
    border-radius: 4px;
    padding: 8px 10px;
    font-size: 12pt;
}}

QLineEdit:focus {{
    border-color: {AMBER};
}}
"""


def _aero() -> None:
    """Windows-Aero-inspired glass look: translucent panels, blur, cool
    blue/white accents, light text on glass."""
    global BACKGROUND, PANEL, PANEL_RAISED, BORDER
    global AMBER, AMBER_DIM, GREEN, GREEN_DIM, RED, RED_DIM, BLUE, BLUE_DIM
    global TEXT, TEXT_MUTED, STYLESHEET

    BACKGROUND = "#0f172a"      # deep slate, almost black
    PANEL = "rgba(30, 41, 59, 0.85)"   # translucent slate
    PANEL_RAISED = "rgba(51, 65, 85, 0.9)"
    BORDER = "rgba(148, 163, 184, 0.5)"

    AMBER = "#fbbf24"
    AMBER_DIM = "#451a03"
    GREEN = "#4ade80"
    GREEN_DIM = "#14532d"
    RED = "#f87171"
    RED_DIM = "#450a0a"
    BLUE = "#60a5fa"
    BLUE_DIM = "#1e3a8a"

    TEXT = "#f8fafc"
    TEXT_MUTED = "#94a3b8"

    STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-family: "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 13pt;
}}

QLabel#heading {{
    font-size: 20pt;
    font-weight: 600;
    letter-spacing: 0.5px;
    color: {TEXT};
}}

QLabel#equipmentLabel {{
    color: {TEXT_MUTED};
    font-size: 10pt;
    letter-spacing: 1px;
}}

QLabel#placeholder {{
    color: {TEXT_MUTED};
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}}

QPushButton {{
    background-color: {PANEL_RAISED};
    border: 1px solid {BORDER};
    border-radius: 10px;
    color: {TEXT};
    font-weight: 600;
    font-size: 13pt;
    padding: 12px;
}}

QPushButton:hover {{
    border-color: {BLUE};
    background-color: rgba(51, 65, 85, 1.0);
}}

QLineEdit {{
    background-color: rgba(15, 23, 42, 0.9);
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 12pt;
}}

QLineEdit:focus {{
    border-color: {BLUE};
}}
"""


def _terminal() -> None:
    """CRT terminal look: black background, green/amber monospace text,
    blocky no-nonsense styling."""
    global BACKGROUND, PANEL, PANEL_RAISED, BORDER
    global AMBER, AMBER_DIM, GREEN, GREEN_DIM, RED, RED_DIM, BLUE, BLUE_DIM
    global TEXT, TEXT_MUTED, STYLESHEET

    BACKGROUND = "#000000"
    PANEL = "#0a0a0a"
    PANEL_RAISED = "#141414"
    BORDER = "#222222"

    AMBER = "#b58900"
    AMBER_DIM = "#3a2a00"
    GREEN = "#859900"
    GREEN_DIM = "#2a3a00"
    RED = "#dc322f"
    RED_DIM = "#3a0a0a"
    BLUE = "#268bd2"
    BLUE_DIM = "#0a2a3a"

    TEXT = "#859900"      # green text on black
    TEXT_MUTED = "#586e75"

    STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-family: "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 13pt;
}}

QLabel#heading {{
    font-size: 18pt;
    font-weight: bold;
    letter-spacing: 4px;
    color: {TEXT};
}}

QLabel#equipmentLabel {{
    color: {TEXT_MUTED};
    font-size: 10pt;
    letter-spacing: 2px;
}}

QLabel#placeholder {{
    color: {TEXT_MUTED};
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}}

QPushButton {{
    background-color: {PANEL_RAISED};
    border: 2px solid {BORDER};
    border-radius: 0px;
    color: {TEXT};
    font-weight: bold;
    font-size: 13pt;
    padding: 10px;
}}

QPushButton:hover {{
    border-color: {GREEN};
    background-color: {PANEL};
}}

QLineEdit {{
    background-color: {BACKGROUND};
    color: {TEXT};
    border: 2px solid {BORDER};
    border-radius: 0px;
    padding: 8px 10px;
    font-size: 12pt;
}}

QLineEdit:focus {{
    border-color: {GREEN};
}}
"""


_THEMES = {
    "modern": _modern,
    "aero": _aero,
    "terminal": _terminal,
}


def apply_theme(name: str) -> None:
    """Rebuild all theme constants and STYLESHEET for the given theme name.

    Unknown names fall back to "modern". After calling this, the caller must
    re-apply `app.setStyleSheet(theme.STYLESHEET)` and re-polish any widgets
    that read theme constants at construction time (custom-drawn widgets like
    IlluminatedButton re-read constants on each paint, so they update
    automatically on next redraw).
    """
    global _CURRENT_THEME
    fn = _THEMES.get(name, _modern)
    fn()
    _CURRENT_THEME = name


def current_theme() -> str:
    return _CURRENT_THEME


# initialise to modern so imports work before apply_theme() is called
_modern()
