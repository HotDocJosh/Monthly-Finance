"""Parse Xero row-based reports (Bank Summary, P&L, Balance Sheet, etc.).

Xero reports share a common shape: a Header row defines the columns, and the
data is a tree of Section -> Row/SummaryRow. This flattens that tree into a
list of dicts keyed by normalised column names, with a ``section`` column
capturing the section each row sits under.

The dedicated Trial Balance fetcher does its own account-aware parsing; this
generic parser is for the aggregate reports where a flat dump is what's wanted.
"""

from __future__ import annotations

import re
from typing import Any


def normalise_header(label: str, index: int) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", (label or "").lower()).strip("_")
    if not key:
        return "label" if index == 0 else f"col_{index}"
    return key


def parse_report(
    report_json: dict[str, Any], include_summary: bool = True
) -> tuple[str, list[str], list[dict[str, str]]]:
    """Return (report_title, fieldnames, records) for a Xero report payload."""
    reports = report_json.get("Reports") or []
    if not reports:
        raise ValueError("Xero returned no report.")
    report = reports[0]
    title = report.get("ReportName") or report.get("ReportID") or "report"

    fields: list[str] = []
    records: list[dict[str, str]] = []
    section = ""

    def set_headers(cells: list[dict[str, Any]]) -> None:
        nonlocal fields
        fields = [
            normalise_header(c.get("Value", ""), i) for i, c in enumerate(cells)
        ]

    def emit(row: dict[str, Any]) -> None:
        row_type = row.get("RowType")
        if row_type == "Header":
            set_headers(row.get("Cells", []))
            return
        if row_type == "Row" or (include_summary and row_type == "SummaryRow"):
            cells = row.get("Cells", [])
            if not cells or not fields:
                return
            record = {"section": section, "row_type": row_type}
            for field, cell in zip(fields, cells):
                record[field] = (cell.get("Value") or "").strip()
            if any(v for k, v in record.items() if k not in ("section", "row_type")):
                records.append(record)

    def walk(row_list: list[dict[str, Any]]) -> None:
        nonlocal section
        for row in row_list:
            if row.get("RowType") == "Section":
                section = (row.get("Title") or "").strip()
                walk(row.get("Rows", []))
            else:
                emit(row)

    walk(report.get("Rows", []))
    fieldnames = ["section", "row_type"] + fields
    return title, fieldnames, records
