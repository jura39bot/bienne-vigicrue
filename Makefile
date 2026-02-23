.PHONY: install run collect backfill show stats db-init

install:
	pip install -r requirements.txt

run:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

db-init:
	python cli/main.py db-init

collect:
	python cli/main.py collect

backfill:
	python cli/main.py collect --backfill 30

show:
	python cli/main.py show

stats:
	python cli/main.py stats

docker-up:
	docker-compose up -d api

docker-collect:
	docker-compose run --rm collector
