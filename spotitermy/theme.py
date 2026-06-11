"""Catppuccin palette and Textual CSS generator.

All four official Catppuccin flavors. The Mocha + Mauve combination is the
default. Constants are named so flavor switching is a single lookup.

Per the catppuccin skill: pick by role, never by hex.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# --------------------------------------------------------------------------- #
# Mocha (default - dark)
# --------------------------------------------------------------------------- #
MOCHA_BASE: Final = "#1e1e2e"
MOCHA_MANTLE: Final = "#181825"
MOCHA_CRUST: Final = "#11111b"
MOCHA_SURFACE0: Final = "#313244"
MOCHA_SURFACE1: Final = "#45475a"
MOCHA_SURFACE2: Final = "#585b70"
MOCHA_OVERLAY0: Final = "#6c7086"
MOCHA_OVERLAY1: Final = "#7f849c"
MOCHA_OVERLAY2: Final = "#9399b2"
MOCHA_SUBTEXT0: Final = "#a6adc8"
MOCHA_SUBTEXT1: Final = "#bac2de"
MOCHA_TEXT: Final = "#cdd6f4"
MOCHA_ROSEWATER: Final = "#f5e0dc"
MOCHA_FLAMINGO: Final = "#f2cdcd"
MOCHA_PINK: Final = "#f5c2e7"
MOCHA_MAUVE: Final = "#cba6f7"
MOCHA_RED: Final = "#f38ba8"
MOCHA_MAROON: Final = "#eba0ac"
MOCHA_PEACH: Final = "#fab387"
MOCHA_YELLOW: Final = "#f9e2af"
MOCHA_GREEN: Final = "#a6e3a1"
MOCHA_TEAL: Final = "#94e2d5"
MOCHA_SKY: Final = "#89dceb"
MOCHA_SAPPHIRE: Final = "#74c7ec"
MOCHA_BLUE: Final = "#89b4fa"
MOCHA_LAVENDER: Final = "#b4befe"

# --------------------------------------------------------------------------- #
# Latte (light)
# --------------------------------------------------------------------------- #
LATTE_BASE: Final = "#eff1f5"
LATTE_MANTLE: Final = "#e6e9ef"
LATTE_CRUST: Final = "#dce0e8"
LATTE_SURFACE0: Final = "#ccd0da"
LATTE_SURFACE1: Final = "#bcc0cc"
LATTE_SURFACE2: Final = "#acb0be"
LATTE_OVERLAY0: Final = "#9ca0b0"
LATTE_OVERLAY1: Final = "#8c8fa1"
LATTE_OVERLAY2: Final = "#7c7f93"
LATTE_SUBTEXT0: Final = "#6c6f85"
LATTE_SUBTEXT1: Final = "#5c5f77"
LATTE_TEXT: Final = "#4c4f69"
LATTE_ROSEWATER: Final = "#dc8a78"
LATTE_FLAMINGO: Final = "#dd7878"
LATTE_PINK: Final = "#ea76cb"
LATTE_MAUVE: Final = "#8839ef"
LATTE_RED: Final = "#d20f39"
LATTE_MAROON: Final = "#e64553"
LATTE_PEACH: Final = "#fe640b"
LATTE_YELLOW: Final = "#df8e1d"
LATTE_GREEN: Final = "#40a02b"
LATTE_TEAL: Final = "#179299"
LATTE_SKY: Final = "#04a5e5"
LATTE_SAPPHIRE: Final = "#209fb5"
LATTE_BLUE: Final = "#1e66f5"
LATTE_LAVENDER: Final = "#7287fd"

# --------------------------------------------------------------------------- #
# Frappe (warm dark)
# --------------------------------------------------------------------------- #
FRAPPE_BASE: Final = "#303446"
FRAPPE_MANTLE: Final = "#292c3c"
FRAPPE_CRUST: Final = "#232634"
FRAPPE_SURFACE0: Final = "#414559"
FRAPPE_SURFACE1: Final = "#51576d"
FRAPPE_SURFACE2: Final = "#626880"
FRAPPE_OVERLAY0: Final = "#737994"
FRAPPE_OVERLAY1: Final = "#838ba7"
FRAPPE_OVERLAY2: Final = "#949cbb"
FRAPPE_SUBTEXT0: Final = "#a5adce"
FRAPPE_SUBTEXT1: Final = "#b5bfe2"
FRAPPE_TEXT: Final = "#c6d0f5"
FRAPPE_MAUVE: Final = "#ca9ee6"
FRAPPE_RED: Final = "#e78284"
FRAPPE_PEACH: Final = "#ef9f76"
FRAPPE_YELLOW: Final = "#e5c890"
FRAPPE_GREEN: Final = "#a6d189"
FRAPPE_TEAL: Final = "#81c8be"
FRAPPE_SKY: Final = "#99d1db"
FRAPPE_BLUE: Final = "#8caaee"
FRAPPE_LAVENDER: Final = "#babbf1"

# --------------------------------------------------------------------------- #
# Macchiato (medium dark)
# --------------------------------------------------------------------------- #
MACCHIATO_BASE: Final = "#24273a"
MACCHIATO_MANTLE: Final = "#1e2030"
MACCHIATO_CRUST: Final = "#181926"
MACCHIATO_SURFACE0: Final = "#363a4f"
MACCHIATO_SURFACE1: Final = "#494d64"
MACCHIATO_SURFACE2: Final = "#5b6078"
MACCHIATO_OVERLAY0: Final = "#6e738d"
MACCHIATO_OVERLAY1: Final = "#8087a2"
MACCHIATO_OVERLAY2: Final = "#939ab7"
MACCHIATO_SUBTEXT0: Final = "#a5adcb"
MACCHIATO_SUBTEXT1: Final = "#b8c0e0"
MACCHIATO_TEXT: Final = "#cad3f5"
MACCHIATO_MAUVE: Final = "#c6a0f6"
MACCHIATO_RED: Final = "#ed8796"
MACCHIATO_PEACH: Final = "#f5a97f"
MACCHIATO_YELLOW: Final = "#eed49f"
MACCHIATO_GREEN: Final = "#a6da95"
MACCHIATO_TEAL: Final = "#8bd5ca"
MACCHIATO_SKY: Final = "#91d7e3"
MACCHIATO_BLUE: Final = "#8aadf4"
MACCHIATO_LAVENDER: Final = "#b7bdf8"


@dataclass(frozen=True)
class Palette:
    """Catppuccin flavor with the colors needed by the TUI."""

    name: str
    base: str
    mantle: str
    crust: str
    surface0: str
    surface1: str
    surface2: str
    overlay0: str
    overlay1: str
    subtext0: str
    subtext1: str
    text: str
    mauve: str
    red: str
    peach: str
    yellow: str
    green: str
    teal: str
    sky: str
    blue: str
    lavender: str


MOCHA: Final = Palette(
    name="mocha",
    base=MOCHA_BASE, mantle=MOCHA_MANTLE, crust=MOCHA_CRUST,
    surface0=MOCHA_SURFACE0, surface1=MOCHA_SURFACE1, surface2=MOCHA_SURFACE2,
    overlay0=MOCHA_OVERLAY0, overlay1=MOCHA_OVERLAY1,
    subtext0=MOCHA_SUBTEXT0, subtext1=MOCHA_SUBTEXT1, text=MOCHA_TEXT,
    mauve=MOCHA_MAUVE, red=MOCHA_RED, peach=MOCHA_PEACH, yellow=MOCHA_YELLOW,
    green=MOCHA_GREEN, teal=MOCHA_TEAL, sky=MOCHA_SKY, blue=MOCHA_BLUE,
    lavender=MOCHA_LAVENDER,
)

LATTE: Final = Palette(
    name="latte",
    base=LATTE_BASE, mantle=LATTE_MANTLE, crust=LATTE_CRUST,
    surface0=LATTE_SURFACE0, surface1=LATTE_SURFACE1, surface2=LATTE_SURFACE2,
    overlay0=LATTE_OVERLAY0, overlay1=LATTE_OVERLAY1,
    subtext0=LATTE_SUBTEXT0, subtext1=LATTE_SUBTEXT1, text=LATTE_TEXT,
    mauve=LATTE_MAUVE, red=LATTE_RED, peach=LATTE_PEACH, yellow=LATTE_YELLOW,
    green=LATTE_GREEN, teal=LATTE_TEAL, sky=LATTE_SKY, blue=LATTE_BLUE,
    lavender=LATTE_LAVENDER,
)

FRAPPE: Final = Palette(
    name="frappe",
    base=FRAPPE_BASE, mantle=FRAPPE_MANTLE, crust=FRAPPE_CRUST,
    surface0=FRAPPE_SURFACE0, surface1=FRAPPE_SURFACE1, surface2=FRAPPE_SURFACE2,
    overlay0=FRAPPE_OVERLAY0, overlay1=FRAPPE_OVERLAY1,
    subtext0=FRAPPE_SUBTEXT0, subtext1=FRAPPE_SUBTEXT1, text=FRAPPE_TEXT,
    mauve=FRAPPE_MAUVE, red=FRAPPE_RED, peach=FRAPPE_PEACH, yellow=FRAPPE_YELLOW,
    green=FRAPPE_GREEN, teal=FRAPPE_TEAL, sky=FRAPPE_SKY, blue=FRAPPE_BLUE,
    lavender=FRAPPE_LAVENDER,
)

MACCHIATO: Final = Palette(
    name="macchiato",
    base=MACCHIATO_BASE, mantle=MACCHIATO_MANTLE, crust=MACCHIATO_CRUST,
    surface0=MACCHIATO_SURFACE0, surface1=MACCHIATO_SURFACE1, surface2=MACCHIATO_SURFACE2,
    overlay0=MACCHIATO_OVERLAY0, overlay1=MACCHIATO_OVERLAY1,
    subtext0=MACCHIATO_SUBTEXT0, subtext1=MACCHIATO_SUBTEXT1, text=MACCHIATO_TEXT,
    mauve=MACCHIATO_MAUVE, red=MACCHIATO_RED, peach=MACCHIATO_PEACH, yellow=MACCHIATO_YELLOW,
    green=MACCHIATO_GREEN, teal=MACCHIATO_TEAL, sky=MACCHIATO_SKY, blue=MACCHIATO_BLUE,
    lavender=MACCHIATO_LAVENDER,
)

FLAVORS: dict[str, Palette] = {
    "mocha":     MOCHA,
    "latte":     LATTE,
    "frappe":    FRAPPE,
    "macchiato": MACCHIATO,
}

VALID_ACCENTS: Final[frozenset[str]] = frozenset(
    {"mauve", "blue", "lavender", "peach", "teal", "sky", "green"}
)


def get_accent(palette: Palette, accent: str) -> str:
    if accent not in VALID_ACCENTS:
        raise ValueError(f"Unknown accent {accent!r}; choose one of {sorted(VALID_ACCENTS)}")
    return getattr(palette, accent)


def build_textual_css(flavor: str = "mocha", accent: str = "mauve") -> str:
    """Render the app stylesheet for the chosen flavor + accent.

    Roles applied (per catppuccin style-guide.md):
      Crust   -> deepest chrome (header band, footer)
      Mantle  -> secondary pane backgrounds
      Base    -> main app canvas
      Surface0/1/2 -> elevation steps
      Text/Subtext1/Subtext0/Overlay1 -> body / labels / hints
      Accent  -> focus borders, headers, active selection
      Lavender -> selection ring
      Green/Yellow/Red -> success/warning/error
    """
    if flavor not in FLAVORS:
        raise ValueError(f"Unknown flavor {flavor!r}; choose one of {sorted(FLAVORS)}")
    p = FLAVORS[flavor]
    a = get_accent(p, accent)

    return f"""
Screen {{
    background: {p.base};
    color: {p.text};
    layout: vertical;
}}

Header {{
    background: {p.crust};
    color: {a};
    text-style: bold;
    height: 1;
}}

Footer {{
    background: {p.crust};
    color: {p.subtext0};
}}

#main {{
    layout: horizontal;
    height: 1fr;
}}

#left-col {{
    layout: vertical;
    width: 30%;
    min-width: 24;
    background: {p.mantle};
}}

#right-col {{
    layout: vertical;
    width: 1fr;
    background: {p.base};
}}

.pane {{
    border: round {p.surface1};
    border-title-color: {p.subtext1};
    background: {p.mantle};
    margin: 0 1 0 1;
    padding: 0 1;
}}

.pane:focus-within {{
    border: round {a};
    border-title-color: {a};
}}

.pane-right {{
    background: {p.base};
}}

#now-playing {{
    height: 5;
    background: {p.crust};
    color: {p.text};
    border-top: solid {p.surface1};
    padding: 0 2;
}}

#np-title {{
    color: {p.text};
    text-style: bold;
}}

#np-artist {{
    color: {p.peach};
}}

#np-progress-bar {{
    color: {a};
    background: {p.surface0};
}}

ListView {{
    background: {p.mantle};
    color: {p.text};
}}

ListView > ListItem {{
    background: {p.mantle};
    color: {p.subtext1};
    padding: 0 1;
}}

ListView > ListItem.--highlight {{
    background: {p.surface0};
    color: {p.text};
}}

ListView:focus > ListItem.--highlight {{
    background: {a};
    color: {p.crust};
    text-style: bold;
}}

DataTable {{
    background: {p.base};
    color: {p.text};
}}

DataTable > .datatable--header {{
    background: {p.mantle};
    color: {p.lavender};
    text-style: bold;
}}

DataTable > .datatable--cursor {{
    background: {a};
    color: {p.crust};
    text-style: bold;
}}

DataTable > .datatable--hover {{
    background: {p.surface0};
}}

Input {{
    background: {p.surface0};
    color: {p.text};
    border: tall {p.surface1};
}}

Input:focus {{
    border: tall {a};
}}

Button {{
    background: {p.surface0};
    color: {p.text};
    border: tall {p.surface1};
}}

Button:hover {{
    background: {p.surface1};
}}

Button.-primary {{
    background: {a};
    color: {p.crust};
    text-style: bold;
}}

Button.-error {{
    background: {p.red};
    color: {p.crust};
}}

.status-ok    {{ color: {p.green}; }}
.status-warn  {{ color: {p.yellow}; }}
.status-error {{ color: {p.red}; }}
.muted        {{ color: {p.overlay1}; }}
.label        {{ color: {p.subtext1}; }}
.accent       {{ color: {a}; text-style: bold; }}
.artist       {{ color: {p.peach}; }}
.track        {{ color: {p.teal}; }}

ModalScreen {{
    align: center middle;
}}

#modal {{
    background: {p.mantle};
    border: round {a};
    padding: 1 2;
    width: 70;
    height: auto;
    max-height: 80%;
}}

#modal-title {{
    color: {a};
    text-style: bold;
    margin: 0 0 1 0;
}}
"""
