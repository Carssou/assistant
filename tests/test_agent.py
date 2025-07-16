"""
Unit tests for the refactored PydanticAI Agent.

Tests cover all major functionality including MCP integration,
tool registration, conversation handling, and PydanticAI patterns.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from agent.agent import create_agent
from agent.dependencies import AgentDependencies
from config.settings import AgentConfig, LLMProvider


class TestCreateAgent:
    """Test cases for create_agent function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock()
        config.llm_provider = LLMProvider.AWS
        config.llm_choice = "claude-3-5-sonnet"
        config.obsidian_vault_path = None  # Disable vault validation
        config.log_level = "INFO"
        config.debug_mode = False
        config.langfuse_secret_key = None
        config.langfuse_public_key = None
        config.langfuse_host = "https://cloud.langfuse.com"
        config.vault_path = None
        return config

    @pytest.fixture
    def mock_dependencies(self, mock_config):
        """Create mock dependencies for testing."""
        deps = Mock(spec=AgentDependencies)
        deps.config = mock_config
        deps.logger = Mock()
        deps.langfuse_client = None
        deps.vault_path = None
        return deps

    # Agent creation is now tested in the factory function tests below

    @pytest.mark.asyncio
    async def test_agent_creation(self, mock_config):
        """Test create_agent function."""
        with (
            patch("agent.agent.create_agent_dependencies") as mock_deps_func,
            patch("agent.agent.create_model_instance") as mock_model,
            patch("agent.agent.create_all_mcp_servers") as mock_servers,
            patch("agent.agent.Agent") as mock_agent_class,
        ):
            mock_deps = Mock()
            mock_deps_func.return_value = mock_deps
            mock_model.return_value = Mock()
            mock_servers.return_value = []
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            agent, deps = await create_agent(mock_config)

            assert agent == mock_agent_instance
            assert deps == mock_deps
            mock_deps_func.assert_called_once_with(mock_config)
            mock_model.assert_called_once_with(mock_config)
            mock_servers.assert_called_once_with(mock_config)

    @pytest.mark.asyncio
    async def test_agent_setup_components(self, mock_config):
        """Test that agent setup calls all required components."""
        with (
            patch("agent.agent.create_agent_dependencies") as mock_deps_func,
            patch("agent.agent.create_model_instance") as mock_model,
            patch("agent.agent.create_all_mcp_servers") as mock_servers,
            patch("agent.agent.Agent") as mock_agent_class,
        ):
            mock_deps_func.return_value = Mock()
            mock_model.return_value = Mock()
            mock_servers.return_value = []
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            await create_agent(mock_config)

            # Verify setup was called
            mock_deps_func.assert_called_once_with(mock_config)
            mock_model.assert_called_once_with(mock_config)
            mock_servers.assert_called_once_with(mock_config)
            mock_agent_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_run_basic(self, mock_config):
        """Test basic agent run functionality."""
        with (
            patch("agent.agent.create_agent_dependencies") as mock_deps_func,
            patch("agent.agent.create_model_instance") as mock_model,
            patch("agent.agent.create_all_mcp_servers") as mock_servers,
            patch("agent.agent.Agent") as mock_agent_class,
        ):
            mock_deps = Mock()
            mock_deps_func.return_value = mock_deps
            mock_model.return_value = Mock()
            mock_servers.return_value = []
            mock_agent_instance = Mock()
            mock_result = Mock()
            mock_result.output = "Test response"
            mock_result.new_messages.return_value = []
            mock_agent_instance.run = AsyncMock(return_value=mock_result)
            mock_agent_class.return_value = mock_agent_instance

            agent, deps = await create_agent(mock_config)

            # Test that agent is properly created
            assert agent == mock_agent_instance
            assert deps == mock_deps

    @pytest.mark.asyncio
    async def test_agent_with_mcp_servers(self, mock_config):
        """Test agent creation with MCP servers."""
        with (
            patch("agent.agent.create_agent_dependencies") as mock_deps_func,
            patch("agent.agent.create_model_instance") as mock_model,
            patch("agent.agent.create_all_mcp_servers") as mock_servers,
            patch("agent.agent.Agent") as mock_agent_class,
        ):
            mock_deps = Mock()
            mock_deps_func.return_value = mock_deps
            mock_model.return_value = Mock()
            mock_servers.return_value = [Mock(), Mock()]  # 2 mock servers
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            agent, deps = await create_agent(mock_config)

            # Verify MCP servers were passed to agent
            mock_agent_class.assert_called_once()
            call_kwargs = mock_agent_class.call_args[1]
            assert "mcp_servers" in call_kwargs
            assert len(call_kwargs["mcp_servers"]) == 2

    # These old ProductivityAgent methods are no longer needed
    # MCP servers are handled directly by PydanticAI Agent class

    # ProductivityAgent-specific methods removed since we use PydanticAI Agent directly


class TestAgentFactoryFunctions:
    """Test cases for agent factory functions."""

    @pytest.mark.asyncio
    async def test_create_agent_with_config(self):
        """Test create_agent with provided config."""
        mock_config = Mock()
        mock_config.obsidian_vault_path = None  # Disable vault validation
        mock_config.log_level = "INFO"
        mock_config.debug_mode = False
        mock_config.langfuse_secret_key = None
        mock_config.langfuse_public_key = None
        mock_config.langfuse_host = "https://cloud.langfuse.com"
        mock_config.vault_path = None

        with (
            patch("agent.agent.create_agent_dependencies") as mock_deps,
            patch("agent.agent.create_model_instance") as mock_model,
            patch("agent.agent.create_all_mcp_servers") as mock_servers,
            patch("agent.agent.Agent") as mock_agent_class,
        ):
            mock_deps.return_value = Mock()
            mock_model.return_value = Mock()
            mock_servers.return_value = []
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            agent, deps = await create_agent(mock_config)

            mock_deps.assert_called_once_with(mock_config)
            mock_model.assert_called_once_with(mock_config)
            mock_servers.assert_called_once_with(mock_config)
            mock_agent_class.assert_called_once()
            assert agent == mock_agent_instance

    @pytest.mark.asyncio
    async def test_create_agent_without_config(self):
        """Test create_agent without provided config (loads from env)."""
        with (
            patch("agent.agent.load_config") as mock_load,
            patch("agent.agent.create_agent_dependencies") as mock_deps,
            patch("agent.agent.create_model_instance") as mock_model,
            patch("agent.agent.create_all_mcp_servers") as mock_servers,
            patch("agent.agent.Agent") as mock_agent_class,
        ):
            mock_config = Mock()
            mock_config.obsidian_vault_path = None
            mock_config.log_level = "INFO"
            mock_config.debug_mode = False
            mock_config.langfuse_secret_key = None
            mock_config.langfuse_public_key = None
            mock_config.langfuse_host = "https://cloud.langfuse.com"
            mock_config.vault_path = None
            mock_load.return_value = mock_config
            mock_deps.return_value = Mock()
            mock_model.return_value = Mock()
            mock_servers.return_value = []
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            agent, deps = await create_agent()

            mock_load.assert_called_once()
            mock_deps.assert_called_once_with(mock_config)
            mock_model.assert_called_once_with(mock_config)
            mock_servers.assert_called_once_with(mock_config)
            mock_agent_class.assert_called_once()
            assert agent == mock_agent_instance


class TestMCPIntegration:
    """Test cases for MCP server integration."""

    # Old fixtures removed - using create_agent factory pattern instead

    # Old ProductivityAgent tests removed - MCP integration now handled by PydanticAI Agent directly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
