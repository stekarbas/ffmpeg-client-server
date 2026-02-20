.PHONY: docker-compose-up-server docker-compose-logs-server docker-compose-validate docker-compose-down docker-compose-clean ffmpeg-remote

SERVER ?= http://ffmpeg-remote-server:18080
ARGS ?= --server $(SERVER) --help
HOST_PORT ?= 18080

docker-compose-up-server:
	HOST_PORT=$(HOST_PORT) docker compose up --build -d --remove-orphans ffmpeg-remote-server

ffmpeg-remote:
	@if echo "$(ARGS)" | grep -Eq -- '--server[= ]+http://localhost:|--server[= ]+http://127\.0\.0\.1:'; then \
		echo "Error: localhost points to the client container itself."; \
		echo "Use --server http://ffmpeg-remote-server:18080 when running via docker compose."; \
		exit 2; \
	fi
	docker compose --profile tools run --rm ffmpeg-remote-client $(ARGS)

docker-compose-logs-server:
	docker compose logs -f ffmpeg-remote-server

docker-compose-validate:
	HOST_PORT=$(HOST_PORT) docker compose config

docker-compose-down:
	docker compose down

docker-compose-clean:
	docker compose down --remove-orphans
