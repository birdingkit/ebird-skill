#!/usr/bin/env python3
"""eBird API 2.0 query tool.

Usage:
    python ebird_api.py <command> --key <API_KEY> [options]

Commands:
    recent, nearby, notable, nearby-notable, species, nearby-species,
    hotspots, nearby-hotspots, taxonomy, hotspot-info, historic,
    top100, stats, sub-regions
"""

import argparse
import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote
from urllib.error import HTTPError, URLError

BASE_URL = "https://api.ebird.org/v2"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "ebird")
CACHE_MAX_AGE = 30 * 24 * 3600  # 30 days in seconds


def api_get(path, api_key, params=None):
    """Make a GET request to the eBird API."""
    url = f"{BASE_URL}{path}"
    if params:
        # Filter out None values
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urlencode(filtered)

    req = Request(url)
    req.add_header("X-eBirdApiToken", api_key)

    try:
        with urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data) if data.strip() else []
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(json.dumps({"error": f"HTTP {e.code}: {e.reason}", "detail": body}))
        sys.exit(1)
    except URLError as e:
        print(json.dumps({"error": f"Connection error: {e.reason}"}))
        sys.exit(1)


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def parse_date(date_str):
    """Parse and validate a YYYY-MM-DD date string. Returns (year, month, day) as strings."""
    parts = date_str.split("-")
    if len(parts) != 3:
        print(json.dumps({"error": f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD."}))
        sys.exit(1)
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        print(json.dumps({"error": f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD with numeric values."}))
        sys.exit(1)
    if not (1 <= m <= 12):
        print(json.dumps({"error": f"Invalid month {m} in date '{date_str}'. Must be 1-12."}))
        sys.exit(1)
    if not (1 <= d <= 31):
        print(json.dumps({"error": f"Invalid day {d} in date '{date_str}'. Must be 1-31."}))
        sys.exit(1)
    return str(y), str(m), str(d)


def _get_cache_path(locale):
    """Return the cache file path for a given locale."""
    return os.path.join(CACHE_DIR, f"taxonomy_{locale}.json")


def _load_taxonomy_cache(locale):
    """Load taxonomy data from cache if valid. Returns data or None."""
    path = _get_cache_path(locale)
    if not os.path.exists(path):
        return None
    try:
        age = time.time() - os.path.getmtime(path)
        if age > CACHE_MAX_AGE:
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_taxonomy_cache(locale, data):
    """Save taxonomy data to cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = _get_cache_path(locale)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def cmd_recent(args):
    """Recent observations in a region."""
    params = {
        "back": args.back,
        "maxResults": args.max,
        "locale": args.locale,
    }
    if args.hotspot:
        params["hotspot"] = "true"
    if args.category:
        params["cat"] = args.category
    data = api_get(f"/data/obs/{args.region}/recent", args.key, params)
    print_json(data)


def cmd_nearby(args):
    """Recent observations near coordinates."""
    params = {
        "lat": args.lat,
        "lng": args.lng,
        "dist": args.dist,
        "back": args.back,
        "maxResults": args.max,
        "locale": args.locale,
    }
    if args.hotspot:
        params["hotspot"] = "true"
    data = api_get("/data/obs/geo/recent", args.key, params)
    print_json(data)


def cmd_notable(args):
    """Notable observations in a region."""
    params = {
        "back": args.back,
        "maxResults": args.max,
        "locale": args.locale,
        "detail": "full",
    }
    data = api_get(f"/data/obs/{args.region}/recent/notable", args.key, params)
    print_json(data)


def cmd_nearby_notable(args):
    """Notable observations near coordinates."""
    params = {
        "lat": args.lat,
        "lng": args.lng,
        "dist": args.dist,
        "back": args.back,
        "maxResults": args.max,
        "locale": args.locale,
        "detail": "full",
    }
    data = api_get("/data/obs/geo/recent/notable", args.key, params)
    print_json(data)


def cmd_species(args):
    """Recent observations of a species in a region."""
    params = {
        "back": args.back,
        "maxResults": args.max,
        "locale": args.locale,
    }
    data = api_get(f"/data/obs/{args.region}/recent/{args.code}", args.key, params)
    print_json(data)


def cmd_nearby_species(args):
    """Recent observations of a species near coordinates."""
    params = {
        "lat": args.lat,
        "lng": args.lng,
        "dist": args.dist,
        "back": args.back,
        "maxResults": args.max,
        "locale": args.locale,
    }
    data = api_get(f"/data/obs/geo/recent/{args.code}", args.key, params)
    print_json(data)


def cmd_hotspots(args):
    """Hotspots in a region."""
    params = {
        "back": args.back,
        "fmt": "json",
    }
    data = api_get(f"/ref/hotspot/{args.region}", args.key, params)
    print_json(data)


def cmd_nearby_hotspots(args):
    """Hotspots near coordinates."""
    params = {
        "lat": args.lat,
        "lng": args.lng,
        "dist": args.dist,
        "back": args.back,
        "fmt": "json",
    }
    data = api_get("/ref/hotspot/geo", args.key, params)
    print_json(data)


def cmd_taxonomy(args):
    """Search taxonomy for species by name."""
    # Try loading from cache first
    data = None
    if not args.no_cache:
        data = _load_taxonomy_cache(args.locale)

    if data is None:
        params = {
            "locale": args.locale,
            "fmt": "json",
            "cat": "species",
        }
        data = api_get("/ref/taxonomy/ebird", args.key, params)
        _save_taxonomy_cache(args.locale, data)

    # Filter by search term
    search = args.species.lower()
    results = []
    for sp in data:
        com = sp.get("comName", "").lower()
        sci = sp.get("sciName", "").lower()
        code = sp.get("speciesCode", "").lower()
        if search in com or search in sci or search in code:
            results.append({
                "speciesCode": sp.get("speciesCode"),
                "comName": sp.get("comName"),
                "sciName": sp.get("sciName"),
                "familyComName": sp.get("familyComName"),
                "order": sp.get("order"),
            })
    # Limit output
    results = results[:20]
    print_json(results)


def cmd_hotspot_info(args):
    """Get info about a specific hotspot."""
    data = api_get(f"/ref/hotspot/info/{args.loc}", args.key)
    print_json(data)


def cmd_historic(args):
    """Observations on a specific date."""
    y, m, d = parse_date(args.date)
    params = {
        "maxResults": args.max,
        "locale": args.locale,
        "detail": "simple",
    }
    if args.category:
        params["cat"] = args.category
    data = api_get(f"/data/obs/{args.region}/historic/{y}/{m}/{d}", args.key, params)
    print_json(data)


def cmd_top100(args):
    """Top 100 contributors on a date in a region."""
    y, m, d = parse_date(args.date)
    params = {
        "maxResults": args.max,
    }
    data = api_get(f"/product/top100/{args.region}/{y}/{m}/{d}", args.key, params)
    print_json(data)


def cmd_stats(args):
    """Regional statistics on a date."""
    y, m, d = parse_date(args.date)
    data = api_get(f"/product/stats/{args.region}/{y}/{m}/{d}", args.key)
    print_json(data)


def cmd_sub_regions(args):
    """List sub-regions of a region."""
    data = api_get(f"/ref/region/list/{args.type}/{args.region}", args.key)
    print_json(data)


def main():
    parser = argparse.ArgumentParser(description="eBird API 2.0 query tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common args helper
    def add_common(p):
        p.add_argument("--key", required=True, help="eBird API key")
        p.add_argument("--locale", default="en", help="Locale for species names")

    def add_region(p):
        p.add_argument("--region", required=True, help="eBird region code")

    def add_geo(p):
        p.add_argument("--lat", required=True, type=float)
        p.add_argument("--lng", required=True, type=float)
        p.add_argument("--dist", type=int, default=25, help="Radius in km (max 50)")

    def add_back(p):
        p.add_argument("--back", type=int, default=14, help="Days back (1-30)")

    def add_max(p):
        p.add_argument("--max", type=int, default=50, help="Max results")

    # recent
    p = subparsers.add_parser("recent")
    add_common(p); add_region(p); add_back(p); add_max(p)
    p.add_argument("--hotspot", action="store_true")
    p.add_argument("--category", default=None)
    p.set_defaults(func=cmd_recent)

    # nearby
    p = subparsers.add_parser("nearby")
    add_common(p); add_geo(p); add_back(p); add_max(p)
    p.add_argument("--hotspot", action="store_true")
    p.set_defaults(func=cmd_nearby)

    # notable
    p = subparsers.add_parser("notable")
    add_common(p); add_region(p); add_back(p); add_max(p)
    p.set_defaults(func=cmd_notable)

    # nearby-notable
    p = subparsers.add_parser("nearby-notable")
    add_common(p); add_geo(p); add_back(p); add_max(p)
    p.set_defaults(func=cmd_nearby_notable)

    # species
    p = subparsers.add_parser("species")
    add_common(p); add_region(p); add_back(p); add_max(p)
    p.add_argument("--code", required=True, help="eBird species code")
    p.set_defaults(func=cmd_species)

    # nearby-species
    p = subparsers.add_parser("nearby-species")
    add_common(p); add_geo(p); add_back(p); add_max(p)
    p.add_argument("--code", required=True, help="eBird species code")
    p.set_defaults(func=cmd_nearby_species)

    # hotspots
    p = subparsers.add_parser("hotspots")
    add_common(p); add_region(p)
    p.add_argument("--back", type=int, default=None)
    p.set_defaults(func=cmd_hotspots)

    # nearby-hotspots
    p = subparsers.add_parser("nearby-hotspots")
    add_common(p); add_geo(p)
    p.add_argument("--back", type=int, default=None)
    p.set_defaults(func=cmd_nearby_hotspots)

    # taxonomy
    p = subparsers.add_parser("taxonomy")
    add_common(p)
    p.add_argument("--species", required=True, help="Species name to search")
    p.add_argument("--no-cache", action="store_true", help="Force re-download taxonomy")
    p.set_defaults(func=cmd_taxonomy)

    # hotspot-info
    p = subparsers.add_parser("hotspot-info")
    add_common(p)
    p.add_argument("--loc", required=True, help="Hotspot location ID")
    p.set_defaults(func=cmd_hotspot_info)

    # historic
    p = subparsers.add_parser("historic")
    add_common(p); add_region(p); add_max(p)
    p.add_argument("--date", required=True, help="Date YYYY-MM-DD")
    p.add_argument("--category", default=None)
    p.set_defaults(func=cmd_historic)

    # top100
    p = subparsers.add_parser("top100")
    add_common(p); add_region(p)
    p.add_argument("--date", required=True, help="Date YYYY-MM-DD")
    p.add_argument("--max", type=int, default=100)
    p.set_defaults(func=cmd_top100)

    # stats
    p = subparsers.add_parser("stats")
    add_common(p); add_region(p)
    p.add_argument("--date", required=True, help="Date YYYY-MM-DD")
    p.set_defaults(func=cmd_stats)

    # sub-regions
    p = subparsers.add_parser("sub-regions")
    add_common(p); add_region(p)
    p.add_argument("--type", default="subnational1", help="subnational1 or subnational2")
    p.set_defaults(func=cmd_sub_regions)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
