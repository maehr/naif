"""Tests for dashboards/_matomo_usage.py."""

from __future__ import annotations

import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parent.parent / "dashboards" / "_matomo_usage.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "dashboards_matomo_usage", MODULE_PATH
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
matomo_usage = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = matomo_usage
MODULE_SPEC.loader.exec_module(matomo_usage)

MatomoConfig = matomo_usage.MatomoConfig
build_snapshot = matomo_usage.build_snapshot
format_duration = matomo_usage.format_duration
format_month_label = matomo_usage.format_month_label
load_matomo_config = matomo_usage.load_matomo_config
make_placeholder_snapshot = matomo_usage.make_placeholder_snapshot
normalise_page_path = matomo_usage.normalise_page_path
_coerce_int = matomo_usage._coerce_int

DEFAULT_MATOMO_BASE_URL = matomo_usage.DEFAULT_MATOMO_BASE_URL
DEFAULT_MATOMO_SITE_ID = matomo_usage.DEFAULT_MATOMO_SITE_ID
DEFAULT_PUBLIC_SITE_URL = matomo_usage.DEFAULT_PUBLIC_SITE_URL


def test_load_matomo_config_returns_none_without_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for key in (
        "MATOMO_TOKEN_AUTH",
        "MATOMO_BASE_URL",
        "MATOMO_SITE_ID",
        "MATOMO_PUBLIC_SITE_URL",
        "MATOMO_REPORT_START_DATE",
    ):
        monkeypatch.delenv(key, raising=False)

    assert load_matomo_config() is None


def test_load_matomo_config_uses_defaults_and_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MATOMO_TOKEN_AUTH", "secret-token")
    monkeypatch.setenv("MATOMO_REPORT_START_DATE", "2025-01-01")

    config = load_matomo_config()

    assert config is not None
    assert config.token_auth == "secret-token"
    assert config.base_url == DEFAULT_MATOMO_BASE_URL
    assert config.site_id == DEFAULT_MATOMO_SITE_ID
    assert config.public_site_url == DEFAULT_PUBLIC_SITE_URL
    assert config.report_start_date == "2025-01-01"


def test_format_duration_handles_hours_minutes_and_seconds() -> None:
    assert format_duration(3723) == "1h 2m 3s"


def test_format_month_label() -> None:
    assert format_month_label("2025-07") == "Jul 2025"


def test_coerce_int_returns_zero_for_parse_failures() -> None:
    assert _coerce_int(None) == 0
    assert _coerce_int("not-a-number") == 0


def test_make_placeholder_snapshot_marks_missing_config() -> None:
    snapshot = make_placeholder_snapshot("No credentials")

    assert snapshot.status == "missing_config"
    assert snapshot.message == "No credentials"
    assert snapshot.totals is None


def test_normalise_page_path_strips_site_prefix() -> None:
    path, href = normalise_page_path(
        "https://eth-library.github.io/naif/posts/2025-07-01-project-start/index.html",
        None,
        DEFAULT_PUBLIC_SITE_URL,
    )

    assert path == "/posts/2025-07-01-project-start/"
    assert href == "https://eth-library.github.io/naif/posts/2025-07-01-project-start/"


def test_normalise_page_path_preserves_external_url() -> None:
    path, href = normalise_page_path(
        "https://example.org/path",
        "/path",
        DEFAULT_PUBLIC_SITE_URL,
    )

    assert path == "/path"
    assert href == "https://example.org/path"


def test_build_snapshot_extracts_lifetime_history_and_top_pages() -> None:
    config = MatomoConfig(token_auth="secret-token")
    totals_payload = {
        "nb_visits": 1200,
        "nb_pageviews": 3400,
        "nb_downloads": 15,
        "nb_outlinks": 78,
        "avg_time_on_site": 142,
        "bounce_rate": "38%",
        "Referrers_visitorsFromSearchEngines": 700,
        "Referrers_visitorsFromSearchEngines_percent": "58%",
        "Referrers_visitorsFromDirectEntry": 300,
        "Referrers_visitorsFromDirectEntry_percent": "25%",
    }
    history_payload = {
        "2025-07": {
            "nb_visits": 300,
            "nb_pageviews": 900,
            "nb_downloads": 2,
            "nb_outlinks": 10,
            "avg_time_on_site": 110,
            "bounce_rate": "42%",
        },
        "2025-08": {
            "nb_visits": 400,
            "nb_pageviews": 1200,
            "nb_downloads": 5,
            "nb_outlinks": 22,
            "avg_time_on_site": 150,
            "bounce_rate": "37%",
        },
    }
    top_pages_payload = [
        {
            "url": "https://eth-library.github.io/naif/posts/2025-07-01-project-start/index.html",
            "label": "/posts/2025-07-01-project-start/",
            "nb_hits": 125,
            "nb_visits": 100,
            "avg_time_on_page": 32,
            "bounce_rate": "40%",
        }
    ]

    snapshot = build_snapshot(
        config,
        totals_payload,
        history_payload,
        top_pages_payload,
        generated_at=datetime(2026, 4, 22, 8, 30, tzinfo=UTC),
        report_end_date="2026-04-22",
    )

    assert snapshot.status == "ok"
    assert snapshot.report_start_date == "2025-07-01"
    assert snapshot.report_end_date == "2026-04-22"
    assert snapshot.totals is not None
    assert snapshot.totals.pageviews == 3400
    assert snapshot.traffic_sources[0].label == "Search engines"
    assert snapshot.traffic_sources[0].visits == 700
    assert [item.month for item in snapshot.history] == ["2025-07", "2025-08"]
    assert snapshot.top_pages[0].path == "/posts/2025-07-01-project-start/"
    assert (
        snapshot.top_pages[0].href
        == "https://eth-library.github.io/naif/posts/2025-07-01-project-start/"
    )
