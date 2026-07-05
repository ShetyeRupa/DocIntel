.PHONY: help install run ingest docker-build docker-up docker-down clean test lint format

help:
	@echo "DocIntel Makefile Commands:"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run Streamlit app"
	@echo "  make ingest       - Ingest documents from data/raw/"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Run with Docker Compose"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make test         - Run unit tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean temporary files"

install:
	pip install -r requirements.txt

run:
	streamlit run app/ui/streamlit_app.py

ingest:
	python scripts/ingest_documents.py data/raw/

docker-build:
	docker build -t docintel .

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	ruff check app/
	mypy app/ --ignore-missing-imports

format:
	black app/
	isort app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml
	rm -rf *.log
	rm -rf *.json