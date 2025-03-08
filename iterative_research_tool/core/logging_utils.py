"""Logging utilities for the Iterative Research Tool."""

import os
import sys
import logging
from typing import Optional, TextIO
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to logs."""
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


def setup_logging(
    verbose: bool = False,
    log_file: Optional[str] = None,
    stdout: TextIO = sys.stdout
) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        verbose: If True, set log level to DEBUG, otherwise INFO
        log_file: If provided, also log to this file
        stdout: Stream to output logs to (default: sys.stdout)
        
    Returns:
        Root logger instance
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create colored formatter
    formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                '%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG and higher to file
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Create a logger for this module
    logger = logging.getLogger(__name__)
    logger.debug("Logging initialized")
    
    return root_logger


class ProgressLogger:
    """Utility for logging progress with a consistent format."""
    
    def __init__(self, logger: logging.Logger, total_steps: int = 0):
        """Initialize progress logger.
        
        Args:
            logger: Logger instance to use
            total_steps: Total number of steps in the process
        """
        self.logger = logger
        self.total_steps = total_steps
        self.current_step = 0
    
    def start(self, message: str = "Starting process") -> None:
        """Log start of process."""
        self.logger.info(f"{message}")
        self.current_step = 0
    
    def step(self, message: str) -> None:
        """Log a step in the process."""
        self.current_step += 1
        step_info = f"[{self.current_step}"
        if self.total_steps:
            step_info += f"/{self.total_steps}"
        step_info += f"] {message}"
        
        self.logger.info(step_info)
    
    def complete(self, message: str = "Process completed") -> None:
        """Log completion of process."""
        if self.total_steps:
            self.logger.info(f"Completed {self.current_step}/{self.total_steps} steps. {message}")
        else:
            self.logger.info(f"Completed {self.current_step} steps. {message}")


# Create and export a default instance
default_progress_logger = ProgressLogger(logging.getLogger(__name__)) 