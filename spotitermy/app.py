"""Textual application for spotiTermy."""
from __future__ import annotations

from typing import Optional

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, ListItem, ListView, Static

from . import __version__
from .config import (
    ensure_default_config,
    config_path,
    load_settings,
    save_settings,
)
from .screens import (
    AuthHelpScreen,
    DeviceScreen,
    PlaylistsChanged,
    SearchScreen,
    SpotagenMenu,
)
from .spotify_client import SpotifyClient, Track
from .theme import FLAVORS, VALID_ACCENTS, build_textual_css
from .widgets import LIBRARY_ITEMS, LibraryPane, NowPlaying, PlaylistsPane, TracksPane


class SpotiTermyApp(App[None]):
    """Catppuccin-themed Spotify TUI.

    Layout (inspired by spotui):

        +---------------------+----------------------------------+
        | Library             | Tracks                           |
        +---------------------+                                  |
        | Playlists           |                                  |
        +---------------------+----------------------------------+
        | Now Playing                                            |
        +--------------------------------------------------------+
        | Footer (keybindings)                                   |
        +--------------------------------------------------------+
    """

    TITLE = "spotiTermy"
    SUB_TITLE = f"v{__version__}"

    BINDINGS = [
        ("space", "toggle_playback", "Play/Pause"),
        ("n", "next_track", "Next"),
        ("p", "previous_track", "Prev"),
        ("s", "toggle_shuffle", "Shuffle"),
        ("r", "cycle_repeat", "Repeat"),
        ("right", "seek_forward", "+10s"),
        ("left", "seek_backward", "-10s"),
        ("slash", "search", "Search"),
        ("d", "devices", "Devices"),
        ("g", "spotagen", "spotagen AI"),
        ("t", "cycle_theme", "Theme"),
        ("tab", "focus_next", "Next pane"),
        ("shift+tab", "focus_previous", "Prev pane"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        flavor_override: Optional[str] = None,
        accent_override: Optional[str] = None,
    ) -> None:
        super().__init__()
        ensure_default_config()
        self.settings = load_settings()
        if flavor_override:
            self.settings.ui.flavor = flavor_override
        if accent_override:
            self.settings.ui.accent = accent_override
        if self.settings.ui.flavor not in FLAVORS:
            self.settings.ui.flavor = "mocha"
        if self.settings.ui.accent not in VALID_ACCENTS:
            self.settings.ui.accent = "mauve"

        self.CSS = build_textual_css(self.settings.ui.flavor, self.settings.ui.accent)

        self.client = SpotifyClient(self.settings)
        self.device_id: str | None = None
        self.current_tracklist_label = "Top Tracks"

    # ----- compose ----- #

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main"):
            with Vertical(id="left-col"):
                yield LibraryPane()
                yield PlaylistsPane()
            with Vertical(id="right-col"):
                yield TracksPane()
        yield NowPlaying()
        yield Footer()

    # ----- lifecycle ----- #

    def on_mount(self) -> None:
        if not self.client.authenticate():
            self.push_screen(AuthHelpScreen(str(config_path())))
            return
        # Persist any username the client back-filled.
        save_settings(self.settings)
        self._initial_load()
        self.set_interval(2.0, self._poll_playback)

    @work(thread=True)
    def _initial_load(self) -> None:
        playlists = self.client.playlists()
        tracks = self.client.top_tracks()
        devs = self.client.devices()
        self.call_from_thread(self._apply_initial, playlists, tracks, devs)

    def _apply_initial(self, playlists, tracks, devs) -> None:
        self.query_one(PlaylistsPane).update_playlists(playlists)
        self.query_one(TracksPane).set_tracks(tracks, "Top Tracks")
        for d in devs:
            if d.active:
                self.device_id = d.id
                break
        if not self.device_id and devs:
            self.device_id = devs[0].id

    # ----- polling ----- #

    @work(thread=True)
    def _poll_playback(self) -> None:
        payload = self.client.current_playback()
        self.call_from_thread(self.query_one(NowPlaying).update_playback, payload)

    # ----- pane events ----- #

    @on(ListView.Selected, "#library-list")
    def _library_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index or 0
        key, label = LIBRARY_ITEMS[idx]
        self._load_library(key, label)

    @work(thread=True)
    def _load_library(self, key: str, label: str) -> None:
        if key == "top":
            tracks = self.client.top_tracks()
        elif key == "recent":
            tracks = self.client.recently_played()
        elif key == "liked":
            tracks = self.client.saved_tracks()
        else:
            tracks = []
        self.call_from_thread(self.query_one(TracksPane).set_tracks, tracks, label)
        self.current_tracklist_label = label

    @on(ListView.Selected, "#playlists-list")
    def _playlist_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index or 0
        playlists = self.query_one(PlaylistsPane).items
        if idx < 0 or idx >= len(playlists):
            return
        p = playlists[idx]
        self._load_playlist(p.id, p.name, p.uri)

    @work(thread=True)
    def _load_playlist(self, pid: str, label: str, uri: str) -> None:
        tracks = self.client.playlist_tracks(pid)
        self.call_from_thread(self.query_one(TracksPane).set_tracks, tracks, label)
        self.current_tracklist_label = label

    @on(DataTable.RowSelected, "#tracks-table")
    def _track_row_selected(self, event: DataTable.RowSelected) -> None:
        tracks = self.query_one(TracksPane).tracks
        idx = event.cursor_row
        if idx is None or idx < 0 or idx >= len(tracks):
            return
        track = tracks[idx]
        if track.kind == "playlist":
            self._load_playlist(track.id, track.name, track.uri)
            return
        if not self.device_id:
            self.notify("No active device. Press 'd' to pick one.", severity="warning")
            return
        # Play the whole tracklist starting at this track.
        uris = [t.uri for t in tracks if t.kind == "track" and t.uri]
        self.client.start_playback(device_id=self.device_id, uris=uris, offset_uri=track.uri)

    # ----- actions ----- #

    def action_toggle_playback(self) -> None:
        payload = self.client.current_playback()
        if not payload:
            if self.device_id:
                self.client.resume(self.device_id)
            return
        if payload.get("is_playing"):
            self.client.pause(self.device_id)
        else:
            self.client.resume(self.device_id)

    def action_next_track(self) -> None:
        self.client.next_track(self.device_id)

    def action_previous_track(self) -> None:
        self.client.previous_track(self.device_id)

    def action_toggle_shuffle(self) -> None:
        payload = self.client.current_playback() or {}
        new = not bool(payload.get("shuffle_state"))
        self.client.toggle_shuffle(new, self.device_id)

    def action_cycle_repeat(self) -> None:
        payload = self.client.current_playback() or {}
        cur = str(payload.get("repeat_state") or "off")
        order = {"off": "context", "context": "track", "track": "off"}
        self.client.cycle_repeat(order.get(cur, "off"), self.device_id)

    def action_seek_forward(self) -> None:
        payload = self.client.current_playback() or {}
        pos = int(payload.get("progress_ms") or 0)
        self.client.seek(pos + 10_000, self.device_id)

    def action_seek_backward(self) -> None:
        payload = self.client.current_playback() or {}
        pos = int(payload.get("progress_ms") or 0)
        self.client.seek(max(0, pos - 10_000), self.device_id)

    @work
    async def action_search(self) -> None:
        query = await self.push_screen_wait(SearchScreen())
        if not query:
            return
        self._run_search(query)

    @work(thread=True)
    def _run_search(self, query: str) -> None:
        results = self.client.search(query)
        self.call_from_thread(
            self.query_one(TracksPane).set_tracks, results, f"Search: {query}"
        )
        self.current_tracklist_label = f"Search: {query}"

    @work
    async def action_devices(self) -> None:
        devices = self.client.devices()
        chosen = await self.push_screen_wait(DeviceScreen(devices))
        if chosen:
            self.device_id = chosen
            self.client.transfer_playback(chosen, play=False)
            self.notify(f"Playback transferred", severity="information")

    def action_spotagen(self) -> None:
        self.push_screen(SpotagenMenu(self.client, self.settings))

    def action_cycle_theme(self) -> None:
        order = ("mocha", "macchiato", "frappe", "latte")
        try:
            i = order.index(self.settings.ui.flavor)
        except ValueError:
            i = 0
        new_flavor = order[(i + 1) % len(order)]
        self.settings.ui.flavor = new_flavor
        save_settings(self.settings)
        # Rebuild the stylesheet at runtime.
        self.stylesheet.clear()
        self.stylesheet.parse(build_textual_css(new_flavor, self.settings.ui.accent))
        self.stylesheet.apply(self)
        self.notify(f"Theme: catppuccin {new_flavor}", severity="information")

    # ----- messages ----- #

    @on(PlaylistsChanged)
    def _reload_playlists(self, _msg: PlaylistsChanged) -> None:
        self._refresh_playlists()

    @work(thread=True)
    def _refresh_playlists(self) -> None:
        pls = self.client.playlists()
        self.call_from_thread(self.query_one(PlaylistsPane).update_playlists, pls)
