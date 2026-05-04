"""Tests for the HEI cross-check helper modules."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

cross_check_hei_common = importlib.import_module("cross_check_hei_common")
cross_check_hei_report = importlib.import_module("cross_check_hei_report")

Issue = cross_check_hei_common.Issue
extract_ror_id = cross_check_hei_common.extract_ror_id
normalise_isni = cross_check_hei_common.normalise_isni
format_report = cross_check_hei_report.format_report


def test_extract_ror_id_strips_url_scaffolding() -> None:
    assert extract_ror_id("https://ror.org/02s376052/") == "02s376052"


def test_normalise_isni_formats_compact_identifier() -> None:
    assert normalise_isni("000000012146438X") == "0000 0001 2146 438X"


def test_format_report_includes_summary_and_totals() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "short_name": "ETHZ",
                "ror_id": "https://ror.org/05a28rw58",
                "wikidata_id": "Q11942",
                "openalex_ids": "I123",
                "openorgs_ids": "",
                "grid_id": "grid.1234.5",
                "isni_id": "0000 0001 2146 438X",
                "crossref_funder_id": "501100001711",
                "geonames_id": "2657896",
            }
        ]
    )
    issues = [
        Issue(
            institution="ETH Zurich",
            short_name="ETHZ",
            source="Local",
            severity="warning",
            field_name="Coordinates",
            message="Missing latitude/longitude",
        )
    ]

    report = format_report(issues, dataframe)

    assert "## Summary" in report
    assert "- **Warnings (missing critical data):** 1" in report
    assert "| ETHZ | Y | Y | Y | - | Y | Y | Y | Y |" in report
    assert "| ROR | 1/1 | 100.0% |" in report
