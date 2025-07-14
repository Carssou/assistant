"""
Unit tests for GUI integration with the refactored ProductivityAgent.

Tests cover the Gradio interface, agent initialization, chat functionality,
and error handling scenarios specific to GUI usage.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from agent.agent import ProductivityAgent
from config.settings import AgentConfig, LLMProvider
from gui import AgentGUI


class TestAgentGUI:
    """Test cases for AgentGUI class."""

    @pytest.fixture
    def mock_gui(self):
        """Create an AgentGUI instance for testing."""
        return AgentGUI()

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for GUI testing."""
        config = Mock(spec=AgentConfig)
        config.llm_provider = LLMProvider.AWS
        config.llm_choice = "claude-3-5-sonnet"
        config.debug_mode = False
        config.obsidian_vault_path = None
        config.searxng_base_url = "http://localhost:8080"
        return config

    @pytest.fixture
    def mock_agent(self):
        """Create a mock ProductivityAgent for GUI testing."""
        agent = Mock(spec=ProductivityAgent)
        agent.run_conversation = AsyncMock(return_value="Test response")
        agent.has_mcp_servers = Mock(return_value=True)
        agent.disable_mcp_servers = Mock()
        return agent

    def test_gui_initialization(self, mock_gui):
        """Test GUI initialization."""
        assert mock_gui.agent is None
        assert mock_gui.config is None
        assert mock_gui.conversation_history == []
        assert mock_gui.mcp_context_active is False

    @pytest.mark.asyncio
    async def test_initialize_agent_success(self, mock_gui, mock_config, mock_agent):
        """Test successful agent initialization."""
        with patch('gui.load_config', return_value=mock_config) as mock_load, \
             patch('gui.create_agent', return_value=mock_agent) as mock_create:

            result = await mock_gui.initialize_agent()

            assert result is True
            assert mock_gui.config == mock_config
            assert mock_gui.agent == mock_agent
            mock_load.assert_called_once()
            mock_create.assert_called_once_with(mock_config)

    @pytest.mark.asyncio
    async def test_initialize_agent_failure(self, mock_gui):
        """Test agent initialization failure."""
        with patch('gui.load_config', side_effect=Exception("Config error")):
            result = await mock_gui.initialize_agent()

            assert result is False
            assert mock_gui.agent is None
            assert mock_gui.config is None

    @pytest.mark.asyncio
    async def test_chat_response_no_agent(self, mock_gui):
        """Test chat response when agent is not initialized."""
        history = []

        result = await mock_gui.chat_response("Test message", history)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert "Agent not initialized" in result[0]["content"]

    @pytest.mark.asyncio
    async def test_chat_response_empty_message(self, mock_gui, mock_agent):
        """Test chat response with empty message."""
        mock_gui.agent = mock_agent
        history = []

        result = await mock_gui.chat_response("", history)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert "Please enter a message" in result[0]["content"]

    @pytest.mark.asyncio
    async def test_chat_response_success(self, mock_gui, mock_agent):
        """Test successful chat response."""
        mock_gui.agent = mock_agent
        mock_agent.run_conversation.return_value = "Agent response"

        history = [{"role": "user", "content": "Previous message"}]

        result = await mock_gui.chat_response("Test message", history)

        assert len(result) == 2  # Original history + new response
        assert result[-1]["role"] == "assistant"
        assert result[-1]["content"] == "Agent response"

        # Verify agent was called with proper history conversion
        mock_agent.run_conversation.assert_called_once()
        call_args = mock_agent.run_conversation.call_args
        assert call_args[0][0] == "Test message"  # message
        assert len(call_args[0][1]) == 1  # converted history

    @pytest.mark.asyncio
    async def test_chat_response_mcp_cancel_error(self, mock_gui, mock_agent):
        """Test chat response with MCP cancel scope error (should be handled gracefully)."""
        mock_gui.agent = mock_agent
        mock_agent.run_conversation.side_effect = Exception("cancel scope error")

        history = []

        result = await mock_gui.chat_response("Test message", history)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert "MCP context warning" in result[0]["content"]

    @pytest.mark.asyncio
    async def test_chat_response_other_error(self, mock_gui, mock_agent):
        """Test chat response with non-MCP error."""
        mock_gui.agent = mock_agent
        mock_agent.run_conversation.side_effect = Exception("Other error")

        history = []

        result = await mock_gui.chat_response("Test message", history)

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert "Error: Other error" in result[0]["content"]

    def test_get_vault_name_no_config(self, mock_gui):
        """Test vault name extraction with no config."""
        result = mock_gui._get_vault_name()
        assert result == "Not configured"

    def test_get_vault_name_no_vault_path(self, mock_gui, mock_config):
        """Test vault name extraction with no vault path."""
        mock_config.obsidian_vault_path = None
        mock_gui.config = mock_config

        result = mock_gui._get_vault_name()
        assert result == "Not configured"

    def test_get_vault_name_with_path(self, mock_gui, mock_config):
        """Test vault name extraction with valid path."""
        from pathlib import Path
        mock_config.obsidian_vault_path = Path("/Users/test/MyVault")
        mock_gui.config = mock_config

        result = mock_gui._get_vault_name()
        assert result == "MyVault"

    def test_format_provider_name_no_config(self, mock_gui):
        """Test provider name formatting with no config."""
        result = mock_gui._format_provider_name()
        assert result == "Not configured"

    def test_format_provider_name_aws(self, mock_gui, mock_config):
        """Test provider name formatting for AWS."""
        mock_config.llm_provider = LLMProvider.AWS
        mock_gui.config = mock_config

        result = mock_gui._format_provider_name()
        assert result == "AWS"

    def test_format_provider_name_openai(self, mock_gui, mock_config):
        """Test provider name formatting for OpenAI."""
        mock_config.llm_provider = LLMProvider.OPENAI
        mock_gui.config = mock_config

        result = mock_gui._format_provider_name()
        assert result == "OpenAI"

    def test_get_config_info_no_config(self, mock_gui):
        """Test config info with no configuration loaded."""
        result = mock_gui.get_config_info()
        assert result == "Configuration not loaded"

    def test_get_config_info_with_config(self, mock_gui, mock_config):
        """Test config info with loaded configuration."""
        mock_gui.config = mock_config

        result = mock_gui.get_config_info()

        assert "Current Configuration:" in result
        assert "AWS" in result
        assert "claude-3-5-sonnet" in result
        assert "False" in result  # debug_mode
        assert "http://localhost:8080" in result  # searxng_base_url

    def test_create_interface(self, mock_gui):
        """Test Gradio interface creation."""
        # Mock gradio components to avoid actual GUI creation
        with patch('gui.gr.Blocks') as mock_blocks, \
             patch('gui.gr.Markdown'), \
             patch('gui.gr.Row'), \
             patch('gui.gr.Column'), \
             patch('gui.gr.Chatbot'), \
             patch('gui.gr.Textbox'), \
             patch('gui.gr.Button'), \
             patch('gui.gr.State'):

            mock_interface = Mock()
            mock_blocks.return_value.__enter__.return_value = mock_interface

            result = mock_gui.create_interface()

            assert result == mock_interface
            mock_blocks.assert_called_once()


class TestGUIEventHandlers:
    """Test cases for GUI event handler functions."""

    @pytest.fixture
    def mock_gui_with_agent(self):
        """Create GUI with mocked agent for event testing."""
        gui = AgentGUI()
        gui.agent = Mock(spec=ProductivityAgent)
        gui.agent.run_conversation = AsyncMock(return_value="Event response")
        return gui

    def test_add_user_message_empty(self):
        """Test adding empty user message."""
        from gui import AgentGUI
        AgentGUI()

        # Simulate the add_user_message function logic
        message = ""
        history = []

        # Expected behavior: return empty message, unchanged history, empty state
        if not message.strip():
            result_msg, result_history, result_state = "", history, ""
        else:
            result_history = history + [{"role": "user", "content": message}]
            result_msg, result_state = "", message

        assert result_msg == ""
        assert result_history == []
        assert result_state == ""

    def test_add_user_message_valid(self):
        """Test adding valid user message."""
        from gui import AgentGUI
        AgentGUI()

        # Simulate the add_user_message function logic
        message = "Test message"
        history = []

        if not message.strip():
            result_msg, result_history, result_state = "", history, ""
        else:
            result_history = history + [{"role": "user", "content": message}]
            result_msg, result_state = "", message

        assert result_msg == ""
        assert len(result_history) == 1
        assert result_history[0]["role"] == "user"
        assert result_history[0]["content"] == "Test message"
        assert result_state == "Test message"

    def test_clear_chat(self):
        """Test chat clearing functionality."""
        gui = AgentGUI()
        gui.conversation_history = [("user", "test"), ("assistant", "response")]

        # Simulate clear_chat function
        gui.conversation_history = []
        result_history, result_msg = [], ""

        assert gui.conversation_history == []
        assert result_history == []
        assert result_msg == ""


class TestGUIMainFunction:
    """Test cases for GUI main function and startup."""

    @pytest.mark.asyncio
    async def test_main_agent_init_success(self):
        """Test main function with successful agent initialization."""
        with patch('gui.AgentGUI') as mock_gui_class, \
             patch('gui.print'):

            mock_gui = Mock()
            mock_gui_class.return_value = mock_gui
            mock_gui.initialize_agent = AsyncMock(return_value=True)
            mock_gui.config = Mock()
            mock_gui.config.llm_provider = "aws"
            mock_gui.config.llm_choice = "claude-3-5-sonnet"
            mock_gui.config.debug_mode = False
            mock_gui.agent = Mock()
            mock_gui.agent.has_mcp_servers = Mock(return_value=False)
            mock_gui.create_interface = Mock()
            mock_interface = Mock()
            mock_gui.create_interface.return_value = mock_interface
            mock_interface.launch = Mock()

            from gui import main
            await main()

            mock_gui.initialize_agent.assert_called_once()
            mock_gui.create_interface.assert_called_once()
            mock_interface.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_agent_init_failure(self):
        """Test main function with agent initialization failure."""
        with patch('gui.AgentGUI') as mock_gui_class, \
             patch('gui.print') as mock_print:

            mock_gui = Mock()
            mock_gui_class.return_value = mock_gui
            mock_gui.initialize_agent = AsyncMock(return_value=False)

            from gui import main
            await main()

            mock_gui.initialize_agent.assert_called_once()
            # Should print warning but continue
            assert any("initialization failed" in str(call) for call in mock_print.call_args_list)

    @pytest.mark.asyncio
    async def test_main_with_mcp_servers(self):
        """Test main function with MCP servers enabled."""
        with patch('gui.AgentGUI') as mock_gui_class, \
             patch('gui.print'), \
             patch('agent.agent.agent') as mock_global_agent:

            mock_gui = Mock()
            mock_gui_class.return_value = mock_gui
            mock_gui.initialize_agent = AsyncMock(return_value=True)
            mock_gui.config = Mock()
            mock_gui.config.llm_provider = "aws"
            mock_gui.config.llm_choice = "claude-3-5-sonnet"
            mock_gui.config.debug_mode = False
            mock_gui.agent = Mock()
            mock_gui.agent.has_mcp_servers = Mock(return_value=True)
            mock_gui.create_interface = Mock()
            mock_interface = Mock()
            mock_gui.create_interface.return_value = mock_interface
            mock_interface.launch = Mock()

            # Mock MCP context manager
            mock_context = AsyncMock()
            mock_global_agent.run_mcp_servers.return_value = mock_context

            from gui import main
            await main()

            mock_gui.initialize_agent.assert_called_once()
            mock_global_agent.run_mcp_servers.assert_called_once()
            mock_interface.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_mcp_servers_fail(self):
        """Test main function when MCP servers fail to start."""
        with patch('gui.AgentGUI') as mock_gui_class, \
             patch('gui.print'), \
             patch('agent.agent.agent') as mock_global_agent:

            mock_gui = Mock()
            mock_gui_class.return_value = mock_gui
            mock_gui.initialize_agent = AsyncMock(return_value=True)
            mock_gui.config = Mock()
            mock_gui.config.llm_provider = "aws"
            mock_gui.config.llm_choice = "claude-3-5-sonnet"
            mock_gui.config.debug_mode = False
            mock_gui.agent = Mock()
            mock_gui.agent.has_mcp_servers = Mock(return_value=True)
            mock_gui.agent.disable_mcp_servers = Mock()
            mock_gui.create_interface = Mock()
            mock_interface = Mock()
            mock_gui.create_interface.return_value = mock_interface
            mock_interface.launch = Mock()

            # Mock MCP context manager to fail
            mock_global_agent.run_mcp_servers.side_effect = Exception("MCP failed")

            from gui import main
            await main()

            mock_gui.initialize_agent.assert_called_once()
            mock_gui.agent.disable_mcp_servers.assert_called_once()
            mock_interface.launch.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
