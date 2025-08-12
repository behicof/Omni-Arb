import pytest
from core.calculations import net_edge_bps, basis_bps, qty_from_notional


def test_net_edge_positive_negative():
    pos = net_edge_bps(100, 101, costs_bps=20)
    neg = net_edge_bps(100, 100.02, costs_bps=10)
    assert pos > 0
    assert neg < 0


def test_basis_bps_sanity():
    assert basis_bps(100, 101) == pytest.approx(100.0)


def test_qty_from_notional_rounding():
    qty = qty_from_notional(1000, price=100, lot=3)
    assert qty == 9
