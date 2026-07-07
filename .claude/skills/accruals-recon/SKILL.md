---
name: accruals-recon
description: Perform the monthly accrued expenses reconciliation - reverse prior accruals, identify current month accruals from GRNI and recurring costs, reconcile to the GL and review accrual accuracy and aged items. Use for accruals or accrued expenses tasks.
argument-hint: [YYYY-MM]
---

# Accrued Expenses Reconciliation — period $ARGUMENTS

Follow section 3 of `process/month-end-close-process.md`.

## Steps
1. Load `inputs/$ARGUMENTS/prior_accruals.csv`. For each prior accrual, check
   `inputs/$ARGUMENTS/ap_invoices.csv` for the matching invoice: mark as
   invoiced (reverse), carry forward, or flag if aged (>3 months) with no
   invoice — aged releases are REQUIRES HUMAN REVIEW, never release them
   yourself.
2. Build current month accruals from:
   - `inputs/$ARGUMENTS/open_pos_grni.csv` (goods/services received not invoiced)
   - Recurring items in prior months' schedules not yet invoiced this month
     (utilities, rent, professional fees, contractors, interest)
   - Any late invoices in `ap_invoices.csv` dated after cut-off but relating to
     this period
3. Document the basis of estimate for every accrual > $5,000.
4. Accrual accuracy check: compare last month's accruals to actual invoices now
   received; report items with >20% variance so estimates can be improved.
5. Reconcile the accruals schedule total to the accrued expenses account in
   `trial_balance.csv`; itemise differences, target nil unexplained.

## Outputs (to `closes/$ARGUMENTS/`)
1. `accruals_schedule.csv` — supplier/description, basis of estimate, amount,
   expense GL code, expected invoice date, status (new/carried/reversed/aged).
2. `accruals_reconciliation.md` — GL vs schedule, accuracy review, aged items.
3. Append journals (reversals and new accruals: Dr expense / Cr accrued
   expenses) to `journals.csv`; update the checklist.
