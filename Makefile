.PHONY: dev ingest test build clean logs

# Development
dev:
	docker-compose up --build

dev-detached:
	docker-compose up --build -d

# Ingestion
ingest:
	docker-compose run --rm ingest-worker python worker.py --once

ingest-continuous:
	docker-compose run --rm ingest-worker python worker.py

# Testing
test:
	@echo "Running tests..."
	@echo "TODO: Add test commands for each service"

test-ingress:
	cd services/ingress-bot && npm test

test-retrieval:
	cd services/retrieval-service && python -m pytest

# Building
build:
	docker-compose build

build-ingress:
	docker-compose build ingress-bot

build-retrieval:
	docker-compose build retrieval-service

build-ingest:
	docker-compose build ingest-worker

# Logs
logs:
	docker-compose logs -f

logs-ingress:
	docker-compose logs -f ingress-bot

logs-retrieval:
	docker-compose logs -f retrieval-service

logs-ingest:
	docker-compose logs -f ingest-worker

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

clean-all:
	docker-compose down -v --rmi all
	docker system prune -af

# Health checks
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8080/health || echo "Retrieval service not responding"
	@curl -s http://localhost:3000/health || echo "Ingress bot not responding"

# Setup
setup:
	@echo "Setting up development environment..."
	@mkdir -p corpus
	@mkdir -p prompts
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; fi
	@echo "Setup complete. Please edit .env with your API keys."

# Local Ollama setup
setup-ollama:
	docker-compose --profile local-llm up -d ollama
	@echo "Waiting for Ollama to start..."
	@sleep 10
	docker exec ollama ollama pull llama2
	@echo "Ollama setup complete"

# Production deployment
deploy:
	@echo "TODO: Add production deployment commands"
	@echo "This would typically involve:"
	@echo "1. Building production images"
	@echo "2. Pushing to registry"
	@echo "3. Running terraform apply" 