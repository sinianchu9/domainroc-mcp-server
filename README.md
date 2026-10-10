# DomainRoc MCP Server — AI Domain Availability & USDT Price Lookup

[简体中文](README.zh-CN.md) · [Security](SECURITY.md) · [DomainRoc Domain Search](https://www.domainroc.com/en/domains)

> **Experimental · Read-only · No automated purchases**

An open-source **Model Context Protocol (MCP) server** that lets AI assistants check **domain name availability** and available **USDT registration quotes** using DomainRoc's existing public domain search API. No account credentials, registrar keys, checkout automation, or changes to DomainRoc's production code.

**AI-ready domain search, not AI-controlled domain purchases.** When others are debating whether to block AI agents, DomainRoc is experimenting with a bounded way to work with them.

## What it does

| MCP tool | Behavior |
| --- | --- |
| `check_domain(domain)` | Queries a single domain using DomainRoc's existing public read-only API; returns a confirmed status, an available first-year USDT quote if reliable, and the official website search URL. |

- Uses **the same public search route as the website**: `GET https://www.domainroc.com/api/public/domains/check?domain=...`.
- Availability is `available`, `unavailable`, or `unknown`. Blocked, restricted, manual-review, failed, and ambiguous results **must not be misrepresented as available**.
- `price_usdt` is a **preview**, not a binding checkout price. Recheck it at checkout.
- The `purchase_url` points to DomainRoc's domain search page, **not** a pre-filled order or payment session. Users manually search and buy on the official site.

## Quick start — local stdio

Python 3.11+:

```bash
git clone https://github.com/sinianchu9/domainroc-mcp-server.git
cd domainroc-mcp-server
python -m pip install -e .
domainroc-mcp
```

The process communicates over MCP **stdio**. It does not open a public port, and it normally prints nothing until an MCP client connects.

### Connect from an MCP-compatible AI client

Example client configuration (field names vary by client):

```json
{
  "mcpServers": {
    "domainroc": {
      "command": "domainroc-mcp",
      "args": []
    }
  }
}
```

Restart your MCP client, then ask:

> Check whether example.com is available through DomainRoc. If the quote is unavailable, say so; do not invent a price.

The example domain is illustrative, not a claim about live inventory. The client must support **local stdio MCP servers**; publishing this repository does **not** automatically make the tool discoverable in every AI app.

## Example response shape

```json
{
  "domain": "sample-project.com",
  "status": "unknown",
  "available": null,
  "price_usdt": null,
  "currency": "USDT",
  "purchase_url": "https://www.domainroc.com/en/domains",
  "checked_at": "2026-10-11T00:00:00+00:00",
  "cached": false,
  "reason": "upstream_unavailable",
  "note": "No confirmed availability or price. Search and checkout on the official website."
}
```

This is a **synthetic error-format example**, not a live search result.

## Guardrails / safety

- Only one tool; **no domain registration, ordering, USDT transfer, wallet action, DNS modification, or user session access**.
- Input must be a valid ASCII domain name (internationalized names can be supplied in their `xn--`/IDNA form); no arbitrary URLs.
- Fixed HTTPS host and endpoint; redirects and environment proxy inheritance disabled.
- Built-in **per-process** budget: max 5 outbound checks/minute, 200 checks/rolling 24h, at most 2 in-flight requests, and 45-second confirmed-result cache.
- 8-second network timeout; failures become `unknown`, never `available`.
- **Local stdio only** in this preview. The built-in budget is **not** a distributed abuse-prevention solution. Do not expose this server directly to the Internet without a separate authenticated gateway, shared quotas, logging, and security review.

See [SECURITY.md](SECURITY.md).

## Development and tests

```bash
python -m pip install -e ".[dev]"
pytest -q
```

Tests use HTTP mocks and never submit real registrations or payments.

## Why this exists

**Block AI or build with it?** DomainRoc's experimental answer is to allow narrowly scoped, verifiable, user-initiated AI-assisted domain search. Responsible access controls and opposition to abusive scraping are fully compatible with useful AI agents.

**English search topics:** domain MCP server, AI domain availability checker, domain registration API, domain price lookup, domain search for AI agents, USDT domain registration.

**中文关键词:** 域名查询 MCP、AI 域名查询、域名注册 API、USDT 购买域名、AI Agent 域名接口。

This is a technical demonstration, **not** a claim that DomainRoc offers autonomous AI domain purchasing.

## Links

- [DomainRoc — domain search and USDT checkout](https://www.domainroc.com/en/domains)
- [DomainRoc 中文域名查询](https://www.domainroc.com/zh/domains)
- [简体中文说明](README.zh-CN.md)
- [Repository SEO & release checklist](docs/SEO.md)

## License

[MIT](LICENSE). No affiliation with the Model Context Protocol maintainers is implied.
