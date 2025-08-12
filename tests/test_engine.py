import logging
import sys

import engine


def test_rest_fallback_via_env(monkeypatch, caplog):
    """WS is disabled when WS_DISABLED=1 and banner is logged."""
    monkeypatch.setenv("WS_DISABLED", "1")
    called = {"rest": False}

    async def fake_run():
        called["rest"] = True

    monkeypatch.setattr("feeds.rest_mark_funding.run", fake_run)
    caplog.set_level(logging.WARNING)

    engine.main()

    assert called["rest"]
    assert "WS blocked → using REST fallback" in caplog.text


def test_ws_default(monkeypatch):
    """WebSocket feed is used when no override is set."""
    monkeypatch.delenv("WS_DISABLED", raising=False)
    called = {"ws": False}

    import types

    dummy = types.SimpleNamespace()

    async def fake_ws():
        called["ws"] = True

    dummy.subscribe_mark_price = fake_ws
    monkeypatch.setitem(sys.modules, "binance_ws", dummy)

    engine.main()

    assert called["ws"]
