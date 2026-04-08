COMPOSE ?= docker compose
PYTHON ?= python3
PIP ?= pip3

.PHONY: help build run stop restart logs clean test install lint check dev-run dev-test status ps

help:
	@echo "Zyxel 5G Router Prometheus Exporter"
	@echo ""
	@echo "Available targets:"
	@echo "  build         - Build Docker image"
	@echo "  run           - Start exporter container"
	@echo "  stop          - Stop exporter container"
	@echo "  restart       - Restart exporter container"
	@echo "  logs          - Show exporter logs"
	@echo "  clean         - Remove containers and images"
	@echo "  test          - Test the exporter endpoint"
	@echo "  install       - Install Python dependencies"
	@echo "  lint          - Run ruff"
	@echo "  check         - Run syntax, tests, and lint"
	@echo "  dev-run       - Run exporter with local Python"
	@echo "  dev-test      - Run unit tests"
	@echo "  status        - Show compose status"

build:
	$(COMPOSE) build

run:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

clean:
	$(COMPOSE) down -v
	docker image rm zyxel-cellwan-exporter:latest 2>/dev/null || true

test:
	@echo "Testing exporter endpoint..."
	@curl -s http://localhost:9101/metrics | head -20

install:
	$(PIP) install -r requirements.txt

lint:
	$(PYTHON) -m ruff check .

check:
	$(PYTHON) -m py_compile cellwan_exporter.py
	$(PYTHON) -m unittest discover -s tests -v
	$(PYTHON) -m ruff check .

# Development targets
dev-run:
	$(PYTHON) cellwan_exporter.py

dev-test:
	$(PYTHON) -m unittest discover -s tests -v

# Status checks
status:
	$(COMPOSE) ps

ps:
	$(COMPOSE) ps
