from unittest.mock import Mock

from account import position_mode


def _mock_session(json_data):
    session = Mock()
    response = Mock()
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    session.get.return_value = response
    session.post.return_value = response
    return session


def test_get_position_mode_true():
    session = _mock_session({"dualSidePosition": "true"})
    assert position_mode.get_position_mode(session) is True
    session.get.assert_called_once_with(
        "https://fapi.binance.com/fapi/v1/positionSide/dual"
    )


def test_set_position_mode_false():
    session = _mock_session({"code": 200})
    result = position_mode.set_position_mode(False, session)
    assert result["code"] == 200
    session.post.assert_called_once_with(
        "https://fapi.binance.com/fapi/v1/positionSide/dual",
        params={"dualSidePosition": "false"},
    )
