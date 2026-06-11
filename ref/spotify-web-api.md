# Spotify Web API Documentation

The Spotify Web API enables the creation of applications that can interact with Spotify's music catalog and user data. It provides access to a wide range of endpoints for managing playlists, browsing music content, controlling playback, and more.

**Base URL:** `https://api.spotify.com/v1`

**Authentication:** All requests require an `Authorization` header with a Bearer token:
```
Authorization: Bearer {access_token}
```

Access tokens expire after **3600 seconds (1 hour)**.

**Rate Limiting:** When rate-limited, the API returns HTTP 429. Check the `Retry-After` header for the number of seconds to wait before retrying.

**Quota Modes:**
- **Development Mode:** search `limit` max = 10
- **Extended Quota Mode:** search `limit` max = 50

---

## Concepts

### Access Token

An access token is a string which contains the credentials and permissions that can be used to access a given resource. It is generated from the Spotify Accounts Service and must be included in every API request.

Tokens are obtained via OAuth 2.0 authorization flows and expire after 3600 seconds. Applications must refresh tokens to maintain access.

### API Calls

All requests are made over HTTPS to `https://api.spotify.com/v1`. The `Authorization` header with a Bearer token is required. Responses are JSON. Standard HTTP status codes are used: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests.

### Apps

Before using the Web API, you must register your application in the Spotify Developer Dashboard to obtain a `client_id` and `client_secret`. Apps operate in Development Mode by default (limited to 25 users). Apply for Extended Quota Mode to remove restrictions.

### Authorization

Spotify uses OAuth 2.0. Four flows are available:

- **Authorization Code Flow** — server-side apps; returns code exchanged for tokens
- **Authorization Code with PKCE** — client-side/mobile apps; no client_secret required
- **Client Credentials Flow** — server-to-server; no user context; cannot access user data
- **Implicit Grant** — [DEPRECATED] use PKCE instead

All flows except Client Credentials return both an `access_token` and a `refresh_token`.

### Redirect URIs

The redirect URI is where Spotify sends the user after authorization. It must be registered in the Developer Dashboard. Wildcards are not supported. Localhost is allowed for development.

### Playlists

Playlists can be public or private. Collaborative playlists allow multiple users to edit. The `snapshot_id` field tracks the playlist's current state and changes whenever the playlist is modified.

### Quota Modes

- **Development Mode:** default; limited functionality; search returns max 10 results
- **Extended Quota Mode:** for production apps; search returns up to 50 results; requires application review

### Rate Limits

The API enforces rate limits. When exceeded, HTTP 429 is returned. The `Retry-After` response header indicates seconds to wait. Requests are counted per application and per user.

### Scopes

Scopes control what data your application can access. Key scopes:

| Scope | Description |
|---|---|
| `user-read-private` | Read user subscription level and country |
| `user-read-email` | Read user email address |
| `user-library-read` | Access saved content |
| `user-library-modify` | Manage saved content |
| `user-read-playback-state` | Read playback state |
| `user-modify-playback-state` | Control playback (Premium only) |
| `user-read-currently-playing` | Read currently playing track |
| `user-read-recently-played` | Access recently played tracks |
| `user-read-playback-position` | Read playback position in episodes |
| `user-top-read` | Read top artists and tracks |
| `user-follow-read` | Read followed artists/users |
| `user-follow-modify` | Follow/unfollow artists/users |
| `playlist-read-private` | Access private playlists |
| `playlist-read-collaborative` | Access collaborative playlists |
| `playlist-modify-public` | Modify public playlists |
| `playlist-modify-private` | Modify private playlists |
| `ugc-image-upload` | Upload images to Spotify |

### Spotify URIs and IDs

Spotify resources are identified by:
- **Spotify ID:** base-62 identifier (e.g., `6rqhFgbbKwnb9MLmUQDhG6`)
- **Spotify URI:** `spotify:{type}:{id}` (e.g., `spotify:track:6rqhFgbbKwnb9MLmUQDhG6`)
- **Spotify URL:** `https://open.spotify.com/{type}/{id}`

### Track Relinking

When a track is unavailable in the requested market, Spotify may link it to an equivalent available track. The `is_playable` field indicates availability. The `linked_from` object (deprecated) contained the original track information.

---

## Tutorials

### Authorization Code Flow

Server-side authorization flow. Most secure for apps with a backend.

**Steps:**
1. Redirect user to `https://accounts.spotify.com/authorize` with `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state`
2. User logs in and approves scopes
3. Spotify redirects to your `redirect_uri` with a `code` parameter
4. Exchange code for tokens via POST to `https://accounts.spotify.com/api/token` with `grant_type=authorization_code`, `code`, `redirect_uri`, `client_id`, `client_secret` (Base64-encoded in Authorization header)
5. Response contains `access_token`, `token_type`, `scope`, `expires_in`, `refresh_token`

### Authorization Code with PKCE

Client-side flow without a client_secret. Use for SPAs and mobile apps.

**Steps:**
1. Generate a `code_verifier` (random string 43-128 chars) and `code_challenge` (SHA-256 hash of verifier, Base64URL-encoded)
2. Redirect to authorization URL with `code_challenge_method=S256` and `code_challenge`
3. Exchange code at token endpoint using `code_verifier` instead of client_secret

### Client Credentials Flow

Machine-to-machine authentication. No user context. Cannot access user-specific endpoints.

**Steps:**
1. POST to `https://accounts.spotify.com/api/token` with `grant_type=client_credentials`
2. Include Base64-encoded `client_id:client_secret` in Authorization header
3. Response contains `access_token` and `expires_in` (no refresh_token)

### Implicit Grant [DEPRECATED]

Browser-based flow that returns the access token directly in the URL fragment. Deprecated due to security concerns. Migrate to Authorization Code with PKCE.

### Refreshing Tokens

Use the `refresh_token` to obtain a new `access_token` without re-authorization.

POST to `https://accounts.spotify.com/api/token` with `grant_type=refresh_token`, `refresh_token`, and client credentials.

### Migration: Implicit Grant to Authorization Code

Replace `response_type=token` with `response_type=code`. Generate a PKCE code verifier/challenge. Update the token exchange to use the code + code verifier. Store the refresh_token for future use.

### Migration: Insecure Redirect URI

Redirect URIs using `http://` (non-localhost) are no longer accepted. Migrate to `https://` or use `http://localhost` for local development.

### Migration: February 2026 Dev Mode Changes

Key changes effective February 2026:

- **Library endpoint unification:** New endpoints `PUT /me/library`, `DELETE /me/library`, `GET /me/library` replace individual save/remove/check endpoints for albums, tracks, episodes, shows, audiobooks, and follow for artists/users/playlists
- **Playlist `/tracks` renamed to `/items`:** `GET/PUT/POST/DELETE /playlists/{id}/tracks` now at `/playlists/{id}/items`
- **Batch endpoints deprecated:** `GET /albums`, `GET /artists`, `GET /tracks`, etc. (get-several-*) are deprecated
- **Search `limit` reduced:** Development Mode max reduced from 50 to 10

---

## How-Tos

### Display Your Spotify Profile Data in a Web App

A step-by-step guide to building a web application that displays the current user's Spotify profile.

1. Register an app in the Developer Dashboard and note the `client_id`
2. Implement Authorization Code with PKCE flow
3. Request the `user-read-private` and `user-read-email` scopes
4. After obtaining an access token, call `GET /me`
5. Display profile data: display_name, images, followers, product

---

## Changelog

### March 2026

- **Reverted:** `external_ids` field for Track and Album objects was reverted. The field is no longer returned in responses after a brief period where it was removed.

### February 2026

- **New unified library endpoints:** `PUT /me/library`, `DELETE /me/library`, `GET /me/library` for all content types (albums, tracks, episodes, shows, audiobooks) and follow (artists, users, playlists)
- **Playlist items rename:** `/playlists/{id}/tracks` endpoints deprecated; use `/playlists/{id}/items`
- **Batch fetch endpoints deprecated:** `GET /albums`, `GET /artists`, `GET /tracks`, `GET /audio-features` (multi), `GET /shows` (multi), `GET /episodes` (multi), `GET /chapters` (multi), `GET /audiobooks` (multi)
- **Search limit change:** In Development Mode, maximum `limit` for search reduced to 10 (was 50)
- **Deprecated fields:** `available_markets`, `popularity`, `genres` (on artist), `followers` (on artist), `preview_url`, `linked_from` are deprecated across various objects

---

## Reference

### Albums

#### Get Album

`GET /albums/{id}`

Get Spotify catalog information for a single album.

**Parameters:**
| Name | Type | Location | Required | Description |
|---|---|---|---|---|
| id | string | path | yes | The Spotify ID of the album |
| market | string | query | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 AlbumObject

| Field | Type | Description |
|---|---|---|
| album_type | string | Type: "album", "single", "compilation" |
| total_tracks | integer | Number of tracks |
| available_markets | array[string] | **Deprecated.** Available markets |
| external_urls | object | Known external URLs; `spotify` field |
| href | string | API endpoint link |
| id | string | Spotify ID |
| images | array[ImageObject] | Cover art (url, height, width) |
| label | string | Record label |
| name | string | Album name |
| popularity | integer | **Deprecated.** 0-100 popularity score |
| release_date | string | First release date |
| release_date_precision | string | "year", "month", or "day" |
| restrictions | object | Restriction reason if restricted |
| type | string | "album" |
| uri | string | Spotify URI |
| artists | array[SimplifiedArtistObject] | Album artists |
| tracks | PagingObject[SimplifiedTrackObject] | Paged tracks |
| copyrights | array[CopyrightObject] | Copyright statements |
| external_ids | object | isrc, ean, upc |
| genres | array[string] | **Deprecated.** Genre list |

```json
{
  "album_type": "compilation",
  "total_tracks": 9,
  "external_urls": { "spotify": "string" },
  "href": "string",
  "id": "2up3OPMp9Tb4dAKM2erWXQ",
  "images": [{ "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228", "height": 300, "width": 300 }],
  "name": "string",
  "release_date": "1981-12",
  "release_date_precision": "year",
  "type": "album",
  "uri": "spotify:album:2up3OPMp9Tb4dAKM2erWXQ",
  "artists": [{ "id": "string", "name": "string", "type": "artist", "uri": "string" }],
  "tracks": { "href": "string", "limit": 20, "next": null, "offset": 0, "previous": null, "total": 9, "items": [] }
}
```

#### Get Several Albums [DEPRECATED]

`GET /albums`

**Note:** Deprecated. Use individual `GET /albums/{id}` calls instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated Spotify IDs. Max 20 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 `{ "albums": [AlbumObject] }`

#### Get Album Tracks

`GET /albums/{id}/tracks`

Get Spotify catalog information about an album's tracks.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the album |
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max items to return. Default: 20, max: 50 |
| offset | integer | no | Index of first item. Default: 0 |

**Response:** 200 Paging object of SimplifiedTrackObjects

```json
{
  "href": "string",
  "limit": 20,
  "next": "string",
  "offset": 0,
  "previous": null,
  "total": 4,
  "items": [{ "id": "string", "name": "string", "duration_ms": 0, "track_number": 1, "type": "track", "uri": "string" }]
}
```

#### Get User's Saved Albums

`GET /me/albums`

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset. Default: 0 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 Paging of SavedAlbumObjects `{ added_at, album }`

#### Save Albums for Current User [DEPRECATED]

`PUT /me/albums`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `user-library-modify`

**Body:** `{ "ids": ["string"] }` — max 20 IDs

**Response:** 200 empty

#### Remove Users' Saved Albums [DEPRECATED]

`DELETE /me/albums`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 20 |

**Body (optional):** `{ "ids": ["string"] }`

**Response:** 200 empty

#### Check User's Saved Albums [DEPRECATED]

`GET /me/albums/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 20 |

**Response:** 200 `[false, true]` — array of booleans

#### Get New Releases

`GET /browse/new-releases`

Get a list of new album releases featured in Spotify.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 `{ "albums": PagingObject[SimplifiedAlbumObject] }`

```json
{
  "albums": {
    "href": "string",
    "limit": 20,
    "next": "string",
    "offset": 0,
    "previous": null,
    "total": 4,
    "items": []
  }
}
```

---

### Artists

#### Get Artist

`GET /artists/{id}`

Get Spotify catalog information for a single artist.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the artist |

**Response:** 200 ArtistObject

| Field | Type | Description |
|---|---|---|
| external_urls | object | Spotify URL |
| followers | object | **Deprecated.** `{ href: null, total }` |
| genres | array[string] | **Deprecated.** Associated genres |
| href | string | API link |
| id | string | Spotify ID |
| images | array[ImageObject] | Artist images |
| name | string | Artist name |
| popularity | integer | **Deprecated.** 0-100 |
| type | string | "artist" |
| uri | string | Spotify URI |

```json
{
  "external_urls": { "spotify": "string" },
  "followers": { "href": null, "total": 0 },
  "genres": ["Prog rock", "Grunge"],
  "href": "string",
  "id": "string",
  "images": [{ "url": "string", "height": 300, "width": 300 }],
  "name": "string",
  "popularity": 0,
  "type": "artist",
  "uri": "string"
}
```

#### Get Several Artists [DEPRECATED]

`GET /artists`

**Note:** Deprecated. Use individual `GET /artists/{id}` calls instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `{ "artists": [ArtistObject] }`

#### Get Artist's Albums

`GET /artists/{id}/albums`

Get Spotify catalog information about an artist's albums.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the artist |
| include_groups | string | no | Comma-separated filter: album, single, appears_on, compilation |
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SimplifiedAlbumObjects

#### Get Artist's Top Tracks

`GET /artists/{id}/top-tracks`

Get Spotify catalog information about an artist's top tracks by country.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the artist |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 `{ "tracks": [TrackObject] }`

#### Get Artist's Related Artists [FAILED]

`GET /artists/{id}/related-artists`

**Note:** This endpoint consistently returned empty content during documentation compilation and could not be documented from the live API. Based on API patterns, it returns `{ "artists": [ArtistObject] }` — a list of artists similar to the given artist.

---

### Audiobooks

#### Get an Audiobook

`GET /audiobooks/{id}`

Get Spotify catalog information for a single audiobook. Audiobooks are only available in certain markets.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the audiobook |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 AudiobookObject

| Field | Type | Description |
|---|---|---|
| authors | array[AuthorObject] | List of authors (`name` field) |
| available_markets | array[string] | Available markets |
| copyrights | array[CopyrightObject] | Copyright statements |
| description | string | Description (may contain HTML) |
| html_description | string | HTML description |
| edition | string | Edition (e.g. "Unabridged") |
| explicit | boolean | Explicit content flag |
| external_urls | object | Spotify URL |
| href | string | API link |
| id | string | Spotify ID |
| images | array[ImageObject] | Cover images |
| languages | array[string] | Languages |
| media_type | string | Media type |
| name | string | Name |
| narrators | array[NarratorObject] | Narrators (`name` field) |
| publisher | string | Publisher |
| type | string | "audiobook" |
| uri | string | Spotify URI |
| total_chapters | integer | Total number of chapters |
| chapters | PagingObject[SimplifiedChapterObject] | Paged chapters |

#### Get Several Audiobooks [DEPRECATED]

`GET /audiobooks`

**Note:** Deprecated. Use individual `GET /audiobooks/{id}` calls instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 `{ "audiobooks": [AudiobookObject] }`

#### Get Audiobook Chapters

`GET /audiobooks/{id}/chapters`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the audiobook |
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SimplifiedChapterObjects

#### Get User's Saved Audiobooks

`GET /me/audiobooks`

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SavedAudiobookObjects `{ added_at, audiobook }`

#### Save Audiobooks for Current User [DEPRECATED]

`PUT /me/audiobooks`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 empty

#### Remove User's Saved Audiobooks [DEPRECATED]

`DELETE /me/audiobooks`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 empty

#### Check User's Saved Audiobooks [DEPRECATED]

`GET /me/audiobooks/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `[false, true]` — array of booleans

---

### Categories

#### Get Several Browse Categories

`GET /browse/categories`

Get a list of categories used to tag items in Spotify.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| locale | string | no | Language/country code (e.g. "sv_SE") |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 `{ "categories": PagingObject[CategoryObject] }`

CategoryObject fields: `href`, `icons` (ImageObject array), `id`, `name`

```json
{
  "categories": {
    "href": "string",
    "limit": 20,
    "next": "string",
    "offset": 0,
    "previous": null,
    "total": 4,
    "items": [{ "href": "string", "icons": [{ "url": "string", "height": 300, "width": 300 }], "id": "string", "name": "string" }]
  }
}
```

#### Get Single Browse Category

`GET /browse/categories/{category_id}`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| category_id | string | yes | Spotify category ID |
| locale | string | no | Language/country code |

**Response:** 200 CategoryObject `{ href, icons, id, name }`

---

### Chapters

#### Get a Chapter

`GET /chapters/{id}`

Get Spotify catalog information for a single audiobook chapter.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the chapter |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 ChapterObject

| Field | Type | Description |
|---|---|---|
| audio_preview_url | string | 30-second preview URL (nullable, deprecated) |
| available_markets | array[string] | Available markets |
| chapter_number | integer | Chapter number |
| description | string | Description (may contain HTML) |
| html_description | string | HTML description |
| duration_ms | integer | Duration in milliseconds |
| explicit | boolean | Explicit flag |
| external_urls | object | Spotify URL |
| href | string | API link |
| id | string | Spotify ID |
| images | array[ImageObject] | Cover images |
| is_playable | boolean | Playable in market |
| languages | array[string] | Languages |
| name | string | Chapter name |
| release_date | string | Release date |
| release_date_precision | string | "year", "month", "day" |
| restrictions | object | Restriction if applied |
| resume_point | object | `{ fully_played, resume_position_ms }` |
| type | string | "episode" |
| uri | string | Spotify URI |
| audiobook | SimplifiedAudiobookObject | Parent audiobook |

#### Get Several Chapters [DEPRECATED]

`GET /chapters`

**Note:** Deprecated. Use individual `GET /chapters/{id}` calls instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 `{ "chapters": [ChapterObject] }`

---

### Episodes

#### Get Episode

`GET /episodes/{id}`

Get Spotify catalog information for a single podcast episode.

**Scopes:** `user-read-playback-position` (for resume_point)

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the episode |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 EpisodeObject

| Field | Type | Description |
|---|---|---|
| audio_preview_url | string | 30-second preview URL (nullable, deprecated) |
| description | string | Description |
| html_description | string | HTML description |
| duration_ms | integer | Duration in milliseconds |
| explicit | boolean | Explicit flag |
| external_urls | object | Spotify URL |
| href | string | API link |
| id | string | Spotify ID |
| images | array[ImageObject] | Cover images |
| is_externally_hosted | boolean | Hosted externally |
| is_playable | boolean | Playable in market |
| languages | array[string] | Languages |
| name | string | Episode name |
| release_date | string | Release date |
| release_date_precision | string | "year", "month", "day" |
| restrictions | object | Restriction if applied |
| resume_point | object | `{ fully_played, resume_position_ms }` |
| type | string | "episode" |
| uri | string | Spotify URI |
| show | SimplifiedShowObject | Parent show |

#### Get Several Episodes [DEPRECATED]

`GET /episodes`

**Note:** Deprecated. Use individual `GET /episodes/{id}` calls instead.

**Scopes:** `user-read-playback-position`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 `{ "episodes": [EpisodeObject] }`

#### Get User's Saved Episodes

`GET /me/episodes`

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SavedEpisodeObjects `{ added_at, episode }`

#### Save Episodes for Current User [DEPRECATED]

`PUT /me/episodes`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `user-library-modify`

**Body:** `{ "ids": ["string"] }` — max 50 IDs

**Response:** 200 empty

#### Remove User's Saved Episodes [DEPRECATED]

`DELETE /me/episodes`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Body (optional):** `{ "ids": ["string"] }`

**Response:** 200 empty

#### Check User's Saved Episodes [DEPRECATED]

`GET /me/episodes/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `[false, true]`

---

### Genres

#### Get Available Genre Seeds

`GET /recommendations/available-genre-seeds`

Retrieve a list of available genre seeds for use in the recommendations endpoint.

**Response:** 200 `{ "genres": ["acoustic", "afrobeat", "alt-rock", ...] }`

```json
{ "genres": ["acoustic", "afrobeat", "alt-rock", "alternative", "ambient"] }
```

---

### Library

#### Save Items to Library

`PUT /me/library`

Save one or more items to the current user's library. Supports albums, tracks, episodes, shows, audiobooks, artists (follow), users (follow), and playlists (follow).

**Scopes:** `user-library-modify` (for content) or `user-follow-modify` (for artists/users) or `playlist-modify-public`/`playlist-modify-private` (for playlists)

**Body:**
```json
{
  "ids": ["string"],
  "type": "album"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| ids | array[string] | yes | Spotify IDs. Max 50 |
| type | string | yes | "album", "track", "episode", "show", "audiobook", "artist", "user", "playlist" |

**Response:** 200 empty

#### Remove Items from Library

`DELETE /me/library`

Remove one or more items from the current user's library.

**Scopes:** `user-library-modify` (content) or `user-follow-modify` (artists/users) or playlist scopes (playlists)

**Body:**
```json
{
  "ids": ["string"],
  "type": "album"
}
```

**Response:** 200 empty

#### Check User's Saved Items

`GET /me/library/contains`

Check if one or more items are saved in the current user's library.

**Scopes:** `user-library-read` (content) or `user-follow-read` (artists/users)

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |
| type | string | yes | "album", "track", "episode", "show", "audiobook", "artist", "user", "playlist" |

**Response:** 200 `[false, true]`

---

### Markets

#### Get Available Markets

`GET /markets`

Get the list of markets where Spotify is available.

**Response:** 200 `{ "markets": ["CA", "BR", "IT", ...] }`

```json
{ "markets": ["CA", "BR", "IT"] }
```

---

### Player

> **Note:** All Player control endpoints (Start/Resume, Pause, Skip, Seek, Set Repeat, Set Volume, Toggle Shuffle, Add to Queue, Transfer Playback) require a **Spotify Premium** subscription. They return `403 Forbidden` for non-Premium users.

#### Get Playback State

`GET /me/player`

Get information about the user's current playback state.

**Scopes:** `user-read-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| market | string | no | ISO 3166-1 alpha-2 country code |
| additional_types | string | no | "track", "episode" (comma-separated) |

**Response:** 200 PlaybackStateObject (or 204 No Content if nothing playing)

| Field | Type | Description |
|---|---|---|
| device | DeviceObject | Active device (id, is_active, is_private_session, is_restricted, name, type, volume_percent, supports_volume) |
| repeat_state | string | "off", "track", "context" |
| shuffle_state | boolean | Shuffle on/off |
| context | ContextObject | Playback context (type, href, external_urls, uri) |
| timestamp | integer | Unix timestamp of last state update |
| progress_ms | integer | Progress in current item (ms) |
| is_playing | boolean | Currently playing |
| item | TrackObject or EpisodeObject | Currently playing item |
| currently_playing_type | string | "track", "episode", "ad", "unknown" |
| actions | ActionsObject | Disallows object |

#### Transfer Playback

`PUT /me/player`

**Premium required.** Transfer playback to a new device.

**Scopes:** `user-modify-playback-state`

**Body:**
```json
{
  "device_ids": ["string"],
  "play": false
}
```

**Response:** 204 No Content

#### Get Available Devices

`GET /me/player/devices`

Get information about a user's available Spotify Connect devices.

**Scopes:** `user-read-playback-state`

**Response:** 200 `{ "devices": [DeviceObject] }`

DeviceObject fields: `id`, `is_active`, `is_private_session`, `is_restricted`, `name`, `type`, `volume_percent`, `supports_volume`

```json
{
  "devices": [{
    "id": "string",
    "is_active": false,
    "is_private_session": false,
    "is_restricted": false,
    "name": "Kitchen speaker",
    "type": "computer",
    "volume_percent": 59,
    "supports_volume": true
  }]
}
```

#### Get Currently Playing Track

`GET /me/player/currently-playing`

Get the object currently being played on the user's Spotify account.

**Scopes:** `user-read-currently-playing`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| market | string | no | ISO 3166-1 alpha-2 country code |
| additional_types | string | no | "track", "episode" |

**Response:** 200 CurrentlyPlayingObject or 204 No Content

| Field | Type | Description |
|---|---|---|
| context | ContextObject | Playback context |
| timestamp | integer | Unix timestamp |
| progress_ms | integer | Progress in ms |
| is_playing | boolean | Playing flag |
| item | TrackObject or EpisodeObject | Current item |
| currently_playing_type | string | "track", "episode", "ad", "unknown" |
| actions | ActionsObject | Disallows |

#### Start/Resume Playback

`PUT /me/player/play`

**Premium required.** Start or resume playback on a device.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| device_id | string | no | Target device ID |

**Body:**
```json
{
  "context_uri": "spotify:album:1Je1IMUlBXcx1Fz0WE7oPT",
  "uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"],
  "offset": { "position": 5 },
  "position_ms": 0
}
```

**Response:** 204 No Content

#### Pause Playback

`PUT /me/player/pause`

**Premium required.** Pause playback.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Skip To Next

`POST /me/player/next`

**Premium required.** Skip to next track.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Skip To Previous

`POST /me/player/previous`

**Premium required.** Skip to previous track.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Seek To Position

`PUT /me/player/seek`

**Premium required.** Seek to the given position in the currently playing track.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| position_ms | integer | yes | Position in milliseconds |
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Set Repeat Mode

`PUT /me/player/repeat`

**Premium required.** Set the repeat mode for the user's playback.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| state | string | yes | "track", "context", or "off" |
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Set Playback Volume

`PUT /me/player/volume`

**Premium required.** Set the volume for the user's current playback device.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| volume_percent | integer | yes | Volume 0-100 |
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Toggle Playback Shuffle

`PUT /me/player/shuffle`

**Premium required.** Toggle shuffle on or off for user's playback.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| state | boolean | yes | true = shuffle on, false = shuffle off |
| device_id | string | no | Target device ID |

**Response:** 204 No Content

#### Get Recently Played Tracks

`GET /me/player/recently-played`

Get tracks from the current user's recently played tracks (up to 50).

**Scopes:** `user-read-recently-played`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| limit | integer | no | Max items. Default: 20, max: 50 |
| after | integer | no | Unix timestamp in ms; returns items after this cursor |
| before | integer | no | Unix timestamp in ms; returns items before this cursor |

**Response:** 200 Cursor-paged PlayHistoryObjects

| Field | Type | Description |
|---|---|---|
| href | string | API link |
| limit | integer | Max items |
| next | string | Next page URL |
| cursors | object | `{ after, before }` (Unix ms timestamps) |
| total | integer | Total available |
| items | array[PlayHistoryObject] | Each has `track`, `played_at` (ISO 8601), `context` |

```json
{
  "href": "string",
  "limit": 20,
  "next": "string",
  "cursors": { "after": "string", "before": "string" },
  "total": 0,
  "items": [{ "track": {}, "played_at": "string", "context": {} }]
}
```

#### Get the User's Queue

`GET /me/player/queue`

Get the list of objects that make up the user's queue.

**Scopes:** `user-read-playback-state`

**Response:** 200 QueueObject

| Field | Type | Description |
|---|---|---|
| currently_playing | TrackObject or EpisodeObject | Currently playing item |
| queue | array[TrackObject or EpisodeObject] | Items in the queue |

#### Add Item to Playback Queue

`POST /me/player/queue`

**Premium required.** Add an item to the end of the user's current playback queue.

**Scopes:** `user-modify-playback-state`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| uri | string | yes | Spotify URI of the item to add |
| device_id | string | no | Target device ID |

**Response:** 204 No Content

---

### Playlists

#### Get Playlist

`GET /playlists/{playlist_id}`

Get a playlist owned by a Spotify user.

**Scopes:** `playlist-read-private` or `playlist-read-collaborative` (for private/collaborative)

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID of the playlist |
| market | string | no | ISO 3166-1 alpha-2 country code |
| fields | string | no | Comma-separated fields to return |
| additional_types | string | no | "track", "episode" |

**Response:** 200 PlaylistObject

| Field | Type | Description |
|---|---|---|
| collaborative | boolean | Collaborative flag |
| description | string | Playlist description |
| external_urls | object | Spotify URL |
| followers | object | `{ href: null, total }` |
| href | string | API link |
| id | string | Spotify ID |
| images | array[ImageObject] | Playlist images |
| name | string | Playlist name |
| owner | PublicUserObject | Owner info |
| public | boolean | Public flag |
| snapshot_id | string | Version identifier |
| tracks | PagingObject[PlaylistItemObject] | Paged playlist items |
| type | string | "playlist" |
| uri | string | Spotify URI |

#### Change Playlist Details

`PUT /playlists/{playlist_id}`

Change a playlist's name, description, and public/collaborative state.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID |

**Body:**
```json
{
  "name": "New Name",
  "public": false,
  "collaborative": true,
  "description": "Updated description"
}
```

**Response:** 200 empty

#### Get Playlist Items [DEPRECATED]

`GET /playlists/{playlist_id}/tracks`

**Note:** Deprecated. Use `GET /playlists/{playlist_id}/items` instead.

#### Update Playlist Items [DEPRECATED]

`PUT /playlists/{playlist_id}/tracks`

**Note:** Deprecated. Use `PUT /playlists/{playlist_id}/items` instead.

#### Add Items to Playlist [DEPRECATED]

`POST /playlists/{playlist_id}/tracks`

**Note:** Deprecated. Use `POST /playlists/{playlist_id}/items` instead.

#### Remove Playlist Items [DEPRECATED]

`DELETE /playlists/{playlist_id}/tracks`

**Note:** Deprecated. Use `DELETE /playlists/{playlist_id}/items` instead.

#### Get Playlist Items

`GET /playlists/{playlist_id}/items`

Get full details of the items of a playlist.

**Scopes:** `playlist-read-private` (private), `playlist-read-collaborative` (collaborative)

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID |
| market | string | no | ISO 3166-1 alpha-2 country code |
| fields | string | no | Comma-separated field filter |
| limit | integer | no | Max items. Default: 20, max: 100 |
| offset | integer | no | Index offset |
| additional_types | string | no | "track", "episode" |

**Response:** 200 Paging of PlaylistItemObjects

PlaylistItemObject fields: `added_at`, `added_by` (PublicUserObject), `is_local`, `item` (TrackObject or EpisodeObject or null)

#### Update Playlist Items

`PUT /playlists/{playlist_id}/items`

Reorder or replace items in a playlist.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Body:**
```json
{
  "uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"],
  "range_start": 1,
  "insert_before": 3,
  "range_length": 2,
  "snapshot_id": "string"
}
```

**Response:** 200 `{ "snapshot_id": "string" }`

#### Add Items to Playlist

`POST /playlists/{playlist_id}/items`

Add one or more items to a playlist.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID |
| position | integer | no | 0-based insert position |

**Body:**
```json
{
  "uris": ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"],
  "position": 0
}
```

**Response:** 201 `{ "snapshot_id": "string" }`

#### Remove Playlist Items

`DELETE /playlists/{playlist_id}/items`

Remove one or more items from a playlist.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Body:**
```json
{
  "tracks": [{ "uri": "spotify:track:4iV5W9uYEdYUVa79Axb7Rh" }],
  "snapshot_id": "string"
}
```

**Response:** 200 `{ "snapshot_id": "string" }`

#### Get Current User's Playlists

`GET /me/playlists`

Get a list of the playlists owned or followed by the current user.

**Scopes:** `playlist-read-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SimplifiedPlaylistObjects

#### Create Playlist

`POST /users/{user_id}/playlists`

Create a playlist for a Spotify user.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| user_id | string | yes | User's Spotify ID |

**Body:**
```json
{
  "name": "New Playlist",
  "public": true,
  "collaborative": false,
  "description": "New playlist description"
}
```

**Response:** 201 PlaylistObject

#### Get User's Playlists

`GET /users/{user_id}/playlists`

Get a list of the playlists owned or followed by a Spotify user.

**Scopes:** `playlist-read-private` (current user's private playlists), `playlist-read-collaborative`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| user_id | string | yes | User's Spotify ID |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SimplifiedPlaylistObjects

#### Create Playlist for User [DEPRECATED]

`POST /users/{user_id}/playlists`

**Note:** Deprecated. Use `Create Playlist` (`POST /users/{user_id}/playlists`) — same endpoint, use that reference instead.

#### Get Featured Playlists

`GET /browse/featured-playlists`

Get a list of Spotify featured playlists.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| locale | string | no | Language/country code |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 `{ "message": "string", "playlists": PagingObject[SimplifiedPlaylistObject] }`

#### Get Category's Playlists

`GET /browse/categories/{category_id}/playlists`

Get a list of Spotify playlists tagged with a particular category.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| category_id | string | yes | Spotify category ID |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 `{ "message": "string", "playlists": PagingObject[SimplifiedPlaylistObject] }`

#### Get Playlist Cover Image

`GET /playlists/{playlist_id}/images`

Get the current image associated with a specific playlist.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID of the playlist |

**Response:** 200 array of ImageObjects `[{ url, height, width }]`

#### Add Custom Playlist Cover Image

`PUT /playlists/{playlist_id}/images`

Replace the image used to represent a specific playlist.

**Scopes:** `ugc-image-upload`, plus `playlist-modify-public` or `playlist-modify-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID |

**Body:** Base64-encoded JPEG image data (Content-Type: image/jpeg). Max size: 256 KB.

**Response:** 202 Accepted

---

### Search

#### Search for Item

`GET /search`

Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes, or audiobooks that match a keyword string.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| q | string | yes | Search query. Supports field filters: album, artist, track, year, upc, tag:hipster, tag:new, isrc, genre |
| type | string | yes | Comma-separated types: album, artist, playlist, track, show, episode, audiobook |
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max results per type. Default: 20. Max: 10 (Dev Mode) / 50 (Extended Quota) |
| offset | integer | no | Index offset. Max: 1000 |
| include_external | string | no | "audio" to include externally hosted audio content |

**Response:** 200 SearchResultObject

| Field | Type | Description |
|---|---|---|
| tracks | PagingObject[TrackObject] | Track results |
| artists | PagingObject[ArtistObject] | Artist results |
| albums | PagingObject[SimplifiedAlbumObject] | Album results |
| playlists | PagingObject[SimplifiedPlaylistObject] | Playlist results |
| shows | PagingObject[SimplifiedShowObject] | Show results |
| episodes | PagingObject[SimplifiedEpisodeObject] | Episode results |
| audiobooks | PagingObject[SimplifiedAudiobookObject] | Audiobook results |

**Query syntax examples:**
- `q=remaster%20track:Doxy%20artist:Miles%20Davis`
- `q=year:1955-1960`
- `q=genre:jazz`

---

### Shows

#### Get Show

`GET /shows/{id}`

Get Spotify catalog information for a single show.

**Scopes:** `user-read-playback-position`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the show |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 ShowObject

| Field | Type | Description |
|---|---|---|
| available_markets | array[string] | Available markets |
| copyrights | array[CopyrightObject] | Copyright info |
| description | string | Description |
| html_description | string | HTML description |
| explicit | boolean | Explicit flag |
| external_urls | object | Spotify URL |
| href | string | API link |
| id | string | Spotify ID |
| images | array[ImageObject] | Show images |
| is_externally_hosted | boolean | Externally hosted |
| languages | array[string] | Languages |
| media_type | string | Media type |
| name | string | Show name |
| publisher | string | Publisher |
| type | string | "show" |
| uri | string | Spotify URI |
| total_episodes | integer | Total episode count |
| episodes | PagingObject[SimplifiedEpisodeObject] | Paged episodes |

#### Get Several Shows [DEPRECATED]

`GET /shows`

**Note:** Deprecated. Use individual `GET /shows/{id}` calls instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| market | string | no | ISO 3166-1 alpha-2 country code |
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `{ "shows": [SimplifiedShowObject] }`

#### Get Show Episodes

`GET /shows/{id}/episodes`

Get Spotify catalog information about an show's episodes.

**Scopes:** `user-read-playback-position`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the show |
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SimplifiedEpisodeObjects

#### Get User's Saved Shows

`GET /me/shows`

Get a list of shows saved in the current Spotify user's library.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset |

**Response:** 200 Paging of SavedShowObjects `{ added_at, show }`

#### Save Shows for Current User [DEPRECATED]

`PUT /me/shows`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 empty

#### Remove User's Saved Shows [DEPRECATED]

`DELETE /me/shows`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 empty

#### Check User's Saved Shows [DEPRECATED]

`GET /me/shows/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `[false, true]`

---

### Tracks

#### Get Track

`GET /tracks/{id}`

Get Spotify catalog information for a single track.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the track |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 TrackObject

| Field | Type | Description |
|---|---|---|
| album | SimplifiedAlbumObject | Album the track appears on |
| artists | array[SimplifiedArtistObject] | Artists who performed the track |
| available_markets | array[string] | **Deprecated.** Available markets |
| disc_number | integer | Disc number (usually 1) |
| duration_ms | integer | Track length in milliseconds |
| explicit | boolean | Explicit lyrics flag |
| external_ids | object | `{ isrc, ean, upc }` |
| external_urls | object | Spotify URL |
| href | string | API link |
| id | string | Spotify ID |
| is_playable | boolean | Playable in given market |
| linked_from | object | **Deprecated.** Original track info if relinked |
| restrictions | object | Restriction reason if restricted |
| name | string | Track name |
| popularity | integer | **Deprecated.** 0-100 popularity |
| preview_url | string | **Deprecated/null.** 30-second preview URL |
| track_number | integer | Track number on disc |
| type | string | "track" |
| uri | string | Spotify URI |
| is_local | boolean | Local file flag |

```json
{
  "album": { "album_type": "compilation", "id": "string", "name": "string", "type": "album", "uri": "string" },
  "artists": [{ "id": "string", "name": "string", "type": "artist", "uri": "string" }],
  "disc_number": 1,
  "duration_ms": 237040,
  "explicit": false,
  "external_ids": { "isrc": "string", "ean": "string", "upc": "string" },
  "external_urls": { "spotify": "string" },
  "href": "string",
  "id": "string",
  "is_playable": true,
  "name": "string",
  "track_number": 1,
  "type": "track",
  "uri": "string",
  "is_local": false
}
```

#### Get Several Tracks [DEPRECATED]

`GET /tracks`

**Note:** Deprecated. Use individual `GET /tracks/{id}` calls instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |
| market | string | no | ISO 3166-1 alpha-2 country code |

**Response:** 200 `{ "tracks": [TrackObject] }`

#### Get User's Saved Tracks

`GET /me/tracks`

Get a list of the songs saved in the current Spotify user's 'Your Music' library.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| market | string | no | ISO 3166-1 alpha-2 country code |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset. Default: 0 |

**Response:** 200 Paging of SavedTrackObjects

| Field | Type | Description |
|---|---|---|
| href | string | API link |
| limit | integer | Max items |
| next | string | Next page URL (null if none) |
| offset | integer | Current offset |
| previous | string | Previous page URL (null if none) |
| total | integer | Total items |
| items | array[SavedTrackObject] | Each has `added_at` and `track` (TrackObject) |

```json
{
  "href": "https://api.spotify.com/v1/me/tracks?offset=0&limit=20",
  "limit": 20,
  "next": null,
  "offset": 0,
  "previous": null,
  "total": 4,
  "items": [{ "added_at": "string", "track": {} }]
}
```

#### Save Tracks for Current User [DEPRECATED]

`PUT /me/tracks`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `user-library-modify`

**Body:**
```json
{
  "ids": ["4iV5W9uYEdYUVa79Axb7Rh"],
  "timestamped_ids": [{ "id": "string", "added_at": "2023-01-15T14:30:00Z" }]
}
```

Note: If `timestamped_ids` is present, `ids` is ignored. Max 50 items.

**Response:** 200 empty

#### Remove User's Saved Tracks [DEPRECATED]

`DELETE /me/tracks`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `user-library-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Body (optional):** `{ "ids": ["string"] }`

**Response:** 200 empty

#### Check User's Saved Tracks [DEPRECATED]

`GET /me/tracks/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Scopes:** `user-library-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `[false, true]`

#### Get Several Tracks' Audio Features [FAILED]

`GET /audio-features`

**Note:** This endpoint returned empty content during documentation compilation. Get audio features for multiple tracks. Returns an `audio_features` array of AudioFeaturesObjects (same fields as single track audio features). Max 100 IDs.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| ids | string | yes | Comma-separated track IDs. Max 100 |

**Response:** 200 `{ "audio_features": [AudioFeaturesObject] }`

#### Get Track's Audio Features

`GET /audio-features/{id}`

Get audio feature information for a single track.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the track |

**Response:** 200 AudioFeaturesObject

| Field | Type | Description |
|---|---|---|
| acousticness | float | 0.0-1.0 confidence measure of acoustic quality |
| analysis_url | string | URL for full audio analysis |
| danceability | float | 0.0-1.0 suitability for dancing |
| duration_ms | integer | Track duration in ms |
| energy | float | 0.0-1.0 intensity/activity measure |
| id | string | Spotify ID |
| instrumentalness | float | 0.0-1.0 likelihood of no vocals |
| key | integer | Pitch class (-1 if none detected). 0=C, 1=C#/Db, ..., 11=B |
| liveness | float | 0.0-1.0 presence of live audience |
| loudness | float | Overall loudness in dB (typically -60 to 0) |
| mode | integer | 0=minor, 1=major |
| speechiness | float | 0.0-1.0 presence of spoken words |
| tempo | float | Estimated BPM |
| time_signature | integer | 3-7 (notational beats per bar) |
| track_href | string | API link to full track |
| type | string | "audio_features" |
| uri | string | Spotify URI |
| valence | float | 0.0-1.0 musical positiveness |

```json
{
  "acousticness": 0.00242,
  "analysis_url": "https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B",
  "danceability": 0.585,
  "duration_ms": 237040,
  "energy": 0.842,
  "id": "2takcwOaAZWiXQijPHIx7B",
  "instrumentalness": 0.00686,
  "key": 9,
  "liveness": 0.0866,
  "loudness": -5.883,
  "mode": 0,
  "speechiness": 0.0556,
  "tempo": 118.211,
  "time_signature": 4,
  "track_href": "https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B",
  "type": "audio_features",
  "uri": "spotify:track:2takcwOaAZWiXQijPHIx7B",
  "valence": 0.428
}
```

#### Get Track's Audio Analysis

`GET /audio-analysis/{id}`

Get a low-level audio analysis for a track. Describes structure and musical content including rhythm, pitch, and timbre.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| id | string | yes | Spotify ID of the track |

**Response:** 200 AudioAnalysisObject

Top-level fields:

| Field | Type | Description |
|---|---|---|
| meta | object | `analyzer_version`, `platform`, `detailed_status`, `status_code`, `timestamp`, `analysis_time`, `input_process` |
| track | object | Track-level summary (see below) |
| bars | array[TimeInterval] | Bar intervals `{ start, duration, confidence }` |
| beats | array[TimeInterval] | Beat intervals `{ start, duration, confidence }` |
| sections | array[Section] | Sections with `start`, `duration`, `confidence`, `loudness`, `tempo`, `key`, `mode`, `time_signature` + confidence values |
| segments | array[Segment] | Segments with `start`, `duration`, `loudness_start`, `loudness_max`, `loudness_max_time`, `pitches` (12-dim chroma vector), `timbre` (12 coefficients) |
| tatums | array[TimeInterval] | Tatum intervals `{ start, duration, confidence }` |

Track object fields: `num_samples`, `duration`, `analysis_sample_rate`, `analysis_channels`, `end_of_fade_in`, `start_of_fade_out`, `loudness`, `tempo`, `tempo_confidence`, `time_signature`, `time_signature_confidence`, `key`, `key_confidence`, `mode`, `mode_confidence`, `codestring`, `echoprintstring`, `synchstring`, `rhythmstring`

```json
{
  "meta": { "analyzer_version": "4.0.0", "platform": "Linux", "detailed_status": "OK", "status_code": 0, "timestamp": 1495193577, "analysis_time": 6.93906, "input_process": "libvorbisfile L+R 44100->22050" },
  "track": { "num_samples": 4585515, "duration": 207.95985, "loudness": -5.883, "tempo": 118.211, "key": 9, "mode": 0, "time_signature": 4 },
  "bars": [{ "start": 0.49567, "duration": 2.18749, "confidence": 0.925 }],
  "beats": [{ "start": 0.49567, "duration": 2.18749, "confidence": 0.925 }],
  "sections": [{ "start": 0, "duration": 6.97092, "confidence": 1, "loudness": -14.938, "tempo": 113.178, "key": 9, "mode": -1, "time_signature": 4 }],
  "segments": [{ "start": 0.70154, "duration": 0.19891, "confidence": 0.435, "loudness_start": -23.053, "loudness_max": -14.25, "pitches": [0.212, 0.141, 0.294], "timbre": [42.115, 64.373, -0.233] }],
  "tatums": [{ "start": 0.49567, "duration": 2.18749, "confidence": 0.925 }]
}
```

#### Get Recommendations [FAILED]

`GET /recommendations`

**Note:** This endpoint returned empty content during documentation compilation. Based on API documentation, it returns track recommendations based on seed artists, tracks, and genres, with optional tunable audio feature targets.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| seed_artists | string | yes* | Comma-separated artist IDs |
| seed_genres | string | yes* | Comma-separated genre names |
| seed_tracks | string | yes* | Comma-separated track IDs |
| limit | integer | no | Max recommendations. Default: 20, max: 100 |
| market | string | no | ISO 3166-1 alpha-2 country code |
| min_*/max_*/target_* | float | no | Tunable audio feature constraints (acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, popularity, speechiness, tempo, time_signature, valence) |

*At least one seed type required. Total seeds (artists + genres + tracks) must not exceed 5.

**Response:** 200 `{ "seeds": [RecommendationSeedObject], "tracks": [SimplifiedTrackObject] }`

---

### Users

#### Get Current User's Profile

`GET /me`

Get detailed profile information about the current user.

**Scopes:** `user-read-private`, `user-read-email`

**Response:** 200 PrivateUserObject

| Field | Type | Description |
|---|---|---|
| country | string | **Deprecated.** ISO 3166-1 alpha-2 code. Requires `user-read-private` |
| display_name | string | Display name (null if unavailable) |
| email | string | **Deprecated.** Email address. Requires `user-read-email` |
| explicit_content | object | **Deprecated.** `{ filter_enabled, filter_locked }`. Requires `user-read-private` |
| external_urls | object | Spotify URL |
| followers | object | **Deprecated.** `{ href: null, total }` |
| href | string | API link |
| id | string | Spotify user ID |
| images | array[ImageObject] | Profile images |
| product | string | **Deprecated.** Subscription level: "premium", "free". Requires `user-read-private` |
| type | string | "user" |
| uri | string | Spotify URI |

```json
{
  "country": "string",
  "display_name": "string",
  "email": "string",
  "explicit_content": { "filter_enabled": false, "filter_locked": false },
  "external_urls": { "spotify": "string" },
  "followers": { "href": null, "total": 0 },
  "href": "string",
  "id": "string",
  "images": [{ "url": "string", "height": 300, "width": 300 }],
  "product": "string",
  "type": "user",
  "uri": "string"
}
```

#### Get User's Top Items

`GET /me/top/{type}`

Get the current user's top artists or tracks based on calculated affinity.

**Scopes:** `user-top-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| type | string | yes | "artists" or "tracks" |
| time_range | string | no | "long_term" (~1 year), "medium_term" (~6 months), "short_term" (~4 weeks). Default: "medium_term" |
| limit | integer | no | Max items. Default: 20, max: 50 |
| offset | integer | no | Index offset. Default: 0 |

**Response:** 200 Paging of ArtistObject or TrackObject (depending on type)

```json
{
  "href": "string",
  "limit": 20,
  "next": null,
  "offset": 0,
  "previous": null,
  "total": 4,
  "items": [{ "id": "string", "name": "string", "type": "artist", "uri": "string" }]
}
```

#### Get User's Profile [DEPRECATED]

`GET /users/{user_id}`

**Note:** Deprecated. Returns public profile information for a Spotify user.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| user_id | string | yes | Spotify user ID |

**Response:** 200 PublicUserObject

| Field | Type | Description |
|---|---|---|
| display_name | string | Display name (null if unavailable) |
| external_urls | object | Public external URLs |
| followers | object | **Deprecated.** `{ href: null, total }` |
| href | string | API link |
| id | string | Spotify user ID |
| images | array[ImageObject] | Profile images |
| type | string | "user" |
| uri | string | Spotify URI |

#### Follow Playlist [DEPRECATED]

`PUT /playlists/{playlist_id}/followers`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID of the playlist |

**Body:** `{ "public": true }` — include in user's public playlists

**Response:** 200 empty

#### Unfollow Playlist [DEPRECATED]

`DELETE /playlists/{playlist_id}/followers`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `playlist-modify-public` or `playlist-modify-private`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID of the playlist |

**Response:** 200 empty

#### Get Followed Artists

`GET /me/following`

Get the current user's followed artists.

**Scopes:** `user-follow-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| type | string | yes | Must be "artist" |
| after | string | no | Last artist ID from previous request (cursor) |
| limit | integer | no | Max items. Default: 20, max: 50 |

**Response:** 200 `{ "artists": CursorPagingObject[ArtistObject] }`

CursorPagingObject fields: `href`, `limit`, `next`, `cursors` (`{ after, before }`), `total`, `items`

```json
{
  "artists": {
    "href": "string",
    "limit": 20,
    "next": "string",
    "cursors": { "after": "string", "before": "string" },
    "total": 0,
    "items": [{ "id": "string", "name": "string", "type": "artist" }]
  }
}
```

#### Follow Artists or Users [DEPRECATED]

`PUT /me/following`

**Note:** Deprecated. Use `PUT /me/library` instead.

**Scopes:** `user-follow-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| type | string | yes | "artist" or "user" |
| ids | string | yes | Comma-separated IDs. Max 50 |

**Body:** `{ "ids": ["string"] }` (body IDs ignored if query `ids` present)

**Response:** 204 No Content

#### Unfollow Artists or Users [DEPRECATED]

`DELETE /me/following`

**Note:** Deprecated. Use `DELETE /me/library` instead.

**Scopes:** `user-follow-modify`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| type | string | yes | "artist" or "user" |
| ids | string | yes | Comma-separated IDs. Max 50 |

**Body (optional):** `{ "ids": ["string"] }`

**Response:** 204 No Content

#### Check If User Follows Artists or Users [DEPRECATED]

`GET /me/following/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Scopes:** `user-follow-read`

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| type | string | yes | "artist" or "user" |
| ids | string | yes | Comma-separated IDs. Max 50 |

**Response:** 200 `[false, true]`

#### Check if Current User Follows Playlist [DEPRECATED]

`GET /playlists/{playlist_id}/followers/contains`

**Note:** Deprecated. Use `GET /me/library/contains` instead.

**Parameters:**
| Name | Type | Required | Description |
|---|---|---|---|
| playlist_id | string | yes | Spotify ID of the playlist |
| ids | string | no | **Deprecated.** Single current user's Spotify username. Max 1 |

**Response:** 200 `[true]` — single-element boolean array

