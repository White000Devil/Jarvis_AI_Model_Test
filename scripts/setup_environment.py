import os
import sys
from pathlib import Path
import yaml
from utils.logger import setup_logging, logger

def setup_directories(config: dict):
    """Creates necessary directories based on config."""
    data_dir = Path(config.get("DATA_DIR", "data"))
    log_dir = Path(config.get("LOG_DIR", "logs"))
    chroma_db_path = Path(config.get("CHROMA_DB_PATH", "data/chroma_db"))
    feedback_log_path = Path(config.get("FEEDBACK_LOG_PATH", "data/feedback_logs/feedback.jsonl")).parent
    scraping_log_path = Path(config.get("SCRAPING_LOG_PATH", "data/scraping_logs/scraping.jsonl")).parent
    ethical_violation_log_path = Path(config.get("ETHICAL_VIOLATION_LOG_PATH", "data/ethical_violations/violations.jsonl")).parent
    self_correction_log_path = Path(config.get("SELF_CORRECTION_LOG_PATH", "data/self_correction_log/corrections.jsonl")).parent

    dirs_to_create = [
        data_dir,
        log_dir,
        chroma_db_path,
        feedback_log_path,
        scraping_log_path,
        ethical_violation_log_path,
        self_correction_log_path,
        Path("data/video_datasets") # For vision engine
    ]

    for d in dirs_to_create:
        try:
            d.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {d}")
        except OSError as e:
            logger.error(f"Error creating directory {d}: {e}")
            sys.exit(1)

def load_config(config_path: str = "config.yaml") -> dict:
    """Loads configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found at {config_path}. Please ensure it exists.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing config file {config_path}: {e}")
        sys.exit(1)

def setup_environment():
    """
    Sets up the necessary environment variables and directories for JARVIS AI.
    """
    logger.info("Setting up JARVIS AI environment...")

    # Load configuration
    config = load_config()

    # Create data directories if they don't exist
    setup_directories(config)

    # Set up dummy environment variables if not already set (for local testing)
    # In a real deployment, these would be managed by the environment.
    os.environ.setdefault("OPENAI_API_KEY", "sk-YOUR_OPENAI_API_KEY")
    os.environ.setdefault("GITHUB_TOKEN", "ghp_YOUR_GITHUB_TOKEN")
    os.environ.setdefault("VIRUSTOTAL_API_KEY", "YOUR_VIRUSTOTAL_API_KEY")
    os.environ.setdefault("SHODAN_API_KEY", "YOUR_SHODAN_API_KEY")
    os.environ.setdefault("SLACK_TOKEN", "xoxb-YOUR_SLACK_TOKEN")
    os.environ.setdefault("DISCORD_TOKEN", "YOUR_DISCORD_TOKEN")
    os.environ.setdefault("DISCORD_SECURITY_CHANNEL", "YOUR_DISCORD_CHANNEL_ID")
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY_ID")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_ACCESS_KEY")
    os.environ.setdefault("AWS_REGION", "us-east-1")

    logger.info("Environment setup complete.")

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(str(Path(__file__).parent.parent))

    # This block is for standalone execution of setup_environment.py
    # When run via main.py, setup_logging is handled by main.py
    setup_logging(debug=True)
    logger.info("Starting environment setup...")
    setup_environment()
    logger.info("Environment setup complete.")
