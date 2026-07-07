---
name: tax-provision
description: Calculate the monthly income tax provision - YTD taxable income with permanent and temporary difference adjustments, current month tax expense, provision account roll-forward and effective tax rate reconciliation. Use for income tax, tax provision or ETR tasks. Must run after all other P&L journals.
argument-hint: [YYYY-MM]
disable-model-invocation: true
---

# Income Tax Provision — period $ARGUMENTS

Follow section 6 of `process/month-end-close-process.md`.

**Precondition:** all other close tasks for $ARGUMENTS must be complete, since
this calculation depends on profit before tax including their journals. If any
P&L-affecting task is incomplete or BLOCKED, stop and flag it.

## Steps
1. Compute YTD profit before tax: trial balance P&L plus all proposed journals
   in `closes/$ARGUMENTS/journals.csv`.
2. Apply adjustments from `inputs/$ARGUMENTS/tax_adjustments.csv` (permanent
   differences, temporary differences). If the file is missing, use only the
   prior month's known recurring adjustments and flag REQUIRES HUMAN REVIEW.
3. Calculate YTD tax expense at the applicable Australian corporate rate
   (confirm the correct rate — base rate entity vs standard — from CLAUDE.md or
   inputs; if unclear, flag rather than assume). Current month expense = YTD
   less previously recognised.
4. Roll forward the provision for income tax: opening + provision − PAYG
   instalments/payments (agree payments to bank statements) = closing per
   `trial_balance.csv`.
5. Effective tax rate reconciliation: tax expense ÷ profit before tax;
   explain deviation from the statutory rate.
6. Deferred tax: monthly under the ETR method; in quarter-end months, prepare
   the full temporary difference computation and DTA recoverability note.
   Uncertain tax positions are always REQUIRES HUMAN REVIEW.

## Outputs (to `closes/$ARGUMENTS/`)
1. `tax_computation.md` — full computation, ETR reconciliation, provision
   roll-forward.
2. Append the tax journal (Dr income tax expense / Cr provision for income tax,
   plus deferred tax movements) to `journals.csv`; update the checklist noting
   CFO approval is required before posting.
