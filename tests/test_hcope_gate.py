from hcope import hcope_gate


def test_lcb_pass():
    assert hcope_gate(1.5, 0.2)


def test_lcb_fail():
    assert not hcope_gate(1.2, 0.4)
