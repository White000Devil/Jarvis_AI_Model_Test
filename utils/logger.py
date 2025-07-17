from loguru import logger
import sys
from pathlib import Path

def setup_logging(debug: bool = False):
    """
    Sets up Loguru logging with console and file outputs,
    and specific sinks for different log types.
    """
    logger.remove() # Remove default handler

    # Console handler
    logger.add(
        sys.stderr,
        level="DEBUG" if debug else "INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Main application log file
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "jarvis_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file_path,
        rotation="1 day", # New file every day
        retention="7 days", # Keep logs for 7 days
        level="INFO",
        enqueue=True # Use a queue for non-blocking writes
    )
    
    # Specific loggers for different data types (JSONL format)
    # Feedback logs
    feedback_log_dir = Path("data/feedback_logs")
    feedback_log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        feedback_log_dir / "feedback.jsonl",
        format="{message}", # Log only the JSON string
        level="INFO",
        rotation="10 MB",
        compression="zip", # Compress old logs
        serialize=True, # Ensure message is treated as JSON
        filter=lambda record: record["extra"].get("log_type") == "feedback"
    )

    # Scraping logs
    scraping_log_dir = Path("data/scraping_logs")
    scraping_log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        scraping_log_dir / "scraping.jsonl",
        format="{message}",
        level="INFO",
        rotation="10 MB",
        compression="zip",
        serialize=True,
        filter=lambda record: record["extra"].get("log_type") == "scraping"
    )

    # Ethical violations logs
    ethical_violations_dir = Path("data/ethical_violations")
    ethical_violations_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        ethical_violations_dir / "violations.jsonl",
        format="{message}",
        level="INFO",
        rotation="10 MB",
        compression="zip",
        serialize=True,
        filter=lambda record: record["extra"].get("log_type") == "ethical_violation"
    )

    # Self-correction logs
    self_correction_dir = Path("data/self_correction_log")
    self_correction_dir.mkdir(parents=True, exist_ok=True)
    logger.add(
        self_correction_dir / "corrections.jsonl",
        format="{message}",
        level="INFO",
        rotation="10 MB",
        compression="zip",
        serialize=True,
        filter=lambda record: record["extra"].get("log_type") == "self_correction"
    )

    return logger # Return the configured logger instance

# Initialize logger when the module is imported
logger = setup_logging()
