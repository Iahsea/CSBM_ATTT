.PHONY: help setup install run test clean docker-up docker-down

help:
	@echo "Backend Commands:"
	@echo "  make setup          - Setup environment (create venv + install deps)"
	@echo "  make install        - Install dependencies"
	@echo "  make run            - Run development server"
	@echo "  make test           - Run API tests"
	@echo "  make clean          - Clean cache and temp files"
	@echo "  make db-setup       - Initialize database"
	@echo "  make docker-up      - Start with Docker Compose"
	@echo "  make docker-down    - Stop Docker Compose"
	@echo "  make lint           - Run linting"
	@echo "  make format         - Format code with black"

setup:
	python -m venv venv
	@echo "✅ Virtual environment created"
	@echo "Next steps:"
	@echo "  - Windows: venv\\Scripts\\activate"
	@echo "  - Mac/Linux: source venv/bin/activate"
	@echo "  - Then run: make install"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

run:
	python main.py

test:
	python test_api.py

db-setup:
	@echo "Setting up database..."
	mysql -u root -p123456 < setup.sql
	@echo "✅ Database setup complete"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

lint:
	flake8 app/ main.py --max-line-length=120

format:
	black app/ main.py --line-length=120

docker-up:
	docker-compose up -d
	@echo "✅ Services started"
	@echo "Backend: http://localhost:8000"
	@echo "Swagger: http://localhost:8000/docs"

docker-down:
	docker-compose down
	@echo "✅ Services stopped"

docker-logs:
	docker-compose logs -f backend

requirements:
	pip freeze > requirements.txt
	@echo "✅ requirements.txt updated"
