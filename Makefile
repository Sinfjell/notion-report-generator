# Notion Report Generator Makefile

# Configuration
PROJECT_ID := $(shell gcloud config get-value project)
REGION := europe-north1
REPO_NAME := notion-report
SERVICE_NAME := notion-report-api
IMAGE_TAG := latest
IMAGE_URI := $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/api:$(IMAGE_TAG)

# Default bucket name (override with make deploy BUCKET=your-bucket)
BUCKET := your-gcs-bucket-name

.PHONY: help setup build push deploy test clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Set up Google Cloud project and enable APIs
	@echo "Setting up Google Cloud project..."
	gcloud config set project $(PROJECT_ID)
	gcloud config set compute/region $(REGION)
	gcloud services enable run.googleapis.com storage-component.googleapis.com artifactregistry.googleapis.com
	@echo "Creating Artifact Registry repository..."
	gcloud artifacts repositories create $(REPO_NAME) --repository-format=docker --location=$(REGION) || echo "Repository may already exist"
	@echo "Creating GCS bucket..."
	gsutil mb -l $(REGION) gs://$(BUCKET) || echo "Bucket may already exist"
	@echo "Setup complete!"

build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(IMAGE_URI) .

push: build ## Push Docker image to Artifact Registry
	@echo "Pushing image to Artifact Registry..."
	docker push $(IMAGE_URI)

deploy: push ## Deploy to Cloud Run
	@echo "Deploying to Cloud Run..."
	@if [ -z "$$NOTION_API_TOKEN" ]; then \
		echo "Error: NOTION_API_TOKEN environment variable is required"; \
		exit 1; \
	fi
	gcloud run deploy $(SERVICE_NAME) \
		--image=$(IMAGE_URI) \
		--region=$(REGION) \
		--set-env-vars=NOTION_API_TOKEN=$$NOTION_API_TOKEN \
		--set-env-vars=GCS_BUCKET=$(BUCKET),NOTION_REL_PROJECT_TO_NOTES=Notes,NOTION_REL_PROJECT_TO_TASKS=Tasks,NOTION_PROJECT_PDF_URL_PROP="Latest PDF URL" \
		--allow-unauthenticated \
		--cpu=1 --memory=512Mi --timeout=120
	@echo "Getting service URL..."
	@echo "Service URL: $$(gcloud run services describe $(SERVICE_NAME) --region=$(REGION) --format='value(status.url)')"

test: ## Test the deployed service
	@echo "Testing service..."
	@RUN_URL=$$(gcloud run services describe $(SERVICE_NAME) --region=$(REGION) --format='value(status.url)') && \
	echo "Service URL: $$RUN_URL" && \
	echo "Testing health check..." && \
	curl -s "$$RUN_URL/healthz" | jq . && \
	echo "Health check passed!"

test-generate: ## Test report generation (requires PROJECT_PAGE_ID)
	@if [ -z "$(PROJECT_PAGE_ID)" ]; then \
		echo "Error: PROJECT_PAGE_ID is required. Usage: make test-generate PROJECT_PAGE_ID=your-page-id"; \
		exit 1; \
	fi
	@RUN_URL=$$(gcloud run services describe $(SERVICE_NAME) --region=$(REGION) --format='value(status.url)') && \
	echo "Testing report generation for page: $(PROJECT_PAGE_ID)" && \
	curl -s "$$RUN_URL/generate?page_id=$(PROJECT_PAGE_ID)" | jq .

logs: ## View service logs
	@echo "Viewing service logs..."
	gcloud run services logs read $(SERVICE_NAME) --region=$(REGION) --limit=50

clean: ## Clean up resources
	@echo "Cleaning up..."
	gcloud run services delete $(SERVICE_NAME) --region=$(REGION) --quiet || echo "Service not found"
	gcloud artifacts repositories delete $(REPO_NAME) --location=$(REGION) --quiet || echo "Repository not found"
	@echo "Cleanup complete!"

# Development commands
dev: ## Run locally for development
	@echo "Running locally..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

install: ## Install Python dependencies
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Quick deployment (setup + deploy)
quick-deploy: setup deploy ## Quick deployment: setup + deploy

# Example usage:
# make setup
# make deploy BUCKET=my-notion-reports-bucket
# make test-generate PROJECT_PAGE_ID=abc123-def456-ghi789