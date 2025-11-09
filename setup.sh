#!/bin/bash

# Setup script for AI-Powered HR Interview Platform
# This script helps automate the initial setup process

set -e

echo "=================================="
echo "HR Interview Platform Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required but not installed. Aborting."; exit 1; }
echo "✓ Python 3 found"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file with your credentials:"
    echo "   - DATABASE_URL"
    echo "   - OPENAI_API_KEY"
    echo "   - SMTP settings"
    echo ""
    echo "After editing .env, run: python init_db.py"
else
    echo "✓ .env file already exists"
    echo ""
    
    # Ask if user wants to initialize database
    read -p "Do you want to initialize the database now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Initializing database..."
        python init_db.py
        echo ""
    fi
fi

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials (if not done)"
echo "2. Run: python init_db.py (if not done)"
echo "3. Start the application: python run.py"
echo "4. Access the app at: http://localhost:5000"
echo ""
echo "Default login:"
echo "  Email: admin@hrplatform.com"
echo "  Password: admin123"
echo ""
echo "⚠️  Remember to change the default password!"
echo ""

