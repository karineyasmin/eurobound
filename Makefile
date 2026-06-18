.PHONY: init down build-package db-shell clean

SHELL := /bin/bash

# Automatizações do Ambiente EuroBound

init:
	@echo "=> Initializing virtual environment with uv..."
	uv venv
	uv pip install -e .

run-api:
	@echo "=> Starting FastAPI Backend on http://localhost:8000..."
	uv run uvicorn backend.app.main:app --reload --port 8000

run-front:
	@echo "=> Starting Streamlit Frontend on http://localhost:8501..."
	uv run streamlit run frontend/app.py

run:
	@echo "=> Starting EuroBound Ecosystem (API + Front)..."
	trap 'kill 0' EXIT; \
	uv run uvicorn backend.app.main:app --port 8000 & \
	uv run streamlit run frontend/app.py

build:
	@echo "=> Compiling project wheel..."
	cd backend && uv build

up:
	@echo "=> Starting PostGIS container..."
	docker compose up -d

down: 
	@echo "=> Stoping database container..."
	docker compose down


db-shell:
	@echo "=> Connecting to interactive PostGIS shell..."
	docker exec it eurobound_spatial_db psql -U geouser -d eurobound_spatial_db

clean:
	@echo "=> Cleaning up build artifacts and caches..."
	rm -rf backend/dist/ backend/*.egg-info backend/.uv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "=> Clean up complete!"

