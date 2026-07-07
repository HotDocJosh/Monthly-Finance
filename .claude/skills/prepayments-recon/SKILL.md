---
name: prepayments-recon
description: Perform the monthly prepayments reconciliation - identify new prepayments from AP invoices, run monthly amortisation on the prepayments schedule, reconcile to the GL and propose journals. Use for prepayments, prepaid expenses or amortisation tasks at month end.
argument-hint: [YYYY-MM]
---

# Prepayments Reconciliation — period $ARGUMENTS

Follow section 2 of `process/month-end-close-process.md`.

## Source of truth
The master Prepayments Schedule is this Google Sheet:
https://docs.google.com/spreadsheets/d/1uUPOHs479r5mX8DaaPJTRkyECb0IkFUcrYKwd8mqw7I/edit?gid=1072322654#gid=1072322654

- If a Google Drive/Sheets MCP tool is available, read the schedule directly
  from the sheet.
- Otherwise use `inputs/$ARGUMENTS/prepayments_schedule.csv` (an export of the
  same sheet). If neither is available, STOP and flag it.

## Steps
1. Load the schedule. Expected columns: supplier, description, invoice ref,
   total amount, period start, period end, monthly amortisation, expense GL
   code, remaining balance.
2. Scan `inputs/$ARGUMENTS/ap_invoices.csv` for new items meeting the
   capitalisation threshold in CLAUDE.md ($500 and >1 month coverage). Add them
   to the schedule; list each addition explicitly for the reviewer.
3. Run the month's amortisation for every active item (pro-rate part months by
   days). Remove or mark complete any fully amortised items and confirm nil
   balances.
4. Reconcile the schedule's closing balance to the prepayments account in
   `inputs/$ARGUMENTS/trial_balance.csv`. Itemise any difference; the target is
   nil unexplained.
5. Flag stale items (no amortisation movement and past their period end, or
   supplier appears inactive) as REQUIRES HUMAN REVIEW — do not write anything
   off yourself.

## Outputs (to `closes/$ARGUMENTS/`)
1. `prepayments_schedule_updated.csv` — the rolled-forward schedule, formatted
   so it can be pasted back into the Google Sheet (same column order).
2. `prepayments_reconciliation.md` — GL balance vs schedule balance, itemised
   differences, new additions, fully amortised removals, stale items flagged.
3. Append amortisation journals (Dr expense GL codes / Cr Prepayments) to
   `journals.csv` and update `close-checklist.md`.
