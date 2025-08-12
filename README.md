# پروژه Omni-Arb ترکیبی

این ریپو یک اسکلت پروژه ترکیبی برای یکپارچه‌سازی FinGPT، FinRL و کانکتور MEXC فیوچرز می‌باشد.

## ساختار پوشه‌ها

```
omni-arb/
├── external/                   # افزودن FinGPT و FinRL به عنوان submodule
│   ├── FinGPT/                 
│   └── FinRL/                  
├── connectors/
│   └── mexc_futures/           # کانکتور MEXC فیوچرز (REST, WS, Auth)
├── signals/
│   ├── base.py                 # اینترفیس سیگنال
│   └── sentiment_fingpt.py     # آداپتور FinGPT برای تولید سیگنال
├── policy/
│   ├── base.py                 # اینترفیس پالیسی
│   ├── rl_agent.py             # پیاده‌سازی RL Agent
│   └── rules.py                # پالیسی مبتنی بر قوانین ساده
├── exec/
│   ├── base.py                 # اینترفیس اجرایی
│   ├── engine.py               # ماژول اجرای سفارش (dry-run اولیه)
│   ├── router.py               # مسیردهی سفارش‌ها
│   └── risk.py                 # مدیریت ریسک و محاسبه اندازه سفارش
├── apps/
│   ├── api.py                  # API پروژه با FastAPI
│   └── dashboard.py            # داشبورد برای نمایش اطلاعات
├── configs/
│   ├── thresholds.yml          # آستانه‌های معاملاتی برای هر صرافی
│   └── risk.yml                # تنظیمات ریسک (EXCHANGES, LIVE, LOG_LEVEL)
├── tests/
│   └── test_smoke.py           # تست Smoke برای بررسی عملکرد اولیه
├── Makefile                    # دستورات ساخت و اجرا
├── pyproject.toml              # تنظیمات Poetry برای مدیریت وابستگی‌ها
└── README.md                   # این فایل راهنما
```

## راهنمای استفاده

1. کلون کردن مخزن:
   ```
   git clone <repository_url>
   cd omni-arb
   git submodule update --init --recursive
   ```
   جهت اضافه کردن submoduleها:
   ```
   git submodule add https://github.com/AI4Finance-Foundation/FinGPT external/FinGPT
   git submodule add https://github.com/AI4Finance-Foundation/FinRL external/FinRL
   ```

2. نصب وابستگی‌ها:
   ```
   poetry install
   ```

3. اجرای API:
   ```
   uvicorn apps.api:app --reload --port 8000
   ```

4. اجرای داشبورد:
   ```
   python apps/dashboard.py
   ```

5. اجرای تست Smoke:
   ```
   pytest tests/test_smoke.py
   ```

## تنظیمات

پیکربندی آستانه‌ها و ریسک در پوشه `configs/` قرار دارد:

- `risk.yml`: شامل لیست صرافی‌های فعال (مانند BINANCE و OKX)، وضعیت اجرای زنده (`LIVE=0`) و سطح لاگ (`LOG_LEVEL=INFO`).
- `thresholds.yml`: تعیین مقادیری مانند `net_edge_bps`، `max_leg_latency_ms`، `slippage_bps` و `min_depth_notional` برای هر صرافی.

## اعتبارسنجی فیلترهای صرافی

پیش از ارسال هر سفارش، اطلاعات نماد از طریق متد `exchangeInfo` دریافت شده و فیلترهای `LOT_SIZE` و `MIN_NOTIONAL` اعتبارسنجی می‌شوند. برای جزئیات بیش‌تر به [مستندات Binance](https://binance-docs.github.io/apidocs/spot/en/#exchange-information) مراجعه کنید.