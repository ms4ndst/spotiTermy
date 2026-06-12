"""Settings + paths for spotiTermy.

Configuration lives at `<user-data-dir>/spotitermy/config.toml` (on Windows:
`%LOCALAPPDATA%\\spotitermy\\config.toml`). The token cache (spotipy) sits
next to it.

A small layer because spotipy already handles the OAuth refresh dance.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import platformdirs

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

import tomli_w  # type: ignore[import-untyped]


APP_NAME = "spotitermy"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Per ref/spotify-web-api.md scopes table - what the TUI actually needs.
SPOTIFY_SCOPES = " ".join([
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "user-read-recently-played",
    "user-top-read",
    "user-library-read",
    "user-library-modify",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private",
    "streaming",
])


@dataclass
class UISettings:
    flavor: str = "mocha"
    accent: str = "mauve"


@dataclass
class SpotifySettings:
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = DEFAULT_REDIRECT_URI
    username: str = ""


@dataclass
class AISettings:
    """Optional AI-provider settings for the spotagen menu.

    Empty values mean "feature disabled" - the menu still works but
    AI-curated commands will show a "configure AI provider" hint.
    """
    provider: str = "none"            # "claude" | "openai" | "ollama" | "mistral" | "none"
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-6"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"


@dataclass
class Settings:
    ui: UISettings = field(default_factory=UISettings)
    spotify: SpotifySettings = field(default_factory=SpotifySettings)
    ai: AISettings = field(default_factory=AISettings)


def config_dir() -> Path:
    return Path(platformdirs.user_data_dir(APP_NAME, appauthor=False, roaming=False))


def config_path() -> Path:
    return config_dir() / "config.toml"


def token_cache_path() -> Path:
    return config_dir() / "token.cache"


def _from_dict(data: dict[str, Any]) -> Settings:
    s = Settings()
    ui = data.get("ui", {}) or {}
    sp = data.get("spotify", {}) or {}
    ai = data.get("ai", {}) or {}
    s.ui.flavor = str(ui.get("flavor", s.ui.flavor))
    s.ui.accent = str(ui.get("accent", s.ui.accent))
    s.spotify.client_id = str(sp.get("client_id", s.spotify.client_id))
    s.spotify.client_secret = str(sp.get("client_secret", s.spotify.client_secret))
    s.spotify.redirect_uri = str(sp.get("redirect_uri", s.spotify.redirect_uri))
    s.spotify.username = str(sp.get("username", s.spotify.username))
    s.ai.provider = str(ai.get("provider", s.ai.provider))
    s.ai.claude_api_key = str(ai.get("claude_api_key", s.ai.claude_api_key))
    s.ai.claude_model = str(ai.get("claude_model", s.ai.claude_model))
    s.ai.openai_api_key = str(ai.get("openai_api_key", s.ai.openai_api_key))
    s.ai.openai_model = str(ai.get("openai_model", s.ai.openai_model))
    s.ai.ollama_base_url = str(ai.get("ollama_base_url", s.ai.ollama_base_url))
    s.ai.ollama_model = str(ai.get("ollama_model", s.ai.ollama_model))
    s.ai.mistral_api_key = str(ai.get("mistral_api_key", s.ai.mistral_api_key))
    s.ai.mistral_model = str(ai.get("mistral_model", s.ai.mistral_model))
    return s


def _to_dict(s: Settings) -> dict[str, Any]:
    return {
        "ui": {"flavor": s.ui.flavor, "accent": s.ui.accent},
        "spotify": {
            "client_id": s.spotify.client_id,
            "client_secret": s.spotify.client_secret,
            "redirect_uri": s.spotify.redirect_uri,
            "username": s.spotify.username,
        },
        "ai": {
            "provider": s.ai.provider,
            "claude_api_key": s.ai.claude_api_key,
            "claude_model": s.ai.claude_model,
            "openai_api_key": s.ai.openai_api_key,
            "openai_model": s.ai.openai_model,
            "ollama_base_url": s.ai.ollama_base_url,
            "ollama_model": s.ai.ollama_model,
            "mistral_api_key": s.ai.mistral_api_key,
            "mistral_model": s.ai.mistral_model,
        },
    }


def load_settings() -> Settings:
    path = config_path()
    if not path.exists():
        return Settings()
    with path.open("rb") as f:
        data = tomllib.load(f)
    s = _from_dict(data)
    # Env overrides (handy for first-run before the config file exists).
    s.spotify.client_id = os.environ.get("SPOTIPY_CLIENT_ID", s.spotify.client_id)
    s.spotify.client_secret = os.environ.get("SPOTIPY_CLIENT_SECRET", s.spotify.client_secret)
    s.spotify.redirect_uri = os.environ.get("SPOTIPY_REDIRECT_URI", s.spotify.redirect_uri)
    s.spotify.username = os.environ.get("SPOTIPY_USERNAME", s.spotify.username)
    return s


def save_settings(s: Settings) -> None:
    config_dir().mkdir(parents=True, exist_ok=True)
    with config_path().open("wb") as f:
        tomli_w.dump(_to_dict(s), f)


def ensure_default_config() -> Path:
    """Create a stub config file on first run so the user has something to edit."""
    path = config_path()
    if not path.exists():
        save_settings(Settings())
    return path
