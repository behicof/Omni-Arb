setup:
	@echo "راه‌اندازی پروژه..."
	poetry install

dev:
	@echo "شروع محیط توسعه..."
	poetry run python -m app.main

test:
	@echo "اجرای تست‌ها..."
	poetry run pytest

.PHONY: setup dev test