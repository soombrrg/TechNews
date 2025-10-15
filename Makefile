manage = uv run python src/manage.py

deps:
	uv sync

fmt:
	black src
	isort src

lint:
	mypy src
	flake8 src

test:
	cd src && uv run pytest

prep:
	$(manage) makemigrations
	$(manage) migrate

up:
	cd src && uvicorn app.asgi:application --host 0.0.0.0 --port 8000 --reload

up-prod: fmt lint
	$(manage) collectstatic --no-input
	$(manage) migrate
	cd src && uvicorn app.asgi:application --host 0.0.0.0 --port 8000

build:
	docker build -t test .


