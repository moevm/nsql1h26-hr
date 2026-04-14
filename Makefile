.PHONY: up down clean front-logs back-logs swagger-up swagger-down

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