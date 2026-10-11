# Reproducible stdio MCP demonstration / 可复现的 MCP 调用演示

**Checked on 2026-10-11 00:58 UTC** against the live, public DomainRoc search endpoint. The client was the **official Python MCP SDK** using local stdio; it did not use a separate AI assistant or demonstrate native integration with any named AI product.

## Run it yourself

Requires Python 3.11+ and outbound HTTPS access.

```bash
git clone https://github.com/sinianchu9/domainroc-mcp-server.git
cd domainroc-mcp-server
python -m pip install -e .
python examples/demo_stdio.py --domain example.com
```

The demo uses `mcp.client.stdio.stdio_client`, initializes a `ClientSession`, lists tools, invokes `check_domain`, and closes the child process. It uses neither registrar API keys nor user credentials, and it never creates orders.

## Actual protocol results (historical samples)

**Example 1 — registered domain**

```console
$ python examples/demo_stdio.py --domain example.com
Discovered MCP tools: check_domain
{
  "domain": "example.com",
  "status": "unavailable",
  "available": false,
  "price_usdt": null,
  "currency": "USDT",
  "purchase_url": "https://www.domainroc.com/en/domains",
  "checked_at": "2026-10-11T00:58:11+00:00",
  "cached": false,
  "reason": "taken",
  "note": "This domain was reported taken. Check on the official website for updates."
}
```

**Example 2 — test domain reported available at that moment**

```console
$ python examples/demo_stdio.py --domain domainrocagentpreview20261011test.com
Discovered MCP tools: check_domain
{
  "domain": "domainrocagentpreview20261011test.com",
  "status": "available",
  "available": true,
  "price_usdt": "13.986000",
  "currency": "USDT",
  "purchase_url": "https://www.domainroc.com/en/domains",
  "checked_at": "2026-10-11T00:58:19+00:00",
  "cached": false,
  "reason": null,
  "note": "Preview only; availability and price must be reconfirmed at official checkout."
}
```

**Example 3 — invalid input**

```console
$ python examples/demo_stdio.py --domain https://127.0.0.1
Discovered MCP tools: check_domain
{
  "domain": "https://127.0.0.1",
  "status": "unknown",
  "available": null,
  "price_usdt": null,
  "currency": "USDT",
  "purchase_url": "https://www.domainroc.com/en/domains",
  "checked_at": "2026-10-11T00:58:12+00:00",
  "cached": false,
  "reason": "invalid_domain",
  "note": "No confirmed availability or price. Search and checkout on the official website."
}
Result not confirmed. Do not infer availability or price.
```

These outputs are actual SDK/protocol observations with no credentials or user data. **They are time-stamped historical examples**, not current availability, guaranteed USDT prices or screenshots from an AI assistant. Live searches must be reconfirmed at official checkout.

## Client configuration example

Only for clients **that explicitly support local stdio MCP**; configuration field names may differ:

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

After setup, an assistant with tool-calling support may be asked: *"Use DomainRoc to check example.com and report the confirmed status. Do not invent a price."* Natural-language auto-selection was **not** part of the SDK protocol test.

## 中文说明

使用 `python examples/demo_stdio.py --domain example.com` 可启动本地 Server、发现 `check_domain`、调用真实公开域名查询接口并安全退出。上面的 3 份结果是 **2026-10-11 UTC 实际调用记录**，不是当前库存，也不是虚构演示。第二个测试域名在调用时显示可注册，参考价格为 13.986000 USDT，但此数据会变化，不能用作现在的购买报价。测试没有使用注册商密钥、客户账号、数据库、订单或支付能力。

## Safety

* Local stdio only; no new public MCP endpoint.
* Tool `check_domain` is read-only.
* Real checks are deliberately manual and low volume; automated tests are mocked.
* Unconfirmed/invalid/upstream-failed calls do not imply availability.
* The official domain search and checkout page is the only place for purchasing.
