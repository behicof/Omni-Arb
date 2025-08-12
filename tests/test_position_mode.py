import unittest

from account.position_mode import (
    PositionMode,
    set_position_mode,
    validate_order,
)


class PositionModeTest(unittest.TestCase):
    def tearDown(self) -> None:
        # reset mode after each test
        set_position_mode(PositionMode.ONE_WAY)

    def test_hedge_requires_position_side(self):
        set_position_mode(PositionMode.HEDGE)
        with self.assertRaises(ValueError):
            validate_order({})

    def test_hedge_allows_reduce_only_with_side(self):
        set_position_mode(PositionMode.HEDGE)
        order = {"positionSide": "LONG", "reduceOnly": True}
        validate_order(order)  # should not raise

    def test_one_way_disallows_position_side(self):
        set_position_mode(PositionMode.ONE_WAY)
        with self.assertRaises(ValueError):
            validate_order({"positionSide": "LONG"})

    def test_one_way_allows_reduce_only(self):
        set_position_mode(PositionMode.ONE_WAY)
        order = {"reduceOnly": True}
        validate_order(order)  # should not raise


if __name__ == "__main__":
    unittest.main()
