#!/bin/bash

# 🚀 Frontend Build Script for Sitemap to LLMS.txt
# This script builds the Svelte frontend for production deployment

set -e  # Exit on any error

echo "🔨 Building Svelte frontend..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "client/package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Navigate to client directory
cd client

# Check if pnpm is installed
if ! command -v pnpm &> /dev/null; then
    print_warning "pnpm not found, installing via npm..."
    npm install -g pnpm
fi

# Install dependencies
print_status "Installing dependencies..."
pnpm install --frozen-lockfile

# Build the application
print_status "Building Svelte application..."
pnpm build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed - dist directory not found"
    exit 1
fi

# Show build info
print_status "Build completed successfully!"
echo "📁 Build output: client/dist/"
echo "📊 Build size:"
du -sh dist/

# Check for important files
if [ -f "dist/index.html" ]; then
    print_status "✅ index.html found"
else
    print_warning "⚠️  index.html not found - SPA routing may not work"
fi

if [ -d "dist/assets" ]; then
    print_status "✅ Assets directory found"
    echo "📦 Number of asset files: $(find dist/assets -type f | wc -l)"
else
    print_warning "⚠️  Assets directory not found"
fi

echo ""
echo "🎉 Frontend build completed! Ready for deployment with Caddy."
echo "💡 Next step: Update your domain in docker/Caddyfile and run deploy.sh"
