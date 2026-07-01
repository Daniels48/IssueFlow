up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

migration:
	docker compose exec api alembic revision --autogenerate -m "$(message)"

upgrade:
	docker compose exec api alembic upgrade head

downgrade:
	docker compose exec api alembic downgrade -1

test:
	docker compose run --rm api pytest -v

lint:
	docker compose exec api ruff check .

format:
	docker compose exec api ruff format .