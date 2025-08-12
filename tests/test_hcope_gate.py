import pytest

from hcope import calculate_lcb, hcope_gate


def test_calculate_lcb_expected_value():
    """LCB should reduce the estimated metric by the z-score scaled std."""
    assert calculate_lcb(1.5, 0.2) == pytest.approx(1.1710293, rel=1e-6)


def test_lcb_pass():
    assert hcope_gate(1.5, 0.2)


def test_lcb_fail():
    assert not hcope_gate(1.2, 0.4)
