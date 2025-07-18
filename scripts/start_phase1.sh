#!/bin/bash

echo "Starting JARVIS AI - Phase 1 (NLP & Memory)"

# Activate the virtual environment
source venv/bin/activate

# Run the main application in chat mode
# In a real Phase 1, you might have a simplified main.py that only initializes NLP and Memory
python3 main.py --mode chat
