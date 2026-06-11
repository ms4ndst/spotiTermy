"""Modal screens: search, devices, spotagen menu, settings hint."""
from __future__ import annotations

from typing import Callable

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, ListItem, ListView, Static

from .ai import CuratedTrack, call_ai
from .config import Settings
from .spotify_client import Device, SpotifyClient, Track


class SearchScreen(ModalScreen[str]):
    """A single-input search modal. Result string returned via dismiss()."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, placeholder: str = "Search Spotify...") -> None:
        super().__init__()
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Container(id="modal"):
            yield Static("Search", id="modal-title")
            yield Input(placeholder=self._placeholder, id="search-input")
            yield Static("Press Enter to search, Esc to cancel", classes="muted")

    def on_mount(self) -> None:
        self.query_one("#search-input", Input).focus()

    @on(Input.Submitted, "#search-input")
    def _submit(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        self.dismiss("")


class DeviceScreen(ModalScreen[str | None]):
    """Pick a playback device. Returns device_id or None on cancel."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, devices: list[Device]) -> None:
        super().__init__()
        self._devices = devices

    def compose(self) -> ComposeResult:
        with Container(id="modal"):
            yield Static("Devices", id="modal-title")
            items = [
                ListItem(Static(
                    f"{'[*]' if d.active else '   '}  {d.name}  ({d.kind})"
                )) for d in self._devices
            ] or [ListItem(Static("No devices found - open Spotify on a device first", classes="muted"))]
            yield ListView(*items, id="dev-list")
            yield Static("Enter = select, Esc = cancel", classes="muted")

    def on_mount(self) -> None:
        self.query_one("#dev-list", ListView).focus()

    @on(ListView.Selected, "#dev-list")
    def _selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index or 0
        if not self._devices:
            self.dismiss(None)
            return
        self.dismiss(self._devices[idx].id)

    def action_cancel(self) -> None:
        self.dismiss(None)


# --------------------------------------------------------------------------- #
# Spotagen menu - the AI playlist generator
# --------------------------------------------------------------------------- #


SPOTAGEN_MODES: tuple[tuple[str, str, str], ...] = (
    ("curate",       "Curate from seed artists (AI)",    "Comma-separated artists you already like"),
    ("discover",     "Discover artists like ... (AI)",   "Comma-separated artists to pivot from"),
    ("genre",        "Build by genre / vibe brief (AI)", "A genre name or free-form brief"),
    ("genre_tag",    "By Spotify genre tag (no AI)",     "Genre tag, e.g. dream pop, shoegaze, lo-fi"),
)


class SpotagenMenu(ModalScreen[None]):
    """Two-step modal: pick a mode, enter a seed, then create the playlist.

    Calls `ai.call_ai()` (uses Claude / OpenAI / Mistral / Ollama based on
    settings). The resulting `CuratedTrack` list is resolved to Spotify URIs
    via `client.search` and added to a newly-created playlist.
    """

    BINDINGS = [("escape", "cancel", "Close")]

    def __init__(self, client: SpotifyClient, settings: Settings) -> None:
        super().__init__()
        self.client = client
        self.settings = settings

    def compose(self) -> ComposeResult:
        with Container(id="modal"):
            yield Static("spotagen - AI playlist curator", id="modal-title")
            ai = self.settings.ai
            ai_ok = ai.provider != "none" and _has_provider_key(self.settings)
            if ai_ok:
                yield Static(f"Provider: {ai.provider}", classes="accent")
            else:
                yield Static(
                    "AI provider not configured - only 'By Spotify genre tag' "
                    "works without one. Edit\n"
                    f"   {_config_hint()}\n"
                    "and set [ai].provider plus the matching api_key for AI modes.",
                    classes="status-warn",
                )
            # Disable AI-backed modes when no provider is set, but keep the
            # genre_tag mode usable - it talks straight to Spotify.
            items: list[ListItem] = []
            for key, label, _ in SPOTAGEN_MODES:
                is_ai = key != "genre_tag"
                if is_ai and not ai_ok:
                    items.append(ListItem(
                        Static(f"{label}  (disabled - no AI provider)", classes="muted"),
                        id=f"mode-{key}",
                    ))
                else:
                    items.append(ListItem(Static(label), id=f"mode-{key}"))
            yield ListView(*items, id="mode-list")
            yield Static("Enter = choose mode, Esc = close", classes="muted")
            yield Input(placeholder="(pick a mode first)", disabled=True, id="seed-input")
            yield Static("", id="seed-help", classes="muted")
            yield Static("", id="seed-status", classes="muted")

    def on_mount(self) -> None:
        try:
            self.query_one("#mode-list", ListView).focus()
        except Exception:
            pass

    @on(ListView.Selected, "#mode-list")
    def _mode_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index or 0
        key, label, help_text = SPOTAGEN_MODES[idx]
        ai_ok = self.settings.ai.provider != "none" and _has_provider_key(self.settings)
        if key != "genre_tag" and not ai_ok:
            self.query_one("#seed-help", Static).update(
                "This mode needs an AI provider. Use 'By Spotify genre tag' instead, "
                "or configure [ai] in the config file."
            )
            return
        self._mode = key
        seed = self.query_one("#seed-input", Input)
        seed.disabled = False
        seed.placeholder = help_text
        seed.focus()
        self.query_one("#seed-help", Static).update(f"Mode: {label}")

    @on(Input.Submitted, "#seed-input")
    def _seed_submitted(self, event: Input.Submitted) -> None:
        seed_text = event.value.strip()
        if not seed_text:
            return
        mode = getattr(self, "_mode", "curate")
        if mode == "genre_tag":
            self.query_one("#seed-status", Static).update(
                f"[*] Searching Spotify artists tagged '{seed_text}'..."
            )
            self._run_genre_tag(seed_text)
        else:
            self.query_one("#seed-status", Static).update(
                "[*] Asking the model, then resolving tracks on Spotify..."
            )
            self._run_curation(seed_text)

    @work(thread=True)
    def _run_curation(self, seed: str) -> None:
        mode = getattr(self, "_mode", "curate")
        curated = call_ai(self.settings, mode, seed, count=25)
        self.app.call_from_thread(self._finish_curation, mode, seed, curated)

    @work(thread=True)
    def _run_genre_tag(self, genre: str) -> None:
        """No-AI flow: pull artists tagged with this Spotify genre, then
        gather their top tracks. Mirrors `spotagen by-genre` with the
        quoted-query fix so multi-word tags like 'dream pop' actually match.
        """
        artists = self.client.artists_in_genre(genre, limit=20)
        uris: list[str] = []
        for aid, _name in artists:
            tracks = self.client.artist_top_tracks(aid)
            for t in tracks:
                if t.uri and t.kind == "track":
                    uris.append(t.uri)
            if len(uris) >= 60:
                break
        # Trim and shuffle in-place would change order; just cap.
        uris = uris[:60]
        self.app.call_from_thread(self._finish_genre_tag, genre, len(artists), uris)

    def _finish_genre_tag(self, genre: str, n_artists: int, uris: list[str]) -> None:
        status = self.query_one("#seed-status", Static)
        if not uris:
            status.update(
                f"[x] No artists found for genre '{genre}'. Try the exact "
                "Spotify tag (e.g. 'dream pop', 'shoegaze')."
            )
            status.add_class("status-error")
            return
        title = f"spotagen: genre - {genre[:40]}"
        playlist = self.client.create_playlist(
            name=title, description=f"By Spotify genre tag: {genre}",
        )
        if not playlist:
            status.update("[x] Could not create playlist (check playlist-modify-* scopes).")
            status.add_class("status-error")
            return
        self.client.playlist_add_tracks(playlist.id, uris)
        status.update(
            f"[v] Created '{playlist.name}' - {n_artists} artists, {len(uris)} tracks."
        )
        status.add_class("status-ok")
        self.app.post_message(PlaylistsChanged())

    def _finish_curation(self, mode: str, seed: str, curated: list[CuratedTrack]) -> None:
        status = self.query_one("#seed-status", Static)
        if not curated:
            status.update("[x] No tracks suggested (model returned nothing).")
            status.add_class("status-error")
            return

        # Resolve each "Artist - Track" to a Spotify URI.
        uris: list[str] = []
        resolved: list[str] = []
        for c in curated:
            q = f"artist:{c.artist} track:{c.track}"
            results = self.client.search(q)
            uri = next((t.uri for t in results if t.kind == "track" and t.uri), None)
            if not uri:
                # Fallback: looser search.
                results = self.client.search(f"{c.artist} {c.track}")
                uri = next((t.uri for t in results if t.kind == "track" and t.uri), None)
            if uri:
                uris.append(uri)
                resolved.append(f"{c.artist} - {c.track}")

        if not uris:
            status.update("[x] Could not resolve any of the suggested tracks on Spotify.")
            status.add_class("status-error")
            return

        title = f"spotagen: {mode} - {seed[:40]}"
        playlist = self.client.create_playlist(name=title, description=f"spotagen {mode} - seed: {seed}")
        if not playlist:
            status.update("[x] Could not create playlist (check playlist-modify-* scopes).")
            status.add_class("status-error")
            return
        self.client.playlist_add_tracks(playlist.id, uris)
        status.update(f"[v] Created '{playlist.name}' with {len(uris)} tracks.")
        status.add_class("status-ok")
        # Tell the app to refresh playlists list.
        self.app.post_message(PlaylistsChanged())

    def action_cancel(self) -> None:
        self.dismiss(None)


def _has_provider_key(s: Settings) -> bool:
    ai = s.ai
    if ai.provider == "claude":  return bool(ai.claude_api_key)
    if ai.provider == "openai":  return bool(ai.openai_api_key)
    if ai.provider == "mistral": return bool(ai.mistral_api_key)
    if ai.provider == "ollama":  return bool(ai.ollama_base_url)
    return False


def _config_hint() -> str:
    from .config import config_path
    return str(config_path())


# Message used by SpotagenMenu to tell the app to reload playlists.
from textual.message import Message  # noqa: E402


class PlaylistsChanged(Message):
    """Fired after spotagen creates a new playlist."""
    pass


# --------------------------------------------------------------------------- #
# First-run helper
# --------------------------------------------------------------------------- #


class AuthHelpScreen(ModalScreen[None]):
    BINDINGS = [("escape,enter,space,q", "close", "Close")]

    def __init__(self, config_path: str) -> None:
        super().__init__()
        self._path = config_path

    def compose(self) -> ComposeResult:
        with Container(id="modal"):
            yield Static("spotiTermy - first run", id="modal-title")
            yield Static(
                "Spotify credentials are not configured.\n\n"
                "1. Create an app at https://developer.spotify.com/dashboard\n"
                "2. Add this redirect URI:    http://127.0.0.1:8888/callback\n"
                f"3. Edit:   {self._path}\n"
                "   set [spotify].client_id and [spotify].client_secret\n\n"
                "Alternatively, set the env vars:\n"
                "   SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI\n\n"
                "Then restart spotitermy.",
                classes="label",
            )
            yield Static("Press any key to exit.", classes="muted")

    def action_close(self) -> None:
        self.app.exit()
