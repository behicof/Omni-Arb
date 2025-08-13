.PHONY: install test run deploy monitor

install:
	pip install -r requirements.txt

test:
	pytest tests/

run:
	python -m orchestrator.pipeline

deploy:
	docker-compose up -d

monitor:
	open http://localhost:3000  # Grafana
