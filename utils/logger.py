import sys
import os
from loguru import logger
from typing import Optional

# Remove default logger to use Loguru's features
# This section will be replaced with the new logging setup

def setup_logging(debug: bool = False, log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Sets up logging configuration for JARVIS AI.
    
    Args:
        debug: Enable debug mode with more verbose logging
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Remove default logger
    logger.remove()
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Console logging format
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # File logging format
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True,
        backtrace=debug,
        diagnose=debug
    )
    
    # Add file handler
    log_file = log_file or "logs/jarvis_ai.log"
    logger.add(
        log_file,
        format=file_format,
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        backtrace=debug,
        diagnose=debug
    )
    
    if debug:
        logger.info("Debug mode enabled - verbose logging active")
    
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")

# Initial setup for when modules are imported
setup_logging() # Call setup_logging on module import

# Example usage (for testing this module directly)
if __name__ == "__main__":
    setup_logging(debug=True)
    logger.info("This is an info message.")
    logger.debug("This is a debug message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    
    # Example of logging with extra context for filtering
    # Note: The extra context filtering is not supported in the standard logging module
    logger.info("An ethical violation occurred.")
    logger.info("Scraping completed successfully.")
    logger.info("Self-correction applied.")

# Export logger for use in other modules
__all__ = ["logger", "setup_logging"]
