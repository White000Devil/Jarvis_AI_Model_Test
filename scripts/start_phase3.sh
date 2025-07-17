#!/bin/bash

echo "--- Starting JARVIS AI (Phase 3: Self-Learning) ---"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Run Phase 3 tests
echo "🧪 Running Phase 3 tests..."
python scripts/test_phase3.py

# This script starts JARVIS AI in chat mode for Phase 3.
echo "Starting JARVIS AI (Phase 3) in chat mode..."

# Run the main JARVIS application in chat mode (which now includes Phase 3 features)
python3 main.py --mode chat

echo "JARVIS AI (Phase 3) stopped."

# Run the main application in learning UI mode
echo "Launching JARVIS AI in learning UI mode..."
python3 main.py --mode learning
if [ $? -ne 0 ]; then
    echo "JARVIS AI failed to start."
    exit 1
fi

echo "--- JARVIS AI (Phase 3) Stopped ---"

echo ""
echo "🎉 Phase 3 setup complete!"
echo ""
echo "Available interfaces:"
echo "1. 💬 Enhanced Chat (with self-learning capabilities): python main.py --mode chat"
echo "2. 📝 Feedback UI (Gradio): python interface/learning/feedback_ui.py"
echo ""
echo "Try providing feedback to JARVIS to help it learn!"
