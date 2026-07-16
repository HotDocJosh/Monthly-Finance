# Xero MCP Connector — Setup Notes

Notes on connecting Xero as an MCP connector so the month-end close can read
data directly from the accounting system instead of (or alongside) the CSV
exports in `inputs/YYYY-MM/`.

> Status as of last review (2026-07): **No Xero connector is configured** on
> this account, and none is enabled in this session. The close currently runs
> entirely off the CSV exports listed in `CLAUDE.md`, plus the Prepayments
> Schedule via the Google Drive connector. These notes are a plan for adding
> Xero, not a description of a live integration.

## Why connect Xero

Today every task reads a CSV that was exported from the GL or a subsystem. A
Xero connector could let Claude pull the same data live, reducing manual export
steps and stale-data risk. Rough mapping of what it could replace:

| Current CSV input | Xero source it could come from |
|-------------------|-------------------------------|
| `trial_balance.csv` | Trial Balance report |
| `ap_invoices.csv` | Accounts Payable / bills |
| `open_pos_grni.csv` | Purchase orders / bills awaiting receipt* |
| `bank_statements.csv` | Bank transactions / statement lines |
| Account balances for each recon | General Ledger / account transactions |

\*GRNI often lives outside Xero (in a procurement system), so this one may still
need a manual export — verify before relying on it.

Revenue-by-partner, payroll/leave, and tax-difference schedules generally come
from other systems (billing, payroll/HRIS, tax workpapers) and would **not** be
sourced from Xero even after connecting it.

## How to add it

MCP connectors can only be authorized from an **interactive** session — the
OAuth flow can't run in a headless/remote session like the ones that run the
scheduled close.

1. **Find a Xero MCP server.** Xero is not currently a first-party connector in
   the Anthropic directory. Options:
   - A third-party or community Xero MCP server, or
   - A custom MCP server your team hosts that wraps the Xero API.
   Confirm the server is reputable and that its scopes are appropriate before
   connecting (see Security below).
2. **Connect it:**
   - **claude.ai / Claude Desktop:** add it under **Settings → Connectors**
     (an org admin may need to add org-level connectors). Then enable it for the
     chat/session where the close runs.
   - **Claude Code (CLI):** run `/mcp` in an interactive session, or configure
     it via `claude mcp add`. See the Claude Code MCP docs for the current
     syntax.
3. **Authorize (OAuth).** Complete the Xero login/consent flow in the browser.
   Xero uses per-organisation authorization, so make sure you connect the
   correct Xero organisation (entity) for this close.
4. **Verify it's live.** In the session, confirm the Xero tools appear and are
   enabled (in Claude Code, `/mcp` lists connected servers; on claude.ai, check
   the connector is toggled on for the chat, not just installed).

## Using it in the close

- Prefer **read-only** access. This workflow's hard rule is that Claude never
  posts to an accounting system — all journals are PROPOSED and posted by a
  human. A read-only Xero connection enforces that at the permission layer.
- Keep the CSV inputs as a **fallback**. Mirror the pattern already used for the
  Prepayments Schedule in `CLAUDE.md`: "if the connector is configured, read it
  directly; otherwise use the CSV export." If Xero is unavailable mid-close, the
  task should fall back to the CSV rather than stopping.
- After connecting, update `CLAUDE.md` (the "Expected input files" table and the
  conventions section) to note which inputs come from Xero live vs CSV, so the
  source of truth for each task is unambiguous.

## Security / governance

- **Scopes:** grant read-only accounting scopes only. Do not grant any scope
  that allows creating or posting transactions/journals.
- **Right entity:** connect the correct Xero organisation; a wrong-org
  connection could silently pull the wrong numbers.
- **Access reviews:** treat the Xero connection like any other system access —
  review who can use it and revoke when no longer needed.
- **Headless runs:** scheduled/headless closes can't complete OAuth. Either run
  the close interactively when Xero data is needed, or keep the CSV export step
  for automated runs.

## Current fallback (no connector)

Until Xero is connected, nothing changes: drop the CSV exports into
`inputs/YYYY-MM/` per `CLAUDE.md` and run the close as normal. The Prepayments
Schedule can still be read live via the Google Drive connector.
