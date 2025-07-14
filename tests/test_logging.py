"""
Unit tests for logging module.
"""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from utils.logger import get_logger, setup_agent_logging, setup_logging


class TestSetupLogging:
    """Test cases for setup_logging function."""

    def test_default_logging_setup(self):
        """Test default logging configuration."""
        # Reset logging before test
        logging.getLogger().handlers.clear()

        langfuse_client = setup_logging()

        # Check that root logger is configured
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) >= 1

        # Should return None when no Langfuse credentials
        assert langfuse_client is None

    def test_debug_mode_logging(self):
        """Test debug mode sets DEBUG level."""
        logging.getLogger().handlers.clear()

        setup_logging(debug_mode=True)

        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

    def test_custom_log_level(self):
        """Test custom log level setting."""
        logging.getLogger().handlers.clear()

        setup_logging(log_level="WARNING")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    def test_file_handler_creation(self):
        """Test that file handler is created."""
        logging.getLogger().handlers.clear()

        setup_logging()

        # Check that logs directory is created
        logs_dir = Path("logs")
        assert logs_dir.exists()

        # Check that log file is created (after first log message)
        log_file = logs_dir / "agent.log"
        test_logger = logging.getLogger("test")
        test_logger.info("Test message")

        assert log_file.exists()

    @patch('utils.logger.Langfuse')
    def test_langfuse_initialization_success(self, mock_langfuse):
        """Test successful Langfuse initialization."""
        logging.getLogger().handlers.clear()

        mock_client = MagicMock()
        mock_langfuse.return_value = mock_client

        langfuse_client = setup_logging(
            langfuse_secret_key="test_secret",
            langfuse_public_key="test_public"
        )

        mock_langfuse.assert_called_once_with(
            secret_key="test_secret",
            public_key="test_public",
            host="https://cloud.langfuse.com"
        )
        assert langfuse_client == mock_client

    @patch('utils.logger.Langfuse')
    def test_langfuse_initialization_failure(self, mock_langfuse):
        """Test Langfuse initialization failure handling."""
        logging.getLogger().handlers.clear()

        mock_langfuse.side_effect = Exception("Connection error")

        # Should not raise exception, just log warning
        langfuse_client = setup_logging(
            langfuse_secret_key="test_secret",
            langfuse_public_key="test_public"
        )

        assert langfuse_client is None

    def test_langfuse_custom_host(self):
        """Test custom Langfuse host configuration."""
        logging.getLogger().handlers.clear()

        with patch('utils.logger.Langfuse') as mock_langfuse:
            mock_client = MagicMock()
            mock_langfuse.return_value = mock_client

            setup_logging(
                langfuse_secret_key="test_secret",
                langfuse_public_key="test_public",
                langfuse_host="https://custom.langfuse.com"
            )

            mock_langfuse.assert_called_once_with(
                secret_key="test_secret",
                public_key="test_public",
                host="https://custom.langfuse.com"
            )

    def test_missing_langfuse_credentials(self):
        """Test that missing credentials don't initialize Langfuse."""
        logging.getLogger().handlers.clear()

        # Only secret key
        langfuse_client = setup_logging(langfuse_secret_key="test_secret")
        assert langfuse_client is None

        # Only public key
        langfuse_client = setup_logging(langfuse_public_key="test_public")
        assert langfuse_client is None

        # Neither key
        langfuse_client = setup_logging()
        assert langfuse_client is None


class TestGetLogger:
    """Test cases for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_different_names(self):
        """Test that different names return different loggers."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 != logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"


class TestSetupAgentLogging:
    """Test cases for setup_agent_logging function."""

    def test_setup_agent_logging_calls_setup_logging(self):
        """Test that setup_agent_logging calls setup_logging with correct parameters."""
        logging.getLogger().handlers.clear()

        with patch('utils.logger.setup_logging') as mock_setup:
            mock_setup.return_value = None

            result = setup_agent_logging(
                log_level="DEBUG",
                debug_mode=True,
                langfuse_secret_key="secret",
                langfuse_public_key="public",
                langfuse_host="https://test.com"
            )

            mock_setup.assert_called_once_with(
                log_level="DEBUG",
                debug_mode=True,
                langfuse_secret_key="secret",
                langfuse_public_key="public",
                langfuse_host="https://test.com"
            )
            assert result is None

    def test_setup_agent_logging_returns_langfuse_client(self):
        """Test that setup_agent_logging returns Langfuse client when available."""
        logging.getLogger().handlers.clear()

        mock_client = MagicMock()
        with patch('utils.logger.setup_logging') as mock_setup:
            mock_setup.return_value = mock_client

            result = setup_agent_logging()
            assert result == mock_client


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_messages_work(self):
        """Test that logging messages are actually written."""
        logging.getLogger().handlers.clear()

        setup_logging(log_level="DEBUG")
        logger = get_logger("test_integration")

        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_log_file_contains_messages(self):
        """Test that log messages are written to file."""
        logging.getLogger().handlers.clear()

        setup_logging(log_level="INFO")
        logger = get_logger("test_file")

        test_message = "Test message for file logging"
        logger.info(test_message)

        # Force flush of handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        log_file = Path("logs") / "agent.log"
        if log_file.exists():
            content = log_file.read_text()
            assert test_message in content


if __name__ == "__main__":
    pytest.main([__file__])
