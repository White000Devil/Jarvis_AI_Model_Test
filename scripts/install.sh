#!/bin/bash

echo "--- Installing JARVIS AI Dependencies ---"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.8+."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install Python dependencies."
    exit 1
fi

# Run environment setup script to create necessary directories
echo "Running environment setup script..."
python3 scripts/setup_environment.py
if [ $? -ne 0 ]; then
    echo "Environment setup script failed."
    exit 1
fi

echo "--- JARVIS AI Installation Complete! ---"
echo "To activate the environment in a new terminal, run: source venv/bin/activate"
echo "Then you can run JARVIS using: python3 main.py --mode chat"
