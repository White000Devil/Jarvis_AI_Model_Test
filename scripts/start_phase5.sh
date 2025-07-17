#!/bin/bash

echo "--- Starting JARVIS AI (Phase 5: Advanced AI & Ethical AI) ---"

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Run Phase 5 tests
echo "🧪 Running Phase 5 tests..."
python scripts/test_phase5.py

# This script starts JARVIS AI in chat mode for Phase 5.
echo "Starting JARVIS AI (Phase 5) in chat mode..."

# Run the main JARVIS application in chat mode (which now includes Phase 5 features)
python3 main.py --mode chat

echo "JARVIS AI (Phase 5) stopped."

# Run the main application in admin dashboard mode
echo "Launching JARVIS AI Admin Dashboard..."
python3 main.py --mode admin
if [ $? -ne 0 ]; then
    echo "JARVIS AI Admin Dashboard failed to start."
    exit 1
fi

echo "--- JARVIS AI (Phase 5) Stopped ---"

echo ""
echo "🎉 Phase 5 setup complete!"
echo ""
echo "Available interfaces:"
echo "1. 💬 Advanced Chat: python main.py --mode chat"
echo "2. 📊 Admin Dashboard (Gradio): python main.py --mode admin"
echo ""
echo "Try interacting with JARVIS in the chat or explore the Admin Dashboard!"
