#!/bin/bash

echo "--- Starting JARVIS AI (Phase 2: Vision & Knowledge Integration) ---"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Run Phase 2 tests
echo "🧪 Running Phase 2 tests..."
python scripts/test_phase2.py

# This script starts JARVIS AI in chat mode for Phase 2.
echo "Starting JARVIS AI (Phase 2) in chat mode..."

# Run the main JARVIS application in chat mode (which now includes Phase 2 features)
python3 main.py --mode chat

echo "JARVIS AI (Phase 2) stopped."

# Run the main application in vision mode
echo "Launching JARVIS AI in vision UI mode..."
python3 main.py --mode vision
if [ $? -ne 0 ]; then
    echo "JARVIS AI failed to start."
    exit 1
fi

# Start JARVIS AI in admin mode for API/Vision interactions
echo "Starting JARVIS AI in admin mode..."
python3 main.py --mode admin

echo "--- JARVIS AI (Phase 2) Stopped ---"

echo ""
echo "🎉 Phase 2 setup complete!"
echo ""
echo "Available interfaces:"
echo "1. 💬 Enhanced Chat (with video analysis capabilities): python main.py --mode chat"
echo "2. 🎥 Video UI (Gradio): python interface/vision/video_ui.py"
echo ""
echo "Try asking JARVIS to analyze a video or use the Video UI!"
