# پروفایل آربیتراژ

## نمای کلی
- پیاده‌سازی Funding-Arb و Cash-and-Carry روی قراردادهای دائمی Binance USDⓈ-M و OKX.
- تمرکز بر همگرایی نرخ‌های تأمین مالی و اختلاف قیمت اسپات/فیوچرز.

## اجرا
- **TIF:** `IOC` | `FOK` | `GTC` | `GTX` (Post-Only).
- شبه‌کد `GTX = Post-Only`:
  ```pseudocode
  if tif == "GTX":
      order.post_only = true
      reject_if_taker = true
  ```
- مسیر Dry-Run:
  - Binance: `POST /fapi/v1/order/test`
  - OKX: هدر `x-simulated-trading: 1`

## داده‌های بازار
- **WebSocket:** جریان "Mark Price Stream (1s)" با الگو `<symbol>@markPrice@1s`.
- **REST:**
  - `GET /fapi/v1/fundingRate`
  - `GET /fapi/v1/fundingInfo`

## ریسک و محافظ
- فیلترهای تأخیر، لغزش و عمق برای جلوگیری از اجرای ناخواسته.
- بررسی مقادیر `LOT` و `MIN_NOTIONAL` پیش از ارسال سفارش.

## نصب / اجرا / تست
```bash
poetry install
uvicorn apps.api:app --reload --port 8000
python apps/dashboard.py
pytest tests/test_smoke.py
```

## مراجع
- [Binance Futures API – Mark Price Stream](https://binance-docs.github.io/apidocs/futures/en/#mark-price-stream)
- [Binance Futures API – Funding Rate History](https://binance-docs.github.io/apidocs/futures/en/#get-funding-rate-history)
- [Binance Futures API – Funding Info](https://binance-docs.github.io/apidocs/futures/en/#get-funding-info)
- [Binance Futures API – Test New Order](https://binance-docs.github.io/apidocs/futures/en/#test-new-order-trade)
- [OKX API – Simulated Trading](https://www.okx.com/docs-v5/en/#overview-simulated-trading)
