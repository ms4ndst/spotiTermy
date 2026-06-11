# spotiTermy

A Catppuccin-themed Spotify terminal UI in Python (Textual), inspired by
[spotui](https://github.com/cjbassi/spotui) and integrating
[spotagen](../spotagen) as an in-app AI playlist menu.

## Features

- 4-pane Textual layout: Library, Playlists, Tracks, Now Playing
- Playback control (play/pause, skip, seek, shuffle, repeat, device pick)
- Spotify search
- **spotagen menu (`g`)**: AI-curated playlists (Claude / OpenAI / Mistral / Ollama)
- Live theme switching across all four Catppuccin flavors (`t`)

## Install

```powershell
cd C:\Users\magnus.sandstrom\Code\Repo\spotiTermy
python -m venv .venv
.venv\Scripts\python -m pip install -e .
```

## Spotify credentials (one-time)

1. Create an app at https://developer.spotify.com/dashboard
2. Add redirect URI: `http://127.0.0.1:8888/callback`
3. Run the app once. It writes a stub config to
   `%APPDATA%\spotitermy\config.toml`. Edit it and fill in `[spotify]`:

```toml
[spotify]
client_id     = "..."
client_secret = "..."
redirect_uri  = "http://127.0.0.1:8888/callback"

[ui]
flavor = "mocha"     # mocha | latte | frappe | macchiato
accent = "mauve"     # mauve | blue | lavender | peach | teal | sky | green

[ai]
provider          = "claude"   # claude | openai | mistral | ollama | none
claude_api_key    = "..."
claude_model      = "claude-sonnet-4-6"
```

Env-var overrides also work: `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`,
`SPOTIPY_REDIRECT_URI`.

## Run

```powershell
spotitermy
# or
python -m spotitermy --flavor latte --accent blue
```

## Keybindings

| Key   | Action |
|-------|--------|
| Space | Play / Pause |
| n / p | Next / Previous track |
| -> <- | Seek +/- 10s |
| s     | Toggle shuffle |
| r     | Cycle repeat (off / context / track) |
| /     | Search |
| d     | Device picker |
| **g** | **spotagen AI menu** |
| t     | Cycle Catppuccin flavor |
| Tab   | Move between panes |
| q     | Quit |

## Spotagen menu

`g` opens a modal with three modes:

- **Curate** - pick deeper cuts by your seed artists
- **Discover** - suggest *new* artists similar to your seeds
- **Genre** - free-form vibe brief ("late-night jazz piano",
  "norwegian black metal", ...)

Suggestions are resolved against Spotify search and added to a new playlist.
No AI provider key configured? The menu opens with a hint pointing at the
config file.

## Theme

All colors come from the official Catppuccin palette (see `spotitermy/theme.py`).
Each color is applied by **role** (Base / Surface / Text / Accent / etc.),
never by raw hex value, so switching flavor at runtime is a single lookup.

Mocha (default) | Latte | Frappe | Macchiato

## Spotify Web API

Endpoints used follow the documentation in `ref/spotify-web-api.md`:
Authorization Code Flow with PKCE-safe token cache, scopes for playback +
library + playlist read/modify, retry-respecting `Retry-After` via spotipy.
