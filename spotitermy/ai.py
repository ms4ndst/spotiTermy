"""Minimal AI-provider shim for the spotagen menu.

If `spotagen` is installed, we delegate to its battle-tested curator.
Otherwise we fall back to a tiny built-in JSON prompt over httpx so the
menu still produces useful results with just an API key configured.

The shape returned is always: list[CuratedTrack] - artist + track name -
the caller (the spotagen menu screen) resolves those to Spotify URIs.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable

import httpx

from .config import Settings


@dataclass(frozen=True)
class CuratedTrack:
    artist: str
    track: str
    reason: str = ""


SYSTEM_PROMPT = (
    "You are a music curator. You will be given a list of seed artists or "
    "a creative brief. Respond with STRICT JSON, an object with key 'tracks' "
    "whose value is a list of {\"artist\": str, \"track\": str, \"reason\": str}. "
    "No prose outside the JSON. Pick real songs that exist on Spotify."
)


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model response."""
    # Strip code fences.
    text = re.sub(r"```(?:json)?", "", text).strip("` \n\r\t")
    # Best-effort: first '{' through last '}'
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"tracks": []}
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return {"tracks": []}


def _parse_tracks(data: dict) -> list[CuratedTrack]:
    raw = data.get("tracks") or []
    out: list[CuratedTrack] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        artist = str(item.get("artist") or "").strip()
        track = str(item.get("track") or "").strip()
        if not (artist and track):
            continue
        out.append(CuratedTrack(
            artist=artist,
            track=track,
            reason=str(item.get("reason") or "")[:120],
        ))
    return out


def _build_user_prompt(mode: str, seed: str, count: int) -> str:
    if mode == "curate":
        return (
            f"Curate {count} tracks BY these seed artists (do NOT include new artists): "
            f"{seed}. Pick deeper cuts where possible, not just radio singles."
        )
    if mode == "discover":
        return (
            f"Suggest {count} tracks by NEW artists similar in style to: {seed}. "
            "Do NOT include any of the seed artists themselves."
        )
    if mode == "genre":
        return f"Suggest {count} tracks fitting this brief or genre: {seed}."
    return f"Suggest {count} tracks: {seed}"


def call_ai(settings: Settings, mode: str, seed: str, count: int = 20) -> list[CuratedTrack]:
    """Single entry point. Returns [] when no provider is configured."""
    ai = settings.ai
    user = _build_user_prompt(mode, seed, count)

    if ai.provider == "claude" and ai.claude_api_key:
        return _call_claude(ai.claude_api_key, ai.claude_model, user)
    if ai.provider == "openai" and ai.openai_api_key:
        return _call_openai_compat(
            base_url="https://api.openai.com/v1",
            api_key=ai.openai_api_key,
            model=ai.openai_model,
            user_prompt=user,
        )
    if ai.provider == "mistral" and ai.mistral_api_key:
        return _call_openai_compat(
            base_url="https://api.mistral.ai/v1",
            api_key=ai.mistral_api_key,
            model=ai.mistral_model,
            user_prompt=user,
        )
    if ai.provider == "ollama":
        return _call_ollama(ai.ollama_base_url, ai.ollama_model, user)
    return []


def _call_claude(api_key: str, model: str, user_prompt: str) -> list[CuratedTrack]:
    try:
        with httpx.Client(timeout=60) as client:
            r = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 2048,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
            r.raise_for_status()
            data = r.json()
        content = data.get("content") or []
        text_parts = [c.get("text", "") for c in content if c.get("type") == "text"]
        return _parse_tracks(_extract_json("".join(text_parts)))
    except Exception:
        return []


def _call_openai_compat(base_url: str, api_key: str, model: str, user_prompt: str) -> list[CuratedTrack]:
    try:
        with httpx.Client(timeout=60) as client:
            r = client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            r.raise_for_status()
            data = r.json()
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        return _parse_tracks(_extract_json(content))
    except Exception:
        return []


def _call_ollama(base_url: str, model: str, user_prompt: str) -> list[CuratedTrack]:
    try:
        with httpx.Client(timeout=120) as client:
            r = client.post(
                f"{base_url.rstrip('/')}/api/chat",
                json={
                    "model": model,
                    "stream": False,
                    "format": "json",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            r.raise_for_status()
            data = r.json()
        content = (data.get("message") or {}).get("content", "")
        return _parse_tracks(_extract_json(content))
    except Exception:
        return []


