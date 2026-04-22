"""Markdown report generation for HEI cross-check findings."""

from __future__ import annotations

import pandas as pd

try:
    from cross_check_hei_common import Issue, _clean_float
except ImportError:  # pragma: no cover - package import path for tests
    from scripts.cross_check_hei_common import Issue, _clean_float


def format_report(issues: list[Issue], df: pd.DataFrame) -> str:
    """Render all issues as a Markdown report."""
    lines: list[str] = []
    lines.append("# Swiss HEI Open Data – Cross-Check Report\n")

    n_inst = len(df)
    n_errors = sum(1 for issue in issues if issue.severity == "error")
    n_warnings = sum(1 for issue in issues if issue.severity == "warning")
    n_info = sum(1 for issue in issues if issue.severity == "info")
    affected = len({issue.short_name for issue in issues})

    lines.append("## Summary\n")
    lines.append(f"- **Institutions checked:** {n_inst}")
    lines.append(f"- **Institutions with findings:** {affected}")
    lines.append(f"- **Errors (conflicts):** {n_errors}")
    lines.append(f"- **Warnings (missing critical data):** {n_warnings}")
    lines.append(f"- **Info (enrichment opportunities):** {n_info}")
    lines.append("")

    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        lines.append("## Errors (data conflicts between sources)\n")
        lines.append("| Institution | Source | Field | Details |")
        lines.append("|:---|:---|:---|:---|")
        for issue in sorted(errors, key=lambda item: item.institution):
            lines.append(
                f"| {issue.short_name} | {issue.source} | {issue.field_name} | {issue.message} |"
            )
        lines.append("")

    warnings = [issue for issue in issues if issue.severity == "warning"]
    if warnings:
        lines.append("## Warnings (missing critical data)\n")
        lines.append("| Institution | Source | Field | Details |")
        lines.append("|:---|:---|:---|:---|")
        for issue in sorted(warnings, key=lambda item: item.institution):
            lines.append(
                f"| {issue.short_name} | {issue.source} | {issue.field_name} | {issue.message} |"
            )
        lines.append("")

    infos = [issue for issue in issues if issue.severity == "info"]
    if infos:
        lines.append("## Info (enrichment opportunities & name differences)\n")
        lines.append("| Institution | Source | Field | Details |")
        lines.append("|:---|:---|:---|:---|")
        for issue in sorted(infos, key=lambda item: item.institution):
            lines.append(
                f"| {issue.short_name} | {issue.source} | {issue.field_name} | {issue.message} |"
            )
        lines.append("")

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

    lines.append("### Coverage totals\n")
    lines.append("| Identifier | Count | Percentage |")
    lines.append("|:---|---:|---:|")
    for col, label in id_cols:
        count = sum(1 for _, row in df.iterrows() if _clean_float(row.get(col, "")))
        pct = f"{100 * count / n_inst:.1f}%" if n_inst else "0%"
        lines.append(f"| {label} | {count}/{n_inst} | {pct} |")
    lines.append("")

    return "\n".join(lines)
