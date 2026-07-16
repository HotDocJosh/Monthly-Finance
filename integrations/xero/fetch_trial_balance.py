#!/usr/bin/env python3
"""Fetch the month-end Trial Balance from Xero into the close inputs.

Usage:
    python integrations/xero/fetch_trial_balance.py YYYY-MM [options]

Examples:
    # Write inputs/2026-07/trial_balance.csv as at 31 Jul 2026
    python integrations/xero/fetch_trial_balance.py 2026-07

    # Preview to stdout without writing a file
    python integrations/xero/fetch_trial_balance.py 2026-07 --stdout

    # Overwrite an existing export
    python integrations/xero/fetch_trial_balance.py 2026-07 --force

This is READ-ONLY: it pulls the Trial Balance report as at the last day of the
period and writes it as the GL export that every close task consumes. It never
posts anything back to Xero. By default it refuses to overwrite an existing
trial_balance.csv (respecting the "inputs are source data" rule) — pass
--force to replace one.

Output columns:
    account_code, account_name, account_type, debit, credit, ytd_debit, ytd_credit
(the numeric columns mirror whatever the Xero Trial Balance report returns for
the chosen date; debit/credit are the account balances as at month end).
"""

from __future__ import annotations

import argparse
import calendar
import csv
import io
import re
import sys
from typing import Any

import xero_client

# Cell values that are section subtotals / totals rather than accounts.
_TOTAL_PREFIXES = ("total",)
# Extract a trailing account code, e.g. "Sales (200)" -> ("Sales", "200").
_CODE_RE = re.compile(r"^(.*?)\s*\(([^)]*)\)\s*$")


def parse_period(period: str) -> tuple[int, int, str]:
    """Validate YYYY-MM and return (year, month, last_day_iso)."""
    match = re.fullmatch(r"(\d{4})-(\d{2})", period.strip())
    if not match:
        raise SystemExit(f"Invalid period {period!r}; expected YYYY-MM (e.g. 2026-07).")
    year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        raise SystemExit(f"Invalid month in {period!r}.")
    last_day = calendar.monthrange(year, month)[1]
    return year, month, f"{year:04d}-{month:02d}-{last_day:02d}"


def _normalise_header(label: str) -> str:
    """Turn a report column label into a snake_case field name."""
    key = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return key or "value"


def _split_account(label: str) -> tuple[str, str]:
    """Split an account cell into (name, code). Code may be empty."""
    match = _CODE_RE.match(label.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return label.strip(), ""


def _is_account_row(cells: list[dict[str, Any]]) -> bool:
    """A data row for a real account has an 'account' attribute on cell 0."""
    if not cells:
        return False
    for attr in cells[0].get("Attributes") or []:
        if attr.get("Id") == "account":
            return True
    return False


def parse_trial_balance(report_json: dict[str, Any]) -> tuple[list[str], list[dict]]:
    """Parse a Xero TrialBalance report into (numeric_fields, records)."""
    reports = report_json.get("Reports") or []
    if not reports:
        raise xero_client.XeroError("Xero returned no Trial Balance report.")
    rows = reports[0].get("Rows", [])

    headers: list[str] = []
    numeric_fields: list[str] = []
    records: list[dict] = []
    section = ""

    def handle_row(row: dict[str, Any]) -> None:
        nonlocal headers, numeric_fields
        row_type = row.get("RowType")
        if row_type == "Header":
            headers = [c.get("Value", "") for c in row.get("Cells", [])]
            numeric_fields = [_normalise_header(h) for h in headers[1:]]
            return
        if row_type not in ("Row",):
            return
        cells = row.get("Cells", [])
        if not _is_account_row(cells):
            return
        label = (cells[0].get("Value") or "").strip()
        if any(label.lower().startswith(p) for p in _TOTAL_PREFIXES):
            return
        name, code = _split_account(label)
        record = {
            "account_code": code,
            "account_name": name,
            "account_type": section,
        }
        for field, cell in zip(numeric_fields, cells[1:]):
            record[field] = (cell.get("Value") or "").strip()
        records.append(record)

    def walk(row_list: list[dict[str, Any]]) -> None:
        nonlocal section
        for row in row_list:
            if row.get("RowType") == "Section":
                section = (row.get("Title") or "").strip()
                walk(row.get("Rows", []))
            else:
                handle_row(row)

    walk(rows)
    return numeric_fields, records


def to_csv(numeric_fields: list[str], records: list[dict]) -> str:
    """Render records as CSV text with a stable column order."""
    preferred = ["debit", "credit", "ytd_debit", "ytd_credit"]
    ordered = [f for f in preferred if f in numeric_fields]
    ordered += [f for f in numeric_fields if f not in ordered]
    fieldnames = ["account_code", "account_name", "account_type"] + ordered
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for record in records:
        writer.writerow({f: record.get(f, "") for f in fieldnames})
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch the Xero Trial Balance for a period (read-only).",
    )
    parser.add_argument("period", help="Reporting period as YYYY-MM, e.g. 2026-07.")
    parser.add_argument(
        "--date",
        help="Override the report date (YYYY-MM-DD). Defaults to month end.",
    )
    parser.add_argument(
        "--output",
        help="Output CSV path. Defaults to inputs/<period>/trial_balance.csv.",
    )
    parser.add_argument(
        "--tenant",
        help="Organisation name, if the connection has more than one.",
    )
    parser.add_argument(
        "--payments-only",
        action="store_true",
        help="Report on a cash (payments) basis instead of accruals.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the CSV instead of writing a file.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    args = parser.parse_args(argv)

    _, _, month_end = parse_period(args.period)
    report_date = args.date or month_end

    # Resolve and guard the output path *before* any network call, so we fail
    # fast rather than fetching and then refusing to write.
    import os

    output_path = None
    if not args.stdout:
        output_path = args.output or f"inputs/{args.period}/trial_balance.csv"
        if os.path.exists(output_path) and not args.force:
            print(
                f"ERROR: {output_path} already exists. Re-run with --force to "
                "overwrite, or use --output to write elsewhere.",
                file=sys.stderr,
            )
            return 1

    params = {"date": report_date}
    if args.payments_only:
        params["paymentsOnly"] = "true"

    try:
        token, tenant_id = xero_client.connect(tenant_name=args.tenant)
        report_json = xero_client.get_report(token, tenant_id, "TrialBalance", params)
    except xero_client.XeroError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    numeric_fields, records = parse_trial_balance(report_json)
    if not records:
        print(
            "ERROR: no account rows parsed from the Trial Balance — check the date "
            "and that the organisation has posted transactions.",
            file=sys.stderr,
        )
        return 1

    csv_text = to_csv(numeric_fields, records)

    if args.stdout:
        sys.stdout.write(csv_text)
        return 0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        handle.write(csv_text)

    print(
        f"Wrote {len(records)} accounts to {output_path} "
        f"(Trial Balance as at {report_date})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
