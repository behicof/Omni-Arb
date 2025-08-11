# Omni-Arb Template

این ریپو به عنوان یک قالب پروژه برای اتصال ۴ ریپوی خارجی به صورت submodule تنظیم شده است.

## ساختار پوشه‌ها

omni-arb-template/           # ✅ ریپوی Template
  external/
    repoA/                   # ← submodule
    repoB/
    repoC/
    repoD/
  app/                       # کد اصلی برنامه
  tests/                     # تست‌های پروژه
  .devcontainer/
    devcontainer.json
    Dockerfile
  .github/workflows/
    init.yml
    sync-submodules.yml
  pyproject.toml             # تنظیمات Poetry (یا requirements.txt)
  Makefile
  README.md

## راهنمای استفاده

1. در صفحه ریپو، روی دکمه "Use this template" کلیک کرده و ریپوی جدید ایجاد کنید.
2. بعد از کلون کردن پروژه، دستور زیر را برای به‌روز کردن submoduleها اجرا کنید:
   
   git submodule update --init --recursive

3. سپس با اجرای دستور `make setup`، وابستگی‌ها نصب خواهند شد.
4. از Makefile برای اجرای پروژه (هدف dev) و تست‌ها (هدف test) استفاده کنید.