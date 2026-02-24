"""Tests for ebird_api.py."""

import argparse
import json
import os
import sys
import tempfile
import time
from unittest import mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ebird_api


# ---------------------------------------------------------------------------
# parse_date
# ---------------------------------------------------------------------------

class TestParseDate:
    def test_valid_date(self):
        assert ebird_api.parse_date("2025-01-15") == ("2025", "1", "15")

    def test_valid_date_leading_zeros(self):
        assert ebird_api.parse_date("2025-03-05") == ("2025", "3", "5")

    def test_missing_parts(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-01")

    def test_too_many_parts(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-01-15-extra")

    def test_non_numeric(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-ab-01")

    def test_invalid_month_zero(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-00-15")

    def test_invalid_month_13(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-13-15")

    def test_invalid_day_zero(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-01-00")

    def test_invalid_day_32(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("2025-01-32")

    def test_empty_string(self):
        with pytest.raises(SystemExit):
            ebird_api.parse_date("")


# ---------------------------------------------------------------------------
# print_json
# ---------------------------------------------------------------------------

class TestPrintJson:
    def test_basic_output(self, capsys):
        ebird_api.print_json({"a": 1})
        out = capsys.readouterr().out
        assert json.loads(out) == {"a": 1}

    def test_unicode(self, capsys):
        ebird_api.print_json({"name": "黑面琵鷺"})
        out = capsys.readouterr().out
        assert "黑面琵鷺" in out


# ---------------------------------------------------------------------------
# api_get — parameter assembly
# ---------------------------------------------------------------------------

class TestApiGet:
    def test_url_construction_no_params(self):
        with mock.patch("ebird_api.urlopen") as mock_urlopen:
            mock_resp = mock.MagicMock()
            mock_resp.read.return_value = b"[]"
            mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = mock.MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            ebird_api.api_get("/data/obs/TW/recent", "TESTKEY")

            call_args = mock_urlopen.call_args
            req = call_args[0][0]
            assert req.full_url == "https://api.ebird.org/v2/data/obs/TW/recent"
            assert req.get_header("X-ebirdapitoken") == "TESTKEY"

    def test_url_construction_with_params(self):
        with mock.patch("ebird_api.urlopen") as mock_urlopen:
            mock_resp = mock.MagicMock()
            mock_resp.read.return_value = b"[]"
            mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = mock.MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            ebird_api.api_get("/data/obs/TW/recent", "KEY", {"back": 7, "locale": "zh"})

            req = mock_urlopen.call_args[0][0]
            assert "back=7" in req.full_url
            assert "locale=zh" in req.full_url

    def test_none_params_filtered(self):
        with mock.patch("ebird_api.urlopen") as mock_urlopen:
            mock_resp = mock.MagicMock()
            mock_resp.read.return_value = b"[]"
            mock_resp.__enter__ = mock.MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = mock.MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            ebird_api.api_get("/test", "KEY", {"back": None, "locale": "en"})

            req = mock_urlopen.call_args[0][0]
            assert "back" not in req.full_url
            assert "locale=en" in req.full_url


# ---------------------------------------------------------------------------
# Taxonomy filtering logic
# ---------------------------------------------------------------------------

SAMPLE_TAXONOMY = [
    {
        "speciesCode": "barswa1",
        "comName": "Barn Swallow",
        "sciName": "Hirundo rustica",
        "familyComName": "Swallows",
        "order": "Passeriformes",
    },
    {
        "speciesCode": "bkfspo1",
        "comName": "Black-faced Spoonbill",
        "sciName": "Platalea minor",
        "familyComName": "Ibises and Spoonbills",
        "order": "Pelecaniformes",
    },
    {
        "speciesCode": "houspa",
        "comName": "House Sparrow",
        "sciName": "Passer domesticus",
        "familyComName": "Old World Sparrows",
        "order": "Passeriformes",
    },
]


class TestTaxonomyFiltering:
    def _run_taxonomy(self, search_term, taxonomy_data=None):
        """Helper to run cmd_taxonomy with mocked API and capture output."""
        data = taxonomy_data or SAMPLE_TAXONOMY
        args = argparse.Namespace(
            key="TESTKEY",
            locale="en",
            species=search_term,
            no_cache=True,
        )
        with mock.patch("ebird_api.api_get", return_value=data):
            with mock.patch("ebird_api._save_taxonomy_cache"):
                import io
                from contextlib import redirect_stdout
                f = io.StringIO()
                with redirect_stdout(f):
                    ebird_api.cmd_taxonomy(args)
                return json.loads(f.getvalue())

    def test_search_by_common_name(self):
        results = self._run_taxonomy("Swallow")
        assert len(results) == 1
        assert results[0]["speciesCode"] == "barswa1"

    def test_search_by_scientific_name(self):
        results = self._run_taxonomy("Hirundo")
        assert len(results) == 1
        assert results[0]["sciName"] == "Hirundo rustica"

    def test_search_by_species_code(self):
        results = self._run_taxonomy("bkfspo1")
        assert len(results) == 1
        assert results[0]["comName"] == "Black-faced Spoonbill"

    def test_search_case_insensitive(self):
        results = self._run_taxonomy("barn swallow")
        assert len(results) == 1

    def test_search_partial_match(self):
        results = self._run_taxonomy("Sparrow")
        assert len(results) == 1
        assert results[0]["speciesCode"] == "houspa"

    def test_search_no_match(self):
        results = self._run_taxonomy("Penguin")
        assert len(results) == 0

    def test_results_limited_to_20(self):
        # Create 25 fake species all matching "bird"
        many = [
            {
                "speciesCode": f"bird{i}",
                "comName": f"Bird {i}",
                "sciName": f"Avis {i}",
                "familyComName": "Birds",
                "order": "Order",
            }
            for i in range(25)
        ]
        results = self._run_taxonomy("bird", many)
        assert len(results) == 20


# ---------------------------------------------------------------------------
# Taxonomy cache
# ---------------------------------------------------------------------------

class TestTaxonomyCache:
    def test_save_and_load(self, tmp_path):
        with mock.patch("ebird_api.CACHE_DIR", str(tmp_path)):
            ebird_api._save_taxonomy_cache("en", SAMPLE_TAXONOMY)
            loaded = ebird_api._load_taxonomy_cache("en")
            assert loaded == SAMPLE_TAXONOMY

    def test_expired_cache_returns_none(self, tmp_path):
        with mock.patch("ebird_api.CACHE_DIR", str(tmp_path)):
            ebird_api._save_taxonomy_cache("en", SAMPLE_TAXONOMY)
            # Set mtime to 31 days ago
            path = ebird_api._get_cache_path("en")
            old_time = time.time() - 31 * 24 * 3600
            os.utime(path, (old_time, old_time))
            assert ebird_api._load_taxonomy_cache("en") is None

    def test_missing_cache_returns_none(self, tmp_path):
        with mock.patch("ebird_api.CACHE_DIR", str(tmp_path)):
            assert ebird_api._load_taxonomy_cache("en") is None


# ---------------------------------------------------------------------------
# Command param assembly — spot check a few commands
# ---------------------------------------------------------------------------

class TestCommandParams:
    """Verify that commands pass the right params to api_get."""

    def test_cmd_recent_params(self):
        args = argparse.Namespace(
            key="K", locale="zh", region="TW", back=7, max=10,
            hotspot=True, category="species",
        )
        with mock.patch("ebird_api.api_get", return_value=[]) as m:
            with mock.patch("ebird_api.print_json"):
                ebird_api.cmd_recent(args)
        path, key, params = m.call_args[0]
        assert path == "/data/obs/TW/recent"
        assert key == "K"
        assert params["back"] == 7
        assert params["locale"] == "zh"
        assert params["hotspot"] == "true"
        assert params["cat"] == "species"

    def test_cmd_historic_params(self):
        args = argparse.Namespace(
            key="K", locale="en", region="US-NY", max=50,
            date="2025-03-15", category=None,
        )
        with mock.patch("ebird_api.api_get", return_value=[]) as m:
            with mock.patch("ebird_api.print_json"):
                ebird_api.cmd_historic(args)
        path, key, params = m.call_args[0]
        assert path == "/data/obs/US-NY/historic/2025/3/15"
        assert params["locale"] == "en"

    def test_cmd_top100_params(self):
        args = argparse.Namespace(
            key="K", locale="en", region="TW", max=100,
            date="2025-01-01",
        )
        with mock.patch("ebird_api.api_get", return_value=[]) as m:
            with mock.patch("ebird_api.print_json"):
                ebird_api.cmd_top100(args)
        path, key, params = m.call_args[0]
        assert path == "/product/top100/TW/2025/1/1"

    def test_cmd_stats_params(self):
        args = argparse.Namespace(
            key="K", locale="en", region="TW",
            date="2025-06-15",
        )
        with mock.patch("ebird_api.api_get", return_value=[]) as m:
            with mock.patch("ebird_api.print_json"):
                ebird_api.cmd_stats(args)
        path, key = m.call_args[0][:2]
        assert path == "/product/stats/TW/2025/6/15"

    def test_cmd_sub_regions_params(self):
        args = argparse.Namespace(
            key="K", locale="en", region="TW", type="subnational1",
        )
        with mock.patch("ebird_api.api_get", return_value=[]) as m:
            with mock.patch("ebird_api.print_json"):
                ebird_api.cmd_sub_regions(args)
        path, key = m.call_args[0][:2]
        assert path == "/ref/region/list/subnational1/TW"

    def test_cmd_nearby_notable_params(self):
        args = argparse.Namespace(
            key="K", locale="en", lat=25.03, lng=121.56,
            dist=50, back=14, max=50,
        )
        with mock.patch("ebird_api.api_get", return_value=[]) as m:
            with mock.patch("ebird_api.print_json"):
                ebird_api.cmd_nearby_notable(args)
        path, key, params = m.call_args[0]
        assert path == "/data/obs/geo/recent/notable"
        assert params["lat"] == 25.03
        assert params["dist"] == 50
        assert params["detail"] == "full"


# ---------------------------------------------------------------------------
# API key resolution: --key flag vs EBIRD_API_KEY env var
# ---------------------------------------------------------------------------

class TestApiKeyResolution:
    """Verify --key flag > env var > error."""

    def _run_main(self, cli_args, env=None):
        """Run main() with given CLI args and optional env override."""
        with mock.patch("sys.argv", ["ebird_api.py"] + cli_args):
            with mock.patch.dict(os.environ, env or {}, clear=False):
                with mock.patch("ebird_api.api_get", return_value=[]):
                    with mock.patch("ebird_api.print_json"):
                        ebird_api.main()

    def test_key_from_flag(self):
        """--key flag should be used when provided."""
        with mock.patch("sys.argv", ["ebird_api.py", "stats", "--key", "FLAG_KEY", "--region", "TW", "--date", "2025-01-01"]):
            with mock.patch("ebird_api.api_get", return_value=[]) as m:
                with mock.patch("ebird_api.print_json"):
                    ebird_api.main()
        assert m.call_args[0][1] == "FLAG_KEY"

    def test_key_from_env(self):
        """EBIRD_API_KEY env var should be used when --key is not provided."""
        with mock.patch("sys.argv", ["ebird_api.py", "stats", "--region", "TW", "--date", "2025-01-01"]):
            with mock.patch.dict(os.environ, {"EBIRD_API_KEY": "ENV_KEY"}):
                with mock.patch("ebird_api.api_get", return_value=[]) as m:
                    with mock.patch("ebird_api.print_json"):
                        ebird_api.main()
        assert m.call_args[0][1] == "ENV_KEY"

    def test_flag_overrides_env(self):
        """--key flag should take priority over env var."""
        with mock.patch("sys.argv", ["ebird_api.py", "stats", "--key", "FLAG_KEY", "--region", "TW", "--date", "2025-01-01"]):
            with mock.patch.dict(os.environ, {"EBIRD_API_KEY": "ENV_KEY"}):
                with mock.patch("ebird_api.api_get", return_value=[]) as m:
                    with mock.patch("ebird_api.print_json"):
                        ebird_api.main()
        assert m.call_args[0][1] == "FLAG_KEY"

    def test_no_key_exits_with_error(self):
        """Missing both --key and env var should exit with error."""
        with mock.patch("sys.argv", ["ebird_api.py", "stats", "--region", "TW", "--date", "2025-01-01"]):
            with mock.patch.dict(os.environ, {}, clear=False):
                # Remove EBIRD_API_KEY if it happens to be set
                env = os.environ.copy()
                env.pop("EBIRD_API_KEY", None)
                with mock.patch.dict(os.environ, env, clear=True):
                    with pytest.raises(SystemExit):
                        ebird_api.main()
