# Month-End Close — Project Context

This repository automates our month-end finance close. The authoritative process
document is `process/month-end-close-process.md`. Always follow it.

## How this project works

- Each month, GL/system exports are dropped into `inputs/YYYY-MM/` (see
  "Expected input files" below).
- Running `/month-end-close YYYY-MM` executes every close task in order and
  writes all outputs to `closes/YYYY-MM/`.
- Individual tasks can be run standalone: `/revenue-share`, `/prepayments-recon`,
  `/accruals-recon`, `/employee-provisions`, `/other-revenue`, `/tax-provision`
  (each takes the period, e.g. `/prepayments-recon 2026-07`).

## Expected input files (in `inputs/YYYY-MM/`)

| File | Source | Used by |
|------|--------|---------|
| `trial_balance.csv` | GL export at month end | all tasks |
| `revenue_by_partner.csv` | Billing system | revenue-share |
| `revenue_share_rates.csv` | Maintained rate table (partner, rate %, effective date, contract ref) | revenue-share |
| `prepayments_schedule.csv` | Export of the Prepayments Schedule Google Sheet* | prepayments-recon |
| `ap_invoices.csv` | AP invoice listing for the month | prepayments-recon, accruals-recon |
| `open_pos_grni.csv` | Goods received not invoiced report | accruals-recon |
| `prior_accruals.csv` | Prior month accruals schedule | accruals-recon |
| `leave_balances.csv` | Payroll/HRIS leave report (employee, hours, pay rate) | employee-provisions |
| `payroll_summary.csv` | Payroll run summary for the month | employee-provisions |
| `bank_statements.csv` / interest schedules | Bank | other-revenue |
| `tax_adjustments.csv` | Permanent/temporary difference schedule | tax-provision |

*The master Prepayments Schedule lives in Google Sheets:
https://docs.google.com/spreadsheets/d/1uUPOHs479r5mX8DaaPJTRkyECb0IkFUcrYKwd8mqw7I/edit?gid=1072322654#gid=1072322654
If the Google Drive MCP connector is configured, read it directly from there;
otherwise use the CSV export in the inputs folder. After completing the
prepayments reconciliation, output the updated schedule so it can be pasted or
synced back to the Google Sheet.

## Conventions and thresholds

- Currency: AUD. Round journals to 2 decimal places.
- Prepayment capitalisation threshold: $500 and covering more than one month.
- Accrual estimation documentation required for items > $5,000.
- Variance investigation threshold: >1% or $1,000 (whichever is lower) for
  revenue share; explain P&L variances > $5,000 vs prior month.
- Employee on-costs: superannuation guarantee at the current statutory rate,
  plus payroll tax and workers' comp per the rates in
  `process/on_cost_rates.md` (verify statutory rates are current before use).
- Income tax: use the applicable Australian corporate rate; effective tax rate
  method monthly, full deferred tax computation quarterly.

## Output requirements (per task)

Write to `closes/YYYY-MM/`:
1. A reconciliation/working paper as CSV or XLSX (supporting balance vs GL,
   itemised, nil unexplained difference).
2. Proposed journal entries in `closes/YYYY-MM/journals.csv`
   (columns: date, journal ref, account code, account name, Dr, Cr, memo, task).
3. An entry in `closes/YYYY-MM/close-checklist.md` recording status,
   preparer (Claude), date, key figures, and any items needing human review.

## Hard rules

- NEVER post anything to an accounting system. All journals are PROPOSED and
  must be reviewed and posted by a human.
- If an expected input file is missing or looks wrong (empty, unbalanced trial
  balance, stale dates), STOP that task and flag it in the checklist rather
  than guessing.
- Flag every judgemental estimate (bonus provisions, aged accrual releases,
  uncertain tax positions) as "REQUIRES HUMAN REVIEW" in the checklist.
- Do not modify anything in `inputs/` — treat it as read-only source data.
