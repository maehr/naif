"""Cross-check logic and orchestration for HEI registry validation."""

from __future__ import annotations

import asyncio
import sys

import httpx
import pandas as pd

try:
    from cross_check_hei_common import (
        OPENALEX_CONCURRENCY,
        REQUEST_TIMEOUT,
        ROR_CONCURRENCY,
        USER_AGENT,
        Issue,
        WikidataRecord,
        _clean_float,
        _name,
        _oa_primary_id,
        _ror_external,
        _ror_name_en,
        _short,
        csv_set,
        extract_ror_id,
        fetch_openalex_record,
        fetch_ror_record,
        fetch_wikidata_batch,
        normalise_crossref,
        normalise_geonames,
        normalise_grid,
        normalise_isni,
    )
except ImportError:  # pragma: no cover - package import path for tests
    from scripts.cross_check_hei_common import (
        OPENALEX_CONCURRENCY,
        REQUEST_TIMEOUT,
        ROR_CONCURRENCY,
        USER_AGENT,
        Issue,
        WikidataRecord,
        _clean_float,
        _name,
        _oa_primary_id,
        _ror_external,
        _ror_name_en,
        _short,
        csv_set,
        extract_ror_id,
        fetch_openalex_record,
        fetch_ror_record,
        fetch_wikidata_batch,
        normalise_crossref,
        normalise_geonames,
        normalise_grid,
        normalise_isni,
    )


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
                message=f"ROR has Wikidata {ror_wds} but CSV is empty – enrichment opportunity",
            )
        )

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

    oa_ids = oa_data.get("ids", {})
    oa_wd = oa_ids.get("wikidata", "") or ""
    oa_wd_qid = oa_wd.rsplit("/", 1)[-1] if oa_wd else ""
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
                    message=f"ROR mismatch – CSV: '{csv_ror_short}', Wikidata: {wd.ror_ids}",
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
                    message=f"Crossref funder mismatch – CSV: '{csv_cf}', Wikidata: {wd_cfs}",
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
                    message=f"GeoNames mismatch – CSV: '{csv_gn}', Wikidata: {wd_gns}",
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


async def run_checks(df: pd.DataFrame) -> list[Issue]:
    """Run all cross-checks and return a flat list of issues."""
    all_issues: list[Issue] = []

    print("Checking for missing data …", file=sys.stderr)
    for _, row in df.iterrows():
        all_issues.extend(check_missing_data(row))

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
        if qids:
            print(f"Querying Wikidata for {len(qids)} entities …", file=sys.stderr)
            wd_records = await fetch_wikidata_batch(client, qids)
            print(f"  Retrieved {len(wd_records)} Wikidata records.", file=sys.stderr)

        ror_sem = asyncio.Semaphore(ROR_CONCURRENCY)
        ror_rows = [
            (idx, row)
            for idx, row in df.iterrows()
            if _clean_float(row.get("ror_id", ""))
        ]
        if ror_rows:
            print(f"Querying ROR for {len(ror_rows)} institutions …", file=sys.stderr)
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
                            message=f"Could not fetch ROR record for '{_clean_float(row['ror_id'])}'",
                        )
                    )
                else:
                    all_issues.extend(check_ror_record(row, ror_data))
            print("  ROR checks complete.", file=sys.stderr)

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
                            message=f"Could not fetch OpenAlex record for '{_oa_primary_id(row)}'",
                        )
                    )
                else:
                    all_issues.extend(check_openalex_record(row, oa_data))
            print("  OpenAlex checks complete.", file=sys.stderr)

    if wd_records:
        print("Running Wikidata cross-checks …", file=sys.stderr)
        for _, row in df.iterrows():
            qid = _clean_float(row.get("wikidata_id", ""))
            if qid and qid in wd_records:
                all_issues.extend(check_wikidata_record(row, wd_records[qid]))
        print("  Wikidata checks complete.", file=sys.stderr)

    return all_issues
