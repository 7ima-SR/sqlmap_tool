# utils/logger.py
import logging
from datetime import datetime
import os
from pathlib import Path

class Logger:
    """Advanced structured logging system with file and console output"""
    
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "VULNERABLE": 25,  # Custom level between INFO and WARNING
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    def __init__(self, filename="sqlmap_v2.log", log_dir="logs"):
        """Initialize logger with file and console handlers"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.log_file = os.path.join(log_dir, filename)
        self.logger = logging.getLogger("SQLMapV2")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler - detailed
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Console handler - warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

    def log(self, message, level="INFO"):
        """Log message with structured format"""
        level = level.upper()
        log_level = self.LOG_LEVELS.get(level, logging.INFO)
        
        if level == "VULNERABLE":
            self.logger.log(log_level, f"🔴 VULNERABLE: {message}")
        else:
            self.logger.log(log_level, message)

    def debug(self, message):
        """Log debug message"""
        self.log(message, "DEBUG")

    def info(self, message):
        """Log info message"""
        self.log(message, "INFO")

    def warning(self, message):
        """Log warning message"""
        self.log(message, "WARNING")

    def vulnerable(self, message):
        """Log vulnerability detection"""
        self.log(message, "VULNERABLE")

    def error(self, message):
        """Log error message"""
        self.log(message, "ERROR")

    def critical(self, message):
        """Log critical error"""
        self.log(message, "CRITICAL")

    def get_log_file(self):
        """Return path to log file"""
        return self.log_file