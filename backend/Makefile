manage = uv run python src/manage.py

deps:
	uv sync

fmt:
	uv run black src
	uv run isort src

lint:
	uv run flake8 src
	uv run mypy src

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
	docker build -t back .

worker:
	uv run celery -A app --workdir src worker --loglevel=info --events --purge

schema:
	$(manage) spectacular --color --file schema.yml --api-version v1