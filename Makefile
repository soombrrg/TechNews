up-prod:
	docker compose up

up-dev:
	docker compose up postgres redis s3

back:
	cd backend && make up

front:
	cd frontend && npm run dev

back-deps:
	cd backend && make deps

back-prep:
	cd backend && make prep

build:
	docker compose build
