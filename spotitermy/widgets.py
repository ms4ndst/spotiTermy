"""TUI widgets composed in app.py.

Each pane is a thin Container around a list view + a title bar. Roles
follow the catppuccin style guide: panels are .pane (round border on
Surface1, lifts to accent on focus).
"""
from __future__ import annotations

from typing import Iterable

from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import DataTable, ListItem, ListView, Static

from .spotify_client import Device, Playlist, Track, format_duration


# --- Library (left top) ----------------------------------------------------- #


LIBRARY_ITEMS: tuple[tuple[str, str], ...] = (
    ("top",    "Top Tracks"),
    ("recent", "Recently Played"),
    ("liked",  "Liked Songs"),
)


class LibraryPane(Container):
    """Top-left pane: built-in playlists/sources."""

    DEFAULT_CSS = ""

    def __init__(self) -> None:
        super().__init__(id="library", classes="pane")
        self.border_title = "Library"

    def compose(self):
        items = [
            ListItem(Static(label), id=f"lib-{key}")
            for key, label in LIBRARY_ITEMS
        ]
        yield ListView(*items, id="library-list")


# --- Playlists (left bottom) ------------------------------------------------ #


class PlaylistsPane(Container):
    def __init__(self) -> None:
        super().__init__(id="playlists", classes="pane")
        self.border_title = "Playlists"
        self._items: list[Playlist] = []

    def compose(self):
        yield ListView(id="playlists-list")

    def update_playlists(self, playlists: Iterable[Playlist]) -> None:
        self._items = list(playlists)
        view = self.query_one("#playlists-list", ListView)
        view.clear()
        for p in self._items:
            view.append(ListItem(Static(p.name or "(untitled)")))

    @property
    def items(self) -> list[Playlist]:
        return self._items


# --- Tracks (right) --------------------------------------------------------- #


class TracksPane(Container):
    """Right pane: a DataTable of tracks for the selected source."""

    title: reactive[str] = reactive("Tracks")

    def __init__(self) -> None:
        super().__init__(id="tracks", classes="pane pane-right")
        self.border_title = "Tracks"
        self._tracks: list[Track] = []

    def compose(self):
        table: DataTable = DataTable(zebra_stripes=False, cursor_type="row", id="tracks-table")
        table.add_columns("#", "Title", "Artist", "Album", "Time")
        yield table

    def set_tracks(self, tracks: Iterable[Track], title: str) -> None:
        self._tracks = list(tracks)
        self.border_title = f"Tracks - {title}"
        table = self.query_one("#tracks-table", DataTable)
        table.clear()
        for idx, t in enumerate(self._tracks, 1):
            table.add_row(
                str(idx),
                t.name,
                t.artist,
                t.album,
                format_duration(t.duration_ms),
            )

    def selected_track(self) -> Track | None:
        table = self.query_one("#tracks-table", DataTable)
        try:
            row = table.cursor_row
        except Exception:
            return None
        if row is None or row < 0 or row >= len(self._tracks):
            return None
        return self._tracks[row]

    @property
    def tracks(self) -> list[Track]:
        return self._tracks


# --- Now Playing (footer above Textual Footer) ------------------------------ #


class NowPlaying(Container):
    """Bottom pane with current track, artist, status, and progress bar."""

    def __init__(self) -> None:
        super().__init__(id="now-playing")

    def compose(self):
        yield Static("Nothing playing", id="np-title")
        yield Static("", id="np-artist")
        yield Static("", id="np-progress")

    def update_playback(self, payload: dict | None) -> None:
        title = self.query_one("#np-title", Static)
        artist = self.query_one("#np-artist", Static)
        progress = self.query_one("#np-progress", Static)

        if not payload or not payload.get("item"):
            title.update("Nothing playing")
            artist.update("")
            progress.update("")
            return

        item = payload["item"]
        name = item.get("name", "")
        artists = item.get("artists") or []
        artist_str = ", ".join(a.get("name", "") for a in artists) if artists else ""
        if not artist_str and item.get("show"):
            artist_str = item["show"].get("publisher") or ""

        is_playing = bool(payload.get("is_playing"))
        shuffle = bool(payload.get("shuffle_state"))
        repeat = str(payload.get("repeat_state") or "off")

        title.update(name)
        artist.update(artist_str)

        pos = int(payload.get("progress_ms") or 0)
        dur = int(item.get("duration_ms") or 0)
        pct = (pos / dur) if dur else 0.0
        bar_w = 30
        filled = int(bar_w * pct)
        bar = "#" * filled + "-" * (bar_w - filled)
        state = ">" if is_playing else "||"
        device = (payload.get("device") or {}).get("name") or ""
        progress.update(
            f"{state}  {format_duration(pos)} [{bar}] {format_duration(dur)}   "
            f"shuffle:{'on' if shuffle else 'off'}  repeat:{repeat}   "
            f"device: {device}"
        )
