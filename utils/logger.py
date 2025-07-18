import logging
from loguru import logger
import sys
from pathlib import Path

# Remove default logger to use Loguru's features
logger.remove()

def setup_logging(debug: bool = False, log_level: str = "INFO"):
    """
    Sets up the logging configuration for the JARVIS AI Assistant.

    Args:
        debug (bool): If True, sets log level to DEBUG and includes file/line info.
        log_level (str): Minimum log level to capture (e.g., "INFO", "DEBUG", "WARNING", "ERROR").
    """
    log_path = Path("logs")
    log_path.mkdir(parents=True, exist_ok=True)

    # Configure Loguru
    # Console logger
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        colorize=True,
        backtrace=debug,
        diagnose=debug
    )

    # File logger for general application logs
    logger.add(
        log_path / "jarvis_app.log",
        level=log_level.upper(),
        rotation="10 MB", # Rotate file every 10 MB
        compression="zip", # Compress old log files
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {file.name}:{line} - {message}",
        backtrace=debug,
        diagnose=debug
    )

    # Separate file loggers for specific components (e.g., ethical violations, scraping, self-correction)
    # These logs are also handled by the respective components writing to JSONL files.
    # This is a fallback/additional stream for these types if needed in the main log.
    logger.add(
        "data/ethical_violations/violations.jsonl",
        filter=lambda record: record["extra"].get("log_type") == "ethical_violation",
        format="{message}",
        serialize=True, # Log as JSON
        rotation="10 MB",
        retention="30 days",
        enqueue=True
    )
    logger.add(
        "data/scraping_logs/scraping.jsonl",
        filter=lambda record: record["extra"].get("log_type") == "scraping",
        format="{message}",
        serialize=True, # Log as JSON
        rotation="10 MB",
        retention="30 days",
        enqueue=True
    )
    logger.add(
        "data/self_correction_log/corrections.jsonl",
        filter=lambda record: record["extra"].get("log_type") == "self_correction",
        format="{message}",
        serialize=True, # Log as JSON
        rotation="10 MB",
        retention="30 days",
        enqueue=True
    )

    if debug:
        logger.debug("Logging configured for DEBUG level.")
    else:
        logger.info(f"Logging configured for {log_level.upper()} level.")

# Initial setup for when modules are imported
setup_logging()

# Example usage (for testing this module directly)
if __name__ == "__main__":
    setup_logging(debug=True)
    logger.info("This is an info message.")
    logger.debug("This is a debug message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    
    # Example of logging with extra context for filtering
    logger.info("An ethical violation occurred.", extra={"log_type": "ethical_violation"})
    logger.info("Scraping completed successfully.", extra={"log_type": "scraping"})
    logger.info("Self-correction applied.", extra={"log_type": "self_correction"})
