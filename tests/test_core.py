import pytest
from core.utils import net_edge_bps, basis_bps, qty_from_notional


def test_net_edge_positive_negative():
    assert net_edge_bps(15, 10) > 0
    assert net_edge_bps(5, 10) < 0


def test_basis_bps_calculation():
    assert basis_bps(100, 101) == pytest.approx(100.0)


def test_qty_from_notional_rounding():
    qty = qty_from_notional(1050, 100, 1)
    assert qty == 10
    qty = qty_from_notional(1060, 100, 0.5)
    assert qty == pytest.approx(10.5)
    assert (qty * 10) % 5 == 0  # multiple of lot size
