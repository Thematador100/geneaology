#!/bin/bash

# Advanced Skip Tracing Platform - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Advanced Skip Tracing Platform..."
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.8+"; exit 1; }

# Create virtual environment
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Created virtual environment"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "✓ Installing Python dependencies..."
pip install -r requirements.txt

# Create directories
echo "✓ Creating necessary directories..."
mkdir -p uploads
mkdir -p pdf_uploads
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file..."
    cp .env.example .env
    echo "  ⚠️  Please edit .env and add your API keys!"
else
    echo "  .env file already exists"
fi

# Check for Redis
echo "✓ Checking for Redis..."
if command -v redis-server &> /dev/null; then
    echo "  Redis is installed"
else
    echo "  ⚠️  Redis not found. Install with:"
    echo "     Ubuntu/Debian: sudo apt-get install redis-server"
    echo "     macOS: brew install redis"
fi

# Check for Tesseract
echo "✓ Checking for Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    echo "  Tesseract is installed"
    tesseract --version | head -1
else
    echo "  ⚠️  Tesseract not found. Install with:"
    echo "     Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "     macOS: brew install tesseract"
fi

# Download spaCy model (optional)
echo "✓ Downloading spaCy model (optional)..."
python -m spacy download en_core_web_sm 2>/dev/null || echo "  Skipped (optional)"

# Initialize database
echo "✓ Initializing database..."
python -c "from app_new import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all(); print('  Database initialized')"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Start Redis: redis-server"
echo "  3. Start Celery: celery -A celery_app worker --loglevel=info"
echo "  4. Start app: python app_new.py"
echo ""
echo "🌐 Access the platform at: http://localhost:5000"
echo ""
