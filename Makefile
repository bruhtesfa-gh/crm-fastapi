.PHONY: run format lint

seed:
	poetry run python seed.py

run:
	poetry run uvicorn app.main:app --reload

format:
	poetry run isort app
	poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
	poetry run black app
	poetry run isort app

lint:
	poetry run mypy app
	poetry run black app --check
	poetry run isort --check-only app
	poetry run flake8 app
