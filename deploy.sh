#!/bin/bash

# 🚀 Sitemap to LLMS.txt Deployment Script (Caddy Edition)
# This script automates the deployment process with Caddy for automatic SSL

set -e  # Exit on any error

echo "🚀 Starting deployment of Sitemap to LLMS.txt with Caddy..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install it first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "docker/docker-compose.prod.yml" ]; then
    print_error "Production Docker Compose file not found. Please run this script from the project root."
    exit 1
fi

# Check if frontend is built
if [ ! -d "client/dist" ]; then
    print_warning "Frontend not built. Building now..."
    if [ -f "build-frontend.sh" ]; then
        chmod +x build-frontend.sh
        ./build-frontend.sh
    else
        print_error "build-frontend.sh not found. Please build the frontend first."
        exit 1
    fi
fi

# Get domain from user
print_step "Domain Configuration"
echo "Please enter your domain name (e.g., example.com):"
read -p "Domain: " DOMAIN

if [ -z "$DOMAIN" ]; then
    print_error "Domain cannot be empty."
    exit 1
fi

print_status "Using domain: $DOMAIN"

# Update Caddyfile with domain
print_step "Updating Caddyfile configuration"
if [ -f "docker/Caddyfile" ]; then
    # Create backup
    cp docker/Caddyfile docker/Caddyfile.backup
    
    # Replace domain in Caddyfile
    sed -i "s/your-domain\.com/$DOMAIN/g" docker/Caddyfile
    
    print_status "Caddyfile updated with domain: $DOMAIN"
else
    print_error "Caddyfile not found in docker/ directory"
    exit 1
fi

# Update docker-compose with domain
print_step "Updating Docker Compose configuration"
if [ -f "docker/docker-compose.prod.yml" ]; then
    # Create backup
    cp docker/docker-compose.prod.yml docker/docker-compose.prod.yml.backup
    
    # Replace domain in docker-compose
    sed -i "s/your-domain\.com/$DOMAIN/g" docker/docker-compose.prod.yml
    
    print_status "Docker Compose updated with domain: $DOMAIN"
else
    print_error "Docker Compose file not found"
    exit 1
fi

# Navigate to docker directory
cd docker

# Stop existing containers if running
print_step "Stopping existing containers"
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Remove old images to ensure fresh build
print_step "Removing old images"
docker-compose -f docker-compose.prod.yml down --rmi all 2>/dev/null || true

# Build and start services
print_step "Building and starting services"
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for services to be healthy
print_step "Waiting for services to be healthy"
sleep 15

# Check service status
print_step "Checking service status"
docker-compose -f docker-compose.prod.yml ps

# Check health endpoints
print_step "Checking health endpoints"

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Backend is healthy"
else
    print_warning "⚠️  Backend health check failed (this might be normal during startup)"
fi

# Check Caddy health
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_status "✅ Caddy is healthy"
else
    print_warning "⚠️  Caddy health check failed (this might be normal during startup)"
fi

# Show logs
print_step "Showing recent logs (press Ctrl+C to exit logs)"
echo "----------------------------------------"
docker-compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "🚀 Deployment completed!"
echo ""
echo "📋 Service Status:"
echo "   Frontend: https://$DOMAIN"
echo "   Backend API: https://$DOMAIN/api/v1"
echo "   Health Check: https://$DOMAIN/health"
echo ""
echo "🔐 SSL/TLS: Automatically managed by Caddy"
echo "   - Certificates will be obtained automatically"
echo "   - HTTP will redirect to HTTPS"
echo "   - Certificates auto-renew every 60 days"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
echo "   View status: docker-compose -f docker-compose.prod.yml ps"
echo "   View Caddy logs: docker-compose -f docker-compose.prod.yml logs caddy"
echo ""
echo "📚 For more information, see DEPLOYMENT.md"
echo ""
echo "🌐 Your application should be available at: https://$DOMAIN"
echo "   (SSL certificate may take a few minutes to be issued)"
