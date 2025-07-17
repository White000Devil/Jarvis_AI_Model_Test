#!/bin/bash

echo "--- Starting JARVIS AI (Phase 1: NLP & Memory) ---"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Run Phase 1 tests
echo "🧪 Running Phase 1 tests..."
python scripts/test_phase1.py

# This script starts JARVIS AI in chat mode for Phase 1.
echo "Launching JARVIS AI in chat mode..."
python3 main.py --mode chat
if [ $? -ne 0 ]; then
    echo "JARVIS AI failed to start."
    exit 1
fi

echo "--- JARVIS AI (Phase 1) Stopped ---"
