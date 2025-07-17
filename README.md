# JARVIS AI Assistant (v12.0.0)

JARVIS AI is an advanced, modular, and self-improving artificial intelligence assistant designed to assist with a wide range of tasks, from natural language understanding and security analysis to collaborative operations and ethical decision-making. This project is structured into several phases, each building upon the last to create a comprehensive AI system.

## Project Structure

The project is organized into the following key directories:

-   `config.yaml`: Central configuration file for all JARVIS AI components.
-   `core/`: Contains the core AI engines and functionalities.
    -   `nlp_engine.py`: Natural Language Processing for understanding user queries.
    -   `memory_manager.py`: Manages long-term and short-term memory using ChromaDB.
    -   `vision_engine.py`: Handles video analysis, object detection, and anomaly detection.
    -   `knowledge_integrator.py`: Integrates various data sources into the knowledge base.
    -   `self_learning.py`: Enables learning from feedback, web scraping, and optimization.
    -   `voice_interface.py`: Provides speech-to-text (STT) and text-to-speech (TTS) capabilities.
    -   `api_integrations.py`: Manages external API calls (e.g., security, weather).
    -   `collaboration_hub.py`: Facilitates multi-user collaboration and session management.
    -   `deployment_manager.py`: Handles deployment tasks (e.g., Docker, Kubernetes).
    -   `ethical_ai.py`: Implements ethical guardrails and violation detection.
    -   `reasoning_engine.py`: Performs complex reasoning, planning, and decision-making.
    -   `human_ai_teaming.py`: Enhances human-AI collaboration through adaptive communication.
    -   `self_correction.py`: Enables JARVIS to detect and correct its own inconsistencies.
-   `interface/`: Contains user interfaces for interacting with JARVIS.
    -   `chat_interface.py`: Gradio-based command-line chat interface.
    -   `vision/video_ui.py`: Gradio UI for video analysis and screen recording.
    -   `learning/feedback_ui.py`: Gradio UI for collecting user feedback and managing learning.
    -   `admin/admin_dashboard.py`: Comprehensive Gradio dashboard for monitoring and managing all components.
-   `scripts/`: Utility scripts for setup, testing, and starting JARVIS.
    -   `install.sh`: Installs Python dependencies and sets up the environment.
    -   `setup_environment.py`: Configures environment variables and creates data directories.
    -   `start_phaseX.sh`: Scripts to start JARVIS in specific development phases.
    -   `test_phaseX.py`: Scripts to run tests for specific development phases.
-   `utils/`: Helper utilities.
    -   `logger.py`: Centralized logging configuration using Loguru.
-   `data/`: Stores persistent data (ChromaDB, logs, video datasets, etc.).

## Setup Instructions

Follow these steps to set up and run JARVIS AI:

1.  **Clone the repository (if not already done):**
    \`\`\`bash
    git clone <repository_url>
    cd Jarvis_AI_Model_Test
    \`\`\`

2.  **Install Dependencies:**
    Run the installation script. This will create a Python virtual environment, install all required packages from `requirements.txt`, and set up necessary data directories.
    \`\`\`bash
    ./scripts/install.sh
    \`\`\`

3.  **Activate the Virtual Environment:**
    You'll need to activate the virtual environment in each new terminal session where you want to run JARVIS.
    \`\`\`bash
    source venv/bin/activate
    \`\`\`

4.  **Configure API Keys (Optional but Recommended):**
    Edit `config.yaml` to add your actual API keys for services like OpenAI, Hugging Face, security APIs, etc.
    \`\`\`yaml
    # config.yaml
    api_integrations:
      openai_api_key: "your_openai_api_key_here"
      huggingface_api_key: "your_huggingface_api_key_here"
      security_api_key: "YOUR_SECURITY_API_KEY"
      weather_api_key: "YOUR_WEATHER_API_KEY"
    \`\`\`

## Running JARVIS AI

JARVIS AI can be run in different modes using `main.py`.

### Chat Mode (Interactive CLI)

This is the primary way to interact with JARVIS.
\`\`\`bash
python3 main.py --mode chat
\`\`\`

### Admin Dashboard (Gradio UI)

Access a web-based dashboard to monitor and manage JARVIS components.
\`\`\`bash
python3 main.py --mode admin
\`\`\`
(The dashboard will typically launch on `http://0.0.0.0:7862` or a similar address.)

### Video Analysis UI (Gradio UI)

Upload videos for analysis or simulate screen recording.
\`\`\`bash
python3 main.py --mode vision
\`\`\`
(The video UI will typically launch on `http://0.0.0.0:7861` or a similar address.)

### Feedback & Learning UI (Gradio UI)

Provide feedback to JARVIS and trigger learning processes.
\`\`\`bash
python3 main.py --mode learning
\`\`\`
(The feedback UI will typically launch on `http://0.0.0.0:7863` or a similar address.)

## Testing

Each phase has a dedicated test script. You can run all tests for a specific phase:

\`\`\`bash
# Test Phase 1 (NLP & Memory)
python3 scripts/test_phase1.py

# Test Phase 2 (Vision & Knowledge Integration)
python3 scripts/test_phase2.py

# Test Phase 3 (Self-Learning)
python3 scripts/test_phase3.py

# Test Phase 4 (Voice, API, Collaboration, Deployment)
python3 scripts/test_phase4.py

# Test Phase 5 (Ethical AI, Reasoning, Human-AI Teaming, Self-Correction)
python3 scripts/test_phase5.py
\`\`\`

## Development Phases Overview

-   **Phase 1: NLP & Memory**: Core natural language understanding and persistent memory.
-   **Phase 2: Vision & Knowledge Integration**: Visual data analysis and integration of diverse knowledge sources.
-   **Phase 3: Self-Learning**: Feedback processing, web scraping for new knowledge, and parameter optimization.
-   **Phase 4: Advanced Integrations**: Voice interface, external API integrations, collaboration hub, and deployment management.
-   **Phase 5: Advanced AI & Ethical AI**: Ethical guardrails, sophisticated reasoning, human-AI teaming, and self-correction capabilities.

## Contributing

Contributions are welcome! Please refer to the project's guidelines for more information.

---

**Note:** This project uses mock implementations for certain external services (e.g., actual model inference, real-time API calls, complex web scraping) to ensure it's runnable in various environments without requiring extensive setup or live credentials. For production use, these would be replaced with robust, real-world integrations.
