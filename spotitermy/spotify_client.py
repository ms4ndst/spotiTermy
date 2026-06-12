"""Thin spotipy wrapper for spotiTermy.

Authentication: Authorization Code Flow (the only OAuth flow on
ref/spotify-web-api.md that returns a refresh token AND lets us read
user-context data).

Every call is wrapped in `_safe` - the TUI must keep running even when a
single endpoint 429s or 5xxs. The wrapper returns `None` / `[]` on error
so callers can render an empty state without a try/except.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from .config import Settings, SPOTIFY_SCOPES, token_cache_path


@dataclass
class Track:
    id: str
    uri: str
    name: str
    artist: str
    album: str
    duration_ms: int
    kind: str = "track"   # "track" | "episode" | "show" | "playlist"


@dataclass
class Playlist:
    id: str
    uri: str
    name: str
    owner: str
    track_count: int


@dataclass
class Device:
    id: str
    name: str
    kind: str
    active: bool


class SpotifyClient:
    """Wraps `spotipy.Spotify` with TUI-friendly return types."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._sp: spotipy.Spotify | None = None

    # ----- auth ----- #

    def authenticate(self) -> bool:
        s = self.settings.spotify
        if not (s.client_id and s.client_secret):
            return False
        auth = SpotifyOAuth(
            client_id=s.client_id,
            client_secret=s.client_secret,
            redirect_uri=s.redirect_uri,
            scope=SPOTIFY_SCOPES,
            cache_path=str(token_cache_path()),
            open_browser=True,
            show_dialog=False,
        )
        self._sp = spotipy.Spotify(auth_manager=auth, requests_timeout=15, retries=2)
        # touch a no-op endpoint so we surface auth errors early
        try:
            me = self._sp.current_user()
            if me and not s.username:
                self.settings.spotify.username = me.get("id", "")
            return True
        except Exception:
            self._sp = None
            return False

    @property
    def sp(self) -> spotipy.Spotify:
        if self._sp is None:
            raise RuntimeError("SpotifyClient is not authenticated.")
        return self._sp

    @property
    def is_ready(self) -> bool:
        return self._sp is not None

    # ----- safe call helper ----- #

    @staticmethod
    def _safe(call, default=None):
        try:
            return call()
        except Exception:
            return default

    # ----- library ----- #

    def top_tracks(self) -> list[Track]:
        data = self._safe(lambda: self.sp.current_user_top_tracks(limit=50), {}) or {}
        return [_to_track(item) for item in (data.get("items") or []) if item]

    def recently_played(self) -> list[Track]:
        data = self._safe(lambda: self.sp.current_user_recently_played(limit=50), {}) or {}
        seen: set[str] = set()
        out: list[Track] = []
        for item in (data.get("items") or []):
            if not item:
                continue
            t = item.get("track") or {}
            if not t:
                continue
            tid = t.get("id") or t.get("uri", "")
            if tid in seen:
                continue
            seen.add(tid)
            out.append(_to_track(t))
        return out

    def saved_tracks(self) -> list[Track]:
        data = self._safe(lambda: self.sp.current_user_saved_tracks(limit=50), {}) or {}
        out: list[Track] = []
        for item in (data.get("items") or []):
            if not item:
                continue
            t = item.get("track") or {}
            if t:
                out.append(_to_track(t))
        return out

    def playlists(self) -> list[Playlist]:
        out: list[Playlist] = []
        offset = 0
        while True:
            data = self._safe(
                lambda: self.sp.current_user_playlists(limit=50, offset=offset), {}
            ) or {}
            items = data.get("items") or []
            if not items:
                break
            for p in items:
                if not p:
                    continue
                out.append(Playlist(
                    id=str(p.get("id") or ""),
                    uri=str(p.get("uri") or ""),
                    name=str(p.get("name") or ""),
                    owner=str((p.get("owner") or {}).get("display_name") or ""),
                    track_count=int(((p.get("tracks") or {}).get("total")) or 0),
                ))
            if len(items) < 50:
                break
            offset += 50
        return out

    def playlist_tracks(self, playlist_id: str) -> list[Track]:
        out: list[Track] = []
        offset = 0
        while True:
            data = self._safe(
                lambda: self.sp.playlist_items(
                    playlist_id, limit=100, offset=offset,
                    additional_types=("track", "episode"),
                ), {},
            ) or {}
            items = data.get("items") or []
            if not items:
                break
            for it in items:
                if not it:
                    continue
                t = it.get("track") or {}
                if t:
                    out.append(_to_track(t))
            if len(items) < 100:
                break
            offset += 100
        return out

    # ----- search ----- #

    def search(self, query: str) -> list[Track]:
        if not query:
            return []
        data = self._safe(
            lambda: self.sp.search(q=query, limit=20, type="track,playlist,show"), {}
        ) or {}
        out: list[Track] = []
        # Spotify returns `None` for items that aren't available in the user's
        # market - filter them out at every bucket before touching attributes.
        for t in ((data.get("tracks") or {}).get("items") or []):
            if not t:
                continue
            out.append(_to_track(t))
        for p in ((data.get("playlists") or {}).get("items") or []):
            if not p:
                continue
            out.append(Track(
                id=str(p.get("id") or ""),
                uri=str(p.get("uri") or ""),
                name=str(p.get("name") or ""),
                artist=str((p.get("owner") or {}).get("display_name") or ""),
                album="",
                duration_ms=0,
                kind="playlist",
            ))
        for s in ((data.get("shows") or {}).get("items") or []):
            if not s:
                continue
            out.append(Track(
                id=str(s.get("id") or ""),
                uri=str(s.get("uri") or ""),
                name=str(s.get("name") or ""),
                artist=str(s.get("publisher") or ""),
                album="",
                duration_ms=0,
                kind="show",
            ))
        return out

    def artists_in_genre(self, genre: str, limit: int = 20) -> list[tuple[str, str]]:
        """Return (artist_id, artist_name) for artists tagged with `genre`.

        Multi-word genres (e.g. "dream pop") MUST be wrapped in double quotes
        in the search query; otherwise Spotify only matches the first word and
        leaks the rest into free search, which silently returns nothing useful.
        """
        if not genre.strip():
            return []
        data = self._safe(
            lambda: self.sp.search(q=f'genre:"{genre}"', type="artist", limit=min(limit, 50)),
            {},
        ) or {}
        items = ((data.get("artists") or {}).get("items") or [])
        out: list[tuple[str, str]] = []
        for a in items:
            if not a:
                continue
            aid = str(a.get("id") or "")
            if aid:
                out.append((aid, str(a.get("name") or "")))
        return out

    def artist_genres(self, artist_id: str) -> list[str]:
        data = self._safe(lambda: self.sp.artist(artist_id), {}) or {}
        return [str(g) for g in (data.get("genres") or [])]

    def search_artist_id(self, name: str) -> str | None:
        data = self._safe(
            lambda: self.sp.search(q=name, limit=1, type="artist"), {}
        ) or {}
        items = ((data.get("artists") or {}).get("items") or [])
        if not items:
            return None
        return str(items[0].get("id") or "") or None

    def artist_top_tracks(self, artist_id: str, market: str = "from_token") -> list[Track]:
        data = self._safe(
            lambda: self.sp.artist_top_tracks(artist_id, country=market), {}
        ) or {}
        return [_to_track(t) for t in (data.get("tracks") or []) if t]

    def recommendations(
        self,
        seed_artists: Iterable[str] = (),
        seed_tracks: Iterable[str] = (),
        seed_genres: Iterable[str] = (),
        limit: int = 30,
    ) -> list[Track]:
        kw: dict[str, Any] = {"limit": min(limit, 100)}
        sa = list(seed_artists)[:5]
        st = list(seed_tracks)[:5]
        sg = list(seed_genres)[:5]
        if sa: kw["seed_artists"] = sa
        if st: kw["seed_tracks"] = st
        if sg: kw["seed_genres"] = sg
        if not (sa or st or sg):
            return []
        data = self._safe(lambda: self.sp.recommendations(**kw), {}) or {}
        return [_to_track(t) for t in (data.get("tracks") or []) if t]

    # ----- playback ----- #

    def devices(self) -> list[Device]:
        data = self._safe(lambda: self.sp.devices(), {}) or {}
        return [
            Device(
                id=str(d.get("id") or ""),
                name=str(d.get("name") or ""),
                kind=str(d.get("type") or ""),
                active=bool(d.get("is_active")),
            )
            for d in (data.get("devices") or [])
        ]

    def current_playback(self) -> dict[str, Any] | None:
        return self._safe(lambda: self.sp.current_playback(), None)

    def start_playback(
        self,
        device_id: str | None = None,
        context_uri: str | None = None,
        uris: list[str] | None = None,
        offset_uri: str | None = None,
    ) -> str | None:
        """Start playback. Returns None on success, error string on failure.

        Spotify returns 404 NO_ACTIVE_DEVICE when the target device is known
        but not currently in the active-playback state. The cure is a transfer
        first - we retry once after `transfer_playback` when device_id is set.
        """
        offset = {"uri": offset_uri} if offset_uri else None
        try:
            self.sp.start_playback(
                device_id=device_id, context_uri=context_uri, uris=uris, offset=offset,
            )
            return None
        except SpotifyException as exc:
            msg = (exc.msg or str(exc)).strip()
            # Transfer-then-retry rescue: only when we have a device_id and
            # the error is the well-known "no active device" path.
            if device_id and ("NO_ACTIVE_DEVICE" in msg.upper() or exc.http_status == 404):
                try:
                    self.sp.transfer_playback(device_id, force_play=False)
                    self.sp.start_playback(
                        device_id=device_id, context_uri=context_uri, uris=uris, offset=offset,
                    )
                    return None
                except SpotifyException as exc2:
                    return f"{exc2.http_status} {(exc2.msg or str(exc2)).strip()}"
            return f"{exc.http_status} {msg}"
        except Exception as exc:
            return str(exc)

    def pause(self, device_id: str | None = None) -> None:
        self._safe(lambda: self.sp.pause_playback(device_id=device_id))

    def resume(self, device_id: str | None = None) -> None:
        self._safe(lambda: self.sp.start_playback(device_id=device_id))

    def next_track(self, device_id: str | None = None) -> None:
        self._safe(lambda: self.sp.next_track(device_id=device_id))

    def previous_track(self, device_id: str | None = None) -> None:
        self._safe(lambda: self.sp.previous_track(device_id=device_id))

    def seek(self, position_ms: int, device_id: str | None = None) -> None:
        self._safe(lambda: self.sp.seek_track(position_ms, device_id=device_id))

    def toggle_shuffle(self, state: bool, device_id: str | None = None) -> None:
        self._safe(lambda: self.sp.shuffle(state, device_id=device_id))

    def cycle_repeat(self, state: str, device_id: str | None = None) -> None:
        # state in {"track", "context", "off"}
        self._safe(lambda: self.sp.repeat(state, device_id=device_id))

    def transfer_playback(self, device_id: str, play: bool = True) -> None:
        self._safe(lambda: self.sp.transfer_playback(device_id, force_play=play))

    # ----- playlist write ----- #

    def create_playlist(self, name: str, description: str = "", public: bool = False) -> Playlist | None:
        uid = self.settings.spotify.username
        if not uid:
            me = self._safe(lambda: self.sp.current_user(), None) or {}
            uid = str(me.get("id") or "")
            if uid:
                self.settings.spotify.username = uid
        if not uid:
            return None
        data = self._safe(
            lambda: self.sp.user_playlist_create(
                user=uid, name=name, public=public, description=description,
            ), None,
        )
        if not data:
            return None
        return Playlist(
            id=str(data.get("id") or ""),
            uri=str(data.get("uri") or ""),
            name=str(data.get("name") or ""),
            owner=uid,
            track_count=0,
        )

    def playlist_add_tracks(self, playlist_id: str, uris: list[str]) -> None:
        for i in range(0, len(uris), 100):
            chunk = uris[i:i + 100]
            self._safe(lambda c=chunk: self.sp.playlist_add_items(playlist_id, c))


def _to_track(item: dict[str, Any]) -> Track:
    """Map a Spotify track/episode dict to a Track."""
    kind = str(item.get("type") or "track")
    artists = item.get("artists") or []
    if kind == "track":
        artist = ", ".join(a.get("name", "") for a in artists) if artists else ""
        album = (item.get("album") or {}).get("name") or ""
    elif kind == "episode":
        artist = (item.get("show") or {}).get("publisher") or ""
        album = (item.get("show") or {}).get("name") or ""
    else:
        artist = ""
        album = ""
    return Track(
        id=str(item.get("id") or ""),
        uri=str(item.get("uri") or ""),
        name=str(item.get("name") or ""),
        artist=artist,
        album=album,
        duration_ms=int(item.get("duration_ms") or 0),
        kind=kind,
    )


def format_duration(ms: int) -> str:
    if ms <= 0:
        return "0:00"
    total = ms // 1000
    m, s = divmod(total, 60)
    return f"{m}:{s:02d}"
