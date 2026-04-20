"""Shared constants and utilities for NAIF dashboards."""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

# -- Data directory ------------------------------------------------------------

# Absolute path to the shared ``_data/`` directory.
DATA_DIR: Path = Path(__file__).resolve().parent / "_data"

# -- Institution type constants ------------------------------------------------

TYPE_ORDER: list[str] = ["University", "Univ. Inst.", "UAS", "UAS Inst.", "UTE"]

TYPE_LABELS: dict[str, str] = {
    "University": "Universities",
    "Univ. Inst.": "University institutes",
    "UAS": "Universities of applied sciences (UAS)",
    "UAS Inst.": "UAS institutes",
    "UTE": "Teacher education institutions",
}

# -- Formatting helpers --------------------------------------------------------


def normalise_yes_no(value: object) -> str:
    """Normalise status values to Yes / No / Unknown."""
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip().lower()
    if text in {"yes", "true", "1"}:
        return "Yes"
    if text in {"no", "false", "0"}:
        return "No"
    return "Unknown"


def format_identifier(value: object) -> str:
    """Convert IDs to stable strings and remove float artefacts."""
    if pd.isna(value):
        return ""

    text = str(value).strip()
    if not text:
        return ""

    if text.endswith(".0"):
        try:
            numeric_value = float(text)
            if numeric_value.is_integer():
                return str(int(numeric_value))
        except ValueError:
            return text

    return text


def format_plain_text(value: object) -> str:
    """Return plain text values with a fallback dash."""
    text = format_identifier(value)
    return text if text else "-"


def format_type_label(value: object, labels: dict[str, str] | None = None) -> str:
    """Return the full label for an institution type.

    Parameters
    ----------
    value:
        Raw institution-type value (e.g. ``"UAS"``).
    labels:
        Optional custom label mapping.  Falls back to :data:`TYPE_LABELS`.
    """
    text = format_identifier(value)
    if not text:
        return "Unknown"
    effective_labels = labels if labels is not None else TYPE_LABELS
    return effective_labels.get(text, text)


def type_order_key(value: object, order: list[str] | None = None) -> int:
    """Return a stable sort key for institution types.

    Parameters
    ----------
    value:
        Raw institution-type value (e.g. ``"UAS"``).
    order:
        Optional custom ordering list.  Falls back to :data:`TYPE_ORDER`.
    """
    text = format_identifier(value)
    effective_order = order if order is not None else TYPE_ORDER
    try:
        return effective_order.index(text)
    except ValueError:
        return len(effective_order)


def pct(value: int, denominator: int) -> str:
    """Format a value as a percentage string."""
    if denominator == 0:
        return "0.0%"
    return f"{(100 * value / denominator):.1f}%"


def make_link(url: str, label: str) -> str:
    """Create a safe external link."""
    return (
        f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
        f"{html.escape(label)}</a>"
    )


def render_table(dataframe: pd.DataFrame) -> str:
    """Return a dataframe as an HTML table string."""
    return dataframe.to_html(
        escape=False,
        index=False,
        classes="table table-sm table-striped align-middle",
        border=0,
    )


# -- Excel export --------------------------------------------------------------


def write_dataframe_xlsx(
    dataframe: pd.DataFrame,
    output_path: str | Path,
    sheet_name: str = "Institutions",
) -> None:
    """Write a DataFrame as a formatted XLSX workbook."""
    with pd.ExcelWriter(str(output_path), engine="xlsxwriter") as writer:
        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        worksheet.freeze_panes(1, 0)
        worksheet.autofilter(0, 0, len(dataframe), len(dataframe.columns) - 1)

        for column_index, column_name in enumerate(dataframe.columns):
            values = dataframe[column_name].astype(str)
            max_length = max(len(column_name), *(len(value) for value in values))
            worksheet.set_column(column_index, column_index, min(max_length + 2, 40))


def ensure_csv_xlsx_export(
    csv_path: str | Path,
    xlsx_path: str | Path,
    sheet_name: str = "Institutions",
) -> Path:
    """Generate an XLSX export from CSV when the workbook is missing or stale."""
    source_path = Path(csv_path)
    output_path = Path(xlsx_path)

    if output_path.exists() and output_path.stat().st_mtime >= source_path.stat().st_mtime:
        return output_path

    dataframe = pd.read_csv(source_path, dtype=str).fillna("")
    write_dataframe_xlsx(dataframe, output_path, sheet_name=sheet_name)
    return output_path


def ensure_hei_xlsx_export() -> Path:
    """Generate the shared Swiss HEI XLSX download from ``hei.csv`` when needed."""
    return ensure_csv_xlsx_export(
        DATA_DIR / "hei.csv",
        DATA_DIR / "hei.xlsx",
        sheet_name="Swiss HEIs",
    )
