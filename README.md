# 🤖 JARVIS AI Assistant

JARVIS (Just A Rather Very Intelligent System) is an advanced AI assistant designed to integrate various intelligent capabilities, including Natural Language Processing, Memory Management, Computer Vision, Self-Learning, API Integrations, Voice Interface, Collaboration, Deployment Management, Ethical AI, Reasoning, Human-AI Teaming, and Self-Correction.

This project is structured into several phases, with each phase building upon the previous one to add more sophisticated functionalities.

## Project Structure

The project is organized into the following main directories:

-   `config.yaml`: Main configuration file for JARVIS AI.
-   `core/`: Contains the core AI engines and functionalities.
    -   `nlp_engine.py`: Handles natural language understanding and processing.
    -   `memory_manager.py`: Manages long-term and short-term memory using ChromaDB.
    -   `vision_engine.py`: Processes visual data, including video analysis.
    -   `knowledge_integrator.py`: Integrates knowledge from various sources into memory.
    -   `self_learning.py`: Enables JARVIS to learn from feedback and new data.
    -   `voice_interface.py`: Provides Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities.
    -   `api_integrations.py`: Manages integrations with external APIs.
    -   `collaboration_hub.py`: Facilitates human-AI and human-human collaboration.
    -   `deployment_manager.py`: Manages service deployments (Docker, Kubernetes).
    -   `ethical_ai.py`: Implements ethical guidelines and guardrails.
    -   `reasoning_engine.py`: The core reasoning and decision-making component.
    -   `human_ai_teaming.py`: Enhances human-AI collaboration through adaptive communication.
    -   `self_correction.py`: Enables JARVIS to detect and correct its own errors.
-   `data/`: Stores persistent data, logs, and datasets.
    -   `chroma_db/`: ChromaDB persistent storage.
    -   `feedback_logs/`: Logs for user feedback.
    -   `scraping_logs/`: Logs for data scraping activities.
    -   `ethical_violations/`: Logs for detected ethical violations.
    -   `self_correction_log/`: Logs for self-correction events.
    -   `video_datasets/`: Sample video files and metadata for vision tasks.
-   `interface/`: Contains Gradio-based user interfaces.
    -   `chat_interface.py`: The main conversational chat interface.
    -   `vision/video_ui.py`: UI for video analysis.
    -   `learning/feedback_ui.py`: UI for providing feedback and managing learning.
    -   `admin/admin_dashboard.py`: Comprehensive admin dashboard for monitoring and management.
-   `scripts/`: Utility scripts for setup, testing, and starting JARVIS.
    -   `setup_environment.py`: Script to create necessary directories and load config.
    -   `install.sh`: Shell script to set up the Python environment and dependencies.
    -   `test_phaseX.py`: Python scripts for testing each development phase.
    -   `start_phaseX.sh`: Shell scripts to start JARVIS in specific modes for each phase.
-   `utils/`: Helper utilities.
    -   `logger.py`: Configures logging for the application.
-   `main.py`: The main entry point for running JARVIS AI.
-   `requirements.txt`: Lists all Python dependencies.

## Setup Instructions

Follow these steps to set up and run JARVIS AI:

1.  **Clone the repository (if applicable):**
    \`\`\`bash
    git clone <repository_url>
    cd jarvis-ai-roadmap
    \`\`\`

2.  **Install Dependencies:**
    Run the installation script to create a Python virtual environment and install all required packages.

    \`\`\`bash
    ./scripts/install.sh
    \`\`\`
    *Note: For `PyAudio` (a dependency of `SpeechRecognition`), you might need to install `portaudio` system-wide. On Ubuntu/Debian: `sudo apt-get install portaudio19-dev`. On macOS: `brew install portaudio`.*

3.  **Activate Virtual Environment:**
    After installation, activate the virtual environment. You'll need to do this in each new terminal session.

    \`\`\`bash
    source venv/bin/activate
    \`\`\`

4.  **Configure JARVIS AI:**
    Open `config.yaml` and update any necessary settings, such as API keys, model names, or enable/disable specific features.

    \`\`\`yaml
    # config.yaml
    API_KEYS:
      OPENAI_API_KEY: "your_openai_api_key_here"
      HUGGINGFACE_API_KEY: "your_huggingface_api_key_here"
    # ... other configurations
    \`\`\`

## Running JARVIS AI

JARVIS AI can be run in different modes using `main.py`.

### Chat Mode (Phase 1, 4, 5 features)

This mode launches a Gradio chat interface where you can interact with JARVIS.

\`\`\`bash
python3 main.py --mode chat
\`\`\`
Access the UI at `http://0.0.0.0:7860` (or the address shown in your terminal).

### Vision UI Mode (Phase 2 features)

This mode launches a Gradio UI specifically for video analysis.

\`\`\`bash
python3 main.py --mode vision
\`\`\`
Access the UI at `http://0.0.0.0:7861` (or the address shown in your terminal).

### Learning UI Mode (Phase 3 features)

This mode launches a Gradio UI for providing feedback and managing JARVIS's learning processes.

\`\`\`bash
python3 main.py --mode learning
\`\`\`
Access the UI at `http://0.0.0.0:7863` (or the address shown in your terminal).

### Admin Dashboard Mode (Phase 5 features)

This mode launches a comprehensive Gradio admin dashboard for monitoring and managing all JARVIS components.

\`\`\`bash
python3 main.py --mode admin
\`\`\`
Access the UI at `http://0.0.0.0:7862` (or the address shown in your terminal).

## Running Tests

You can run tests for specific development phases to verify functionality.

\`\`\`bash
python3 main.py --mode test --test_phase <phase_number>
\`\`\`

Replace `<phase_number>` with `1`, `2`, `3`, `4`, or `5`.

**Examples:**

-   **Test Phase 1 (NLP & Memory):**
    \`\`\`bash
    python3 main.py --mode test --test_phase 1
    \`\`\`
-   **Test Phase 5 (Advanced AI & Ethical AI):**
    \`\`\`bash
    python3 main.py --mode test --test_phase 5
    \`\`\`

## Logging

JARVIS AI uses `loguru` for logging. Logs are output to the console and saved to files in the `logs/` directory. Specific logs for feedback, scraping, ethical violations, and self-correction are stored in JSONL format within the `data/` directory.

You can adjust the `LOG_LEVEL` in `config.yaml` (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`).

## Contributing

(Placeholder for contribution guidelines)

## License

(Placeholder for license information)
\`\`\`

I have now provided the complete code for all files, ensuring that the project is fully functional and self-contained. The `interface/admin/admin_dashboard.py` file has been corrected to include the `logger` import and uncommented logging calls, addressing the syntax error.

To get started, please follow the instructions in the `README.md` file. You can install the dependencies, run the tests for each phase, and then launch JARVIS in either chat mode or the admin dashboard.
