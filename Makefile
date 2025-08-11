.PHONY: setup dev run test

setup:
	@echo "نصب وابستگی‌ها..."
	poetry install
	@cp -n .env.example .env || echo ".env وجود دارد."

dev:
	@echo "اجرای سرور FastAPI..."
	uvicorn apps.api:app --reload --port 8000

run:
	@echo "اجرای داشبورد..."
	python apps/dashboard.py

test:
	@echo "اجرای تست Smoke..."
	pytest tests/test_smoke.py