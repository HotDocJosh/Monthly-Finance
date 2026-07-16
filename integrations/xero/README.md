# Xero integration (read-only)

Pulls source data for the month-end close directly from Xero instead of a
manual GL export. Today it fetches the **Trial Balance** — the input every
close task reconciles against — and writes it to `inputs/YYYY-MM/`.

> **Read-only by design.** These scripts only ever call Xero's *read* endpoints
> and request only read scopes. There is no code path that creates, updates,
> deletes, or posts anything in Xero. This mirrors the project hard rule:
> nothing is ever posted to an accounting system by automation — all journals
> stay PROPOSED for a human to review and post.

No third-party packages are required (Python 3.9+ standard library only).

## 1. Create a Xero Custom Connection

A [Custom Connection](https://developer.xero.com/documentation/guides/oauth2/custom-connections/)
is a machine-to-machine (client-credentials) app tied to a single organisation
— no interactive login, ideal for a scheduled close.

1. Sign in at <https://developer.xero.com/app/manage> and **New app → Custom
   connection**.
2. Select the organisation this close runs for.
3. Add these **read-only** scopes (and no others):
   - `accounting.reports.read`
   - `accounting.settings.read`
4. On the app's **Configuration** page, copy the **Client id** and generate a
   **Client secret**.
5. Have the organisation's authoriser accept the connection.

## 2. Set the credentials on the environment

Set these environment variables (do **not** commit them or paste secrets into
chat):

- `XERO_CLIENT_ID` = your Custom Connection **Client id**
- `XERO_CLIENT_SECRET` = your generated **Client secret**

For **Claude Code on the web**, add them in the environment's settings so every
session can read them. Locally, export them in your shell (e.g. via a
`.env` you keep untracked) before running the scripts.

## 3. Verify the connection

```bash
python integrations/xero/check_connection.py
```

Prints the connected organisation name on success (no secrets). A non-zero exit
means the credentials or scopes need attention.

## 4. Fetch the month-end Trial Balance

```bash
# Writes inputs/2026-07/trial_balance.csv as at 31 Jul 2026
python integrations/xero/fetch_trial_balance.py 2026-07
```

Useful options:

| Option | Effect |
|--------|--------|
| `--stdout` | Print the CSV instead of writing a file (safe preview). |
| `--force` | Overwrite an existing `trial_balance.csv`. |
| `--output PATH` | Write somewhere other than the default input path. |
| `--date YYYY-MM-DD` | Override the report date (defaults to month end). |
| `--tenant NAME` | Choose the org if the connection has more than one. |
| `--payments-only` | Cash (payments) basis instead of accruals. |

By default the fetcher **refuses to overwrite** an existing
`trial_balance.csv`, so it won't silently clobber a file already dropped into
`inputs/`. Use `--force` when you intend to refresh it.

Output columns:

```
account_code, account_name, account_type, debit, credit, ytd_debit, ytd_credit
```

`debit`/`credit` are the account balances as at the report date; `ytd_*` are the
year-to-date figures Xero returns alongside them.

## Extending

`xero_client.py` exposes `connect()` and `get_report(...)`. Other read-only
reports (e.g. `ProfitAndLoss`, `BalanceSheet`, `BankSummary`, `AgedPayables`)
can be fetched the same way — keep new scripts read-only and never add write
scopes.
