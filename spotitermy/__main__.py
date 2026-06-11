"""Entry point: `python -m spotitermy` or `spotitermy`."""
from __future__ import annotations

import argparse
import sys

from . import __version__


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="spotitermy",
        description="Catppuccin-themed Spotify TUI with AI playlist curation.",
    )
    parser.add_argument("--version", action="version", version=f"spotitermy {__version__}")
    parser.add_argument(
        "--flavor",
        choices=("mocha", "latte", "frappe", "macchiato"),
        default=None,
        help="Override Catppuccin flavor for this run.",
    )
    parser.add_argument(
        "--accent",
        choices=("mauve", "blue", "lavender", "peach", "teal", "sky", "green"),
        default=None,
        help="Override accent color for this run.",
    )
    args = parser.parse_args()

    from .app import SpotiTermyApp

    app = SpotiTermyApp(flavor_override=args.flavor, accent_override=args.accent)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
