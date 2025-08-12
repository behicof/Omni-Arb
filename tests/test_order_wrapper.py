import pytest
from unittest.mock import Mock

import order


def _mock_session(json_data):
    session = Mock()
    response = Mock()
    response.json.return_value = json_data
    session.post.return_value = response
    return session


def test_invalid_position_side_single_mode():
    with pytest.raises(ValueError):
        order.order_test({"positionSide": "LONG", "timeInForce": "GTC"}, dual_mode=False, session=_mock_session({}))


def test_invalid_position_side_dual_mode():
    with pytest.raises(ValueError):
        order.order_test({"positionSide": "BOTH", "timeInForce": "GTC"}, dual_mode=True, session=_mock_session({}))


def test_reduce_only_requires_position_side():
    with pytest.raises(ValueError):
        order.order_test({"reduceOnly": True, "timeInForce": "GTC"}, dual_mode=True, session=_mock_session({}))


def test_invalid_time_in_force():
    with pytest.raises(ValueError):
        order.order_test({"timeInForce": "BAD", "positionSide": "BOTH"}, dual_mode=False, session=_mock_session({}))


def test_gtx_error_detection():
    session = _mock_session({"code": -5022, "msg": "GTX not allowed"})
    with pytest.raises(order.GTXError):
        order.order_test({"timeInForce": "GTX", "positionSide": "BOTH"}, dual_mode=False, session=session)
