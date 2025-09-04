#!/bin/bash

# Emergency Incidents Analysis Setup Script
echo "🚨 Setting up Emergency Incidents Analysis Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the analysis:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the data analyzer: python data_analyzer.py"
echo "3. Run the dashboard: streamlit run dashboard.py"
echo ""
echo "📊 Your emergency incidents analysis environment is ready!"
