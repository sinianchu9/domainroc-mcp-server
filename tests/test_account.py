"""Offline authenticated adapter tests; no real money or account access."""
import asyncio
import httpx
import pytest
from domainroc_mcp.account import account_call, register_account_tools, site_url
from mcp.server.fastmcp import FastMCP


def test_no_key_means_no_account_request(monkeypatch):
    monkeypatch.delenv("DOMAINROC_AGENT_TOKEN", raising=False)
    def unexpected(request): raise AssertionError("must not call upstream")
    assert asyncio.run(account_call("wallet", transport=httpx.MockTransport(unexpected)))["error"] == "connection_required"

@pytest.mark.parametrize("site,host", [("domainroc", "www.domainroc.com"), ("namepopo", "namepopo.com")])
def test_fixed_account_endpoint_and_no_caller_identity(monkeypatch, site, host):
    monkeypatch.setenv("DOMAINROC_SITE", site)
    monkeypatch.setenv("DOMAINROC_AGENT_TOKEN", "droc_test-only-key")
    def handler(request):
        assert request.method == "POST" and request.url.host == host
        assert request.url.path == "/api/agent/call"
        assert request.headers["authorization"] == "Bearer droc_test-only-key"
        assert request.content == b'{"action":"wallet"}'
        return httpx.Response(200, json={"available_usdt": "20"})
    assert asyncio.run(account_call("wallet", transport=httpx.MockTransport(handler)))["available_usdt"] == "20"

@pytest.mark.parametrize("status,error", [(401,"connection_expired"),(403,"permission_required"),(409,"request_conflict"),(422,"invalid_request"),(429,"try_later"),(503,"service_paused"),(502,"service_unavailable"),(302,"service_unavailable")])
def test_errors_hide_upstream_details_and_do_not_follow_redirects(monkeypatch, status, error):
    monkeypatch.setenv("DOMAINROC_AGENT_TOKEN", "droc_test-only-key")
    def handler(request): return httpx.Response(status, headers={"Location": "https://evil.test"}, json={"secret": "private-value"})
    result = asyncio.run(account_call("wallet", transport=httpx.MockTransport(handler)))
    assert result["error"] == error
    assert "private-value" not in str(result)


def test_recharge_retries_keep_request_identifier(monkeypatch):
    monkeypatch.setenv("DOMAINROC_AGENT_TOKEN", "droc_test-only-key")
    seen=[]
    def handler(request):
        seen.append(request.content)
        raise httpx.ReadTimeout("uncertain", request=request)
    for _ in range(2):
        result=asyncio.run(account_call("recharge", transport=httpx.MockTransport(handler), amount_usdt="20", payment_method="usdt_trc20", request_id="same-request"))
        assert result["error"] == "service_unavailable"
        assert "same request_id" in result["message"]
    assert seen[0] == seen[1]

@pytest.mark.parametrize("site", ["http://localhost", "https://evil.test", ""])
def test_site_cannot_redirect_credentials(monkeypatch, site):
    monkeypatch.setenv("DOMAINROC_SITE", site)
    with pytest.raises(ValueError): site_url()

@pytest.mark.parametrize("amount", ["NaN", "Infinity", "0", "100001", "1.0000001", "abc"])
def test_invalid_recharge_amount_rejected_before_network(amount):
    async def run():
        mcp = FastMCP("test")
        register_account_tools(mcp)
        result = await mcp.call_tool("create_recharge", {"amount_usdt": amount, "payment_method": "usdt_trc20", "request_id": "test-request"})
        assert "invalid_amount" in str(result)
    asyncio.run(run())


def test_annotations_and_discovery():
    async def run():
        mcp = FastMCP("test")
        register_account_tools(mcp)
        tools = {tool.name: tool for tool in await mcp.list_tools()}
        assert len(tools) == 8
        assert tools["create_recharge"].annotations.readOnlyHint is False
        assert tools["create_recharge"].annotations.idempotentHint is True
        assert all(t.annotations.readOnlyHint for name, t in tools.items() if name != "create_recharge")
    asyncio.run(run())
