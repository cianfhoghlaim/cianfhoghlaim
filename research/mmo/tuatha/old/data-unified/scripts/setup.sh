#!/bin/bash

# Setup script for data-unified

set -e

echo "🚀 Setting up Data Unified..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm version: $(npm --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please update with your credentials."
else
    echo "✅ .env file already exists"
fi

# Check if Redis/Dragonfly is running
echo ""
echo "🔍 Checking for Redis/Dragonfly..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Starting with Docker Compose..."
        docker-compose up -d dragonfly
        echo "✅ Dragonfly started"
    fi
else
    echo "⚠️  redis-cli not found. Starting services with Docker Compose..."
    docker-compose up -d
    echo "✅ Services started"
fi

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 3

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Visit http://localhost:3000 to see the API"
echo "4. Run 'curl -X POST http://localhost:3000/seed' to create sample data"
echo ""
