from hcope import hcope_gate


def test_lcb_pass(capsys):
    assert hcope_gate(1.5, 0.2)
    captured = capsys.readouterr().out.strip()
    assert "Policy passed HCOPE gate" in captured


def test_lcb_fail(capsys):
    assert not hcope_gate(1.2, 0.4)
    captured = capsys.readouterr().out.strip()
    assert captured.startswith("Policy failed HCOPE gate. LCB:")
    assert "< threshold: 1.0" in captured
