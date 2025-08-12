# Omni-Arb

این ریپو اسکلت اولیه برای سیستم آربیتراژ **OMNI-ARB** است. تمرکز فعلی روی فاز صفر و فاز یک یعنی ساخت زیرساخت و پیاده‌سازی ماژول‌های Funding-Rate Arbitrage و Cash-and-Carry می‌باشد.

## ساختار پوشه‌ها

```
omni-arb/
├── core/
│   ├── execution/
│   │   ├── funding_arb.py
│   │   ├── cash_and_carry.py
│   │   └── cross_exchange.py
│   ├── exchange/
│   │   ├── binance.py
│   │   └── okx.py
│   └── risk/
│       ├── sizing.py
│       └── guards.py
├── orchestrator/
│   └── finrobot_flow.py
├── nlp/
│   └── fingpt_hooks.py
├── research/
│   ├── finrl_meta_scenarios/
│   ├── elegantrl_training/
│   └── deepseek_risk_fusion/
├── deploy/
│   ├── docker-compose.yml
│   └── config/
│       ├── exchanges.yml
│       ├── thresholds.yml
│       └── risk.yml
└── tests/
    └── test_smoke.py
```

## اجرا و تست

### تست سریع
```
pytest
```

### Docker Compose
```
cd deploy
docker compose up
```

این ساختار پایه برای توسعه‌های بعدی بر اساس نقشه‌راه ارائه شده آماده شده است.
