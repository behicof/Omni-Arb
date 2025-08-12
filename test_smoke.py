"""Simple smoke test for orchestrator flow."""
from orchestrator import finrobot_flow


def test_smoke_run():
    result = finrobot_flow.run()
    assert "net_edge_bps" in result
