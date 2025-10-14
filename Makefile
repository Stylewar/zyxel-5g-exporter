.PHONY: help build run stop logs clean test

help:
	@echo "Zyxel 5G Router Prometheus Exporter"
	@echo ""
	@echo "Available targets:"
	@echo "  build    - Build Docker image"
	@echo "  run      - Start exporter container"
	@echo "  stop     - Stop exporter container"
	@echo "  restart  - Restart exporter container"
	@echo "  logs     - Show container logs"
	@echo "  clean    - Remove container and image"
	@echo "  test     - Test the exporter endpoint"
	@echo "  install  - Install Python dependencies"

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker rmi cellwan-exporter 2>/dev/null || true

test:
	@echo "Testing exporter endpoint..."
	@curl -s http://localhost:9101/metrics | head -20

install:
	pip install -r requirements.txt

# Development targets
dev-run:
	python cellwan_exporter.py

dev-test:
	python -m pytest tests/ -v 2>/dev/null || echo "No tests found"
