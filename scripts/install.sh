#!/bin/bash

echo "Starting JARVIS AI dependency installation..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.8+ to proceed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Installing pip..."
    python3 -m ensurepip --default-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install pip. Please install it manually."
        exit 1
    fi
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
    echo "Failed to activate virtual environment. Please activate it manually: source venv/bin/activate"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies from requirements.txt. Please check the file and your internet connection."
        exit 1
    fi
else
    echo "requirements.txt not found. Please ensure it exists in the project root."
    exit 1
fi

# Set up directories
echo "Setting up directories..."
python3 scripts/setup_directories.py

# Install specific packages that might have issues or are optional
echo "Installing optional/platform-specific dependencies..."

# For playing audio on Linux (mpg123) - user needs to install system-wide
# echo "If on Linux, consider installing mpg123 for voice output: sudo apt-get install mpg123"

# For Whisper models (if using local Whisper, not just gTTS)
# pip install openai-whisper # Uncomment if you plan to use local Whisper models

echo "Dependency installation complete. Virtual environment activated."
echo "You can now run JARVIS AI using 'python3 main.py --mode <mode>'."
echo "Available modes: chat, admin, feedback, video_analysis"
echo "Remember to configure your API keys in config.yaml."
