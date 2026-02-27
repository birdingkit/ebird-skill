[繁體中文](README.zh-TW.md) | **English**

# ebird-skill

A [Claude Code](https://claude.com/claude-code) skill for querying the [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59). Ask about bird sightings, hotspots, rare birds, species lists, and regional statistics — Claude handles the API calls for you.

## Installation

Add this skill to Claude Code:

```bash
claude skill add /path/to/ebird-skill
```

## API Key

You need a free eBird API key. Register at: https://ebird.org/api/keygen

When you use the skill, Claude will ask for your API key if you haven't provided one yet.

## What You Can Ask

**Bird sightings**
- "What birds have been seen in Taipei recently?"
- "Where can I see a Black-faced Spoonbill?"
- "What rare birds are near me?"
- "Best birding hotspots in Yilan?"
- "Who are the top eBird contributors in Taiwan today?"
- "台北最近有什麼鳥？" (supports Mandarin and other languages)

**Data analysis & export**
- "Export the results to CSV"
- "Compare species counts between Taipei and Tainan over the past month"
- "Plot the Black-faced Spoonbill count trend in Qigu over the past two weeks"
- "Use R to analyze bird diversity in Chiayi coastal wetlands"
- "Map the number of eBird hotspots by county across Taiwan"

## Supported Commands

| Command | Description |
|---------|-------------|
| `recent` | Recent observations in a region |
| `nearby` | Recent observations near coordinates |
| `notable` | Rare/notable observations in a region |
| `nearby-notable` | Rare/notable observations near coordinates |
| `species` | Recent observations of a specific species |
| `nearby-species` | Find a specific species near coordinates |
| `nearest-species` | Nearest locations where a species has been seen |
| `hotspots` | Birdwatching hotspots in a region |
| `nearby-hotspots` | Hotspots near coordinates |
| `taxonomy` | Search for species by name (with local cache) |
| `hotspot-info` | Details about a specific hotspot |
| `historic` | Observations on a specific date |
| `recent-checklists` | Most recently submitted checklists in a region |
| `checklist-feed` | Checklists submitted on a specific date |
| `species-list` | All species ever observed in a region |
| `view-checklist` | View details of a specific checklist |
| `top100` | Top 100 contributors on a date |
| `stats` | Regional statistics on a date |
| `sub-regions` | List sub-regions of a region |
| `region-info` | Name, bounds, and geographic info for a region |
| `adjacent-regions` | Regions sharing a border |
| `taxonomy-forms` | Subspecies/forms for a species |
| `taxonomy-versions` | List all taxonomy versions |
| `taxonomy-groups` | Species groups (terns, finches, etc.) |
| `taxonomy-locales` | Supported locale codes for species names |

## Using with R or Other Languages

This skill fetches data via a Python script, but the returned JSON can be analyzed and visualized in any language. For example, you can ask Claude to plot species observations with R (ggplot2) or perform statistical analysis — Claude will use this skill to fetch the data, then write R code to process it.

Requirements: Python (for the skill script) plus your preferred analysis environment (R, Julia, etc.).

## Direct Usage

You can also run the script directly:

```bash
python ebird_api.py recent --key YOUR_API_KEY --region TW --back 7 --locale zh
python ebird_api.py taxonomy --key YOUR_API_KEY --species "Barn Swallow"
python ebird_api.py notable --key YOUR_API_KEY --region TW-TPE --back 14
```

Run `python ebird_api.py --help` to see all options.

## License

MIT
