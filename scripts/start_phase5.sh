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
echo "Starting JARVIS AI in chat mode with full Phase 5 capabilities..."
python3 main.py --mode chat
if [ $? -ne 0 ]; then
    echo "JARVIS AI failed to start."
    exit 1
fi

# Run the main application, perhaps starting the admin dashboard to test new features
echo "Starting JARVIS AI Admin Dashboard..."
python3 main.py --mode admin

echo "--- JARVIS AI (Phase 5) Stopped ---"

echo ""
echo "🎉 Phase 5 setup complete!"
echo ""
echo "Available interfaces:"
echo "1. 💬 Fully Integrated Chat: python main.py --mode chat"
echo "2. ⚙️ Admin Dashboard (Gradio): python main.py --mode admin"
echo "3. 🎥 Video UI (Gradio): python main.py --mode vision"
echo "4. 📝 Feedback UI (Gradio): python main.py --mode learning"
echo ""
echo "Explore JARVIS's advanced capabilities, ethical reasoning, and self-correction!"
