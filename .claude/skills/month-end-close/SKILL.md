---
name: month-end-close
description: Run the full month-end finance close for a given period. Executes revenue share, prepayments, accruals, employee provisions, other revenue and income tax provision in order, producing reconciliations, proposed journals and a close checklist. Use when asked to run, start or complete the month-end close.
argument-hint: [YYYY-MM]
disable-model-invocation: true
---

# Month-End Close — Full Run

Run the complete month-end close for period **$ARGUMENTS**.

## Setup
1. Read `process/month-end-close-process.md` in full.
2. Verify `inputs/$ARGUMENTS/` exists and list its contents against the
   "Expected input files" table in CLAUDE.md. Report anything missing before
   proceeding.
3. Create `closes/$ARGUMENTS/` and initialise `close-checklist.md` from
   `process/checklist-template.md`, and an empty `journals.csv` with headers:
   `date,journal_ref,account_code,account_name,dr,cr,memo,task`.

## Execute tasks in this order
Run each task per its skill instructions, appending journals and checklist
entries as you go:
1. **Revenue share** — follow `/revenue-share`
2. **Other revenue** — follow `/other-revenue`
3. **Prepayments reconciliation** — follow `/prepayments-recon`
4. **Accrued expenses reconciliation** — follow `/accruals-recon`
5. **Employee provisions** — follow `/employee-provisions`
6. **Income tax provision** — follow `/tax-provision` (must run LAST, after all
   other P&L journals, since it depends on profit before tax)

If a task cannot complete (missing/bad data), mark it BLOCKED in the checklist
with the reason and continue with independent tasks, but do NOT run the tax
provision unless all P&L-affecting tasks completed.

## Wrap up
1. Verify `journals.csv` balances (total Dr = total Cr per journal ref).
2. Produce `closes/$ARGUMENTS/close-summary.md`: key balances, total proposed
   journals by task, month-on-month movements vs `closes/<prior period>/` if it
   exists, and a consolidated list of all items flagged REQUIRES HUMAN REVIEW.
3. Print a short summary in chat: what completed, what's blocked, what needs
   review, and the exact files the reviewer should open.

Remember the hard rules in CLAUDE.md: propose journals only, never fabricate
missing data, flag all judgement calls.
