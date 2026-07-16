#!/usr/bin/env python3
"""Fetch a standard Xero report to CSV (read-only).

Usage:
    python integrations/xero/fetch_report.py REPORT --period YYYY-MM [options]

Examples:
    # Bank Summary for July 2026 (cash movements per bank account)
    python integrations/xero/fetch_report.py BankSummary --period 2026-07

    # Profit & Loss for the month
    python integrations/xero/fetch_report.py ProfitAndLoss --period 2026-07

    # Balance Sheet as at month end
    python integrations/xero/fetch_report.py BalanceSheet --period 2026-07

    # Aged Payables for one supplier as at month end
    python integrations/xero/fetch_report.py AgedPayablesByContact \
        --period 2026-07 --param contactID=<guid>

Supporting data for the close's analytical review (variance vs prior month,
interest visibility, etc.). READ-ONLY — it only reads reports from Xero.

These are supporting reports, not the exact named inputs: the Xero accounting
API has no GRNI/goods-receipt data (open_pos_grni.csv) or raw bank-statement
lines (bank_statements.csv), so those still come from their source systems.

Date parameters are derived from --period unless you override them:
    - BalanceSheet, TrialBalance                 -> date = month end
    - BankSummary, ProfitAndLoss, and others     -> fromDate/toDate = the month
Override with --date / --from-date / --to-date, or pass any report parameter
verbatim with --param key=value (repeatable).
"""

from __future__ import annotations

import argparse
import calendar
import csv
import io
import os
import re
import sys

import report_parser
import xero_client

# Reports that take a single as-at date rather than a from/to range.
_AS_AT_REPORTS = {"balancesheet", "trialbalance", "agedpayablesbycontact",
                  "agedreceivablesbycontact"}


def month_bounds(period: str) -> tuple[str, str]:
    match = re.fullmatch(r"(\d{4})-(\d{2})", period.strip())
    if not match:
        raise SystemExit(f"Invalid period {period!r}; expected YYYY-MM (e.g. 2026-07).")
    year, month = int(match.group(1)), int(match.group(2))
    if not 1 <= month <= 12:
        raise SystemExit(f"Invalid month in {period!r}.")
    last_day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01", f"{year:04d}-{month:02d}-{last_day:02d}"


def build_params(args: argparse.Namespace) -> dict[str, str]:
    params: dict[str, str] = {}
    from_date = to_date = as_at = None
    if args.period:
        from_date, as_at = month_bounds(args.period)
        to_date = as_at
    if args.from_date:
        from_date = args.from_date
    if args.to_date:
        to_date = args.to_date
    if args.date:
        as_at = args.date

    if args.report.lower() in _AS_AT_REPORTS:
        if as_at:
            params["date"] = as_at
    else:
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date

    for item in args.param or []:
        if "=" not in item:
            raise SystemExit(f"--param must be key=value, got {item!r}.")
        key, value = item.split("=", 1)
        params[key.strip()] = value.strip()
    return params


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a standard Xero report to CSV (read-only).",
    )
    parser.add_argument(
        "report",
        help="Report name, e.g. BankSummary, ProfitAndLoss, BalanceSheet, "
        "AgedPayablesByContact.",
    )
    parser.add_argument("--period", help="Period YYYY-MM to derive dates from.")
    parser.add_argument("--date", help="As-at date override (YYYY-MM-DD).")
    parser.add_argument("--from-date", help="Range start override (YYYY-MM-DD).")
    parser.add_argument("--to-date", help="Range end override (YYYY-MM-DD).")
    parser.add_argument(
        "--param",
        action="append",
        help="Extra report parameter as key=value (repeatable).",
    )
    parser.add_argument("--tenant", help="Organisation name, if more than one.")
    parser.add_argument("--output", help="Output CSV path.")
    parser.add_argument("--stdout", action="store_true", help="Print instead of write.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file.")
    args = parser.parse_args(argv)

    params = build_params(args)

    output_path = None
    if not args.stdout:
        if args.output:
            output_path = args.output
        elif args.period:
            output_path = f"inputs/{args.period}/{args.report.lower()}.csv"
        else:
            print(
                "ERROR: provide --output or --period (or use --stdout).",
                file=sys.stderr,
            )
            return 1
        if os.path.exists(output_path) and not args.force:
            print(
                f"ERROR: {output_path} already exists. Re-run with --force to "
                "overwrite, or use --output to write elsewhere.",
                file=sys.stderr,
            )
            return 1

    try:
        token, tenant_id = xero_client.connect(tenant_name=args.tenant)
        report_json = xero_client.get_report(token, tenant_id, args.report, params)
    except xero_client.XeroError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        title, fieldnames, records = report_parser.parse_report(report_json)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for record in records:
        writer.writerow({f: record.get(f, "") for f in fieldnames})
    csv_text = buffer.getvalue()

    if args.stdout:
        sys.stdout.write(csv_text)
        return 0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as handle:
        handle.write(csv_text)
    print(f"Wrote {len(records)} row(s) of '{title}' to {output_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
