# Xero MCP connector setup

This repo is configured to use the official [Xero MCP server](https://github.com/XeroAPI/xero-mcp-server)
(`@xeroapi/xero-mcp-server`) so Claude Code can read data directly from Xero
(trial balance, invoices, contacts, etc.) instead of relying only on the CSV
drops in `inputs/YYYY-MM/`.

The server is registered in `.mcp.json` at the repo root and is launched on
demand via `npx` — there is no dependency to install into a `package.json`.

## Credentials (required)

The server authenticates with a Xero **Custom Connection** (machine-to-machine
OAuth2). You must create one and provide its credentials as environment
variables — **never commit them**.

1. In the [Xero Developer portal](https://developer.xero.com/app/manage), create
   a new app of type **Custom Connection**.
2. Grant it the scopes you need (e.g. `accounting.transactions.read`,
   `accounting.reports.read`, `accounting.contacts.read`).
3. Authorise the connection against the correct Xero organisation.
4. Copy the generated **Client ID** and **Client Secret**.

Then export them into the environment where Claude Code runs:

```sh
export XERO_CLIENT_ID="your-client-id"
export XERO_CLIENT_SECRET="your-client-secret"
```

The server reads `XERO_CLIENT_ID` and `XERO_CLIENT_SECRET` (and optionally
`XERO_CLIENT_BEARER_TOKEN` / `XERO_SCOPES`). The `.mcp.json` file references the
two variables above via `${...}` substitution, so no secrets live in the repo.

## Enabling the server in Claude Code

Project-scoped MCP servers require approval the first time. In an interactive
session run `/mcp` (or restart Claude Code) and approve the `xero` server. Once
approved, its tools appear as `mcp__xero__*`.

## Verifying

With the env vars set, you can confirm the server starts:

```sh
npx -y @xeroapi/xero-mcp-server
```

It should start and wait on stdio rather than exiting with
"Environment Variables not set".

## Notes

- All access should remain **read-only** for the close process. Per the project
  hard rules, nothing is ever posted to an accounting system — Xero data is used
  as a source, and all journals stay PROPOSED for human review.
