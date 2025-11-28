.PHONY: help build run stop logs shell test clean rebuild up down ps

# Variables
IMAGE_NAME := prometheus-task
IMAGE_TAG := 1.0
IMAGE := $(IMAGE_NAME):$(IMAGE_TAG)
CONTAINER_NAME := prometheus-task-manager

help: ## Display this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

# Build targets
build: ## Build Docker image
	docker build --network=host -t $(IMAGE) .

build-nocache: ## Build without cache
	docker build --no-cache -t $(IMAGE) .

# Compose targets
up: build ## Start services with docker-compose
	docker-compose up -d
	@docker-compose ps

down: ## Stop and remove services
	docker-compose down

restart: ## Restart services
	docker-compose restart

# Container targets
run: build ## Build and run the simulation interactively
	docker run -it --rm \
		--name $(CONTAINER_NAME) \
		-v $$(pwd)/prometheus_task:/app/prometheus_task \
		$(IMAGE) \
		python3 test_scenarios.py

stop: ## Stop running container
	docker stop $(CONTAINER_NAME) 2>/dev/null || true
	docker rm $(CONTAINER_NAME) 2>/dev/null || true

ps: ## Show running containers
	docker-compose ps

logs: ## Show logs from all services
	docker-compose logs -f

# Interactive targets
shell: ## Open interactive shell in container
	docker-compose exec prometheus-task bash

python: ## Open Python shell in container
	docker-compose exec prometheus-task python3

# Testing targets
test: up ## Run test suite
	docker-compose exec prometheus-task python3 -m pytest test_suite.py -v

# Cleanup targets
clean: down ## Remove containers and volumes
	docker-compose down -v

remove-image: ## Remove Docker image
	docker rmi $(IMAGE) 2>/dev/null || true

distclean: clean remove-image ## Full cleanup

# Info targets
info: ## Display environment info
	@echo "Image: $(IMAGE)"
	@echo "Container: $(CONTAINER_NAME)"
	@docker --version
	@docker-compose --version

.DEFAULT_GOAL := help
