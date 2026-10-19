# Product Comparison POC - Build & Run Commands
#
# Usage:
#   make help            - show available targets
#   make setup           - install deps for backend + price-whiz
#   make backend         - run FastAPI backend (http://localhost:8000)
#   make whiz            - run app-price-whiz (Vite, http://localhost:5173)
#   make dev             - run backend + price-whiz together in one terminal
#   make test            - run QuickCommerce API integration test
#   make lint            - lint price-whiz
#   make docker-up       - build & start backend + frontend in Docker
#   make docker-down     - stop the Docker stack
#   make docker-logs     - follow Docker stack logs

BACKEND_DIR    := backend
WHIZ_DIR       := app-price-whiz

PYTHON         ?= python3
PIP            ?= pip
VITE_PORT      ?= 5173

.PHONY: help setup backend whiz dev test lint clean docker-up docker-down docker-logs

help:
	@echo "Product Comparison POC"
	@echo ""
	@echo "  make setup        Install all dependencies"
	@echo "  make dev          Run backend + price-whiz together"
	@echo "  make backend      Run FastAPI backend  (http://localhost:8000)"
	@echo "  make whiz         Run price-whiz app   (http://localhost:$(VITE_PORT))"
	@echo "  make test         Run QuickCommerce integration test"
	@echo "  make lint         Lint price-whiz"
	@echo "  make clean        Remove caches and build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    Build & start backend + frontend (http://localhost:5173)"
	@echo "  make docker-down  Stop the Docker stack"
	@echo "  make docker-logs  Follow Docker stack logs"

setup:
	cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt
	cd $(WHIZ_DIR) && npm install

backend:
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload

whiz:
	cd $(WHIZ_DIR) && npm run dev -- --port $(VITE_PORT)

# Run both in one terminal. Ctrl+C stops both.
dev:
	$(MAKE) -j2 backend whiz

test:
	cd $(BACKEND_DIR) && $(PYTHON) test_quickcommerce_api.py

lint:
	cd $(WHIZ_DIR) && npm run lint

clean:
	rm -rf $(BACKEND_DIR)/__pycache__ $(BACKEND_DIR)/app/__pycache__ \
	       $(BACKEND_DIR)/.pytest_cache $(BACKEND_DIR)/.venv
	cd $(WHIZ_DIR) && rm -rf dist
	find . -name "*.pyc" -delete

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f
