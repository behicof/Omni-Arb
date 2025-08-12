# Omni-Arb

Utilities for funding & basis arbitrage on Binance and OKX.

## Features
- **Order wrapper** toggles dry‑run (`POST /fapi/v1/order/test`) vs live (`POST /fapi/v1/order`),
  supporting `timeInForce` values `IOC`, `FOK`, `GTC` and `GTX` (Post‑Only).
- **WebSocket mark price feed** subscribes to `<symbol>@markPrice@1s` and persists
  `ts`, `markPrice`, `fundingRate`, `nextFunding` to CSV and Parquet.
- **Funding poller** queries `GET /fapi/v1/fundingRate` and
  `GET /fapi/v1/fundingInfo` then computes `NetEdge_bps`.
- **OKX demo/live switcher** adds header `x-simulated-trading: 1` for demo
  trading and omits it for live orders.
- Sample configs in `configs/` and environment variables in `.env.example`.

## Quick Start
```bash
poetry install
cp .env.example .env
python -m pytest
```

## Documentation Links
- [Binance Mark‑Price WebSocket 1s](https://binance-docs.github.io/apidocs/futures/en/#mark-price-stream-for-all-market)
- [Binance Funding Rate History](https://binance-docs.github.io/apidocs/futures/en/#get-funding-rate-history)
- [Binance Funding Info](https://binance-docs.github.io/apidocs/futures/en/#get-funding-info)
- [Binance New Order (timeInForce incl. GTX)](https://binance-docs.github.io/apidocs/futures/en/#new-order-trade)
- [OKX Simulated Trading Header](https://www.okx.com/docs-v5/en/#rest-api-simulated-trading-introduction)

## Acceptance Checklist
- [x] WebSocket snapshot validated
- [x] Funding pollers validated
- [x] Order wrapper (IOC/GTX) validated
- [x] Dry‑run `/order/test` validated
