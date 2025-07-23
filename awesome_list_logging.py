"""Logging configuration for the Awesome List application."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO", 
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """Set up comprehensive logging for the Awesome List application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, uses default location.
        console_output: Whether to also output logs to console
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Set default log file if not provided
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"awesome_list_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger("awesome_list_agent")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (if enabled)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    return logger


def log_input_output(logger: logging.Logger):
    """Decorator to log function inputs and outputs."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Log input
            logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            
            try:
                result = func(*args, **kwargs)
                # Log successful output
                logger.debug(f"{func.__name__} returned: {result}")
                return result
            except Exception as e:
                # Log error
                logger.error(f"{func.__name__} raised exception: {e}")
                raise
        return wrapper
    return decorator


def log_async_input_output(logger: logging.Logger):
    """Decorator to log async function inputs and outputs."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Log input
            logger.debug(f"Calling async {func.__name__} with args: {args}, kwargs: {kwargs}")
            
            try:
                result = await func(*args, **kwargs)
                # Log successful output
                logger.debug(f"Async {func.__name__} returned: {result}")
                return result
            except Exception as e:
                # Log error
                logger.error(f"Async {func.__name__} raised exception: {e}")
                raise
        return wrapper
    return decorator
