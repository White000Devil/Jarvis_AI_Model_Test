# JARVIS AI Assistant

JARVIS (Just A Rather Very Intelligent System) is an advanced AI assistant designed to integrate various AI capabilities into a unified, modular, and extensible platform. This project aims to demonstrate a multi-faceted AI system capable of natural language processing, memory management, API integrations, computer vision, ethical AI considerations, reasoning, self-correction, and continuous self-learning.

## Project Structure

The project is organized into several key directories:

-   `config.yaml`: Main configuration file for all JARVIS components.
-   `main.py`: The orchestrator, initializing and managing all AI engines.
-   `core/`: Contains the core AI engines and their functionalities.
    -   `api_integrations.py`: Manages external API calls (security, weather, etc.).
    -   `collaboration_hub.py`: Facilitates real-time human-AI collaboration.
    -   `deployment_manager.py`: Handles deployment and lifecycle of AI components.
    -   `ethical_ai.py`: Implements ethical guidelines and guardrails.
    -   `human_ai_teaming.py`: Enhances human-AI interaction and communication.
    -   `knowledge_integrator.py`: Integrates knowledge from various sources, including real-time feeds.
    -   `memory_manager.py`: Manages long-term and short-term memory (using ChromaDB).
    -   `nlp_engine.py`: Handles natural language processing tasks.
    -   `reasoning_engine.py`: Performs complex reasoning, planning, and decision-making.
    -   `self_correction.py`: Enables JARVIS to detect and correct its own errors.
    -   `self_learning.py`: Manages continuous learning from feedback and new data.
    -   `vision_engine.py`: Handles computer vision tasks (object detection, video analysis).
    -   `voice_interface.py`: Manages speech-to-text and text-to-speech.
-   `data/`: Stores persistent data like ChromaDB, logs, and cached datasets.
    -   `chroma_db/`: Persistent storage for ChromaDB.
    -   `ethical_violations/`: Logs of ethical violations.
    -   `feedback_logs/`: User feedback logs.
    -   `scraping_logs/`: Logs from web scraping activities.
    -   `self_correction_log/`: Logs of self-correction events.
    -   `video_datasets/`: Sample video metadata for vision tasks.
-   `interface/`: Contains user interfaces (Gradio-based).
    -   `admin/admin_dashboard.py`: Comprehensive admin panel for monitoring and control.
    -   `chat_interface.py`: The main conversational interface.
    -   `learning/feedback_ui.py`: UI for collecting user feedback.
    -   `vision/video_ui.py`: UI for interacting with vision capabilities.
-   `scripts/`: Utility scripts for setup, testing, and starting JARVIS.
    -   `install.sh`: Installs necessary dependencies.
    -   `setup_environment.py`: Sets up directories and initial configurations.
    -   `start_phaseX.sh`: Scripts to start JARVIS in specific development phases.
    -   `test_phaseX.py`: Unit and integration tests for each development phase.
-   `utils/`: Helper utilities.
    -   `logger.py`: Centralized logging configuration.
    -   `config_loader.py`: (Not explicitly shown, but implied for config loading)

## Setup and Installation

1.  **Clone the repository:**
    \`\`\`bash
    git clone <repository_url>
    cd jarvis-ai-assistant
    \`\`\`

2.  **Create a Python virtual environment (recommended):**
    \`\`\`bash
    python3 -m venv venv
    source venv/bin/activate # On Windows: `venv\Scripts\activate`
    \`\`\`

3.  **Install dependencies:**
    Use the provided `install.sh` script (for Linux/macOS) or manually install from `requirements.txt`.

    **On Linux/macOS:**
    \`\`\`bash
    chmod +x scripts/install.sh
    ./scripts/install.sh
    \`\`\`
    **On Windows (using Git Bash or WSL):**
    \`\`\`bash
    ./scripts/install.sh
    \`\`\`
    **Manual Installation (if `install.sh` fails or for specific environments):**
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

4.  **Configure `config.yaml`:**
    Open `config.yaml` and adjust settings as needed.
    -   **API Keys**: Replace placeholder API keys (`YOUR_SECURITY_API_KEY`, `YOUR_WEATHER_API_KEY`, `your_openai_api_key_here`, etc.) with your actual keys for external services.
    -   **Enable/Disable Features**: Toggle `enabled` flags for `vision`, `voice`, `ethical_ai`, `collaboration`, `deployment`, and `realtime_feeds` based on your needs.
    -   **Real-time Feeds**: Configure `realtime_feeds.sources` to define what real-time data JARVIS should monitor.

5.  **Set up environment (optional but recommended):**
    This script creates necessary data directories.
    \`\`\`bash
    python3 scripts/setup_environment.py
    \`\`\`

## Running JARVIS AI

JARVIS can be run in different modes using `main.py`.

-   **Chat Mode (Default):**
    Starts the Gradio chat interface.
    \`\`\`bash
    python3 main.py --mode chat
    \`\`\`

-   **Admin Dashboard Mode:**
    Starts the Gradio admin dashboard for monitoring and control.
    \`\`\`bash
    python3 main.py --mode admin
    \`\`\`

-   **Feedback UI Mode:**
    Starts a dedicated Gradio interface for collecting user feedback.
    \`\`\`bash
    python3 main.py --mode feedback
    \`\`\`

-   **Video Analysis UI Mode:**
    Starts a dedicated Gradio interface for interacting with vision capabilities.
    \`\`\`bash
    python3 main.py --mode video_analysis
    \`\`\`

## Testing

Unit and integration tests are provided for various phases of development.

To run all tests for a specific phase:

\`\`\`bash
python3 scripts/test_phase1.py
python3 scripts/test_phase2.py
python3 scripts/test_phase3.py
python3 scripts/test_phase4.py
python3 scripts/test_phase5.py
\`\`\`

## Key Features and Modules

### Core AI Engines

-   **Natural Language Processing (NLP)**: Understands user queries, extracts intent, entities, and sentiment.
-   **Memory Management**: Stores and retrieves conversational history, general knowledge, and security-specific data using ChromaDB.
-   **API Integrations**: Connects to external services for real-time data (e.g., news, threat intelligence), security analysis, weather, etc.
-   **Computer Vision**: Analyzes images and video streams for objects, events, and facial recognition.
-   **Ethical AI**: Implements guardrails to ensure responses are fair, unbiased, and safe.
-   **Reasoning Engine**: Performs multi-step reasoning, planning, and decision-making.
-   **Human-AI Teaming**: Facilitates seamless collaboration, including adaptive communication and clarification.
-   **Self-Correction**: Detects and corrects JARVIS's own errors or inconsistencies.
-   **Self-Learning**: Enables continuous improvement through user feedback, log analysis, and new data integration.
-   **Collaboration Hub**: Supports real-time multi-user interaction with JARVIS.
-   **Deployment Manager**: Manages the deployment lifecycle of JARVIS components (simulated Docker/Kubernetes).
-   **Voice Interface**: Provides speech-to-text and text-to-speech capabilities.

### Real-time Information Collection

JARVIS can now collect real-time information from configured sources. This is managed by:
-   **`config.yaml`**: Defines `realtime_feeds` with `interval_seconds` and `sources` (e.g., `security_news`, `threat_intelligence`).
-   **`core/api_integrations.py`**: Contains methods like `fetch_realtime_news` and `fetch_threat_intelligence` to simulate fetching data from external APIs.
-   **`core/knowledge_integrator.py`**: Uses `APIIntegrations` to `monitor_realtime_feeds` and integrate the fetched data into JARVIS's memory.
-   **`main.py`**: Starts a background `_run_realtime_monitoring` task that periodically calls the `KnowledgeIntegrator` to update JARVIS with fresh information.

### User Interfaces

-   **Chat Interface**: The primary way to interact with JARVIS.
-   **Admin Dashboard**: A powerful tool for administrators to monitor JARVIS's internal state, trigger learning processes, manage deployments, and view statistics.
-   **Feedback UI**: A dedicated interface for users to provide structured feedback on JARVIS's performance.
-   **Video Analysis UI**: An interface to upload and analyze images and video files using JARVIS's vision capabilities.

## Extending JARVIS

The modular design allows for easy extension:

-   **Add New APIs**: Implement new methods in `core/api_integrations.py` and integrate them into `core/reasoning_engine.py` or `core/knowledge_integrator.py`.
-   **Enhance Memory**: Integrate with other database types or knowledge graphs in `core/memory_manager.py`.
-   **Improve NLP/Vision Models**: Swap out placeholder models with more advanced ones from Hugging Face, OpenAI, etc.
-   **Custom Learning Routines**: Add new logic to `core/self_learning.py` for specific learning tasks.
-   **New UIs**: Create additional Gradio interfaces in `interface/` for specialized interactions.

## Contributing

Contributions are welcome! Please refer to the project's contribution guidelines (if any) for more details.

## License

This project is open-source and available under the [MIT License](LICENSE).
\`\`\`

```shellscript file="scripts/install.sh"
#!/bin/bash

echo "Starting JARVIS AI dependency installation..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install Python 3.8+ to proceed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null
then
    echo "pip3 is not installed. Installing pip..."
    python3 -m ensurepip --default-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install pip. Please install it manually."
        exit 1
    fi
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Please activate it manually: source venv/bin/activate"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies from requirements.txt. Please check the file and your internet connection."
    exit 1
fi

# Install specific packages that might have issues or are optional
echo "Installing optional/platform-specific dependencies..."

# For playing audio on Linux (mpg123) - user needs to install system-wide
# echo "If on Linux, consider installing mpg123 for voice output: sudo apt-get install mpg123"

# For Whisper models (if using local Whisper, not just gTTS)
# pip install openai-whisper # Uncomment if you plan to use local Whisper models

echo "Dependency installation complete. Virtual environment activated."
echo "You can now run JARVIS AI using 'python3 main.py --mode <mode>'."
echo "Remember to configure your API keys in config.yaml or as environment variables."
