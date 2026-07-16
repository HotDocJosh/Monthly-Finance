#!/usr/bin/env python3
"""Fetch the month's AP invoices (bills) from Xero into the close inputs.

Usage:
    python integrations/xero/fetch_ap_invoices.py YYYY-MM [options]

Examples:
    # Write inputs/2026-07/ap_invoices.csv for bills dated in July 2026
    python integrations/xero/fetch_ap_invoices.py 2026-07

    # Widen the window to catch late invoices relating to the period
    python integrations/xero/fetch_ap_invoices.py 2026-07 --to-date 2026-08-10

Pulls accounts-payable invoices (Type ACCPAY) dated within the period and
writes one row per invoice line — the granularity prepayments-recon and
accruals-recon need (line description, expense account, amount). READ-ONLY: it
never creates or edits anything in Xero.

By default only posted bills are included (AUTHORISED / PAID); pass
--include-drafts to also include DRAFT and SUBMITTED.

Output columns:
    invoice_date, due_date, invoice_number, reference, supplier, status,
    line_description, account_code, account_name, line_amount, tax_amount,
    currency, invoice_total, invoice_id
"""

from __future__ import annotations

import argparse
import calendar
import csv
import io
import os
import re
import sys
from typing import Any

import xero_client

_POSTED_STATUSES = {"AUTHORISED", "PAID"}
_DRAFT_STATUSES = {"DRAFT", "SUBMITTED"}
# Never include these regardless of flags.
_EXCLUDED_STATUSES = {"DELETED", "VOIDED"}

_FIELDNAMES = [
    "invoice_date",
    "due_date",
    "invoice_number",
    "reference",
    "supplier",
    "status",
    "line_description",
    "account_code",
    "account_name",
    "line_amount",
    "tax_amount",
    "currency",
    "invoice_total",
    "invoice_id",
]


def parse_period(period: str) -> tuple[str, str]:
    """Validate YYYY-MM; return (first_day_iso, first_day_of_next_month_iso)."""
    match = re.fullmatch(r"(\d{4})-(\d{2})", period.strip())
    if not match:
        raise SystemExit(f"Invalid period {period!r}; expected YYYY-MM (e.g. 2026-07).")
    year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        raise SystemExit(f"Invalid month in {period!r}.")
    last_day = calendar.monthrange(year, month)[1]
    first = f"{year:04d}-{month:02d}-01"
    # Exclusive upper bound = day after the last day of the month.
    next_day = (year, month, last_day)
    ny, nm, nd = _next_day(*next_day)
    return first, f"{ny:04d}-{nm:02d}-{nd:02d}"


def _next_day(year: int, month: int, day: int) -> tuple[int, int, int]:
    last_day = calendar.monthrange(year, month)[1]
    if day < last_day:
        return year, month, day + 1
    if month < 12:
        return year, month + 1, 1
    return year + 1, 1, 1


def _iso_to_datetime_clause(iso: str) -> str:
    """Turn 'YYYY-MM-DD' into Xero's DateTime(y,m,d) where-clause literal."""
    year, month, day = iso.split("-")
    return f"DateTime({int(year)},{int(month)},{int(day)})"


def build_where(from_date: str, to_date_exclusive: str) -> str:
    """Build the Xero 'where' filter for ACCPAY invoices in a date range."""
    return (
        'Type=="ACCPAY"'
        f" AND Date>={_iso_to_datetime_clause(from_date)}"
        f" AND Date<{_iso_to_datetime_clause(to_date_exclusive)}"
    )


def invoices_to_rows(
    invoices: list[dict[str, Any]], include_drafts: bool
) -> list[dict[str, str]]:
    """Flatten Xero invoices into one row per line item."""
    allowed = set(_POSTED_STATUSES)
    if include_drafts:
        allowed |= _DRAFT_STATUSES

    rows: list[dict[str, str]] = []
    for inv in invoices:
        status = (inv.get("Status") or "").upper()
        if status in _EXCLUDED_STATUSES or status not in allowed:
            continue
        contact = (inv.get("Contact") or {}).get("Name", "")
        base = {
            "invoice_date": _date(inv.get("DateString") or inv.get("Date")),
            "due_date": _date(inv.get("DueDateString") or inv.get("DueDate")),
            "invoice_number": inv.get("InvoiceNumber", ""),
            "reference": inv.get("Reference", ""),
            "supplier": contact,
            "status": status,
            "currency": inv.get("CurrencyCode", ""),
            "invoice_total": _num(inv.get("Total")),
            "invoice_id": inv.get("InvoiceID", ""),
        }
        line_items = inv.get("LineItems") or []
        if not line_items:
            rows.append({**base, "line_description": "", "account_code": "",
                         "account_name": "", "line_amount": "", "tax_amount": ""})
            continue
        for line in line_items:
            rows.append({
                **base,
                "line_description": line.get("Description", ""),
                "account_code": line.get("AccountCode", ""),
                "account_name": line.get("AccountName", ""),
                "line_amount": _num(line.get("LineAmount")),
                "tax_amount": _num(line.get("TaxAmount")),
            })
    return rows


def _date(value: Any) -> str:
    """Return an ISO date. Xero gives either 'YYYY-MM-DDT...' or /Date(ms)/."""
    if not value:
        return ""
    text = str(value)
    if text.startswith("/Date("):
        digits = re.search(r"/Date\((\d+)", text)
        if digits:
            # milliseconds since epoch -> date (UTC)
            import datetime

            seconds = int(digits.group(1)) / 1000
            return datetime.datetime.utcfromtimestamp(seconds).date().isoformat()
    return text[:10]


def _num(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value)


def to_csv(rows: list[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=_FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({f: row.get(f, "") for f in _FIELDNAMES})
    return buffer.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch AP invoices (bills) for a period from Xero (read-only).",
    )
    parser.add_argument("period", help="Reporting period as YYYY-MM, e.g. 2026-07.")
    parser.add_argument("--from-date", help="Override start date (YYYY-MM-DD).")
    parser.add_argument(
        "--to-date",
        help="Override inclusive end date (YYYY-MM-DD); useful to catch late "
        "invoices relating to the period.",
    )
    parser.add_argument(
        "--include-drafts",
        action="store_true",
        help="Also include DRAFT and SUBMITTED bills (default: posted only).",
    )
    parser.add_argument("--tenant", help="Organisation name, if more than one.")
    parser.add_argument("--output", help="Output CSV path.")
    parser.add_argument("--stdout", action="store_true", help="Print instead of write.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file.")
    args = parser.parse_args(argv)

    from_default, to_default_exclusive = parse_period(args.period)
    from_date = args.from_date or from_default
    if args.to_date:
        # Convert an inclusive end date to Xero's exclusive upper bound.
        ey, em, ed = (int(p) for p in args.to_date.split("-"))
        ny, nm, nd = _next_day(ey, em, ed)
        to_exclusive = f"{ny:04d}-{nm:02d}-{nd:02d}"
    else:
        to_exclusive = to_default_exclusive

    output_path = None
    if not args.stdout:
        output_path = args.output or f"inputs/{args.period}/ap_invoices.csv"
        if os.path.exists(output_path) and not args.force:
            print(
                f"ERROR: {output_path} already exists. Re-run with --force to "
                "overwrite, or use --output to write elsewhere.",
                file=sys.stderr,
            )
            return 1

    where = build_where(from_date, to_exclusive)
    try:
        token, tenant_id = xero_client.connect(tenant_name=args.tenant)
        invoices = xero_client.get_paged(
            token, tenant_id, "Invoices", "Invoices", {"where": where}
        )
    except xero_client.XeroError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    rows = invoices_to_rows(invoices, include_drafts=args.include_drafts)
    csv_text = to_csv(rows)

    if args.stdout:
        sys.stdout.write(csv_text)
        return 0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        handle.write(csv_text)
    print(
        f"Wrote {len(rows)} invoice line(s) from {len(invoices)} bill(s) to "
        f"{output_path} (dated {from_date} to <{to_exclusive})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
