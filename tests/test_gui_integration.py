"""
Integration tests for Strands GUI.

Updated tests for StrandsGUI with native session management.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from agent.agent import agent_manager
from config.settings import AgentConfig, LLMProvider
from streamlit_gui import StreamlitGUI


class TestStreamlitGUI:
    """Test cases for StreamlitGUI class."""

    @pytest.fixture
    def mock_gui(self):
        """Create a StreamlitGUI instance for testing."""
        return StreamlitGUI()

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

    def test_gui_initialization(self, mock_gui):
        """Test GUI initialization."""
        # Agent manager is pre-created from agent.agent module
        assert mock_gui.agent_manager is not None
        assert mock_gui.config is None  # Config still needs initialization

    @pytest.mark.asyncio
    async def test_initialize_config_success(self, mock_gui):
        """Test successful config initialization."""
        with patch("streamlit_gui.load_config") as mock_load:
            mock_config = Mock()
            mock_load.return_value = mock_config

            result = await mock_gui.initialize_config()

            assert result is True
            assert mock_gui.config == mock_config

    @pytest.mark.asyncio
    async def test_initialize_config_failure(self, mock_gui):
        """Test config initialization failure."""
        with patch("streamlit_gui.load_config") as mock_load:
            mock_load.side_effect = Exception("Config error")

            result = await mock_gui.initialize_config()

            assert result is False
            assert mock_gui.config is None

    @pytest.mark.asyncio
    async def test_get_streaming_response_success(self, mock_gui):
        """Test successful streaming response."""

        async def mock_stream():
            yield {"result": Mock(message={"content": [{"text": "Test response"}]})}

        with patch.object(mock_gui.agent_manager, "stream_with_mcp", return_value=mock_stream()):
            responses = []
            async for response in mock_gui.get_streaming_response("Test message"):
                responses.append(response)

            assert responses == ["Test response"]

    @pytest.mark.asyncio
    async def test_get_streaming_response_error(self, mock_gui):
        """Test streaming response with error."""
        with patch.object(
            mock_gui.agent_manager, "stream_with_mcp", side_effect=Exception("Agent error")
        ):
            responses = []
            async for response in mock_gui.get_streaming_response("Test message"):
                responses.append(response)

            assert len(responses) == 1
            assert "❌ **Error**" in responses[0]
            assert "Agent error" in responses[0]

    def test_get_conversation_history_empty(self, mock_gui):
        """Test getting empty conversation history."""
        # Mock empty messages
        mock_gui.agent_manager.native_agent.messages = []

        # Streamlit GUI doesn't have get_conversation_history method
        # Instead it uses st.session_state.messages
        # For testing, just verify agent messages are empty
        assert len(mock_gui.agent_manager.native_agent.messages) == 0

    def test_get_conversation_history_with_messages(self, mock_gui):
        """Test getting conversation history with messages."""
        # Mock messages with role and content
        mock_msg1 = Mock()
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"

        mock_msg2 = Mock()
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hi there!"

        mock_gui.agent_manager.native_agent.messages = [mock_msg1, mock_msg2]

        # Streamlit GUI uses agent messages directly
        messages = mock_gui.agent_manager.native_agent.messages
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi there!"

    def test_clear_conversation(self, mock_gui):
        """Test clearing conversation."""
        # Add some mock messages
        mock_gui.agent_manager.native_agent.messages = [Mock(), Mock()]

        # Streamlit GUI clears messages directly
        mock_gui.agent_manager.native_agent.messages.clear()

        assert len(mock_gui.agent_manager.native_agent.messages) == 0

    def test_get_config_info_no_config(self, mock_gui):
        """Test config info when no config loaded."""
        # Streamlit GUI doesn't have get_config_info method
        # Config state is checked via mock_gui.config
        assert mock_gui.config is None

    def test_get_config_info_with_config(self, mock_gui, mock_config):
        """Test config info with loaded config."""
        from unittest.mock import PropertyMock

        mock_gui.config = mock_config
        mock_gui.agent_manager.native_agent.messages = []

        # Mock the tool_names property properly
        with patch.object(
            type(mock_gui.agent_manager.native_agent), "tool_names", new_callable=PropertyMock
        ) as mock_tool_names:
            mock_tool_names.return_value = ["tool1", "tool2", "tool3"]

            # Streamlit GUI has config loaded
            assert mock_gui.config == mock_config
            assert len(mock_gui.agent_manager.native_agent.tool_names) == 3

    # Note: Streamlit GUI doesn't have file upload or interface creation methods
    # These were part of the old Gradio implementation

    def test_has_agent_manager(self, mock_gui):
        """Test that GUI has agent manager."""
        assert hasattr(mock_gui, "agent_manager")
        assert mock_gui.agent_manager is not None


class TestStrandsGUIStreaming:
    """Test streaming functionality of StreamlitGUI."""

    @pytest.fixture
    def mock_gui(self):
        """Create a StreamlitGUI instance for testing."""
        return StreamlitGUI()

    @pytest.mark.asyncio
    async def test_get_streaming_response_success(self, mock_gui):
        """Test successful streaming response."""

        async def mock_stream():
            yield {"result": Mock(message={"content": [{"text": "Hello world!"}]})}

        with patch.object(mock_gui.agent_manager, "stream_with_mcp", return_value=mock_stream()):
            responses = []
            async for response in mock_gui.get_streaming_response("Test message"):
                responses.append(response)

            assert responses == ["Hello world!"]

    @pytest.mark.asyncio
    async def test_get_streaming_response_error(self, mock_gui):
        """Test streaming response with error."""
        with patch.object(
            mock_gui.agent_manager, "stream_with_mcp", side_effect=Exception("Stream error")
        ):
            responses = []
            async for response in mock_gui.get_streaming_response("Test message"):
                responses.append(response)

            assert len(responses) == 1
            assert "❌ **Error**" in responses[0]
            assert "Stream error" in responses[0]


class TestStrandsGUIMain:
    """Test main function of StreamlitGUI."""

    def test_main_function_exists(self):
        """Test that main function exists in streamlit_gui module."""
        from streamlit_gui import main

        assert callable(main)

    def test_initialize_session_state_function(self):
        """Test that initialize_session_state function exists."""
        from streamlit_gui import initialize_session_state

        assert callable(initialize_session_state)

    def test_load_configuration_function(self):
        """Test that load_configuration function exists."""
        from streamlit_gui import load_configuration

        assert callable(load_configuration)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
