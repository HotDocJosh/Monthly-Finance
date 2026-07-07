---
name: employee-provisions
description: Calculate month-end employee provisions - annual leave, long service leave, bonus accruals and unpaid payroll with on-costs - reconcile to payroll reports and propose movement journals. Use for leave provisions, employee entitlements or payroll accrual tasks.
argument-hint: [YYYY-MM]
---

# Employee Provisions — period $ARGUMENTS

Follow section 4 of `process/month-end-close-process.md`.

## Steps
1. Load `inputs/$ARGUMENTS/leave_balances.csv` (per employee: leave hours,
   current pay rate) and `inputs/$ARGUMENTS/payroll_summary.csv`.
2. **Annual leave:** per employee, hours × rate × (1 + on-costs %). Use the
   on-cost rates in `process/on_cost_rates.md`; if that file is missing or the
   statutory rates may be stale, flag REQUIRES HUMAN REVIEW rather than
   guessing rates.
3. **Long service leave** (if data provided): update per policy; split
   current/non-current; flag assumption changes for review.
4. **Bonus provision:** accrue YTD per the scheme parameters in the inputs; if
   no scheme data is provided, carry the prior balance and flag for review —
   never invent performance assumptions.
5. **Payroll accruals:** unpaid days worked after the last pay run, plus super
   and payroll tax not yet remitted.
6. Compute movements vs prior month provisions (from prior close or trial
   balance) and explain significant changes (headcount, pay rises, leave taken).
7. Reconcile each provision balance to its calculation and to the payroll
   report.

## Outputs (to `closes/$ARGUMENTS/`)
1. `employee_provisions_workbook.csv` — per-employee leave calc plus summary
   tabs/sections for LSL, bonus and payroll accruals.
2. `employee_provisions_reconciliation.md` — balances, movements, explanations.
3. Append movement journals (Dr employee benefits expense / Cr each provision)
   to `journals.csv`; update the checklist. Bonus movements are always
   REQUIRES HUMAN REVIEW.
