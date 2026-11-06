"""MiddleTV's look: a dark equipment panel with illuminated controls --
80s/90s pro-audio gear and an old car dashboard at night, not a modern
app. Dark surfaces stay dark; only the controls themselves glow.
"""

# --- Base surfaces -----------------------------------------------------
BACKGROUND = "#141210"   # the room: near-black, warm-neutral charcoal
PANEL = "#1f1c18"        # equipment chassis / card surfaces
PANEL_RAISED = "#29251f"  # a slightly raised bezel/control surface
BORDER = "#3a352c"       # seams between panel pieces

# --- Indicator colors (semantic, not decorative) ------------------------
AMBER = "#ffa726"        # illuminated / active / selected
AMBER_DIM = "#4a3418"    # an unlit amber segment/LED -- just a hint of it
GREEN = "#5fbf5f"        # normal / working
GREEN_DIM = "#223422"
RED = "#e5544a"          # error
RED_DIM = "#3a211e"
BLUE = "#5b9bd5"         # informational
BLUE_DIM = "#1e2b38"

TEXT = "#f2e8d5"         # warm white -- display text, labels
TEXT_MUTED = "#9c9284"   # secondary label text, still warm not blue-gray

# --- Qt stylesheet for ordinary (non custom-drawn) widgets --------------
STYLESHEET = f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-family: "DejaVu Sans Mono", monospace;
    font-size: 13pt;
}}

QLabel#heading {{
    font-size: 16pt;
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
"""
