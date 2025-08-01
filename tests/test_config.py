"""
Unit tests for configuration module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from config.settings import AgentConfig, LLMProvider, create_model_instance, load_config


class TestAgentConfig:
    """Test cases for AgentConfig class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            config = AgentConfig(_env_file=None)  # Disable .env file loading

            assert config.llm_provider == LLMProvider.AWS
            assert config.llm_choice == "claude-3-5-sonnet"
            assert config.aws_region == "us-east-1"
            assert config.log_level == "INFO"
            assert config.debug_mode is True
            assert config.gui_port == 7860
            assert config.gui_share is False

    def test_env_variable_loading(self):
        """Test that environment variables are loaded correctly."""
        test_env = {
            "LLM_PROVIDER": "openai",
            "LLM_CHOICE": "gpt-4o",
            "LOG_LEVEL": "DEBUG",
            "DEBUG_MODE": "true",
            "GUI_PORT": "8080",
            "SEARXNG_BASE_URL": "http://test:9090",
        }

        with patch.dict(os.environ, test_env, clear=True):
            config = AgentConfig(_env_file=None)

            assert config.llm_provider == LLMProvider.OPENAI
            assert config.llm_choice == "gpt-4o"
            assert config.log_level == "DEBUG"
            assert config.debug_mode is True
            assert config.gui_port == 8080
            assert config.searxng_base_url == "http://test:9090"

    def test_boolean_parsing(self):
        """Test that boolean environment variables are parsed correctly."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("random", False),
        ]

        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"DEBUG_MODE": env_value}, clear=True):
                config = AgentConfig(_env_file=None)
                assert config.debug_mode == expected, f"Failed for '{env_value}'"

    def test_llm_provider_enum(self):
        """Test LLM provider enum validation."""
        # Valid providers
        with patch.dict(os.environ, {"LLM_PROVIDER": "aws"}, clear=True):
            config = AgentConfig(_env_file=None)
            assert config.llm_provider == LLMProvider.AWS

        with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}, clear=True):
            config = AgentConfig(_env_file=None)
            assert config.llm_provider == LLMProvider.OPENAI

        # Invalid provider should raise validation error
        with patch.dict(os.environ, {"LLM_PROVIDER": "invalid"}, clear=True):
            with pytest.raises(ValueError):
                AgentConfig(_env_file=None)


# Model creation tests removed - Strands handles this internally


class TestLoadConfig:
    """Test cases for load_config function."""

    def test_load_config_returns_agent_config(self):
        """Test that load_config returns an AgentConfig instance."""
        # Use clean environment for this test
        with patch.dict(os.environ, {"LLM_PROVIDER": "aws"}, clear=True):
            config = load_config()
            assert isinstance(config, AgentConfig)

    @patch("config.settings.AgentConfig")
    def test_load_config_calls_agent_config(self, mock_agent_config):
        """Test that load_config calls AgentConfig constructor."""
        mock_instance = MagicMock()
        mock_agent_config.return_value = mock_instance

        result = load_config()

        mock_agent_config.assert_called_once()
        assert result == mock_instance


if __name__ == "__main__":
    pytest.main([__file__])
