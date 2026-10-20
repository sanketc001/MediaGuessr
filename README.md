# MediaGuessr

**An MCP (Model Context Protocol) server that turns a multimodal LLM client into a "media detective": show it a frame from a movie, show, game, or a dish, and it identifies the source, pulls IMDb metadata, finds recipe videos, and plans a trip around the real-world filming location.**

## What it does and why

Vision-capable LLMs are good at recognising a scene, but they need grounded tools to fetch reliable metadata and to act on what they see. MediaGuessr exposes a small set of tools and prompt templates over MCP so any MCP-compatible client (e.g. an IDE agent or desktop chat app) can:

- Identify a movie/show/game scene and fetch structured metadata from IMDb.
- Locate the real-world shooting location and suggest a themed travel itinerary.
- Identify a dish, find YouTube recipe videos for it, and suggest places to try it near the user.

The orchestration logic lives in the `mediaGuessr` prompt; the server supplies the tools the model calls along the way.

## Architecture

```
 MCP client (vision LLM)
        │  stdio (MCP)
        ▼
 FastMCP server "MediaGuessr"  (main.py)
   ├── tool   get_info_imdb_id(imdb_id)      → Cinemagoer (IMDb)
   ├── tool   get_user_location()            → ip-api.com (IP geolocation)
   ├── tool   youtube_recipe_search(query)   → youtube-search (top 2 results)
   ├── prompt mediaGuessr()                  → step-by-step agent instructions
   └── prompt hotel_search_assistant(loc)    → travel/hotel prompt template
```

| Component | Description |
|---|---|
| `get_info_imdb_id` | Looks up a title by IMDb ID (numeric part, e.g. `0111161`) via Cinemagoer and returns all fields as JSON-safe strings. |
| `get_user_location` | Approximate latitude/longitude, city, region and country from the caller's public IP. |
| `youtube_recipe_search` | Returns the top 2 YouTube results for a recipe query. |
| `mediaGuessr` prompt | Instruction set: classify the image (scene vs. food), identify the source, fetch IMDb info, describe real and fictional locations, build a trip plan or recipe/restaurant suggestions, and return top-3 guesses when uncertain. |
| `hotel_search_assistant` prompt | Parameterised travel-assistant prompt for a destination. |

## Tech stack

- Python 3.12, managed with [uv](https://docs.astral.sh/uv/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) (`FastMCP`)
- [Cinemagoer](https://cinemagoer.github.io/) (IMDb data), `youtube-search`, `requests`

## Quickstart

```bash
git clone https://github.com/sanketc001/MediaGuessr.git
cd MediaGuessr
uv sync

# Interactive testing with the MCP Inspector
uv run mcp dev main.py

# Run as a stdio server
uv run mcp run main.py
```

### Connecting from an MCP client

Register it as a stdio server. Example (VS Code `mcp.json`-style config; adjust paths):

```json
{
  "servers": {
    "MediaGuessr": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "mcp", "run", "/absolute/path/to/MediaGuessr/main.py"]
    }
  }
}
```

## Configuration

No API keys or environment variables are required. The server calls public endpoints (IMDb via Cinemagoer, `ip-api.com`, YouTube search) and needs outbound internet access.

## Usage

1. Connect the server to a client that supports images.
2. Select the `mediaGuessr` prompt and attach a screenshot (a film still, game scene, or food photo).
3. The model identifies the media and calls the tools as needed, for example:
   - `get_info_imdb_id("0111161")` → metadata for *The Shawshank Redemption*
   - `youtube_recipe_search("ratatouille recipe")` → recipe videos
   - `get_user_location()` → used to localise restaurant suggestions

## Limitations and next steps

- Image recognition itself is done by the client's model; the server does not perform any vision processing, so accuracy depends on the model used.
- `hotel_search_assistant` refers to a `search_hotels` tool that is not implemented yet.
- Restaurant and filming-location lookups rely on the model's own knowledge; adding a maps/places API tool would ground these.
- IP-based geolocation is approximate and reflects the machine running the server.
- `youtube-search` scrapes YouTube results and can break when the page format changes; the official YouTube Data API would be more robust.
- No automated tests yet.
