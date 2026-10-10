"""Single-tool, local-stdio MCP adapter for DomainRoc's public domain search."""

from __future__ import annotations

import asyncio
import re
import time
from collections import deque
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx
from mcp.server.fastmcp import FastMCP

API_URL = "https://www.domainroc.com/api/public/domains/check"
PURCHASE_URL = "https://www.domainroc.com/en/domains"
DOMAIN_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
MAX_REQUESTS_PER_MINUTE = 5
MAX_REQUESTS_PER_DAY = 200
CACHE_SECONDS = 45

mcp = FastMCP(
    "DomainRoc Domain Search",
    instructions=(
        "Experimental read-only domain lookup. Never claim a domain is available "
        "when status is unknown. Price is a non-binding preview; purchases require "
        "the user to use the official DomainRoc website."
    ),
)


def normalize_domain(value: str) -> str:
    """Validate a DNS name; never accept URLs or caller-supplied upstream hosts."""
    if not isinstance(value, str):
        raise ValueError("invalid_domain")
    name = value.strip().lower().removesuffix(".")
    if not 3 <= len(name) <= 253 or not name.isascii():
        raise ValueError("invalid_domain")
    labels = name.split(".")
    if len(labels) < 2 or any(not DOMAIN_LABEL.fullmatch(label) for label in labels):
        raise ValueError("invalid_domain")
    if len(labels[-1]) < 2 or labels[-1].isdigit():
        raise ValueError("invalid_domain")
    return name


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_quote(payload: dict) -> str | None:
    """Read only the known first-year USDT total, never synthesize a price."""
    price = payload.get("price")
    if not isinstance(price, dict):
        return None
    value = price.get("total_usdt")
    if not isinstance(value, (str, int, float, Decimal)) or isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        return None
    if not amount.is_finite() or amount < 0:
        return None
    return str(amount)


def result(
    domain: str,
    status: str = "unknown",
    *,
    price_usdt: str | None = None,
    reason: str | None = None,
    checked_at: str | None = None,
    cached: bool = False,
) -> dict:
    return {
        "domain": domain,
        "status": status,
        "available": True if status == "available" else False if status == "unavailable" else None,
        "price_usdt": price_usdt if status == "available" else None,
        "currency": "USDT",
        "purchase_url": PURCHASE_URL,
        "checked_at": checked_at or timestamp(),
        "cached": cached,
        "reason": reason,
        "note": (
            "Preview only; availability and price must be reconfirmed at official checkout."
            if status == "available"
            else "No confirmed availability or price. Search and checkout on the official website."
            if status == "unknown"
            else "This domain was reported taken. Check on the official website for updates."
        ),
    }


def interpret(domain: str, payload: object) -> dict:
    """Fail closed for malformed, blocked, restricted, or manual-review results."""
    if not isinstance(payload, dict):
        return result(domain, reason="invalid_upstream_response")
    reported_domain = payload.get("domain")
    if not isinstance(reported_domain, str) or reported_domain.lower() != domain:
        return result(domain, reason="invalid_upstream_response")
    state = payload.get("status")
    available = payload.get("available")
    flow = payload.get("flow")
    if state == "taken" and available is False:
        return result(domain, status="unavailable", reason="taken")
    if state in ("available", "premium") and available is True and flow == "instant":
        quote = safe_quote(payload)
        return result(
            domain,
            status="available",
            price_usdt=quote,
            reason="premium" if state == "premium" else None,
        )
    reason = state if state in ("restricted", "blocked", "unknown", "premium") else "requires_review"
    return result(domain, reason=reason)


class DomainChecker:
    """Process-local limits and cache. This is NOT a public Internet gateway."""

    def __init__(self) -> None:
        self._minute: deque[float] = deque()
        self._day: deque[float] = deque()
        self._cache: dict[str, tuple[float, dict]] = {}
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(2)

    async def check(
        self, domain: str, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> dict:
        try:
            domain = normalize_domain(domain)
        except ValueError:
            return result(str(domain)[:253], reason="invalid_domain")

        now = time.monotonic()
        async with self._lock:
            entry = self._cache.get(domain)
            if entry is not None and entry[0] > now:
                return {**entry[1], "cached": True}
            while self._minute and self._minute[0] <= now - 60:
                self._minute.popleft()
            while self._day and self._day[0] <= now - 86400:
                self._day.popleft()
            if (
                len(self._minute) >= MAX_REQUESTS_PER_MINUTE
                or len(self._day) >= MAX_REQUESTS_PER_DAY
            ):
                return result(domain, reason="rate_limited")
            self._minute.append(now)
            self._day.append(now)

        async with self._semaphore:
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(8.0),
                    follow_redirects=False,
                    trust_env=False,
                    transport=transport,
                ) as client:
                    response = await client.get(
                        API_URL,
                        params={"domain": domain},
                        headers={"Accept": "application/json", "User-Agent": "domainroc-mcp/0.1.0"},
                    )
                    response.raise_for_status()
                    if response.headers.get("content-type", "").split(";")[0].strip() != "application/json":
                        return result(domain, reason="invalid_upstream_response")
                    if len(response.content) > 131072:
                        return result(domain, reason="invalid_upstream_response")
                    checked = interpret(domain, response.json())
            except (httpx.HTTPError, ValueError):
                return result(domain, reason="upstream_unavailable")

        if checked["status"] in ("available", "unavailable"):
            async with self._lock:
                self._cache[domain] = (time.monotonic() + CACHE_SECONDS, checked)
        return checked


_checker = DomainChecker()


@mcp.tool()
async def check_domain(domain: str) -> dict:
    """Check a single domain's confirmed availability and first-year USDT preview price.

    Input: a fully-qualified DNS domain, e.g. example.com (IDN in xn-- ASCII form).
    Returns unknown if upstream fails, restricts the domain, or requires manual review.
    Does not create orders, charge accounts, or register domains.
    """
    return await _checker.check(domain)


def main() -> None:
    """Run only as a locally launched stdio MCP service."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
