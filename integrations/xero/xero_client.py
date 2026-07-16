"""Read-only Xero API client for the month-end close.

This module authenticates to Xero using a **Custom Connection** (OAuth 2.0
client-credentials grant) and exposes helpers to read reports and settings.

READ-ONLY BY DESIGN
-------------------
Every request this module makes is a GET, except the single OAuth token POST
to Xero's identity server (which creates nothing in the accounting ledger).
It only ever requests read scopes and there is no code path that creates,
updates, deletes, or posts anything in Xero. This mirrors the project's hard
rule: nothing is ever posted to an accounting system by automation.

Credentials
-----------
The client reads two environment variables (never hard-coded, never logged):

    XERO_CLIENT_ID       Custom Connection "Client id"
    XERO_CLIENT_SECRET   Custom Connection "Client secret"

Set these on the environment (for Claude Code on the web, in the environment's
settings). See integrations/xero/README.md for the full setup.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

TOKEN_URL = "https://identity.xero.com/connect/token"
CONNECTIONS_URL = "https://api.xero.com/connections"
API_BASE = "https://api.xero.com/api.xro/2.0"

# Read-only scopes only. Do not add write scopes (e.g. accounting.transactions)
# — this integration must never be able to modify the ledger.
DEFAULT_SCOPES = "accounting.reports.read accounting.settings.read"

_TIMEOUT = 60  # seconds


class XeroError(Exception):
    """Raised for any Xero authentication or API failure."""


def credentials_from_env() -> tuple[str, str]:
    """Return (client_id, client_secret) from the environment.

    Raises a clear, secret-free error if either variable is missing.
    """
    client_id = os.environ.get("XERO_CLIENT_ID", "").strip()
    client_secret = os.environ.get("XERO_CLIENT_SECRET", "").strip()
    missing = [
        name
        for name, value in (
            ("XERO_CLIENT_ID", client_id),
            ("XERO_CLIENT_SECRET", client_secret),
        )
        if not value
    ]
    if missing:
        raise XeroError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ". Set your Xero Custom Connection credentials on the environment "
            "(see integrations/xero/README.md)."
        )
    return client_id, client_secret


def get_access_token(
    client_id: str, client_secret: str, scopes: str = DEFAULT_SCOPES
) -> str:
    """Exchange client credentials for a short-lived access token.

    Uses the OAuth 2.0 client-credentials grant, as required by Xero Custom
    Connections. The credentials are sent via HTTP Basic auth and are never
    written to logs or disk.
    """
    body = urllib.parse.urlencode(
        {"grant_type": "client_credentials", "scope": scopes}
    ).encode("utf-8")
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode(
        "ascii"
    )
    request = urllib.request.Request(
        TOKEN_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Surface Xero's error description but never echo the credentials.
        detail = _safe_error_detail(exc)
        raise XeroError(
            f"Token request failed ({exc.code}). {detail} "
            "Check the Client id/secret and that the Custom Connection is active."
        ) from None
    except urllib.error.URLError as exc:
        raise XeroError(f"Could not reach Xero identity server: {exc.reason}") from None

    token = payload.get("access_token")
    if not token:
        raise XeroError("Xero did not return an access token.")
    return token


def get_tenants(access_token: str) -> list[dict[str, Any]]:
    """Return the list of Xero organisations this connection can access.

    A Custom Connection is tied to exactly one organisation, so this normally
    returns a single entry.
    """
    return _get(CONNECTIONS_URL, access_token)


def resolve_tenant_id(access_token: str, tenant_name: str | None = None) -> str:
    """Return the tenant (organisation) id to use for API calls.

    If ``tenant_name`` is given, match it case-insensitively against the
    connected organisations; otherwise return the sole connection.
    """
    tenants = get_tenants(access_token)
    if not tenants:
        raise XeroError(
            "No Xero organisations are connected to this Custom Connection."
        )
    if tenant_name:
        wanted = tenant_name.strip().lower()
        for tenant in tenants:
            if (tenant.get("tenantName") or "").strip().lower() == wanted:
                return tenant["tenantId"]
        names = ", ".join(t.get("tenantName", "?") for t in tenants)
        raise XeroError(
            f"No connected organisation named {tenant_name!r}. Available: {names}."
        )
    if len(tenants) > 1:
        names = ", ".join(t.get("tenantName", "?") for t in tenants)
        raise XeroError(
            "Multiple organisations are connected; pass --tenant to choose one. "
            f"Available: {names}."
        )
    return tenants[0]["tenantId"]


def get_report(
    access_token: str,
    tenant_id: str,
    report: str,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Fetch a Xero accounting report (e.g. ``TrialBalance``) as parsed JSON."""
    url = f"{API_BASE}/Reports/{report}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    return _get(url, access_token, tenant_id)


def connect(
    tenant_name: str | None = None, scopes: str = DEFAULT_SCOPES
) -> tuple[str, str]:
    """Convenience: read env creds, authenticate, resolve tenant.

    Returns (access_token, tenant_id).
    """
    client_id, client_secret = credentials_from_env()
    token = get_access_token(client_id, client_secret, scopes)
    tenant_id = resolve_tenant_id(token, tenant_name)
    return token, tenant_id


def _get(
    url: str, access_token: str, tenant_id: str | None = None
) -> Any:
    """Issue a read-only GET request and return parsed JSON."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    if tenant_id:
        headers["Xero-tenant-id"] = tenant_id
    request = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = _safe_error_detail(exc)
        raise XeroError(f"Xero API request failed ({exc.code}). {detail}") from None
    except urllib.error.URLError as exc:
        raise XeroError(f"Could not reach the Xero API: {exc.reason}") from None


def _safe_error_detail(exc: urllib.error.HTTPError) -> str:
    """Extract a human-readable message from a Xero error response."""
    try:
        payload = json.loads(exc.read().decode("utf-8"))
    except Exception:
        return ""
    for key in ("error_description", "Detail", "Message", "error"):
        value = payload.get(key)
        if value:
            return str(value)
    return ""
