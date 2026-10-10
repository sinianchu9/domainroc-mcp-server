# Security / 安全说明

## English

This repository is a **local, read-only MCP preview**. It exposes one domain lookup tool only.

- No checkout, order creation, wallet, account, login, registrar key, direct database, or DNS mutation.
- External input is a domain name, never a URL or arbitrary upstream host.
- Only a fixed DomainRoc HTTPS API endpoint is contacted; automatic redirects are disabled.
- Results from upstream failures, restrictions, and manual review are `unknown` rather than guessed.
- Limits (5/minute, 200/24h, 2 concurrent, 45-second cache) are **per process**, not a public-service firewall.
- Stdio is designed for clients you control. **Do not deploy a public network endpoint** without authentication, shared rate limits, network egress controls, monitoring, and explicit review.
- No credentials or payment details are required. Never post real private keys or account tokens in issues.

Report sensitive vulnerabilities privately via the repository's GitHub vulnerability reporting features if enabled; otherwise contact the site's published security channel. Do not place exploitable secrets in public issues.

## 简体中文

本仓库是**本地只读 MCP 实验**，只包含域名查询工具。没有订单、扣款、支付、注册商密钥、数据库直连或 DNS 修改权限。

- 用户输入只能是域名，不能是 URL 或任意远程地址。
- 外部请求固定为 DomainRoc 官方 HTTPS 查询路径，禁用自动重定向。
- 失败、限制、审核中的状态都返回 `unknown`，不推断为可注册。
- 每分钟 5 次、滚动 24 小时 200 次、并发 2 次及缓存均为**单进程限制**，不是公网安全网关。
- 不得未经专项安全审核就在公网开放 MCP 服务。
- 漏洞请通过 GitHub 私密报告功能（如已启用）或 DomainRoc 官网公布的安全渠道反馈，不要在公开 Issue 发布敏感凭据。
