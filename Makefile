.PHONY: up down clean front-logs back-logs swagger-up swagger-down tests

PYTEST_FLAGS = -v --tb=short

up:
	docker compose up -d --build

down:
	docker compose down

clean:
	sudo rm -rf neo4j/data neo4j/logs

front-logs:
	docker logs frontend-container

back-logs:
	docker logs backend-container

swagger-up:
	docker compose up -d swagger-service

swagger-stop:
	docker compose stop swagger-service

tests:
	cd backend && python3 -m pytest tests/ $(PYTEST_FLAGS)
