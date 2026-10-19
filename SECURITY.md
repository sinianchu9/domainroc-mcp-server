# Security model

This package runs locally over MCP stdio. It is not an Internet-facing gateway.

- Public search targets one fixed HTTPS route. `DOMAINROC_SITE` selects only DomainRoc or Namepopo. Redirects and inherited environment proxies are disabled; never accept an arbitrary base URL for account credentials.
- Account credentials come only from `DOMAINROC_AGENT_TOKEN` in the local environment, not tool arguments or chat. Avoid committing client configuration or logging this environment variable.
- Website endpoints authenticate a high-entropy key hash, active account, permission, expiry and revocation for every request. Agent keys do not work as website login tokens and cannot call arbitrary user or administrator routes.
- Only a narrow set of account operations is exposed. No arbitrary URL/path, user ID, registrar credentials, DNS changes, domain purchase, balance debit, withdrawal or wallet credit endpoint is available through these tools.
- Creating a recharge needs explicit recharge permission. It produces a checkout; the existing signed payment workflow performs settlement and credit. Mandatory per-connection request IDs protect retries. A request admitted before revocation may finish; revocation blocks subsequent admissions.
- Account activity persists admission before a business action. Pending records are unconfirmed, failed records do not establish lack of a gateway order, and checkout creation does not imply payment. Reporting joins actual recharge records and deduplicates IDs, including uncertain gateway outcomes.
- Account limits are database-backed (30 admissions per connection per minute), in addition to site-wide request limits. Public search limits remain per-process, not distributed.
- MCP tool annotations describe behavior and are not authorization. Authorization is enforced by the website.

Do not expose this local server publicly without separate authentication, shared limits, transport review and deployment hardening. Do not claim compatibility with AI clients that have not been tested.

Tests use mocked network responses and an isolated backend database. Do not use real customer keys, real payments or production databases in automated tests. Do not include secrets in reports or issues.
