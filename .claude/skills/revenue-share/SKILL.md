---
name: revenue-share
description: Calculate and update partner revenue share for the month - apply contractual rates to gross revenue by partner, propose the accrual journal and reconcile the revenue share payable account. Use for revenue share, partner share or rev share tasks.
argument-hint: [YYYY-MM]
---

# Update Revenue Share — period $ARGUMENTS

Follow section 1 of `process/month-end-close-process.md`.

## Steps
1. Load `inputs/$ARGUMENTS/revenue_by_partner.csv` (gross revenue by partner)
   and `inputs/$ARGUMENTS/revenue_share_rates.csv` (partner, rate %, effective
   date, contract ref, any tiers/minimum guarantees).
2. Check for rate changes effective this month and call them out explicitly.
3. Calculate the month's revenue share per partner: gross revenue × applicable
   rate, applying any tiers or minimum guarantees. Show the calculation per
   partner.
4. If partner statements are present in the inputs folder, agree the calculated
   share to each statement; flag variances above the threshold in CLAUDE.md as
   REQUIRES HUMAN REVIEW.
5. Reconcile the revenue share payable account: opening balance (prior close or
   trial balance) + this month's accrual − payments in the period = closing
   balance per `trial_balance.csv`.

## Outputs (to `closes/$ARGUMENTS/`)
1. `revenue_share_schedule.csv` — per partner: gross revenue, rate, contract
   ref, share amount, statement variance if applicable.
2. `revenue_share_reconciliation.md` — payable account roll-forward.
3. Append the accrual journal (Dr revenue share expense or contra-revenue per
   policy / Cr revenue share payable) to `journals.csv`; update the checklist.
