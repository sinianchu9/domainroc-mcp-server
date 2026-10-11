# DomainRoc MCP Server — AI 域名查询与 USDT 注册报价

[English](README.md) · [安全说明](SECURITY.md) · [DomainRoc AI Agent 预览](https://www.domainroc.com/zh/ai-agent-domain-search)

> **实验预览 · 仅限只读 · 不支持 AI 自动购买**

这是一个开源 **MCP（Model Context Protocol）服务端**，允许支持 MCP 的 AI 助手调用 DomainRoc 原有公开查询接口，检查**域名能否注册**，在有可靠报价时显示 **USDT 首年注册参考价**，再引导用户前往官网自行下单。

**不修改 DomainRoc 生产代码，不连接数据库，不持有注册商密钥，不碰订单和支付。**

## 功能范围

仅提供一个工具：`check_domain(domain)`。

- 使用网站现有的 `GET /api/public/domains/check`，不是单独研发一套注册商查询系统。
- 返回状态：`available`（可注册）、`unavailable`（确认不可注册）或 `unknown`（无法确认）。
- 查询失败、受限、需要人工审核等情况一律**不能冒充可注册**。
- 有可靠报价时返回 `price_usdt`，仅为预览价格，实际金额以下单时的最终复核为准。
- `purchase_url` 是官网域名查询页，不是订单、自动支付链接；用户需要自行在官网查询、确认并购买。

## 本地安装

要求 Python 3.11 或更新版本：

```bash
git clone https://github.com/sinianchu9/domainroc-mcp-server.git
cd domainroc-mcp-server
python -m pip install -e .
domainroc-mcp
```

运行使用本地 **stdio** MCP 协议，不对公网监听端口。

### 连接 AI 客户端

支持本地 stdio MCP 的客户端可参考以下配置（不同客户端的配置入口可能不同）：

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

然后向 AI 提问：

> 请用 DomainRoc 检查 example.com 是否可注册。没有可靠报价就明确说明，不要编造价格。

注意：发布 GitHub 项目**不代表**所有 AI 平台会自动发现或调用此工具，用户仍需通过支持 MCP 的客户端进行配置。

## 一条命令运行真实 MCP 演示

安装完成后，可以通过**官方 MCP Python SDK** 客户端运行只读查询演示。示例将启动本地服务、发现 `check_domain`、调用真实官网公开域名查询接口、输出结果并自动退出：

```bash
python examples/demo_stdio.py --domain example.com
```

**2026-10-11 UTC 实测：** `example.com` 返回 `unavailable`，另一测试域名在查询时返回 `available` 与 USDT 参考价，无效 URL 返回 `unknown`。详见 [带时间戳的真实演示与输出](docs/DEMO.md)。历史样本不能当作当前库存或最终购买价格。官方 SDK 的 stdio 协议测试通过，不代表所有 AI 客户端均原生兼容。

**DomainRoc 官网 AI Agent 预览：** https://www.domainroc.com/zh/ai-agent-domain-search

**观点文章：** https://www.domainroc.com/zh/blog/block-ai-or-build-with-it-domainroc

## 实验安全边界

- **无**自动下单、扣余额、付款、改 DNS、域名转移和账号读取能力。
- 校验域名格式；不接受任意 URL 或自定义访问目标；仅请求固定 HTTPS 域名。
- 禁止自动 HTTP 重定向、禁用从系统环境继承代理。
- 单进程最多每分钟 5 次、滚动 24 小时 200 次、并发 2 次真实查询；成功结果缓存 45 秒。
- 单次网络超时 8 秒。失败统一返回无法确认，不误导用户。
- 只面向本地实验。**不能把本地内存限流当成公网安全防护**；要开放公网 MCP，必须另行增加授权、统一配额及网关审查。

详见 [SECURITY.md](SECURITY.md)。

## 测试

```bash
python -m pip install -e ".[dev]"
pytest -q
```

测试使用模拟 HTTP 响应，不会产生实际订单或付款。

## 为什么开放给 AI？

**新的互联网时代，是严防死守，还是融合共生？**

我们认为：阻止未经授权的滥用行为，与支持经过边界约束的 AI Agent 并不矛盾。DomainRoc 通过一个可验证、可关闭的只读实验，探索用户授权的 AI 助手如何真正使用域名查询服务。

**关键词方向**：AI 域名查询、域名查询 MCP、MCP 域名注册接口、域名注册 API、USDT 域名注册、AI Agent 域名搜索。

本项目只证明 AI 可以查询域名，**绝不宣传尚未实现的 AI 自动购买能力**。

## 相关链接

- [DomainRoc 官网域名查询](https://www.domainroc.com/zh/domains)
- [DomainRoc 英文域名查询](https://www.domainroc.com/en/domains)
- [English README](README.md)
- [GitHub 中英文 SEO 设置建议](docs/SEO.md)

[MIT License](LICENSE)
