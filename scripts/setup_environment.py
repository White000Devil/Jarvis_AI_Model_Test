import os
import yaml
from utils.logger import setup_logging, logger

def setup_directories(config: dict):
    """Ensures all necessary data and log directories exist."""
    app_config = config.get("app", {})
    data_dir = app_config.get("data_dir", "data")
    log_dir = app_config.get("log_dir", "logs")

    # Create base data and log directories
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    logger.info(f"Ensured base data directory: {data_dir}")
    logger.info(f"Ensured base log directory: {log_dir}")

    # Create specific sub-directories based on config paths
    memory_config = config.get("memory", {})
    if memory_config.get("db_type") == "chromadb":
        chroma_path = memory_config.get("chroma_path", os.path.join(data_dir, "chroma_db"))
        os.makedirs(chroma_path, exist_ok=True)
        logger.info(f"Ensured ChromaDB directory: {chroma_path}")

    vision_config = config.get("vision", {})
    if vision_config.get("enabled"):
        cache_dir = vision_config.get("cache_dir", os.path.join(data_dir, "vision_cache"))
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Ensured Vision cache directory: {cache_dir}")

    learning_config = config.get("learning", {})
    if learning_config.get("feedback_collection"):
        feedback_log_path = learning_config.get("feedback_log_path", os.path.join(data_dir, "feedback_logs", "feedback.jsonl"))
        os.makedirs(os.path.dirname(feedback_log_path), exist_ok=True)
        logger.info(f"Ensured Feedback logs directory: {os.path.dirname(feedback_log_path)}")
    if learning_config.get("scraping_enabled"):
        scraping_log_path = learning_config.get("scraping_log_path", os.path.join(data_dir, "scraping_logs", "scraping.jsonl"))
        os.makedirs(os.path.dirname(scraping_log_path), exist_ok=True)
        logger.info(f"Ensured Scraping logs directory: {os.path.dirname(scraping_log_path)}")

    ethical_ai_config = config.get("ethical_ai", {})
    if ethical_ai_config.get("enabled") and ethical_ai_config.get("log_violations"):
        ethical_violation_log_path = ethical_ai_config.get("ethical_violation_log_path", os.path.join(data_dir, "ethical_violations", "violations.jsonl"))
        os.makedirs(os.path.dirname(ethical_violation_log_path), exist_ok=True)
        logger.info(f"Ensured Ethical violations logs directory: {os.path.dirname(ethical_violation_log_path)}")

    self_correction_config = config.get("self_correction", {})
    if self_correction_config.get("enabled") and self_correction_config.get("log_corrections"):
        self_correction_log_path = self_correction_config.get("self_correction_log_path", os.path.join(data_dir, "self_correction_log", "corrections.jsonl"))
        os.makedirs(os.path.dirname(self_correction_log_path), exist_ok=True)
        logger.info(f"Ensured Self-correction logs directory: {os.path.dirname(self_correction_log_path)}")

    # Ensure video_datasets directory exists and contains metadata.json (if applicable)
    video_datasets_dir = os.path.join(data_dir, "video_datasets")
    os.makedirs(video_datasets_dir, exist_ok=True)
    metadata_file = os.path.join(video_datasets_dir, "metadata.json")
    if not os.path.exists(metadata_file):
        logger.warning(f"metadata.json not found in {video_datasets_dir}. Creating a placeholder.")
        # Create a minimal placeholder metadata.json
        placeholder_metadata = {
            "dataset_name": "Placeholder Video Dataset",
            "description": "This is a placeholder metadata file. Add your video details here.",
            "videos": []
        }
        with open(metadata_file, 'w') as f:
            yaml.safe_dump(placeholder_metadata, f, indent=2)
    logger.info(f"Ensured Video datasets directory: {video_datasets_dir}")


def main():
    """Main function to load config and set up environment."""
    config_path = "config.yaml"
    
    # Load config to get log level and debug status for initial logging setup
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: config.yaml not found at {config_path}. Please ensure it exists.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}")
        exit(1)

    setup_logging(debug=config["app"]["debug"], log_level=config["app"]["log_level"])
    logger.info("Starting environment setup...")
    setup_directories(config)
    logger.info("Environment setup complete.")

if __name__ == "__main__":
    main()
