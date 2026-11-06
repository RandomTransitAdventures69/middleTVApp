"""Custom-drawn widgets that make up MiddleTV's instrument-panel look:
a segmented digit display, a physical-looking illuminated button, and a
small status LED. These are drawn with QPainter rather than styled with
QSS, the same way real equipment panels are machined pieces, not paint.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPolygonF, QFont, QPen, QLinearGradient
from PySide6.QtWidgets import QWidget, QPushButton, QLineEdit, QGraphicsDropShadowEffect

from core import theme

# --- Seven-segment digit font -------------------------------------------
# Segments, standard naming:  A top, B top-right, C bottom-right, D bottom,
# E bottom-left, F top-left, G middle.
_DIGIT_SEGMENTS = {
    "0": "ABCDEF", "1": "BC", "2": "ABGED", "3": "ABGCD",
    "4": "FGBC", "5": "AFGCD", "6": "AFGEDC", "7": "ABC",
    "8": "ABCDEFG", "9": "ABCDFG", "-": "G", " ": "",
}


def _seg_h(x1, x2, y, t):
    """A horizontal lozenge-shaped segment, pointed at both ends."""
    h = t / 2
    return QPolygonF([
        QPointF(x1, y), QPointF(x1 + h, y - h), QPointF(x2 - h, y - h),
        QPointF(x2, y), QPointF(x2 - h, y + h), QPointF(x1 + h, y + h),
    ])


def _seg_v(x, y1, y2, t):
    """A vertical lozenge-shaped segment, pointed at both ends."""
    h = t / 2
    return QPolygonF([
        QPointF(x, y1), QPointF(x + h, y1 + h), QPointF(x + h, y2 - h),
        QPointF(x, y2), QPointF(x - h, y2 - h), QPointF(x - h, y1 + h),
    ])


class SegmentedDisplay(QWidget):
    """A row of 7-segment-style characters, like an old digital clock or a
    piece of rack gear's readout. Lit segments use `color`; unlit segments
    stay faintly visible (`dim_color`), the way real LED displays never go
    fully dark.
    """

    def __init__(self, text: str = "", color: str = theme.AMBER,
                 dim_color: str = theme.AMBER_DIM, parent=None):
        super().__init__(parent)
        self._text = text
        self._color = QColor(color)
        self._dim_color = QColor(dim_color)
        self.setMinimumHeight(60)

    def setText(self, text: str):
        self._text = text
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(theme.BACKGROUND))

        chars = self._text or " "
        n = len(chars)
        cell_w = self.width() / max(n, 1)
        margin = cell_w * 0.14
        digit_w = cell_w - 2 * margin
        digit_h = self.height() * 0.78
        top = (self.height() - digit_h) / 2
        thickness = max(digit_w, digit_h) * 0.14

        for i, ch in enumerate(chars):
            x0 = i * cell_w + margin
            if ch == ":":
                cx = x0 + digit_w / 2
                p.setPen(Qt.NoPen)
                p.setBrush(self._color)
                r = thickness * 0.6
                p.drawEllipse(QPointF(cx, top + digit_h * 0.3), r, r)
                p.drawEllipse(QPointF(cx, top + digit_h * 0.7), r, r)
                continue

            lit = _DIGIT_SEGMENTS.get(ch.upper(), "")
            x1, x2 = x0, x0 + digit_w
            y1, ym, y2 = top, top + digit_h / 2, top + digit_h

            segs = {
                "A": _seg_h(x1, x2, y1, thickness),
                "G": _seg_h(x1, x2, ym, thickness),
                "D": _seg_h(x1, x2, y2, thickness),
                "F": _seg_v(x1, y1, ym, thickness),
                "B": _seg_v(x2, y1, ym, thickness),
                "E": _seg_v(x1, ym, y2, thickness),
                "C": _seg_v(x2, ym, y2, thickness),
            }
            p.setPen(Qt.NoPen)
            for name, poly in segs.items():
                p.setBrush(self._color if name in lit else self._dim_color)
                p.drawPolygon(poly)


class StatusLED(QWidget):
    """A small round indicator light, like the ones scattered across a
    piece of rack equipment: lit or unlit, in one of the panel's semantic
    colors (amber/green/red/blue)."""

    def __init__(self, color: str = theme.GREEN, lit: bool = True, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._lit = lit
        self.setFixedSize(12, 12)

    def set_lit(self, lit: bool):
        self._lit = lit
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        if self._lit:
            glow = QColor(self._color)
            glow.setAlpha(70)
            p.setBrush(glow)
            p.drawEllipse(self.rect().adjusted(-2, -2, 2, 2))
            p.setBrush(self._color)
        else:
            dim = QColor(self._color)
            dim.setAlpha(50)
            p.setBrush(dim)
        p.drawEllipse(self.rect().adjusted(2, 2, -2, -2))


class PanelLineEdit(QLineEdit):
    """A text field styled to match the panel -- a recessed slot rather
    than a modern rounded input box, with the same amber focus glow as
    everything else on the panel."""

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setColor(QColor(theme.AMBER))
        self._glow.setOffset(0, 0)
        self._glow.setBlurRadius(0)
        self.setGraphicsEffect(self._glow)
        self._apply_style(False)

    def _apply_style(self, focused: bool):
        border = theme.AMBER if focused else theme.BORDER
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.BACKGROUND};
                color: {theme.TEXT};
                border: 2px solid {border};
                border-radius: 4px;
                padding: 8px 10px;
                font-size: 12pt;
            }}
        """)
        self._glow.setBlurRadius(18 if focused else 0)

    def focusInEvent(self, event):
        self._apply_style(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._apply_style(False)
        super().focusOutEvent(event)


class IlluminatedButton(QPushButton):
    """A square physical-looking button that glows when selected, instead
    of a flat modern button that just changes background color."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._selected = False
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        # Qt only activates a plain button on Return/Enter (not just Space)
        # when it's marked as a "default" button -- normally a dialog
        # concept, but needed here too since every screen in this app
        # treats Enter/Return/Space as the same "activate" action.
        self.setAutoDefault(True)
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setColor(QColor(theme.AMBER))
        self._glow.setOffset(0, 0)
        self._glow.setBlurRadius(0)
        self.setGraphicsEffect(self._glow)
        self._apply_style()

    def set_selected(self, selected: bool):
        self._selected = selected
        self._glow.setBlurRadius(28 if selected else 0)
        self._apply_style()

    # When a button is used somewhere that relies on Qt's real focus
    # system (e.g. mixed with a text field, like in Settings) rather than
    # a screen's own manual index-based selection, the glow still follows
    # focus automatically -- no extra wiring needed either way.
    def focusInEvent(self, event):
        self.set_selected(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.set_selected(False)
        super().focusOutEvent(event)

    def _apply_style(self):
        if self._selected:
            bg, border, fg = theme.AMBER, theme.AMBER, "#1a1208"
        else:
            bg, border, fg = theme.PANEL_RAISED, theme.BORDER, theme.TEXT
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 6px;
                color: {fg};
                font-weight: bold;
                font-size: 13pt;
                letter-spacing: 1px;
                padding: 10px;
            }}
        """)
