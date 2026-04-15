#!/usr/bin/env python3
"""Cross-check swiss-hei-open-data against ROR, OpenAlex, and Wikidata.

Reads dashboards/_data/hei.csv and queries external registry APIs to verify
identifiers, detect discrepancies, and report missing data.

Usage::

    uv run python scripts/cross_check_hei.py
    uv run python scripts/cross_check_hei.py --output report.md
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_PATH: Path = (
    Path(__file__).resolve().parent.parent / "dashboards" / "_data" / "hei.csv"
)

ROR_API_BASE: str = "https://api.ror.org/v2/organizations"
OPENALEX_API_BASE: str = "https://api.openalex.org/institutions"
WIKIDATA_SPARQL_URL: str = "https://query.wikidata.org/sparql"

USER_AGENT: str = (
    "naif-cross-check/1.0 (https://github.com/eth-library/naif; mailto:info@naif.ch)"
)

# Concurrency limits for external APIs.
ROR_CONCURRENCY: int = 5
OPENALEX_CONCURRENCY: int = 10
REQUEST_TIMEOUT: float = 30.0

# Wikidata property IDs used for cross-referencing.
WD_PROP_ROR: str = "P6782"
WD_PROP_ISNI: str = "P213"
WD_PROP_GRID: str = "P2427"
WD_PROP_OPENALEX: str = "P10283"
WD_PROP_CROSSREF: str = "P3153"
WD_PROP_GEONAMES: str = "P1566"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Issue:
    """A single finding from the cross-check."""

    institution: str
    short_name: str
    source: str  # ROR | OpenAlex | Wikidata | Local
    severity: str  # error | warning | info
    field_name: str
    message: str


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def _clean_float(value: object) -> str:
    """Strip trailing .0 from float-encoded strings and NaN."""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        try:
            return str(int(float(text)))
        except ValueError:
            pass
    return text


def extract_ror_id(ror_url: str) -> str:
    """Extract the short ROR identifier from a full URL.

    ``https://ror.org/02s376052`` → ``02s376052``
    """
    return ror_url.strip().rstrip("/").rsplit("/", 1)[-1]


def normalise_isni(value: str) -> str:
    """Normalise ISNI to the canonical 16-character space-separated form.

    The last character may be ``X`` (check digit), so we preserve it.
    """
    chars = re.sub(r"[^0-9Xx]", "", value).upper()
    if len(chars) == 16:
        return f"{chars[0:4]} {chars[4:8]} {chars[8:12]} {chars[12:16]}"
    return value.strip()


def normalise_grid(value: str) -> str:
    """Normalise GRID ID (lowercase, strip whitespace)."""
    return value.strip().lower()


def normalise_crossref(value: str) -> str:
    """Normalise Crossref funder ID to plain digits."""
    return re.sub(r"\D", "", _clean_float(value))


def normalise_geonames(value: str) -> str:
    """Normalise GeoNames ID to plain digits."""
    return re.sub(r"\D", "", _clean_float(value))


def csv_set(value: object, sep: str = "|") -> set[str]:
    """Split a pipe-separated cell into a set of stripped, non-empty strings."""
    raw = _clean_float(value)
    if not raw:
        return set()
    return {part.strip() for part in raw.split(sep) if part.strip()}


def _name(row: pd.Series) -> str:
    return str(row["name"])


def _short(row: pd.Series) -> str:
    return str(row["short_name"])


# ---------------------------------------------------------------------------
# API helpers – ROR v2
# ---------------------------------------------------------------------------


async def fetch_ror_record(
    client: httpx.AsyncClient,
    ror_url: str,
    sem: asyncio.Semaphore,
) -> dict | None:
    """Fetch a single ROR v2 record.  Returns parsed JSON or ``None``."""
    ror_id = extract_ror_id(ror_url)
    url = f"{ROR_API_BASE}/{ror_id}"
    async with sem:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                await asyncio.sleep(5)
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp.json()
            return None
        except httpx.HTTPError:
            return None


def _ror_external(data: dict, ext_type: str) -> set[str]:
    """Extract external IDs of *ext_type* from a ROR v2 record."""
    result: set[str] = set()
    for entry in data.get("external_ids", []):
        if entry.get("type", "").lower() == ext_type.lower():
            for val in entry.get("all", []):
                result.add(str(val).strip())
    return result


def _ror_name_en(data: dict) -> str:
    """Best-effort English display name from a ROR record."""
    for name_obj in data.get("names", []):
        if "ror_display" in name_obj.get("types", []):
            return name_obj.get("value", "")
    for name_obj in data.get("names", []):
        if name_obj.get("lang") == "en":
            return name_obj.get("value", "")
    names = data.get("names", [])
    return names[0].get("value", "") if names else ""


# ---------------------------------------------------------------------------
# API helpers – OpenAlex
# ---------------------------------------------------------------------------


async def fetch_openalex_record(
    client: httpx.AsyncClient,
    oa_id: str,
    sem: asyncio.Semaphore,
) -> dict | None:
    """Fetch a single OpenAlex institution record."""
    url = f"{OPENALEX_API_BASE}/{oa_id}"
    params = {
        "select": "id,display_name,ror,ids,country_code,type,lineage",
    }
    async with sem:
        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                await asyncio.sleep(5)
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    return resp.json()
            return None
        except httpx.HTTPError:
            return None


def _oa_primary_id(row: pd.Series) -> str | None:
    """Return the primary OpenAlex ID from the openalex_url column."""
    url = _clean_float(row.get("openalex_url", ""))
    if url:
        # https://openalex.org/institutions/I5124864 → I5124864
        return url.rstrip("/").rsplit("/", 1)[-1]
    # Fallback: first ID in the pipe-separated list.
    ids = csv_set(row.get("openalex_ids", ""))
    return sorted(ids)[0] if ids else None


# ---------------------------------------------------------------------------
# API helpers – Wikidata SPARQL
# ---------------------------------------------------------------------------


_SPARQL_TEMPLATE: str = """
SELECT
  ?item ?itemLabel
  (GROUP_CONCAT(DISTINCT ?ror;      SEPARATOR="|") AS ?rors)
  (GROUP_CONCAT(DISTINCT ?isni;     SEPARATOR="|") AS ?isnis)
  (GROUP_CONCAT(DISTINCT ?grid;     SEPARATOR="|") AS ?grids)
  (GROUP_CONCAT(DISTINCT ?openalex; SEPARATOR="|") AS ?openalexes)
  (GROUP_CONCAT(DISTINCT ?crossref; SEPARATOR="|") AS ?crossrefs)
  (GROUP_CONCAT(DISTINCT ?geonames; SEPARATOR="|") AS ?geonameses)
WHERE {{
  VALUES ?item {{ {qid_values} }}
  OPTIONAL {{ ?item wdt:{ror}      ?ror . }}
  OPTIONAL {{ ?item wdt:{isni}     ?isni . }}
  OPTIONAL {{ ?item wdt:{grid}     ?grid . }}
  OPTIONAL {{ ?item wdt:{openalex} ?openalex . }}
  OPTIONAL {{ ?item wdt:{crossref} ?crossref . }}
  OPTIONAL {{ ?item wdt:{geonames} ?geonames . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,de,fr,it" . }}
}}
GROUP BY ?item ?itemLabel
"""


@dataclass
class WikidataRecord:
    """Aggregated Wikidata data for one entity."""

    qid: str
    label: str = ""
    ror_ids: set[str] = field(default_factory=set)
    isni_ids: set[str] = field(default_factory=set)
    grid_ids: set[str] = field(default_factory=set)
    openalex_ids: set[str] = field(default_factory=set)
    crossref_ids: set[str] = field(default_factory=set)
    geonames_ids: set[str] = field(default_factory=set)


async def fetch_wikidata_batch(
    client: httpx.AsyncClient,
    qids: list[str],
) -> dict[str, WikidataRecord]:
    """Run a single SPARQL query to fetch properties for all *qids*."""
    if not qids:
        return {}

    qid_values = " ".join(f"wd:{qid}" for qid in qids)
    query = _SPARQL_TEMPLATE.format(
        qid_values=qid_values,
        ror=WD_PROP_ROR,
        isni=WD_PROP_ISNI,
        grid=WD_PROP_GRID,
        openalex=WD_PROP_OPENALEX,
        crossref=WD_PROP_CROSSREF,
        geonames=WD_PROP_GEONAMES,
    )

    headers = {"Accept": "application/sparql-results+json"}
    try:
        resp = await client.get(
            WIKIDATA_SPARQL_URL,
            params={"query": query},
            headers=headers,
            timeout=60.0,
        )
        if resp.status_code != 200:
            print(f"  Wikidata SPARQL returned {resp.status_code}", file=sys.stderr)
            return {}
        data = resp.json()
    except httpx.HTTPError as exc:
        print(f"  Wikidata SPARQL error: {exc}", file=sys.stderr)
        return {}

    records: dict[str, WikidataRecord] = {}
    for binding in data.get("results", {}).get("bindings", []):
        uri = binding.get("item", {}).get("value", "")
        qid = uri.rsplit("/", 1)[-1] if uri else ""
        if not qid:
            continue

        rec = records.setdefault(qid, WikidataRecord(qid=qid))
        rec.label = binding.get("itemLabel", {}).get("value", "")

        for val in _split_sparql(binding, "rors"):
            rec.ror_ids.add(val)
        for val in _split_sparql(binding, "isnis"):
            rec.isni_ids.add(val)
        for val in _split_sparql(binding, "grids"):
            rec.grid_ids.add(val)
        for val in _split_sparql(binding, "openalexes"):
            rec.openalex_ids.add(val)
        for val in _split_sparql(binding, "crossrefs"):
            rec.crossref_ids.add(val)
        for val in _split_sparql(binding, "geonameses"):
            rec.geonames_ids.add(val)

    return records


def _split_sparql(binding: dict, key: str) -> list[str]:
    raw = binding.get(key, {}).get("value", "")
    if not raw:
        return []
    return [v.strip() for v in raw.split("|") if v.strip()]


# ---------------------------------------------------------------------------
# Cross-check logic
# ---------------------------------------------------------------------------


def check_missing_data(row: pd.Series) -> list[Issue]:
    """Flag locally missing identifiers."""
    issues: list[Issue] = []
    name, short = _name(row), _short(row)

    checks: list[tuple[str, str, str]] = [
        ("ror_id", "ROR ID", "warning"),
        ("wikidata_id", "Wikidata ID", "warning"),
        ("openalex_ids", "OpenAlex ID(s)", "warning"),
        ("openorgs_ids", "OpenOrgs ID(s)", "info"),
        ("grid_id", "GRID ID", "info"),
        ("isni_id", "ISNI", "info"),
        ("crossref_funder_id", "Crossref funder ID", "info"),
        ("geonames_id", "GeoNames ID", "info"),
    ]

    for col, label, severity in checks:
        val = _clean_float(row.get(col, ""))
        if not val:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Local",
                    severity=severity,
                    field_name=label,
                    message=f"Missing {label}",
                )
            )

    # Missing coordinates
    if pd.isna(row.get("lat")) or pd.isna(row.get("lon")):
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Local",
                severity="warning",
                field_name="Coordinates",
                message="Missing latitude/longitude",
            )
        )

    return issues


def check_ror_record(row: pd.Series, ror_data: dict) -> list[Issue]:
    """Compare a ROR API response against the local CSV row."""
    issues: list[Issue] = []
    name, short = _name(row), _short(row)

    # Check ROR record status.
    status = ror_data.get("status", "active")
    if status != "active":
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="ROR",
                severity="error",
                field_name="Status",
                message=f"ROR record status is '{status}' (not active)",
            )
        )

    # Name comparison.
    ror_name = _ror_name_en(ror_data)
    if ror_name and ror_name.lower() != name.lower():
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="ROR",
                severity="info",
                field_name="Name",
                message=f"ROR display name differs: '{ror_name}'",
            )
        )

    # Country check.
    for loc in ror_data.get("locations", []):
        cc = loc.get("geonames_details", {}).get("country_code", "")
        if cc and cc != "CH":
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="ROR",
                    severity="error",
                    field_name="Country",
                    message=f"ROR country is '{cc}', expected 'CH'",
                )
            )

    # GRID cross-reference.
    ror_grids = {normalise_grid(g) for g in _ror_external(ror_data, "grid")}
    csv_grid = normalise_grid(_clean_float(row.get("grid_id", "")))
    if ror_grids and csv_grid:
        if csv_grid not in ror_grids:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="ROR",
                    severity="error",
                    field_name="GRID",
                    message=f"GRID mismatch – CSV: '{csv_grid}', ROR: {ror_grids}",
                )
            )
    elif ror_grids and not csv_grid:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="ROR",
                severity="info",
                field_name="GRID",
                message=f"ROR has GRID {ror_grids} but CSV is empty – enrichment opportunity",
            )
        )

    # ISNI cross-reference.
    ror_isnis = {normalise_isni(i) for i in _ror_external(ror_data, "isni")}
    csv_isni = normalise_isni(_clean_float(row.get("isni_id", "")))
    if ror_isnis and csv_isni:
        if csv_isni not in ror_isnis:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="ROR",
                    severity="error",
                    field_name="ISNI",
                    message=f"ISNI mismatch – CSV: '{csv_isni}', ROR: {ror_isnis}",
                )
            )
    elif ror_isnis and not csv_isni:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="ROR",
                severity="info",
                field_name="ISNI",
                message=f"ROR has ISNI {ror_isnis} but CSV is empty – enrichment opportunity",
            )
        )

    # Wikidata cross-reference.
    ror_wds = _ror_external(ror_data, "wikidata")
    csv_wd = _clean_float(row.get("wikidata_id", ""))
    if ror_wds and csv_wd:
        if csv_wd not in ror_wds:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="ROR",
                    severity="error",
                    field_name="Wikidata",
                    message=f"Wikidata mismatch – CSV: '{csv_wd}', ROR: {ror_wds}",
                )
            )
    elif ror_wds and not csv_wd:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="ROR",
                severity="info",
                field_name="Wikidata",
                message=(
                    f"ROR has Wikidata {ror_wds} but CSV is empty – enrichment opportunity"
                ),
            )
        )

    # Fundref (Crossref funder) cross-reference.
    ror_fundrefs = {normalise_crossref(f) for f in _ror_external(ror_data, "fundref")}
    csv_fundref = normalise_crossref(_clean_float(row.get("crossref_funder_id", "")))
    if ror_fundrefs and csv_fundref:
        if csv_fundref not in ror_fundrefs:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="ROR",
                    severity="error",
                    field_name="Crossref funder",
                    message=(
                        f"Crossref funder mismatch – "
                        f"CSV: '{csv_fundref}', ROR: {ror_fundrefs}"
                    ),
                )
            )
    elif ror_fundrefs and not csv_fundref:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="ROR",
                severity="info",
                field_name="Crossref funder",
                message=(
                    f"ROR has Crossref funder {ror_fundrefs} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    return issues


def check_openalex_record(row: pd.Series, oa_data: dict) -> list[Issue]:
    """Compare an OpenAlex API response against the local CSV row."""
    issues: list[Issue] = []
    name, short = _name(row), _short(row)

    # Check if primary ID was redirected (merged institution).
    returned_id = oa_data.get("id", "").rsplit("/", 1)[-1]
    primary_id = _oa_primary_id(row)
    if primary_id and returned_id and returned_id != primary_id:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="OpenAlex",
                severity="warning",
                field_name="ID redirect",
                message=(
                    f"Primary ID '{primary_id}' redirected to '{returned_id}' "
                    f"– institution may have been merged"
                ),
            )
        )

    # Name comparison.
    oa_name = oa_data.get("display_name", "")
    if oa_name and oa_name.lower() != name.lower():
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="OpenAlex",
                severity="info",
                field_name="Name",
                message=f"OpenAlex display name differs: '{oa_name}'",
            )
        )

    # ROR cross-reference.
    oa_ror = oa_data.get("ror", "") or ""
    csv_ror = _clean_float(row.get("ror_id", ""))
    if oa_ror and csv_ror:
        if extract_ror_id(oa_ror) != extract_ror_id(csv_ror):
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="OpenAlex",
                    severity="error",
                    field_name="ROR",
                    message=f"ROR mismatch – CSV: '{csv_ror}', OpenAlex: '{oa_ror}'",
                )
            )
    elif oa_ror and not csv_ror:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="OpenAlex",
                severity="info",
                field_name="ROR",
                message=(
                    f"OpenAlex has ROR '{oa_ror}' but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    # Wikidata cross-reference.
    oa_ids = oa_data.get("ids", {})
    oa_wd = oa_ids.get("wikidata", "") or ""
    if oa_wd:
        oa_wd_qid = oa_wd.rsplit("/", 1)[-1]  # https://www.wikidata.org/entity/Q262760
    else:
        oa_wd_qid = ""
    csv_wd = _clean_float(row.get("wikidata_id", ""))
    if oa_wd_qid and csv_wd:
        if oa_wd_qid != csv_wd:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="OpenAlex",
                    severity="error",
                    field_name="Wikidata",
                    message=(
                        f"Wikidata mismatch – CSV: '{csv_wd}', OpenAlex: '{oa_wd_qid}'"
                    ),
                )
            )
    elif oa_wd_qid and not csv_wd:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="OpenAlex",
                severity="info",
                field_name="Wikidata",
                message=(
                    f"OpenAlex has Wikidata '{oa_wd_qid}' but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    # Country check.
    cc = oa_data.get("country_code", "")
    if cc and cc != "CH":
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="OpenAlex",
                severity="error",
                field_name="Country",
                message=f"OpenAlex country is '{cc}', expected 'CH'",
            )
        )

    return issues


def check_wikidata_record(
    row: pd.Series,
    wd: WikidataRecord,
) -> list[Issue]:
    """Compare Wikidata SPARQL results against the local CSV row."""
    issues: list[Issue] = []
    name, short = _name(row), _short(row)

    # Label comparison.
    if wd.label and wd.label.lower() != name.lower():
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="Label",
                message=f"Wikidata English label differs: '{wd.label}'",
            )
        )

    # ROR cross-reference.
    csv_ror_short = extract_ror_id(_clean_float(row.get("ror_id", "")))
    if wd.ror_ids and csv_ror_short:
        if csv_ror_short not in wd.ror_ids:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Wikidata",
                    severity="error",
                    field_name="ROR",
                    message=(
                        f"ROR mismatch – CSV: '{csv_ror_short}', Wikidata: {wd.ror_ids}"
                    ),
                )
            )
    elif wd.ror_ids and not csv_ror_short:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="ROR",
                message=(
                    f"Wikidata has ROR {wd.ror_ids} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )
    elif not wd.ror_ids and csv_ror_short:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="ROR",
                message=(
                    f"CSV has ROR '{csv_ror_short}' but Wikidata P6782 is empty "
                    f"– Wikidata update opportunity"
                ),
            )
        )

    # ISNI cross-reference.
    csv_isni = normalise_isni(_clean_float(row.get("isni_id", "")))
    wd_isnis = {normalise_isni(i) for i in wd.isni_ids}
    if wd_isnis and csv_isni:
        if csv_isni not in wd_isnis:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Wikidata",
                    severity="error",
                    field_name="ISNI",
                    message=f"ISNI mismatch – CSV: '{csv_isni}', Wikidata: {wd_isnis}",
                )
            )
    elif wd_isnis and not csv_isni:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="ISNI",
                message=(
                    f"Wikidata has ISNI {wd_isnis} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )
    elif not wd_isnis and csv_isni:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="ISNI",
                message=(
                    f"CSV has ISNI '{csv_isni}' but Wikidata P213 is empty "
                    f"– Wikidata update opportunity"
                ),
            )
        )

    # GRID cross-reference.
    csv_grid = normalise_grid(_clean_float(row.get("grid_id", "")))
    wd_grids = {normalise_grid(g) for g in wd.grid_ids}
    if wd_grids and csv_grid:
        if csv_grid not in wd_grids:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Wikidata",
                    severity="error",
                    field_name="GRID",
                    message=f"GRID mismatch – CSV: '{csv_grid}', Wikidata: {wd_grids}",
                )
            )
    elif wd_grids and not csv_grid:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="GRID",
                message=(
                    f"Wikidata has GRID {wd_grids} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    # OpenAlex cross-reference.
    csv_oa_ids = csv_set(row.get("openalex_ids", ""))
    if wd.openalex_ids and csv_oa_ids:
        missing_in_csv = wd.openalex_ids - csv_oa_ids
        if missing_in_csv:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Wikidata",
                    severity="info",
                    field_name="OpenAlex",
                    message=(
                        f"Wikidata has OpenAlex IDs {missing_in_csv} not in CSV "
                        f"– enrichment opportunity"
                    ),
                )
            )
    elif wd.openalex_ids and not csv_oa_ids:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="OpenAlex",
                message=(
                    f"Wikidata has OpenAlex {wd.openalex_ids} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    # Crossref funder cross-reference.
    csv_cf = normalise_crossref(_clean_float(row.get("crossref_funder_id", "")))
    wd_cfs = {normalise_crossref(c) for c in wd.crossref_ids}
    if wd_cfs and csv_cf:
        if csv_cf not in wd_cfs:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Wikidata",
                    severity="error",
                    field_name="Crossref funder",
                    message=(
                        f"Crossref funder mismatch – "
                        f"CSV: '{csv_cf}', Wikidata: {wd_cfs}"
                    ),
                )
            )
    elif wd_cfs and not csv_cf:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="Crossref funder",
                message=(
                    f"Wikidata has Crossref funder {wd_cfs} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    # GeoNames cross-reference.
    csv_gn = normalise_geonames(_clean_float(row.get("geonames_id", "")))
    wd_gns = {normalise_geonames(g) for g in wd.geonames_ids}
    if wd_gns and csv_gn:
        if csv_gn not in wd_gns:
            issues.append(
                Issue(
                    institution=name,
                    short_name=short,
                    source="Wikidata",
                    severity="warning",
                    field_name="GeoNames",
                    message=(
                        f"GeoNames mismatch – CSV: '{csv_gn}', Wikidata: {wd_gns}"
                    ),
                )
            )
    elif wd_gns and not csv_gn:
        issues.append(
            Issue(
                institution=name,
                short_name=short,
                source="Wikidata",
                severity="info",
                field_name="GeoNames",
                message=(
                    f"Wikidata has GeoNames {wd_gns} but CSV is empty "
                    f"– enrichment opportunity"
                ),
            )
        )

    return issues


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def format_report(issues: list[Issue], df: pd.DataFrame) -> str:
    """Render all issues as a Markdown report."""
    lines: list[str] = []
    lines.append("# Swiss HEI Open Data – Cross-Check Report\n")

    # --- Summary ---
    n_inst = len(df)
    n_errors = sum(1 for i in issues if i.severity == "error")
    n_warnings = sum(1 for i in issues if i.severity == "warning")
    n_info = sum(1 for i in issues if i.severity == "info")
    affected = len({i.short_name for i in issues})

    lines.append("## Summary\n")
    lines.append(f"- **Institutions checked:** {n_inst}")
    lines.append(f"- **Institutions with findings:** {affected}")
    lines.append(f"- **Errors (conflicts):** {n_errors}")
    lines.append(f"- **Warnings (missing critical data):** {n_warnings}")
    lines.append(f"- **Info (enrichment opportunities):** {n_info}")
    lines.append("")

    # --- Errors ---
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        lines.append("## Errors (data conflicts between sources)\n")
        lines.append("| Institution | Source | Field | Details |")
        lines.append("|:---|:---|:---|:---|")
        for iss in sorted(errors, key=lambda x: x.institution):
            lines.append(
                f"| {iss.short_name} | {iss.source} | {iss.field_name} "
                f"| {iss.message} |"
            )
        lines.append("")

    # --- Warnings ---
    warnings = [i for i in issues if i.severity == "warning"]
    if warnings:
        lines.append("## Warnings (missing critical data)\n")
        lines.append("| Institution | Source | Field | Details |")
        lines.append("|:---|:---|:---|:---|")
        for iss in sorted(warnings, key=lambda x: x.institution):
            lines.append(
                f"| {iss.short_name} | {iss.source} | {iss.field_name} "
                f"| {iss.message} |"
            )
        lines.append("")

    # --- Info ---
    infos = [i for i in issues if i.severity == "info"]
    if infos:
        lines.append("## Info (enrichment opportunities & name differences)\n")
        lines.append("| Institution | Source | Field | Details |")
        lines.append("|:---|:---|:---|:---|")
        for iss in sorted(infos, key=lambda x: x.institution):
            lines.append(
                f"| {iss.short_name} | {iss.source} | {iss.field_name} "
                f"| {iss.message} |"
            )
        lines.append("")

    # --- Coverage matrix ---
    lines.append("## Identifier coverage matrix\n")
    id_cols = [
        ("ror_id", "ROR"),
        ("wikidata_id", "Wikidata"),
        ("openalex_ids", "OpenAlex"),
        ("openorgs_ids", "OpenOrgs"),
        ("grid_id", "GRID"),
        ("isni_id", "ISNI"),
        ("crossref_funder_id", "Crossref"),
        ("geonames_id", "GeoNames"),
    ]

    header = "| Institution | " + " | ".join(label for _, label in id_cols) + " |"
    sep = "|:---|" + "|".join(":---:" for _ in id_cols) + "|"
    lines.append(header)
    lines.append(sep)

    for _, row in df.iterrows():
        short = str(row["short_name"])
        cells: list[str] = []
        for col, _ in id_cols:
            val = _clean_float(row.get(col, ""))
            cells.append("Y" if val else "-")
        lines.append(f"| {short} | " + " | ".join(cells) + " |")
    lines.append("")

    # --- Totals ---
    lines.append("### Coverage totals\n")
    lines.append("| Identifier | Count | Percentage |")
    lines.append("|:---|---:|---:|")
    for col, label in id_cols:
        count = sum(1 for _, r in df.iterrows() if _clean_float(r.get(col, "")))
        pct = f"{100 * count / n_inst:.1f}%" if n_inst else "0%"
        lines.append(f"| {label} | {count}/{n_inst} | {pct} |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


async def run_checks(df: pd.DataFrame) -> list[Issue]:
    """Run all cross-checks and return a flat list of issues."""
    all_issues: list[Issue] = []

    # 1. Local missing-data checks (no API calls).
    print("Checking for missing data …", file=sys.stderr)
    for _, row in df.iterrows():
        all_issues.extend(check_missing_data(row))

    # 2. Wikidata batch SPARQL query.
    qids = [
        _clean_float(row["wikidata_id"])
        for _, row in df.iterrows()
        if _clean_float(row.get("wikidata_id", ""))
    ]
    wd_records: dict[str, WikidataRecord] = {}

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(REQUEST_TIMEOUT, read=60.0),
        follow_redirects=True,
    ) as client:
        # Wikidata.
        if qids:
            print(
                f"Querying Wikidata for {len(qids)} entities …",
                file=sys.stderr,
            )
            wd_records = await fetch_wikidata_batch(client, qids)
            print(
                f"  Retrieved {len(wd_records)} Wikidata records.",
                file=sys.stderr,
            )

        # 3. ROR checks.
        ror_sem = asyncio.Semaphore(ROR_CONCURRENCY)
        ror_rows = [
            (idx, row)
            for idx, row in df.iterrows()
            if _clean_float(row.get("ror_id", ""))
        ]
        if ror_rows:
            print(
                f"Querying ROR for {len(ror_rows)} institutions …",
                file=sys.stderr,
            )
            ror_tasks = [
                fetch_ror_record(client, _clean_float(row["ror_id"]), ror_sem)
                for _, row in ror_rows
            ]
            ror_results = await asyncio.gather(*ror_tasks)
            for (_, row), ror_data in zip(ror_rows, ror_results):
                if ror_data is None:
                    all_issues.append(
                        Issue(
                            institution=_name(row),
                            short_name=_short(row),
                            source="ROR",
                            severity="error",
                            field_name="API",
                            message=(
                                f"Could not fetch ROR record for "
                                f"'{_clean_float(row['ror_id'])}'"
                            ),
                        )
                    )
                else:
                    all_issues.extend(check_ror_record(row, ror_data))
            print("  ROR checks complete.", file=sys.stderr)

        # 4. OpenAlex checks.
        oa_sem = asyncio.Semaphore(OPENALEX_CONCURRENCY)
        oa_rows = [(idx, row) for idx, row in df.iterrows() if _oa_primary_id(row)]
        if oa_rows:
            print(
                f"Querying OpenAlex for {len(oa_rows)} institutions …",
                file=sys.stderr,
            )
            oa_tasks = [
                fetch_openalex_record(
                    client,
                    _oa_primary_id(row),
                    oa_sem,  # type: ignore[arg-type]
                )
                for _, row in oa_rows
            ]
            oa_results = await asyncio.gather(*oa_tasks)
            for (_, row), oa_data in zip(oa_rows, oa_results):
                if oa_data is None:
                    all_issues.append(
                        Issue(
                            institution=_name(row),
                            short_name=_short(row),
                            source="OpenAlex",
                            severity="error",
                            field_name="API",
                            message=(
                                f"Could not fetch OpenAlex record for "
                                f"'{_oa_primary_id(row)}'"
                            ),
                        )
                    )
                else:
                    all_issues.extend(check_openalex_record(row, oa_data))
            print("  OpenAlex checks complete.", file=sys.stderr)

    # 5. Wikidata cross-checks.
    if wd_records:
        print("Running Wikidata cross-checks …", file=sys.stderr)
        for _, row in df.iterrows():
            qid = _clean_float(row.get("wikidata_id", ""))
            if qid and qid in wd_records:
                all_issues.extend(check_wikidata_record(row, wd_records[qid]))
        print("  Wikidata checks complete.", file=sys.stderr)

    return all_issues


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-check swiss-hei-open-data against external registries.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Write Markdown report to FILE (default: stdout).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DATA_PATH,
        help=f"Path to hei.csv (default: {DATA_PATH}).",
    )
    args = parser.parse_args()

    csv_path: Path = args.csv
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} institutions from {csv_path.name}.", file=sys.stderr)

    issues = asyncio.run(run_checks(df))
    report = format_report(issues, df)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"\nReport written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
