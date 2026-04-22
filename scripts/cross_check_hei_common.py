"""Shared constants, models, helpers, and API clients for HEI cross-checks."""

from __future__ import annotations

import asyncio
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import pandas as pd

DATA_PATH: Path = (
    Path(__file__).resolve().parent.parent / "dashboards" / "_data" / "hei.csv"
)

ROR_API_BASE: str = "https://api.ror.org/v2/organizations"
OPENALEX_API_BASE: str = "https://api.openalex.org/institutions"
WIKIDATA_SPARQL_URL: str = "https://query.wikidata.org/sparql"

USER_AGENT: str = (
    "naif-cross-check/1.0 (https://github.com/eth-library/naif; mailto:info@naif.ch)"
)

ROR_CONCURRENCY: int = 5
OPENALEX_CONCURRENCY: int = 10
REQUEST_TIMEOUT: float = 30.0

WD_PROP_ROR: str = "P6782"
WD_PROP_ISNI: str = "P213"
WD_PROP_GRID: str = "P2427"
WD_PROP_OPENALEX: str = "P10283"
WD_PROP_CROSSREF: str = "P3153"
WD_PROP_GEONAMES: str = "P1566"


@dataclass
class Issue:
    """A single finding from the cross-check."""

    institution: str
    short_name: str
    source: str
    severity: str
    field_name: str
    message: str


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
    """Extract the short ROR identifier from a full URL."""
    return ror_url.strip().rstrip("/").rsplit("/", 1)[-1]


def normalise_isni(value: str) -> str:
    """Normalise ISNI to the canonical 16-character space-separated form."""
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


async def fetch_ror_record(
    client: httpx.AsyncClient,
    ror_url: str,
    sem: asyncio.Semaphore,
) -> dict | None:
    """Fetch a single ROR v2 record."""
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
    """Return the primary OpenAlex ID used for direct API lookups."""
    primary_id = _clean_float(row.get("openalex_primary_id", ""))
    return primary_id or None


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
    return [value.strip() for value in raw.split("|") if value.strip()]
