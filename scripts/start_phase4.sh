#!/bin/bash

echo "--- Starting JARVIS AI (Phase 4: Voice, API, Collaboration, Deployment) ---"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Please activate your virtual environment first:"
    echo "   source venv/bin/activate"
    exit 1
fi

# Run Phase 4 tests
echo "🧪 Running Phase 4 tests..."
python scripts/test_phase4.py

# Run the main application in chat mode (or a specific UI if available for Phase 4)
echo "Launching JARVIS AI in chat mode (Phase 4 features enabled)..."
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
echo "2. 📊 Admin Dashboard (Gradio): python main.py --mode admin"
echo ""
echo "Try using voice commands or checking the Admin Dashboard!"
