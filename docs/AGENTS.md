# AGENTS for Omni-Arb (Codex)

## Setup
- Python 3.11
- Install: pip install -e .
- Smoke:  python main.py --smoke

## Safety & Secrets
- LIVE=0 (default). Binance uses POST /fapi/v1/order/test; OKX uses x-simulated-trading:1.
- Never commit .env.

## Tasks (first wave)
1) WS: subscribe <symbol>@markPrice@1s; CSV snapshots (ts, mark, estFunding, nextFunding).
2) REST pollers: fundingRate + fundingInfo (cap/floor/interval) → compute NetEdge_bps.
3) Order wrapper: support TIF {IOC,GTC,FOK,GTX}; Hedge mode positionSide; reduceOnly; /order/test in LIVE=0.
4) Guards & Sizer: latency/slippage/depth + LOT/MIN_NOTIONAL filters.
5) Funding P&L: windowed aggregation; daily report; FinGPT hook (optional).
