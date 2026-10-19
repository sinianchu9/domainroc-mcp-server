# DomainRoc Agent MCP

[简体中文](README.zh-CN.md) · [Security](SECURITY.md)

Connect an MCP-compatible AI assistant to domain search and your authorized account services. Public domain search works without an account. Account services require a connection key created in **Dashboard → Agent MCP** on a site running the account-service update.

| Tool | What you can do | Permission |
| --- | --- | --- |
| `check_domain` | Check domain availability and a first-year USDT price preview | Public |
| `get_wallet` | View available and reserved balance | Balance and billing |
| `list_transactions` | View wallet transactions | Balance and billing |
| `list_domains` | View your domains, expiry and renewal preferences | Domains |
| `list_orders` | Track domain orders and payments | Orders |
| `list_monitors` | View monitoring results and service expiry | Monitoring |
| `get_payment_methods` | View available USDT payment networks | Balance and billing |
| `create_recharge` | Create a recharge checkout | Recharge |
| `get_recharge` | Track your recharge and balance credit | Recharge |

Recharges require the user to pay at checkout. These tools cannot transfer funds, withdraw, buy or renew domains, change DNS, or grant permissions. Confirm purchases and service changes on the official website. Prices from public search are previews, not checkout commitments.

## Connect your assistant

Python 3.11+:

```sh
python -m pip install git+https://github.com/sinianchu9/domainroc-mcp-server.git
```

1. Open your account's **Agent MCP** page.
2. Choose the permissions and expiry (up to 90 days), then create a connection key. Recharge is optional.
3. Copy the provided settings into an AI client that supports local MCP servers. The key is shown once; do not paste it into chat or commit it to a repository.

```json
{
  "mcpServers": {
    "domainroc": {
      "command": "domainroc-mcp",
      "env": {
        "DOMAINROC_SITE": "domainroc",
        "DOMAINROC_AGENT_TOKEN": "YOUR_CONNECTION_KEY"
      }
    }
  }
}
```

Use `DOMAINROC_SITE=namepopo` for a **separate Namepopo account and connection key**. Only these two fixed HTTPS destinations are accepted. Never reuse a connection key across sites. To use public search alone, omit `DOMAINROC_AGENT_TOKEN`.

Examples: “When do my domains expire?”, “Show my available USDT balance”, “Create a 20 USDT recharge using the network I selected.”

Client setup varies. This repository provides a local stdio MCP server; it does not register automatically in AI products or expose a public port. Account functions require the new backend migration and routes to have been deployed on the chosen site; a local test does not establish production availability.

## Recharge reliability

Select a supported network using `get_payment_methods`, obtain the user's choice of amount and network, then call `create_recharge`. Supply a unique `request_id` of 8–64 letters, digits, underscores or hyphens for each intended recharge. **Reuse that same ID and parameters on every retry**, especially after a timeout. Changed parameters under the same ID are rejected. Reconnects should use existing recharge numbers rather than generating replacement orders.

A checkout URL or `payment_status` alone does not establish wallet credit. Only a populated `credited_at` from `get_recharge` confirms credit. Settlement, signatures, callbacks and once-only balance credit remain the website's existing wallet responsibility.

## Limits and privacy

- Keys are scoped to one account and expire; users and administrators can revoke them.
- Servers store a key hash, never the full key. Activity records exclude keys and tool payloads.
- Account services admit at most 30 requests per connection per minute, backed by the website database; other site limits also apply.
- List tools support `limit` (1–100) and `offset`.
- Public domain search retains its per-process 5/minute, 200/day budget and 45-second result cache; public search is outside account activity statistics.
- HTTPS targets are fixed; redirects and inherited proxy settings are disabled. Network errors remain unconfirmed.

## Development

```sh
uv sync --extra dev
uv run --frozen pytest -q
python examples/demo_stdio.py --domain example.com
```

Automated tests use mocked HTTP and never submit real payments or registrations. The demo performs a live public lookup only. [Historical demo evidence](docs/DEMO.md) refers to the original search release, not the new account tools.

[MIT](LICENSE).
