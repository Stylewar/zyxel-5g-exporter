.PHONY: help build run stop logs clean test install

help:
	@echo "Zyxel 5G Router Prometheus Exporter"
	@echo ""
	@echo "Available targets:"
	@echo "  build         - Build Docker image"
	@echo "  run           - Start full stack (exporter + prometheus + grafana)"
	@echo "  run-exporter  - Start exporter only"
	@echo "  stop          - Stop all services"
	@echo "  stop-exporter - Stop exporter only"
	@echo "  restart       - Restart all services"
	@echo "  logs          - Show container logs (full stack)"
	@echo "  logs-exporter - Show exporter logs only"
	@echo "  clean         - Remove containers and images"
	@echo "  test          - Test the exporter endpoint"
	@echo "  install       - Install Python dependencies"
	@echo ""
	@echo "Docker Compose Files:"
	@echo "  docker-compose.yml          - Full stack (exporter + prometheus + grafana)"
	@echo "  docker-compose.exporter.yml - Exporter only"

build:
	docker-compose build

run:
	@echo "Starting full stack (exporter + prometheus + grafana)..."
	docker-compose up -d

run-exporter:
	@echo "Starting exporter only..."
	docker-compose -f docker-compose.exporter.yml up -d

stop:
	docker-compose down

stop-exporter:
	docker-compose -f docker-compose.exporter.yml down

restart:
	docker-compose restart

restart-exporter:
	docker-compose -f docker-compose.exporter.yml restart

logs:
	docker-compose logs -f

logs-exporter:
	docker-compose -f docker-compose.exporter.yml logs -f

clean:
	docker-compose down -v
	docker-compose -f docker-compose.exporter.yml down -v
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

# Status checks
status:
	@echo "=== Full Stack Status ==="
	@docker-compose ps
	@echo ""
	@echo "=== Exporter Only Status ==="
	@docker-compose -f docker-compose.exporter.yml ps

ps:
	docker-compose ps

ps-exporter:
	docker-compose -f docker-compose.exporter.yml ps
