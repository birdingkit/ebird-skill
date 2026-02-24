---
name: ebird-query
description: Query the eBird API to answer birdwatching questions. Use this skill whenever the user asks about birds, bird sightings, birdwatching locations, recent observations, rare birds, hotspots, species lists, or anything related to eBird data. Trigger on phrases like "where can I see [bird]", "what birds are in [location]", "recent sightings", "rare birds near me", "birding hotspots", "eBird", "鳥", "賞鳥", "野鳥", or any conversation about bird species and their locations. Also trigger when the user asks about top eBird contributors, checklist statistics, or notable observations in a region. Even if the user doesn't mention eBird explicitly, if they're asking about real-world bird sighting data or where to find specific species, use this skill.
---

# eBird Query Skill

This skill lets you query the eBird API 2.0 to answer birdwatching questions. You can look up recent observations, find hotspots, search for specific species, discover rare/notable birds, and get regional statistics.

## Setup

The user needs an eBird API key. If they haven't provided one yet in this conversation, ask them to paste it.

API keys are free — users can register at https://ebird.org/api/keygen

**IMPORTANT — API key must never appear in plaintext in terminal commands.** Follow this procedure:

1. After the user provides a key, write it to a temp file: `cat > /tmp/.ebird_env <<< "export EBIRD_API_KEY=<key>"`
2. Source it before every command: `source /tmp/.ebird_env && python ebird_api.py ...`
3. Never use the `--key <key>` flag or inline `EBIRD_API_KEY=<key> python ...` syntax — both expose the key in terminal output

## How to Use

Run the bundled Python script `ebird_api.py` (located in this skill's directory) to make API calls. The script reads the API key from the `EBIRD_API_KEY` environment variable, so always source the key file before running.

### General Pattern

```bash
source /tmp/.ebird_env && python /path/to/ebird_api.py <command> [options]
```

### Available Commands

#### 1. `recent` — Recent observations in a region
Find what birds have been seen recently in a region.

```bash
source /tmp/.ebird_env && python ebird_api.py recent --region TW --back 7 --locale zh
```
- `--region`: eBird region code (e.g., `TW`, `JP`, `US-NY`, `TW-TPE`)
- `--back`: Number of days back (1-30, default 14)
- `--locale`: Language for common names (default `en`, use `zh` for Chinese)
- `--max`: Max results (default 50)
- `--hotspot`: If set, only include observations from hotspots
- `--category`: Filter by category (e.g., `species`, `hybrid`)

#### 2. `nearby` — Recent observations near coordinates
Find what birds have been seen near a specific location.

```bash
python ebird_api.py nearby --lat 25.03 --lng 121.56 --dist 25 --back 7
```
- `--lat`, `--lng`: Coordinates (required)
- `--dist`: Search radius in km (default 25, max 50)
- `--back`: Days back (1-30, default 14)

#### 3. `notable` — Notable/rare observations in a region
Find rare or unusual species reported in a region.

```bash
python ebird_api.py notable --region TW --back 14
```

#### 4. `nearby-notable` — Notable observations near coordinates

```bash
python ebird_api.py nearby-notable --lat 25.03 --lng 121.56 --dist 50
```

#### 5. `species` — Recent observations of a specific species
Find where a specific species has been seen recently.

```bash
python ebird_api.py species --code barswa1 --region TW
```
- `--code`: eBird species code (e.g., `barswa1` for Barn Swallow). Use the `taxonomy` command to look up codes.

#### 6. `nearby-species` — Find a specific species near coordinates

```bash
python ebird_api.py nearby-species --code barswa1 --lat 25.03 --lng 121.56
```

#### 7. `hotspots` — Hotspots in a region
Find popular birdwatching locations.

```bash
python ebird_api.py hotspots --region TW-TPE
```

#### 8. `nearby-hotspots` — Hotspots near coordinates

```bash
python ebird_api.py nearby-hotspots --lat 25.03 --lng 121.56 --dist 25
```

#### 9. `taxonomy` — Search for species by name
Look up species codes and scientific names. Useful when you need the species code for other commands.

```bash
python ebird_api.py taxonomy --species "Barn Swallow"
python ebird_api.py taxonomy --species "黑面琵鷺" --locale zh
```
- `--species`: Common or partial name to search for
- `--locale`: Language of the name you're searching

#### 10. `hotspot-info` — Details about a specific hotspot

```bash
python ebird_api.py hotspot-info --loc L1234567
```

#### 11. `historic` — Observations on a specific date

```bash
python ebird_api.py historic --region TW --date 2025-01-15
```

#### 12. `top100` — Top 100 contributors in a region on a date

```bash
python ebird_api.py top100 --region TW --date 2025-01-15
```

#### 13. `stats` — Regional statistics (number of contributors, checklists, species) on a date

```bash
python ebird_api.py stats --region TW --date 2025-01-15
```

#### 14. `sub-regions` — List sub-regions of a region

```bash
python ebird_api.py sub-regions --region TW --type subnational1
```
- `--type`: `subnational1` (states/counties) or `subnational2` (cities/districts)

## Region Code Reference

eBird uses hierarchical region codes:
- Country: `TW` (Taiwan), `JP` (Japan), `US`, `GB`, etc.
- State/County: `TW-TPE` (Taipei), `JP-13` (Tokyo), `US-NY` (New York)
- Sub-region: `US-NY-061` (New York County)
- Location: `L1234567` (specific hotspot ID)

If the user mentions a place name instead of a code, help them figure out the right code. You can use `sub-regions` to discover valid sub-region codes, or look up the region code from your knowledge.

### Taiwan Region Codes

- `TW-TPE` Taipei City, `TW-NWT` New Taipei, `TW-KEE` Keelung
- `TW-TAO` Taoyuan, `TW-HSZ` Hsinchu City, `TW-HSQ` Hsinchu County
- `TW-MIA` Miaoli, `TW-TXG` Taichung, `TW-CHA` Changhua, `TW-NAN` Nantou
- `TW-YUN` Yunlin, `TW-CYI` Chiayi County, `TW-CYQ` Chiayi City
- `TW-TNN` Tainan, `TW-KHH` Kaohsiung, `TW-PIF` Pingtung
- `TW-ILA` Yilan, `TW-HUA` Hualien, `TW-TTT` Taitung
- `TW-PEN` Penghu, `TW-KIN` Kinmen, `TW-LIE` Lienchiang (Matsu)

### Handling Sub-county Locations (Townships, Wetlands, Scenic Areas)

eBird region codes only go down to county level. For townships or specific locations (e.g., 布袋, 鰲鼓, 七股), there is no region code. **Use coordinates with `nearby` series commands instead.** Look up approximate coordinates from your knowledge and use `--dist` to set an appropriate radius.

## Interpreting Results and Responding

When presenting results to the user:

1. **Summarize clearly in conversation** — don't dump raw JSON. Pull out the interesting bits: species name, location, date, count.
2. **Use the user's language** — if the user writes in Chinese, respond in Chinese and use `--locale zh` when available.
3. **Be a helpful birding companion** — if the user asks "where can I see a Black-faced Spoonbill", first look up the species code via taxonomy, then query recent observations or nearby-species. Chain multiple calls as needed.
4. **Handle errors gracefully** — if a species code is wrong or a region code is invalid, explain and suggest alternatives.
5. **Suggest follow-ups** — after showing results, you might suggest checking nearby hotspots, looking at notable birds, or broadening the search area.

## Multi-step Query Strategy

Many user questions require chaining multiple API calls:

- "Where can I see [bird]?" → `taxonomy` (get code) → `species` or `nearby-species`
- "[specific location] 的 [bird]" → `taxonomy` (get code) → `nearby-species` (use coordinates of that location)
- "What rare birds are near me?" → `nearby-notable` (with user's coordinates)
- "Best birding spots in [area]?" → `hotspots` → optionally `recent` for top hotspots
- "What birds are at [hotspot]?" → `recent` with the hotspot's region or location ID
- "Who are the top birders in Taiwan today?" → `top100`
