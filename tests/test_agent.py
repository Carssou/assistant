"""
Unit tests for the refactored ProductivityAgent class.

Tests cover all major functionality including MCP integration,
tool registration, conversation handling, and PydanticAI patterns.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from agent.agent import ProductivityAgent, create_agent
from agent.dependencies import AgentDependencies
from config.settings import AgentConfig, LLMProvider


class TestProductivityAgent:
    """Test cases for ProductivityAgent class."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = AgentConfig(_env_file=None)
        config.llm_provider = LLMProvider.AWS
        config.llm_choice = "claude-3-5-sonnet"
        config.obsidian_vault_path = None  # Disable vault validation
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

    @pytest.fixture
    def mock_productivity_agent(self, mock_dependencies):
        """Create a ProductivityAgent with mocked dependencies."""
        with patch('agent.agent.create_model_instance') as mock_model, \
             patch('agent.agent.create_all_mcp_servers') as mock_servers, \
             patch('agent.agent.register_tools') as mock_register, \
             patch('agent.agent.Agent') as mock_agent_class:

            mock_model.return_value = Mock()
            mock_servers.return_value = [Mock(), Mock()]  # 2 mock servers
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            agent = ProductivityAgent(mock_dependencies)
            agent._mock_agent_instance = mock_agent_instance  # Store for test access
            return agent

    def test_initialization(self, mock_productivity_agent, mock_dependencies):
        """Test ProductivityAgent initialization."""
        assert mock_productivity_agent.deps == mock_dependencies
        assert mock_productivity_agent.config == mock_dependencies.config
        assert mock_productivity_agent.logger == mock_dependencies.logger

    def test_setup_agent_called_during_init(self, mock_dependencies):
        """Test that _setup_agent is called during initialization."""
        with patch('agent.agent.create_model_instance') as mock_model, \
             patch('agent.agent.create_all_mcp_servers') as mock_servers, \
             patch('agent.agent.register_tools') as mock_register, \
             patch('agent.agent.Agent') as mock_agent_class:

            mock_model.return_value = Mock()
            mock_servers.return_value = []
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            agent = ProductivityAgent(mock_dependencies)

            # Verify setup was called
            mock_model.assert_called_once_with(mock_dependencies.config)
            mock_servers.assert_called_once_with(mock_dependencies.config)
            mock_agent_class.assert_called_once()
            mock_register.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_conversation(self, mock_productivity_agent):
        """Test run_conversation method."""
        # Mock the global agent
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = [Mock(), Mock()]
            mock_context = AsyncMock()
            mock_global_agent.run_mcp_servers.return_value = mock_context
            mock_result = Mock()
            mock_result.output = "Test response"
            mock_result.new_messages.return_value = []
            mock_global_agent.run = AsyncMock(return_value=mock_result)

            response = await mock_productivity_agent.run_conversation("Test message")

            assert response == "Test response"
            mock_global_agent.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_conversation(self, mock_productivity_agent):
        """Test run_conversation method."""
        with patch.object(mock_productivity_agent, 'run_conversation', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = "Test response with history"

            response = await mock_productivity_agent.run_conversation(
                "Test message", None
            )

            assert response == "Test response with history"
            mock_run.assert_called_once_with("Test message", None)

    def test_has_mcp_servers_true(self, mock_productivity_agent):
        """Test has_mcp_servers returns True when servers exist."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = [Mock(), Mock()]

            assert mock_productivity_agent.has_mcp_servers() is True

    def test_has_mcp_servers_false(self, mock_productivity_agent):
        """Test has_mcp_servers returns False when no servers exist."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = []

            assert mock_productivity_agent.has_mcp_servers() is False

    def test_mcp_servers_property(self, mock_productivity_agent):
        """Test mcp_servers property returns the servers."""
        mock_servers = [Mock(), Mock()]
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = mock_servers

            assert mock_productivity_agent.mcp_servers == mock_servers

    def test_disable_mcp_servers(self, mock_productivity_agent):
        """Test disable_mcp_servers clears the server list."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = [Mock(), Mock()]

            mock_productivity_agent.disable_mcp_servers()

            assert mock_global_agent._mcp_servers == []

    @pytest.mark.asyncio
    async def test_list_available_tools_with_servers(self, mock_productivity_agent):
        """Test list_available_tools with MCP servers."""
        mock_server1 = Mock()
        mock_server1.command = "npx"
        mock_server1.args = ["-y", "test-server"]

        mock_server2 = Mock()
        mock_server2.command = "python"
        mock_server2.args = ["server.py"]

        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = [mock_server1, mock_server2]

            tools_info = await mock_productivity_agent.list_available_tools()

            assert len(tools_info) == 2
            assert "server_0" in tools_info
            assert "server_1" in tools_info
            assert tools_info["server_0"]["command"] == "npx"
            assert tools_info["server_1"]["command"] == "python"

    @pytest.mark.asyncio
    async def test_list_available_tools_no_servers(self, mock_productivity_agent):
        """Test list_available_tools with no MCP servers."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = []

            tools_info = await mock_productivity_agent.list_available_tools()

            assert tools_info == {"message": "No MCP servers configured"}

    @pytest.mark.asyncio
    async def test_close(self, mock_productivity_agent):
        """Test close method."""
        mock_productivity_agent.deps.langfuse_client = Mock()
        mock_productivity_agent.deps.close = AsyncMock()

        await mock_productivity_agent.close()

        mock_productivity_agent.deps.langfuse_client.flush.assert_called_once()
        mock_productivity_agent.deps.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_no_langfuse(self, mock_productivity_agent):
        """Test close method without Langfuse client."""
        mock_productivity_agent.deps.langfuse_client = None
        mock_productivity_agent.deps.close = AsyncMock()

        await mock_productivity_agent.close()

        mock_productivity_agent.deps.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_conversation_error_handling(self, mock_productivity_agent):
        """Test error handling in run_conversation."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = [Mock()]
            mock_context = AsyncMock()
            mock_global_agent.run_mcp_servers.return_value = mock_context
            mock_global_agent.run = AsyncMock(side_effect=Exception("Test error"))

            response = await mock_productivity_agent.run_conversation("Test message")

            assert "I encountered an error: Test error" in response


class TestAgentFactoryFunctions:
    """Test cases for agent factory functions."""

    @pytest.mark.asyncio
    async def test_create_agent_with_config(self):
        """Test create_agent with provided config."""
        mock_config = Mock(spec=AgentConfig)
        mock_config.obsidian_vault_path = None  # Disable vault validation

        with patch('agent.dependencies.create_agent_dependencies') as mock_deps, \
             patch('agent.agent.ProductivityAgent') as mock_agent_class:

            mock_deps.return_value = Mock()
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            result = await create_agent(mock_config)

            mock_deps.assert_called_once_with(mock_config)
            mock_agent_class.assert_called_once()
            assert result == mock_agent_instance

    @pytest.mark.asyncio
    async def test_create_agent_without_config(self):
        """Test create_agent without provided config (loads from env)."""
        with patch('config.settings.load_config') as mock_load, \
             patch('agent.dependencies.create_agent_dependencies') as mock_deps, \
             patch('agent.agent.ProductivityAgent') as mock_agent_class:

            mock_config = Mock()
            mock_config.obsidian_vault_path = None
            mock_load.return_value = mock_config
            mock_deps.return_value = Mock()
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            result = await create_agent()

            mock_load.assert_called_once()
            mock_deps.assert_called_once_with(mock_config)
            mock_agent_class.assert_called_once()
            assert result == mock_agent_instance


class TestMCPIntegration:
    """Test cases for MCP server integration."""

    @pytest.fixture
    def mock_productivity_agent(self):
        """Create a ProductivityAgent with mocked dependencies."""
        with patch('agent.agent.create_model_instance') as mock_model, \
             patch('agent.agent.create_all_mcp_servers') as mock_servers, \
             patch('agent.agent.register_tools') as mock_register, \
             patch('agent.agent.Agent') as mock_agent_class:

            mock_model.return_value = Mock()
            mock_servers.return_value = [Mock(), Mock()]  # 2 mock servers
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance

            mock_deps = Mock()
            mock_deps.config = Mock()
            mock_deps.logger = Mock()
            mock_deps.langfuse_client = None

            agent = ProductivityAgent(mock_deps)
            return agent

    @pytest.fixture
    def mock_agent_with_mcp(self, mock_productivity_agent):
        """Create an agent with mock MCP servers."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_server1 = Mock()
            mock_server1.command = "npx"
            mock_server1.args = ["-y", "obsidian-mcp"]

            mock_server2 = Mock()
            mock_server2.command = "npx"
            mock_server2.args = ["-y", "searxng-mcp"]

            mock_global_agent._mcp_servers = [mock_server1, mock_server2]
            yield mock_productivity_agent

    @pytest.mark.asyncio
    async def test_mcp_context_management(self, mock_productivity_agent):
        """Test that MCP servers are used in proper async context."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_context = AsyncMock()
            mock_global_agent.run_mcp_servers.return_value = mock_context
            mock_result = Mock()
            mock_result.output = "MCP response"
            mock_result.new_messages.return_value = []
            mock_global_agent.run = AsyncMock(return_value=mock_result)
            mock_global_agent._mcp_servers = [Mock()]

            response = await mock_productivity_agent.run_conversation("Test with MCP")

            # Verify context manager was used
            mock_global_agent.run_mcp_servers.assert_called_once()
            mock_context.__aenter__.assert_called_once()
            mock_context.__aexit__.assert_called_once()
            assert response == "MCP response"

    @pytest.mark.asyncio
    async def test_no_mcp_servers_fallback(self, mock_productivity_agent):
        """Test fallback behavior when no MCP servers are configured."""
        with patch('agent.agent.agent') as mock_global_agent:
            mock_global_agent._mcp_servers = []
            mock_result = Mock()
            mock_result.output = "No MCP response"
            mock_result.new_messages.return_value = []
            mock_global_agent.run = AsyncMock(return_value=mock_result)

            response = await mock_productivity_agent.run_conversation("Test without MCP")

            # Verify no MCP context was used
            mock_global_agent.run_mcp_servers.assert_not_called()
            mock_global_agent.run.assert_called_once()
            assert response == "No MCP response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
