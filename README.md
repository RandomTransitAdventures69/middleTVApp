# MiddleTV (app)

Want the simplicity of middleTV but don't want to install an OS? this is the underlying app (middleTV is a distro pending based TV OS)  of the OS!


middleTV: https://github.com/RandomTransitAdventures69/middleTV/

## Look and feel

Dark equipment-panel aesthetic — 80s/90s pro-audio gear and an old car
dashboard at night. Reusable pieces live in `ui/instruments.py`:
`SegmentedDisplay` (7-segment digits, used by the new native Clock),
`IlluminatedButton` (physical-looking buttons that glow amber when
selected, used for every tile and the profile button), and `StatusLED`.
Colors and surfaces are in `core/theme.py`. This is the foundation the
rest of the app (Settings, new apps) will be built on, rather than
redone later.

One thing worth knowing: the glow effect is real-time blurring, which
is GPU-accelerated on a normal machine but can look slow in a sandbox
with no graphics hardware (like the one I tested this in) — not
something I'd expect on your actual machine.

## What's in this phase

- Profile switcher ("Who's watching?") shown first on every launch, as you
  asked for — picking a profile goes on to the home screen
- The home tile grid, arrow-key navigable, including up into the profile
  button from the top row
- **Esc always goes back**, everywhere — including out of an embedded web
  page, which took real work to get right (see "How Esc works," below)
- Jellyfin, YouTube, Flight Tracker, and Clock all open **inside the app**,
  in a real embedded browser engine — not a popup, not the system browser.
  This is the only place any web rendering happens; everything else here
  is plain native Qt widgets
- YouTube (and Jellyfin) logins persist on their own — the embedded engine
  keeps its own saved cookies/storage automatically, same as a real browser
- Settings, Files, About show a placeholder for now, same as before

Not built yet: Settings itself (updates/installs, media server config,
startup video/animation, notifications, and whatever else lands there),
Files, About.

## Setup

    pip install -r requirements.txt
    python3 main.py

### Linux only: one extra package

Qt's windowing needs `libxcb-cursor0`, which isn't always preinstalled:

    sudo apt install libxcb-cursor0      # Debian/Ubuntu
    sudo dnf install xcb-util-cursor     # Fedora
    sudo pacman -S xcb-util-cursor       # Arch

## The honest gap: this still needs Python and pip installed

Right now this needs Python 3 and the one `pip install` above — it does
**not** yet meet "no extra installs," which was the whole point of the
rewrite in the first place.

The fix is to package it into a single executable (PyInstaller is the
standard tool), so what you'd actually run is one `.exe`/binary with
Python and PySide6 already baked in — nothing for you to install. I
haven't done that packaging step yet in this round; it's a reasonably
mechanical next step, flagging it now rather than glossing over it.
Worth knowing up front: a PySide6 app packaged this way typically lands
around 100–150 MB (Qt is a big framework), noticeably larger than the Go
build was.

## How Esc works inside embedded pages

Jellyfin/YouTube/etc. run in a real embedded Chromium engine, which
normally keeps keyboard input to itself — a plain "Esc closes this" rule
at the Qt level doesn't reliably reach it. To make Esc still work there,
a small script is injected into the embedded page that watches for Esc
and signals back to the app through the page's title (invisibly — the
real title is restored right after). It's a workaround, not a hack with
side effects: nothing about it is visible or changes how the embedded
page behaves otherwise.

## Controls

- Arrow keys — move the selection
- Enter / Return / Space — activate what's selected
- Esc — go back, always, from anywhere
