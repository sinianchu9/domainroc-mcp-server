"""Authenticated account tools. Credentials remain in the local process environment."""
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation

import httpx

SITES = {"domainroc": "https://www.domainroc.com", "namepopo": "https://www.namepopo.com"}


def site_url() -> str:
    site = os.environ.get("DOMAINROC_SITE", "domainroc")
    if site not in SITES:
        raise ValueError("unsupported_site")
    return SITES[site]


async def account_call(action: str, *, transport=None, **fields) -> dict:
    token = os.environ.get("DOMAINROC_AGENT_TOKEN", "")
    if not token.startswith("droc_") or len(token) > 100 or any(c.isspace() for c in token):
        return {"error": "connection_required", "message": "Connect your assistant from your account's Agent MCP page."}
    try:
        base = site_url()
    except ValueError:
        return {"error": "unsupported_site"}
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=False, trust_env=False, transport=transport) as client:
            response = await client.post(base + "/api/agent/call", json={"action": action, **fields}, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
        if not response.is_success:
            # Never return upstream exception bodies, which may contain operational data.
            return {"error": {401: "connection_expired", 403: "permission_required", 409: "request_conflict", 422: "invalid_request", 429: "try_later", 503: "service_paused"}.get(response.status_code, "service_unavailable"), "status": response.status_code, "message": "Review your assistant permissions or continue in your account dashboard. For a recharge retry, reuse the same request_id."}
        if len(response.content) > 524288:
            return {"error": "invalid_response"}
        payload = response.json()
        return payload if isinstance(payload, dict) else {"error": "invalid_response"}
    except (httpx.HTTPError, ValueError):
        return {"error": "service_unavailable", "message": "The result could not be confirmed. Retry a recharge with the same request_id; do not create another request."}


def register_account_tools(mcp):
    read = {"readOnlyHint": True, "openWorldHint": False}

    @mcp.tool(annotations=read)
    async def get_wallet() -> dict:
        """View available and reserved USDT balance. Requires account permission."""
        return await account_call("wallet")

    @mcp.tool(annotations=read)
    async def list_transactions(limit: int = 20, offset: int = 0) -> dict:
        """View your wallet transactions; page with limit (1–100) and offset."""
        return await account_call("transactions", limit=limit, offset=offset)

    @mcp.tool(annotations=read)
    async def list_domains(limit: int = 20, offset: int = 0) -> dict:
        """View your domains, expiration dates and renewal preferences. Requires domains permission."""
        return await account_call("domains", limit=limit, offset=offset)

    @mcp.tool(annotations=read)
    async def list_orders(limit: int = 20, offset: int = 0) -> dict:
        """Track your domain orders and payments. Requires orders permission."""
        return await account_call("orders", limit=limit, offset=offset)

    @mcp.tool(annotations=read)
    async def list_monitors(limit: int = 20, offset: int = 0) -> dict:
        """View your domain monitoring results and paid service expiry. Requires monitoring permission."""
        return await account_call("monitoring", limit=limit, offset=offset)

    @mcp.tool(annotations=read)
    async def get_payment_methods() -> dict:
        """List supported USDT payment networks before creating a recharge. Requires account permission."""
        return await account_call("payment_methods")

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False})
    async def create_recharge(amount_usdt: str, payment_method: str, request_id: str) -> dict:
        """Create a USDT recharge checkout after the user chooses amount and network.

        Requires recharge permission. The user completes payment; this tool cannot
        transfer money or credit a balance. Use a unique 8–64 character request_id
        (letters, numbers, underscore, hyphen) per intended recharge and reuse it
        on every retry, including after timeouts. Never claim payment until credited_at.
        """
        try:
            amount = Decimal(amount_usdt)
            if not amount.is_finite() or not 1 <= amount <= 100000 or amount.as_tuple().exponent < -6:
                raise ValueError
        except (InvalidOperation, ValueError):
            return {"error": "invalid_amount"}
        return await account_call("recharge", amount_usdt=str(amount), payment_method=payment_method, request_id=request_id)

    @mcp.tool(annotations=read)
    async def get_recharge(recharge_no: str) -> dict:
        """Check one of your recharge orders. Only credited_at confirms balance credit."""
        return await account_call("recharge_status", recharge_no=recharge_no)
