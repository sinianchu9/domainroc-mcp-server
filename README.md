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

## Connect your assistant — no installation

| Site | Remote MCP URL | Account page |
| --- | --- | --- |
| DomainROC | `https://www.domainroc.com/api/mcp` | [Agent MCP](https://www.domainroc.com/dashboard/agent-mcp) |
| Namepopo | `https://www.namepopo.com/api/mcp` | [Agent MCP](https://www.namepopo.com/dashboard/agent-mcp) |

Add the URL in your assistant's **remote MCP** settings. Use a connection key if your client supports bearer authentication, or complete website sign-in and consent when prompted. Never put a key in the URL or a chat message.

- **Codex and bearer-capable clients:** copy the URL, create a key on the account page and enter it in the client's authentication field. If a header is required, use `Authorization: Bearer YOUR_CONNECTION_KEY`. In Codex configuration use `url` and `bearer_token_env_var` or `http_headers` as documented by [Codex](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).
- **ChatGPT:** add a custom MCP with the server URL and OAuth sign-in, then select the operations on the website. ChatGPT does not accept a custom connection key for authenticated MCP; availability depends on the account's custom-MCP feature. See [official authentication guidance](https://developers.openai.com/plugins/build/auth).
- **Grok / Grok Bot:** use New Connector → Custom, supply the URL and complete authentication. See [official connector guidance](https://docs.x.ai/grok/connectors). Exact Bot entry points depend on its client.
- **Muse.ai:** add an MCP connection and enter the service URL and connection key. Keep the key in connection settings, never in chat.

Each of the eight account operations is authorized separately: view balance, wallet transactions, domains and expiry, domain orders, existing monitoring, payment networks, create recharge, and check recharge credit. Creating a recharge does not imply permission to view other wallet data. Choose a per-checkout amount ceiling (new connections default to 100 USDT), a lifetime of up to 90 days, and revoke or reduce permissions anytime. Adding permissions requires a fresh connection and consent.

The website hosts the remote service using the official MCP SDK's stateless Streamable HTTP transport. OAuth uses PKCE, short-lived access tokens and rotating refresh tokens tied to the same revocable account connection. The original package in this repository remains available for existing local integrations; ordinary remote users do not install it.

Use separate accounts and grants for the two sites. Public search is also available directly on each website without connecting an account. The authenticated remote endpoint requires a key or OAuth even for its domain-search tool.

Examples: “When do my domains expire?”, “Show my available USDT balance”, “Create a 20 USDT recharge using the network I selected.”

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
