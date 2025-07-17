#!/bin/bash

echo "--- Starting JARVIS AI (Phase 4: Advanced Integrations) ---"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Run Phase 4 tests
echo "🧪 Running Phase 4 tests..."
python scripts/test_phase4.py

# This script starts JARVIS AI in chat mode for Phase 4.
echo "Launching JARVIS AI in chat mode..."
python3 main.py --mode chat
if [ $? -ne 0 ]; then
    echo "JARVIS AI failed to start."
    exit 1
fi

echo "--- JARVIS AI (Phase 4) Stopped ---"

echo ""
echo "🎉 Phase 4 setup complete!"
echo ""
echo "Available interfaces:"
echo "1. 💬 Enhanced Chat (with voice, API, collaboration, deployment capabilities): python main.py --mode chat"
echo "2. ⚙️ Admin Dashboard (Gradio): python main.py --mode admin"
echo ""
echo "Try interacting with JARVIS using voice commands or check the admin dashboard!"
