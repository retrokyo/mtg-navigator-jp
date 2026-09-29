# MTG Navigator JP

A desktop tool for searching *Magic: The Gathering* card availability and prices across Japanese online card shops.

Enter a card name (in any language/misspelling Scryfall can resolve via fuzzy search), and MTG Navigator opens the resolved card's search results side-by-side across:

- [BigWeb](https://mtg.bigweb.co.jp)
- [Hareruya](https://www.hareruyamtg.com)
- [SingleStar](https://www.singlestar.jp)

Results are sorted by price (ascending) and can optionally be filtered to in-stock listings only.

## How it works

1. A card name is resolved to its canonical English name via the [Scryfall](https://scryfall.com) API (`/cards/named?fuzzy=`).
2. A persistent Playwright-controlled Chromium browser session opens one tab per shop.
3. Each shop's tab is navigated to that shop's search/filter results for the resolved card name, sorted by price and optionally filtered to in-stock items.
4. A small Tkinter GUI drives the search and reports success/failure per query; the browser window itself is left open so you can review and purchase.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
uv run playwright install chromium
```

## Usage

```bash
uv run mtg-navigator
```

This opens a small window with a card name field and an "In Stock Only" checkbox. Enter a card name and press Enter (or click Search) — a browser window will open (or reuse the existing one) and navigate each shop to the matching results.

## Project layout

```
main.py                          # Tkinter GUI entry point
src/mtg_navigator/
├── scryfall.py                  # Scryfall fuzzy-search client (rate-limited)
├── BrowserSession.py            # Background asyncio + Playwright browser lifecycle
├── BaseWeb.py                   # Shared interface for per-shop search adapters
├── bigweb.py                    # BigWeb search adapter
├── hareruya.py                  # Hareruya search adapter
└── singlestar.py                # SingleStar search adapter
```

Each shop adapter subclasses `BaseWeb`, which reuses an existing browser tab for that shop's domain if one is already open, and implements `search()` to navigate to that shop's price-sorted (and optionally in-stock-only) results for a given card name.

## Notes

- The browser launches non-headless (`headless=False`) since the intent is to leave the results open for browsing/purchasing, not to scrape data.
- All three shop searches run concurrently via `asyncio.gather`.
- Scryfall requests are throttled to respect its API guidelines (~100ms between requests) and back off on `429` responses.
