#!/bin/bash
# QuickCommerce API Test Setup Script

set -e

echo "======================================================"
echo "QuickCommerce API Test - PHASE 1 Setup"
echo "======================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required but not installed."; exit 1; }

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "======================================================"
echo "Setup complete!"
echo "======================================================"
echo ""
echo "IMPORTANT: Before running the test, you need a QuickCommerce API key."
echo ""
echo "Steps:"
echo "1. Visit https://quickcommerceapi.com"
echo "2. Sign up and get your API key"
echo "3. Edit backend/.env and set QUICKCOMMERCE_API_KEY=your_actual_key"
echo ""
echo "Then run the test:"
echo "  python test_quickcommerce_api.py"
echo ""
