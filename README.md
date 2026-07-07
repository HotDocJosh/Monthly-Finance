# Month-End Close — Claude Code Automation

Runs the monthly finance close (revenue share, prepayments, accruals, employee
provisions, other revenue, income tax provision) as a repeatable Claude Code
workflow. Claude prepares reconciliations and PROPOSED journals; a human
reviews and posts.

## One-time setup

1. Install Claude Code (see https://docs.claude.com/en/docs/claude-code/overview
   for the current install instructions) and open a terminal in this folder.
2. Run `claude` once here — it will pick up `CLAUDE.md` and the skills in
   `.claude/skills/` automatically. Type `/` to confirm you can see
   `/month-end-close` and the six task commands.
3. (Optional, recommended) Connect the Google Drive MCP connector so Claude can
   read the Prepayments Schedule Google Sheet directly instead of a CSV export.
   Run `/mcp` in Claude Code to manage connectors.
4. Review the thresholds and conventions in `CLAUDE.md` and adjust to your
   policies. Add your on-cost rates to `process/on_cost_rates.md`.
5. Recommended: initialise a git repo so each month's close is version-controlled.

## Monthly run (e.g. July 2026)

1. Create `inputs/2026-07/` and drop in the exports listed in `CLAUDE.md`
   (trial balance, revenue by partner, AP invoices, GRNI, leave balances, etc.).
2. Start Claude Code in this folder and run:

   /month-end-close 2026-07

3. Claude works through all six tasks in order, writing everything to
   `closes/2026-07/`:
   - a reconciliation/working paper per task
   - `journals.csv` — all proposed journals
   - `close-checklist.md` — status and items flagged for review
   - `close-summary.md` — key figures and month-on-month movements
4. Review the flagged items and journals, sign off the checklist, and post the
   approved journals to your accounting system.
5. For prepayments, paste `prepayments_schedule_updated.csv` back into the
   master Google Sheet (or let Claude update it via the Drive connector).

You can also run any task on its own, e.g. `/prepayments-recon 2026-07`.

## Running it hands-free

Once you trust the workflow, it can be run headlessly (e.g. from a scheduled
job on working day 2):

    claude -p "/month-end-close 2026-07"

Even when scheduled, keep the human review step — the skills are designed so
Claude never posts journals and always flags judgement calls.

## Folder structure

```
month-end-close/
├── CLAUDE.md                  # standing context: conventions, thresholds, rules
├── .claude/skills/            # the runnable commands
│   ├── month-end-close/       # /month-end-close YYYY-MM (full close)
│   ├── revenue-share/
│   ├── prepayments-recon/     # linked to the Prepayments Google Sheet
│   ├── accruals-recon/
│   ├── employee-provisions/
│   ├── other-revenue/
│   └── tax-provision/
├── process/                   # the process document + templates
├── inputs/YYYY-MM/            # monthly source exports (read-only)
└── closes/YYYY-MM/            # Claude's outputs each month
```
