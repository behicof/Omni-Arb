# Omni-Arb — Funding & Basis Arbitrage (Binance / OKX)

**هدف:** موتور آربیتراژ «Rule-based و سریع» برای:
- **Funding-Rate Arbitrage** (دلتا-نوتورال: دریافت/پرداخت Funding با هج دلتا)
- **Cash-and-Carry / Basis** (قفل فاصله‌ی فیوچرز–اسپات پس از کسر هزینه‌ها)
- (بعداً اختیاری) Cross-Exchange / Triangular روی نمادهای پرنقد

> پیش‌فرض: **Binance USDⓈ-M** و **OKX Perpetuals**. پشتیبانی **MEXC** بعداً به‌صورت ماژول اختیاری اضافه می‌شود.

---

## معماری
- **Core:**  \\
  \[
  \text{NetEdge}_{bps}=\text{Funding}_{recv}-\text{Fees}-\text{Borrow/Carry}-\text{Slippage}
  \]
  آستانه‌ها/گاردها از `configs/thresholds.yml` خوانده می‌شوند.  \\
- **Execution:** سفارش‌های Limit با **IOC** (اتمیک) یا **GTX/Post-Only** (میکر واقعی). Dry-Run بایننس از مسیر **`POST /fapi/v1/order/test`** و OKX با هدر **`x-simulated-trading: 1`**.  \\
- **Risk & Guards:** گارد تأخیر لِگ، اسلیپیج، عمق، سقف ناتیونال، و اعمال فیلترهای LOT/NOTIONAL.  \\
- **Market Data:** WebSocket مارک‌پرایس/فاندینگ + Poll اندپوینت‌های Funding/Info.  \\
- **NLP/RL Hooks (اختیاری):** FinGPT برای گزارش زبانی؛ FinRobot/FinRL برای پژوهش.

- **Core:**
  \[
  \text{NetEdge}_{bps}=\text{Funding}_{recv}-\text{Fees}-\text{Borrow/Carry}-\text{Slippage}
  \]
  آستانه‌ها/گاردها از `configs/thresholds.yml` خوانده می‌شوند.
- **Execution:** سفارش‌های Limit با **IOC** (اتمیک) یا **GTX/Post-Only** (میکر واقعی). Dry-Run بایننس از مسیر **`POST /fapi/v1/order/test`** و OKX با هدر **`x-simulated-trading: 1`**.
- **Risk & Guards:** گارد تأخیر لِگ، اسلیپیج، عمق، سقف ناتیونال، و اعمال فیلترهای LOT/NOTIONAL.
- **Market Data:** WebSocket مارک‌پرایس/فاندینگ + Poll اندپوینت‌های Funding/Info.
- **NLP/RL Hooks (اختیاری):** FinGPT برای گزارش زبانی؛ FinRobot/FinRL برای پژوهش.

**مراجع:** Binance Funding History/Info، Mark-Price Stream، Position Mode؛ OKX Funding Mechanism و Demo Header.
(به منابع انتهای README مراجعه کنید.)

---

## ساختار ریپو (به‌روز با فایل‌های فعلی)

.
├── engine.py              # هسته‌ی اجرا (ورود/خروج، Dry-Run/LIVE switch)
├── ws.py                  # فید WS (e.g., <symbol>@markPrice\@1s)
├── rest.py                # REST (Binance/OKX) + امضا
├── risk.py                # sizing, guards, limits
├── sentiment_fingpt.py    # hook اختیاری به FinGPT (گزارش)
├── base.py, auth.py       # کمک‌کارها (signing/session)
├── main.py                # entrypoint (smoke-run/daemon)
├── test_smoke.py          # تست پایه
├── configs/
│   ├── thresholds.yml     # آستانه‌ها (θ، slippage، latency، depth)
│   └── risk.yml           # سقف‌ها (max_notional, per-symbol caps)
├── .env.example           # کلیدها و تنظیمات اجرایی (بدون کامیت کلید واقعی)
├── Dockerfile
├── Makefile
└── pyproject.toml

````

---

## نصب و اجرای سریع
```bash
# نصب
pip install -e .     # یا poetry/uv به انتخاب شما
pytest -q            # تست پایه

# Smoke: چاپ NetEdge فرضی + گاردها
python main.py --smoke

# Dry-Run واقعی
export LIVE=0        # Binance: /order/test / OKX: x-simulated-trading: 1
python main.py --symbols BTCUSDT,ETHUSDT --mode funding
```

---

## سیاست ورود/خروج

**Funding-Arb (دلتا-نوتورال):**

```
Enter if:   NetEdge_bps ≥ THRESHOLD
Guards:     latency ≤ Lmax, slippage ≤ Smax, depth ≥ Dmin
```

**Cash-and-Carry (Basis):**

```
Enter if:   ((Futures - Spot) / Spot)×10,000 ≥ THRESHOLD  # پس از کسر fee/carry/slippage
Exit:       افت لبه، تغییر نامطلوب Cap/Floor/Interval، یا نقض گاردها
```

---

## سفارش‌ها و حالت حساب (Binance)

* **TIF:** `IOC | FOK | GTC | GTX(Post-Only)`؛ GTX فقط اگر سفارش *حتماً* میکر بماند پذیرفته می‌شود.
* **Position Mode:** `POST/GET /fapi/v1/positionSide/dual` برای Hedge/One-way؛ `positionSide` و `reduceOnly` متناسب تنظیم می‌شوند.

---

## داده‌های بازار

* **WS (Binance):** `<symbol>@markPrice@1s` → مارک‌پرایس + فاندینگ تخمینی.
* **REST Poll (Binance):**
  `GET /fapi/v1/fundingRate` (هیستوری/آخرین نرخ)
  `GET /fapi/v1/fundingInfo` (cap/floor/interval)
* **OKX:** فرمول فاندینگ = Clamp\[Average Premium Index ± interest tweak, Cap, Floor] (WMA)؛ دمو با `x-simulated-trading: 1`.

---

## پیکربندی کلیدها

```
# .env.example
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
OKX_API_KEY=...
OKX_API_SECRET=...
OKX_PASSPHRASE=...
ENV=dev
LIVE=0
LOG_LEVEL=INFO
```

---

## تست‌ها

```bash
pytest -q
# شامل: محاسبه‌ی net_edge، basis، رُندینگ lot، مسیرهای IOC/GTX و order/test، و Hedge mode
```

---

## نقشهٔ راه کوتاه

* [ ] CSV logger برای NetEdge/Guards/Reject
* [ ] گزارش روزانه Funding P&L
* [ ] Cross-Exchange روی نمادهای پرنقد
* [ ] FinRobot pipeline (Scout→Risk→Sizer→Trader→Settlement)

---

## منابع

* Binance — Funding Rate History: [https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History)
* Binance — Funding Rate Info (Cap/Floor/Interval): [https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-Info](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-Info)
* Binance — Mark Price Stream: [https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream)
* Binance — Position Mode (set/get): [https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Change-Position-Mode](https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Change-Position-Mode) , [https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Get-Current-Position-Mode](https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Get-Current-Position-Mode)
* Binance — Announcements/FAQ for funding caps/frequency: [https://www.binance.com/en/support/announcement/detail/3243c81a35bd4f0c86a37315c3dc96cc](https://www.binance.com/en/support/announcement/detail/3243c81a35bd4f0c86a37315c3dc96cc) , [https://www.binance.com/en/support/announcement/detail/98d6b24d3e5c4f84a8ed04087997d8d0](https://www.binance.com/en/support/announcement/detail/98d6b24d3e5c4f84a8ed04087997d8d0)
* Binance — TIF definitions (GTX = Post-Only): [https://developers.binance.com/docs/derivatives/coin-margined-futures/common-definition](https://developers.binance.com/docs/derivatives/coin-margined-futures/common-definition)
* OKX — Funding fee mechanism (Clamp/Cap/Floor + WMA update): [https://www.okx.com/en-us/help/iv-introduction-to-perpetual-swap-funding-fee](https://www.okx.com/en-us/help/iv-introduction-to-perpetual-swap-funding-fee) , [https://www.okx.com/help/okx-to-optimize-funding-rate-calculation](https://www.okx.com/help/okx-to-optimize-funding-rate-calculation)
* OKX — API v5 & Simulated trading header: [https://www.okx.com/docs-v5/en/](https://www.okx.com/docs-v5/en/) , [https://www.okx.com/en-us/help/api-faq](https://www.okx.com/en-us/help/api-faq)

```

> نکته: لینک‌های بالا در متن به‌صورت مرجع ذکر شدند؛ خلاصه‌ی رسمی هرکدام در بخش «Resources/مراجع» آمده است. (برای جلوگیری از شکستن فرمت، URLها در بلوک کد بالا درج شده‌اند.)

---

