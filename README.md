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
│   └── settings.example.yaml   # فایل نمونه تنظیمات پروژه
├── tests/
│   └── test_smoke.py           # تست Smoke برای بررسی عملکرد اولیه
├── Makefile                    # دستورات ساخت و اجرا
├── pyproject.toml              # تنظیمات Poetry برای مدیریت وابستگی‌ها
├── funding.py                 # محاسبه NetEdge بر اساس نرخ‌های Funding Binance
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