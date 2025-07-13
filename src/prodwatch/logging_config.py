from __future__ import annotations

import logging
import logging.config
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any



class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id

        return json.dumps(log_entry)


def get_default_config() -> Dict[str, Any]:
    """Get default logging configuration."""
    log_format = os.getenv("PRODWATCH_LOG_FORMAT", "text")
    log_level = os.getenv("PRODWATCH_LOG_LEVEL", "INFO")
    log_file = os.getenv("PRODWATCH_LOG_FILE")

    # Configure formatters based on format type
    if log_format == "json":
        formatters = {
            "standard": {
                "()": f"{__name__}.StructuredFormatter",
            }
        }
    else:
        formatters = {
            "standard": {
                "format": "%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
            }
        }

    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
        "loggers": {
            "prodwatch": {
                "level": log_level,
                "propagate": True,
            },
        },
    }

    # Add file handler if log file is specified
    if log_file:
        file_handler = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "standard",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        config["handlers"]["file"] = file_handler
        config["root"]["handlers"].append("file")

    return config


def load_config_file(config_path: Path) -> Dict[str, Any] | None:
    """Load logging configuration from file."""
    if not config_path.exists():
        return None

    try:
        with open(config_path, "r") as f:
            if config_path.suffix.lower() == ".json":
                loaded_config: Dict[str, Any] = json.load(f)
                return loaded_config
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}. Only JSON is supported."
                )
    except Exception as e:
        # Use basic logging since our logger might not be configured yet
        print(
            f"Warning: Failed to load logging config from {config_path}: {e}",
            file=sys.stderr,
        )
        return None


def configure_logging(
    level: str | None = None, config_file: str | None = None
) -> None:
    """Configure logging for the prodwatch package.

    Args:
        level: The logging level to use. Overrides config file and environment.
        config_file: Path to logging configuration file (JSON only).
    """
    config: Dict[str, Any] | None = None

    # Try to load from config file
    if config_file:
        config = load_config_file(Path(config_file))
    else:
        # Look for default config file
        config_path = Path("prodwatch_logging.json")
        config = load_config_file(config_path)

    # Use default config if no file config found
    if not config:
        config = get_default_config()

    # Override level if specified
    if level:
        if "root" in config:
            config["root"]["level"] = level
        if "loggers" in config and "prodwatch" in config["loggers"]:
            config["loggers"]["prodwatch"]["level"] = level

    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    This is a convenience function that ensures consistent logger creation.
    """
    return logging.getLogger(name)
