.PHONY: test
test:
	docker compose up --build -d
	docker compose stop edge-sim
	pytest -q
	docker compose down
