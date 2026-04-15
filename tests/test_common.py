"""Tests for dashboards/_common.py shared utilities."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

COMMON_PATH = Path(__file__).resolve().parent.parent / "dashboards" / "_common.py"
COMMON_SPEC = importlib.util.spec_from_file_location("dashboards_common", COMMON_PATH)
assert COMMON_SPEC is not None and COMMON_SPEC.loader is not None
common = importlib.util.module_from_spec(COMMON_SPEC)
COMMON_SPEC.loader.exec_module(common)

DATA_DIR = common.DATA_DIR
TYPE_LABELS = common.TYPE_LABELS
TYPE_ORDER = common.TYPE_ORDER
format_identifier = common.format_identifier
format_plain_text = common.format_plain_text
format_type_label = common.format_type_label
make_link = common.make_link
normalise_yes_no = common.normalise_yes_no
pct = common.pct
render_table = common.render_table
type_order_key = common.type_order_key
write_dataframe_xlsx = common.write_dataframe_xlsx


# ---------------------------------------------------------------------------
# DATA_DIR
# ---------------------------------------------------------------------------


def test_data_dir_exists() -> None:
    assert DATA_DIR.is_dir(), f"Expected data directory at {DATA_DIR}"


# ---------------------------------------------------------------------------
# normalise_yes_no
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Yes", "Yes"),
        ("yes", "Yes"),
        ("TRUE", "Yes"),
        ("1", "Yes"),
        ("No", "No"),
        ("no", "No"),
        ("false", "No"),
        ("0", "No"),
        ("", "Unknown"),
        ("maybe", "Unknown"),
        (None, "Unknown"),
        (float("nan"), "Unknown"),
    ],
)
def test_normalise_yes_no(raw: object, expected: str) -> None:
    assert normalise_yes_no(raw) == expected


# ---------------------------------------------------------------------------
# format_identifier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, ""),
        (float("nan"), ""),
        ("", ""),
        ("  ", ""),
        ("42.0", "42"),
        ("hello", "hello"),
        ("3.14", "3.14"),
        ("Q12345", "Q12345"),
    ],
)
def test_format_identifier(raw: object, expected: str) -> None:
    assert format_identifier(raw) == expected


# ---------------------------------------------------------------------------
# format_plain_text
# ---------------------------------------------------------------------------


def test_format_plain_text_with_value() -> None:
    assert format_plain_text("Zurich") == "Zurich"


def test_format_plain_text_empty() -> None:
    assert format_plain_text(None) == "-"


# ---------------------------------------------------------------------------
# format_type_label
# ---------------------------------------------------------------------------


def test_format_type_label_default() -> None:
    assert format_type_label("UAS") == TYPE_LABELS["UAS"]


def test_format_type_label_custom() -> None:
    custom = {"UAS": "Custom label"}
    assert format_type_label("UAS", labels=custom) == "Custom label"


def test_format_type_label_unknown() -> None:
    assert format_type_label(None) == "Unknown"


# ---------------------------------------------------------------------------
# type_order_key
# ---------------------------------------------------------------------------


def test_type_order_key_known() -> None:
    assert type_order_key("UAS") == TYPE_ORDER.index("UAS")


def test_type_order_key_unknown() -> None:
    assert type_order_key("Unknown") == len(TYPE_ORDER)


def test_type_order_key_custom() -> None:
    custom = ["A", "B"]
    assert type_order_key("B", order=custom) == 1
    assert type_order_key("C", order=custom) == 2


# ---------------------------------------------------------------------------
# pct
# ---------------------------------------------------------------------------


def test_pct_normal() -> None:
    assert pct(1, 4) == "25.0%"


def test_pct_zero_denominator() -> None:
    assert pct(5, 0) == "0.0%"


# ---------------------------------------------------------------------------
# make_link
# ---------------------------------------------------------------------------


def test_make_link_escapes() -> None:
    result = make_link("https://example.com", "A & B")
    assert "A &amp; B" in result
    assert 'target="_blank"' in result
    assert 'rel="noopener noreferrer"' in result


# ---------------------------------------------------------------------------
# render_table
# ---------------------------------------------------------------------------


def test_render_table_html() -> None:
    df = pd.DataFrame({"A": [1], "B": [2]})
    html_str = render_table(df)
    assert "<table" in html_str
    assert "table-sm" in html_str


# ---------------------------------------------------------------------------
# write_dataframe_xlsx
# ---------------------------------------------------------------------------


def test_write_dataframe_xlsx(tmp_path: Path) -> None:
    df = pd.DataFrame({"name": ["A", "B"], "value": ["1", "2"]})
    out = tmp_path / "test.xlsx"
    write_dataframe_xlsx(df, out, sheet_name="Sheet")
    assert out.exists()
    assert out.stat().st_size > 0
