# Omni-Arb Funding & Basis Engine

## 1. Overview
Arbitrage engine for funding-rate and cash-and-carry spreads across **Binance USDⓈ-M** futures and **OKX perpetuals**.

## 2. Execution
Orders are sent through `order.py` which supports `IOC`, `FOK`, `GTC` and `GTX (Post-Only)`.
- Dry‑run on Binance uses `POST /fapi/v1/order/test` when `LIVE=0`.
- Live trading switches to `POST /fapi/v1/order`.
- OKX demo trading adds header `x-simulated-trading: 1` and removes it for live.
- Post‑only semantics reject orders that would cross the book.

## 3. Market Data
- **WebSocket:** `ws_binance_mark.py` subscribes to `<symbol>@markPrice@1s`.
- **REST:** `poll_funding.py` queries `GET /fapi/v1/fundingRate` and `GET /fapi/v1/fundingInfo`.

## 4. Risk & Guards
- Validate `LOT_SIZE` and `MIN_NOTIONAL` via `exchangeInfo` before placing orders.
- Configurable thresholds in `configs/thresholds.yml` and symbol caps in `configs/risk.yml` cover latency, slippage and depth limits.

## 5. Install / Run / Test
```bash
poetry install
python ws_binance_mark.py BTCUSDT
python poll_funding.py BTCUSDT
pytest -q
```
Use `.env.example` to configure keys and `LIVE` flag.

## 6. References
- [Mark Price Stream – Binance Developer Center](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream)
- [Get Funding Rate History – Binance Developer Center](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History)
- [Funding Info – Binance Developer Center](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Funding-Rate)
- [Exchange Info – Binance Developer Center](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information)
- [OKX API Guide](https://www.okx.com/docs-v5/en/)
- [go-binance futures package](https://pkg.go.dev/github.com/adshao/go-binance/futures)
