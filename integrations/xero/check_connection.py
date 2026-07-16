#!/usr/bin/env python3
"""Verify the Xero Custom Connection works (read-only).

Usage:
    python integrations/xero/check_connection.py

Reads XERO_CLIENT_ID / XERO_CLIENT_SECRET from the environment, requests a
token, and lists the connected organisation(s). Prints no secrets. Exit code 0
means the credentials and scopes are working.
"""

from __future__ import annotations

import sys

import xero_client


def main() -> int:
    try:
        client_id, client_secret = xero_client.credentials_from_env()
        token = xero_client.get_access_token(client_id, client_secret)
        tenants = xero_client.get_tenants(token)
    except xero_client.XeroError as exc:
        print(f"NOT CONNECTED: {exc}", file=sys.stderr)
        return 1

    if not tenants:
        print(
            "Authenticated, but no organisation is connected to this Custom "
            "Connection. Add an organisation in the Xero developer portal.",
            file=sys.stderr,
        )
        return 1

    print("Xero connection OK. Connected organisation(s):")
    for tenant in tenants:
        name = tenant.get("tenantName", "?")
        tenant_type = tenant.get("tenantType", "")
        print(f"  - {name} ({tenant_type})" if tenant_type else f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
