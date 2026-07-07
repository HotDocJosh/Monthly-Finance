---
name: other-revenue
description: Recognise other revenue for the month - interest income accruals, sublease or rental income, grants and sundry items - with correct-period recognition and variance commentary. Use for other revenue, interest income or grant recognition tasks.
argument-hint: [YYYY-MM]
---

# Other Revenue — period $ARGUMENTS

Follow section 5 of `process/month-end-close-process.md`.

## Steps
1. Load `inputs/$ARGUMENTS/bank_statements.csv` and any interest/term deposit
   schedules, sublease agreements or grant documentation in the inputs folder.
2. **Interest income:** accrue interest earned but not yet credited (balance ×
   rate × days). Show the calculation per account/deposit.
3. **Grants/rebates:** only recognise where the documentation shows conditions
   are met; otherwise propose deferral and flag REQUIRES HUMAN REVIEW.
4. **Sundry items:** agree each to its supporting document; anything without
   support is flagged, not recognised.
5. Reconcile related accrued income / deferred income accounts to
   `trial_balance.csv`.
6. Variance commentary: other revenue vs prior month (and budget if provided);
   explain movements above the CLAUDE.md threshold.

## Outputs (to `closes/$ARGUMENTS/`)
1. `other_revenue_schedule.csv` — item, category, basis, amount, support ref.
2. `other_revenue_notes.md` — recognition treatment and variance commentary.
3. Append journals (Dr cash/receivable/accrued income / Cr other revenue by
   category) to `journals.csv`; update the checklist.
