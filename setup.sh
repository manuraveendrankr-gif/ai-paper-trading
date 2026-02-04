#!/bin/bash

# TradeForge Quick Start Script

echo "=================================="
echo "TradeForge Setup & Launch"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "To start the platform:"
echo "1. Backend: python backend.py"
echo "2. Frontend: Open trading-platform.html in your browser"
echo ""
echo "Or run both with:"
echo "./start.sh"
echo ""
