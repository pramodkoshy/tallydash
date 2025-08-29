.PHONY: help install install-dev test lint format type-check clean docker-build docker-run setup-env

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting (ruff)"
	@echo "  format       Format code (black, isort)"
	@echo "  type-check   Run type checking (mypy)"
	@echo "  clean        Clean cache and build files"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo "  setup-env    Set up conda environment"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

lint:
	ruff check src/ tests/ --fix
	flake8 src/ tests/

format:
	black src/ tests/ notebooks/
	isort src/ tests/

type-check:
	mypy src/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

docker-build:
	docker build -t tallydash .

docker-run:
	docker-compose up

setup-env:
	conda env create -f environment.yml
	conda activate tallydash
	pre-commit install

run:
	python run.py

dev:
	reflex run --env dev

build:
	reflex build

export:
	reflex export

init:
	reflex init