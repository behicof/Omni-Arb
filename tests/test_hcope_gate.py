from hcope import hcope_gate


def test_lcb_pass():
    """Gate should pass when the LCB exceeds the default threshold."""
    assert hcope_gate(1.5, 0.4)


def test_lcb_fail():
    """Gate should fail when the LCB falls below the default threshold."""
    assert not hcope_gate(0.8, 0.6)
