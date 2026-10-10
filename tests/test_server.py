"""Offline contract tests. Never contact the real DomainRoc service."""

import asyncio

import httpx

from domainroc_mcp.server import DomainChecker, normalize_domain, safe_quote


def check(domain, response):
    def handler(request):
        assert request.method == "GET"
        assert request.url.scheme == "https"
        assert request.url.host == "www.domainroc.com"
        assert request.url.path == "/api/public/domains/check"
        assert request.url.params["domain"] == domain.lower()
        return response

    return asyncio.run(
        DomainChecker().check(domain, transport=httpx.MockTransport(handler))
    )


def sample(domain="example.com", *, status="available", available=True, flow="instant"):
    return {
        "domain": domain,
        "status": status,
        "available": available,
        "flow": flow,
        "price": {"total_usdt": "9.123456"},
    }


def test_available_and_price():
    output = check(
        "Example.COM",
        httpx.Response(200, json=sample(), headers={"content-type": "application/json"}),
    )
    assert output["status"] == "available"
    assert output["available"] is True
    assert output["price_usdt"] == "9.123456"
    assert output["purchase_url"] == "https://www.domainroc.com/en/domains"


def test_taken():
    output = check(
        "example.com",
        httpx.Response(
            200,
            json=sample(status="taken", available=False),
            headers={"content-type": "application/json"},
        ),
    )
    assert output["status"] == "unavailable"
    assert output["available"] is False
    assert output["price_usdt"] is None


def test_manual_review_is_never_available():
    output = check(
        "example.com",
        httpx.Response(
            200,
            json=sample(flow="manual_review"),
            headers={"content-type": "application/json"},
        ),
    )
    assert output["status"] == "unknown"
    assert output["available"] is None
    assert output["price_usdt"] is None


def test_restricted_is_unknown():
    output = check(
        "example.com",
        httpx.Response(
            200,
            json=sample(status="restricted", available=False),
            headers={"content-type": "application/json"},
        ),
    )
    assert output["status"] == "unknown"


def test_bad_http_and_html_fail_closed():
    assert check("example.com", httpx.Response(429))["status"] == "unknown"
    assert check("example.com", httpx.Response(200, text="oops"))["status"] == "unknown"


def test_wrong_domain_is_not_accepted():
    out = check(
        "example.com",
        httpx.Response(
            200,
            json=sample("other.com"),
            headers={"content-type": "application/json"},
        ),
    )
    assert out["status"] == "unknown"


def test_bad_price_not_invented():
    payload = sample()
    payload["price"] = {"total_usdt": "NaN"}
    out = check(
        "example.com",
        httpx.Response(200, json=payload, headers={"content-type": "application/json"}),
    )
    assert out["status"] == "available"
    assert out["price_usdt"] is None
    assert safe_quote({"price": {"total_usdt": -1}}) is None


def test_domain_validation_rejects_urls_ssrf_and_bad_labels():
    for bad in (
        "https://example.com",
        "http://localhost",
        "127.0.0.1",
        "example.com/path",
        "user@host.com",
        "-bad.com",
        "bad_.com",
        "example..com",
        "localhost",
        "a." + ("b" * 64) + ".com",
    ):
        try:
            normalize_domain(bad)
            assert False, bad
        except ValueError:
            pass
    assert normalize_domain("Example.COM.") == "example.com"
    assert normalize_domain("xn--bcher-kva.de") == "xn--bcher-kva.de"


def test_cached_only_confirmed_results():
    calls = 0
    def handler(_request):
        nonlocal calls
        calls += 1
        return httpx.Response(
            200, json=sample(), headers={"content-type": "application/json"}
        )
    async def run():
        checker = DomainChecker()
        transport = httpx.MockTransport(handler)
        a = await checker.check("example.com", transport=transport)
        b = await checker.check("example.com", transport=transport)
        return a, b
    a, b = asyncio.run(run())
    assert calls == 1
    assert a["cached"] is False
    assert b["cached"] is True


def test_rate_limit_rejects_sixth_distinct_query():
    calls = 0
    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(
            200,
            json=sample(domain=request.url.params["domain"]),
            headers={"content-type": "application/json"},
        )
    async def run():
        checker = DomainChecker()
        outputs = []
        for idx in range(6):
            outputs.append(await checker.check(f"example{idx}.com", transport=httpx.MockTransport(handler)))
        return outputs
    results = asyncio.run(run())
    assert calls == 5
    assert results[-1]["status"] == "unknown"
    assert results[-1]["reason"] == "rate_limited"
