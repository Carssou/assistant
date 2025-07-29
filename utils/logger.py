"""
Logging configuration using Langfuse.

This module provides centralized logging and observability configuration
for the PydanticAI agent using Langfuse for tracing and monitoring.
"""

import logging
import sys
from pathlib import Path

from langfuse import Langfuse


def setup_logging(
    log_level: str = "INFO",
    debug_mode: bool = False,
    langfuse_secret_key: str | None = None,
    langfuse_public_key: str | None = None,
    langfuse_host: str = "https://cloud.langfuse.com",
) -> Langfuse | None:
    """
    Configure logging and Langfuse observability.

    Args:
        log_level: Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug_mode: Enable debug mode for more verbose logging
        langfuse_secret_key: Langfuse secret key for tracing
        langfuse_public_key: Langfuse public key for tracing
        langfuse_host: Langfuse host URL

    Returns:
        Langfuse client if credentials provided, None otherwise
    """
    # Set up Python logging
    if debug_mode:
        log_level = "DEBUG"

    # Configure logging format
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Create logs directory for file logging
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Add file handler
    file_handler = logging.FileHandler(logs_dir / "agent.log")
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
        )
    )

    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # Initialize Langfuse if credentials provided
    langfuse_client = None
    if langfuse_secret_key and langfuse_public_key:
        try:
            langfuse_client = Langfuse(
                secret_key=langfuse_secret_key, public_key=langfuse_public_key, host=langfuse_host
            )
            logging.info("Langfuse observability initialized")
        except Exception as e:
            logging.warning(f"Failed to initialize Langfuse: {e}")

    # Enable HTTP request/response logging for API calls
    if debug_mode:
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logging.getLogger("httpcore").setLevel(logging.DEBUG)
        logging.getLogger("botocore").setLevel(logging.DEBUG)
        logging.getLogger("botocore.httpsession").setLevel(logging.DEBUG)
        logging.getLogger("botocore.endpoint").setLevel(logging.DEBUG)
        logging.getLogger("boto3").setLevel(logging.DEBUG)
        logging.getLogger("urllib3").setLevel(logging.DEBUG)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)
    else:
        # Suppress all third-party library noise
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("botocore.httpsession").setLevel(logging.WARNING)
        logging.getLogger("botocore.endpoint").setLevel(logging.WARNING)
        logging.getLogger("botocore.hooks").setLevel(logging.WARNING)
        logging.getLogger("botocore.auth").setLevel(logging.WARNING)
        logging.getLogger("botocore.parsers").setLevel(logging.WARNING)
        logging.getLogger("botocore.retryhandler").setLevel(logging.WARNING)
        logging.getLogger("botocore.utils").setLevel(logging.WARNING)
        logging.getLogger("botocore.credentials").setLevel(logging.WARNING)
        logging.getLogger("botocore.loaders").setLevel(logging.WARNING)
        logging.getLogger("botocore.regions").setLevel(logging.WARNING)
        logging.getLogger("botocore.client").setLevel(logging.WARNING)
        logging.getLogger("botocore.configprovider").setLevel(logging.WARNING)
        logging.getLogger("gradio").setLevel(logging.WARNING)
        logging.getLogger("uvicorn").setLevel(logging.WARNING)

    logging.info(f"Logging initialized with level: {log_level}")
    if debug_mode:
        logging.debug("Debug mode enabled")

    return langfuse_client


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_agent_logging(
    log_level: str = "INFO",
    debug_mode: bool = False,
    langfuse_secret_key: str | None = None,
    langfuse_public_key: str | None = None,
    langfuse_host: str = "https://cloud.langfuse.com",
) -> Langfuse | None:
    """
    Set up logging specifically for the agent application.

    Args:
        log_level: Logging level
        debug_mode: Enable debug mode
        langfuse_secret_key: Langfuse secret key
        langfuse_public_key: Langfuse public key
        langfuse_host: Langfuse host URL

    Returns:
        Langfuse client if available
    """
    return setup_logging(
        log_level=log_level,
        debug_mode=debug_mode,
        langfuse_secret_key=langfuse_secret_key,
        langfuse_public_key=langfuse_public_key,
        langfuse_host=langfuse_host,
    )


# Export convenience functions
__all__ = ["setup_logging", "get_logger", "setup_agent_logging"]
