#!/bin/bash
# Docker run script for Notion Report Generator

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading environment from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if NOTION_API_TOKEN is set
if [ -z "$NOTION_API_TOKEN" ]; then
    echo "❌ Error: NOTION_API_TOKEN environment variable is required"
    echo "   Set it with: export NOTION_API_TOKEN='your_token_here'"
    echo "   Or create a .env file with: NOTION_API_TOKEN=your_token_here"
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t notion-report-generator .

# Remove existing container if it exists
echo "🧹 Cleaning up existing container..."
docker rm -f notion-report-generator 2>/dev/null || true

# Run the container
echo "🚀 Starting Notion Report Generator..."
echo "   Web interface: http://localhost:8080"
echo "   API docs: http://localhost:8080/docs"
echo "   Press Ctrl+C to stop"

docker run --name notion-report-generator -p 8080:8080 \
    -e NOTION_API_TOKEN="$NOTION_API_TOKEN" \
    -e USE_LOCAL_STORAGE=true \
    -e LOCAL_STORAGE_PATH=/app/local_reports \
    -v "$(pwd)/local_reports:/app/local_reports" \
    --memory=1g \
    --memory-swap=2g \
    notion-report-generator
