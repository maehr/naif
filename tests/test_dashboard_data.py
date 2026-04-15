"""Validate dashboard CSV data against Pydantic schemas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from pydantic import BaseModel, field_validator

DATA_DIR = Path(__file__).resolve().parent.parent / "dashboards" / "_data"

VALID_TYPES = {"University", "Univ. Inst.", "UAS", "UAS Inst.", "UTE"}

# ---------------------------------------------------------------------------
# HEI schema
# ---------------------------------------------------------------------------

HEI_REQUIRED_COLUMNS = [
    "name",
    "short_name",
    "type",
    "town",
    "lat",
    "lon",
    "ror_id",
    "wikidata_id",
    "coara_signatory",
    "dora_signatory",
    "coara_member",
    "openalex_ids",
    "openorgs_ids",
]


class HEIRecord(BaseModel):
    """Schema for a single row in hei.csv."""

    name: str
    short_name: str
    type: str
    town: str
    lat: float | None = None
    lon: float | None = None

    @field_validator("name", "short_name", "type", "town")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("type")
    @classmethod
    def must_be_valid_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"{v!r} is not a valid institution type")
        return v

    @field_validator("lat")
    @classmethod
    def lat_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (45.0 <= v <= 48.0):
            raise ValueError(f"latitude {v} is outside Switzerland bounds")
        return v

    @field_validator("lon")
    @classmethod
    def lon_in_range(cls, v: float | None) -> float | None:
        if v is not None and not (5.0 <= v <= 11.0):
            raise ValueError(f"longitude {v} is outside Switzerland bounds")
        return v


# ---------------------------------------------------------------------------
# TOBI schema
# ---------------------------------------------------------------------------

TOBI_REQUIRED_COLUMNS = [
    "name",
    "short_name",
    "type",
    "town",
    "tobi_findable_dim",
    "tobi_findable_scopus",
    "tobi_findable_wos",
    "tobi_findable_openaire",
    "tobi_findable_openalex",
]


class TOBIRecord(BaseModel):
    """Schema for a single row in tobi.csv."""

    name: str
    short_name: str
    type: str
    town: str

    @field_validator("name", "short_name", "type", "town")
    @classmethod
    def must_be_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("type")
    @classmethod
    def must_be_valid_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"{v!r} is not a valid institution type")
        return v


# ---------------------------------------------------------------------------
# Tests – hei.csv
# ---------------------------------------------------------------------------


class TestHEIData:
    """Validate dashboards/_data/hei.csv."""

    @pytest.fixture(scope="class")
    def hei_df(self) -> pd.DataFrame:
        path = DATA_DIR / "hei.csv"
        assert path.exists(), f"hei.csv not found at {path}"
        return pd.read_csv(path)

    def test_has_required_columns(self, hei_df: pd.DataFrame) -> None:
        missing = set(HEI_REQUIRED_COLUMNS) - set(hei_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_not_empty(self, hei_df: pd.DataFrame) -> None:
        assert len(hei_df) > 0, "hei.csv must contain at least one row"

    def test_no_duplicate_names(self, hei_df: pd.DataFrame) -> None:
        duplicates = hei_df["name"][hei_df["name"].duplicated()].tolist()
        assert not duplicates, f"Duplicate institution names: {duplicates}"

    def test_valid_types(self, hei_df: pd.DataFrame) -> None:
        invalid = set(hei_df["type"].dropna().unique()) - VALID_TYPES
        assert not invalid, f"Invalid types: {invalid}"

    def test_each_row_validates(self, hei_df: pd.DataFrame) -> None:
        errors: list[str] = []
        for idx, row in hei_df.iterrows():
            try:
                HEIRecord(
                    name=str(row["name"]),
                    short_name=str(row["short_name"]),
                    type=str(row["type"]),
                    town=str(row["town"]),
                    lat=row["lat"] if pd.notna(row["lat"]) else None,
                    lon=row["lon"] if pd.notna(row["lon"]) else None,
                )
            except Exception as exc:
                errors.append(f"Row {idx} ({row.get('name', '?')}): {exc}")
        assert not errors, "\n".join(errors)

    def test_signatory_values(self, hei_df: pd.DataFrame) -> None:
        allowed = {"Yes", "No"}
        for col in ("dora_signatory", "coara_signatory", "coara_member"):
            values = set(hei_df[col].dropna().unique())
            invalid = values - allowed
            assert not invalid, f"{col} has invalid values: {invalid}"


# ---------------------------------------------------------------------------
# Tests – tobi.csv
# ---------------------------------------------------------------------------


class TestTOBIData:
    """Validate dashboards/_data/tobi.csv."""

    @pytest.fixture(scope="class")
    def tobi_df(self) -> pd.DataFrame:
        path = DATA_DIR / "tobi.csv"
        assert path.exists(), f"tobi.csv not found at {path}"
        return pd.read_csv(path)

    def test_has_required_columns(self, tobi_df: pd.DataFrame) -> None:
        missing = set(TOBI_REQUIRED_COLUMNS) - set(tobi_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_not_empty(self, tobi_df: pd.DataFrame) -> None:
        assert len(tobi_df) > 0, "tobi.csv must contain at least one row"

    def test_no_duplicate_names(self, tobi_df: pd.DataFrame) -> None:
        duplicates = tobi_df["name"][tobi_df["name"].duplicated()].tolist()
        assert not duplicates, f"Duplicate institution names: {duplicates}"

    def test_valid_types(self, tobi_df: pd.DataFrame) -> None:
        invalid = set(tobi_df["type"].dropna().unique()) - VALID_TYPES
        assert not invalid, f"Invalid types: {invalid}"

    def test_each_row_validates(self, tobi_df: pd.DataFrame) -> None:
        errors: list[str] = []
        for idx, row in tobi_df.iterrows():
            try:
                TOBIRecord(
                    name=str(row["name"]),
                    short_name=str(row["short_name"]),
                    type=str(row["type"]),
                    town=str(row["town"]),
                )
            except Exception as exc:
                errors.append(f"Row {idx} ({row.get('name', '?')}): {exc}")
        assert not errors, "\n".join(errors)

    def test_findability_values(self, tobi_df: pd.DataFrame) -> None:
        allowed = {"Yes", "No"}
        findability_cols = [
            c for c in tobi_df.columns if c.startswith("tobi_findable_")
        ]
        for col in findability_cols:
            values = set(tobi_df[col].dropna().unique())
            invalid = values - allowed
            assert not invalid, f"{col} has invalid values: {invalid}"

    def test_output_columns_numeric(self, tobi_df: pd.DataFrame) -> None:
        output_cols = [
            c for c in tobi_df.columns if c.startswith("tobi_total_outputs_")
        ]
        for col in output_cols:
            non_null = tobi_df[col].dropna()
            numeric = pd.to_numeric(non_null, errors="coerce")
            bad_count = numeric.isna().sum()
            assert bad_count == 0, f"{col} has {bad_count} non-numeric values"
