import datetime as dt

from accounting.funding_pnl import FundingPnL, read_settlement_schedule


def test_fee_calculation_and_daily_summary():
    tracker = FundingPnL()
    ts = dt.datetime(2024, 1, 1, 0, 0)
    fee = tracker.log_window("BTCUSDT", position_nominal=1000, funding_rate=0.0001, timestamp=ts)
    assert fee == 0.1
    summary = tracker.summarize_daily()
    assert summary[dt.date(2024, 1, 1)] == 0.1


def test_default_settlement_schedule():
    interval = read_settlement_schedule("UNKNOWN")
    assert interval == dt.timedelta(hours=8)
