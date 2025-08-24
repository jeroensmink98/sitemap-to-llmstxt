#!/bin/bash

echo "🚀 Starting Sitemap to LLMS.txt API with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start the services
echo "📦 Starting services..."
docker-compose -f docker/docker-compose.yml up -d

echo "✅ Services started!"
echo ""
echo "🌐 API is running at: http://localhost:8000"
echo "📚 API documentation: http://localhost:8000/docs"
echo "🔍 Health check: http://localhost:8000/health"
echo "🌸 Celery Flower (monitoring): http://localhost:5555"
echo ""
echo "📋 To stop services: docker-compose -f docker/docker-compose.yml down"
echo "📋 To view logs: docker-compose -f docker/docker-compose.yml logs -f"
