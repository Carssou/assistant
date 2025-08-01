"""
Integration tests for Strands GUI.

Updated tests for StrandsGUI with native session management.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from agent.agent import agent
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
        # Agent is pre-created from agent.agent module
        assert mock_gui.agent is not None
        assert mock_gui.config is None  # Config still needs initialization

    @pytest.mark.asyncio
    async def test_initialize_config_success(self, mock_gui):
        """Test successful config initialization."""
        with patch("gui.load_config") as mock_load:
            mock_config = Mock()
            mock_load.return_value = mock_config

            result = await mock_gui.initialize_config()

            assert result is True
            assert mock_gui.config == mock_config

    @pytest.mark.asyncio
    async def test_initialize_config_failure(self, mock_gui):
        """Test config initialization failure."""
        with patch("gui.load_config") as mock_load:
            mock_load.side_effect = Exception("Config error")

            result = await mock_gui.initialize_config()

            assert result is False
            assert mock_gui.config is None

    @pytest.mark.asyncio
    async def test_get_agent_response_success(self, mock_gui):
        """Test successful agent response."""
        with patch.object(mock_gui.agent, "invoke_async") as mock_invoke:
            mock_invoke.return_value = "Test response"

            result = await mock_gui.get_agent_response("Test message")

            assert result == "Test response"
            mock_invoke.assert_called_once_with("Test message")

    @pytest.mark.asyncio
    async def test_get_agent_response_error(self, mock_gui):
        """Test agent response with error."""
        with patch.object(mock_gui.agent, "invoke_async") as mock_invoke:
            mock_invoke.side_effect = Exception("Agent error")

            result = await mock_gui.get_agent_response("Test message")

            assert "❌ **Error**" in result
            assert "Agent error" in result

    def test_get_conversation_history_empty(self, mock_gui):
        """Test getting empty conversation history."""
        # Mock empty messages
        mock_gui.agent.messages = []

        history = mock_gui.get_conversation_history()

        assert history == []

    def test_get_conversation_history_with_messages(self, mock_gui):
        """Test getting conversation history with messages."""
        # Mock messages with role and content
        mock_msg1 = Mock()
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"

        mock_msg2 = Mock()
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hi there!"

        mock_gui.agent.messages = [mock_msg1, mock_msg2]

        history = mock_gui.get_conversation_history()

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"

    def test_clear_conversation(self, mock_gui):
        """Test clearing conversation."""
        # Add some mock messages
        mock_gui.agent.messages = [Mock(), Mock()]

        result = mock_gui.clear_conversation()

        assert result is True
        assert len(mock_gui.agent.messages) == 0

    def test_get_config_info_no_config(self, mock_gui):
        """Test config info when no config loaded."""
        result = mock_gui.get_config_info()

        assert "❌ **Configuration not loaded**" in result

    def test_get_config_info_with_config(self, mock_gui, mock_config):
        """Test config info with loaded config."""
        from unittest.mock import PropertyMock

        mock_gui.config = mock_config
        mock_gui.agent.messages = []

        # Mock the tool_names property properly
        with patch.object(
            type(mock_gui.agent), "tool_names", new_callable=PropertyMock
        ) as mock_tool_names:
            mock_tool_names.return_value = ["tool1", "tool2", "tool3"]

            result = mock_gui.get_config_info()

            assert "✅ **LLM Provider**: AWS" in result
            assert "✅ **Model**: claude-3-5-sonnet" in result
            assert "💬 **Messages in conversation**: 0" in result
            assert "🛠️ **Available Tools**: 3" in result

    def test_process_uploaded_file_text(self, mock_gui):
        """Test processing text file upload."""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            result = mock_gui.process_uploaded_file(temp_path)

            assert "📎 Uploaded File" in result
            assert "Test content" in result
        finally:
            os.unlink(temp_path)

    def test_process_uploaded_file_empty(self, mock_gui):
        """Test processing empty file path."""
        result = mock_gui.process_uploaded_file("")

        assert result == ""

    def test_create_interface(self, mock_gui):
        """Test creating Gradio interface."""
        interface = mock_gui.create_interface()

        # Basic checks that interface was created
        assert interface is not None
        assert hasattr(interface, "launch")


class TestStrandsGUIStreaming:
    """Test streaming functionality of StrandsGUI."""

    @pytest.fixture
    def mock_gui(self):
        """Create a StrandsGUI instance for testing."""
        return StreamlitGUI()

    @pytest.mark.asyncio
    async def test_get_streaming_response_success(self, mock_gui):
        """Test successful streaming response."""

        async def mock_stream():
            yield Mock(text="Hello ")
            yield Mock(text="world!")

        with patch.object(mock_gui.agent, "stream_async", return_value=mock_stream()):
            responses = []
            async for response in mock_gui.get_streaming_response("Test message"):
                responses.append(response)

            assert responses == ["Hello ", "Hello world!"]

    @pytest.mark.asyncio
    async def test_get_streaming_response_fallback(self, mock_gui):
        """Test streaming fallback to invoke_async."""

        async def mock_empty_stream():
            # Empty stream should trigger fallback
            return
            yield  # unreachable

        with patch.object(mock_gui.agent, "stream_async", return_value=mock_empty_stream()):
            with patch.object(mock_gui.agent, "invoke_async", return_value="Fallback response"):
                responses = []
                async for response in mock_gui.get_streaming_response("Test message"):
                    responses.append(response)

                assert responses == ["Fallback response"]

    @pytest.mark.asyncio
    async def test_get_streaming_response_error(self, mock_gui):
        """Test streaming response with error."""
        with patch.object(mock_gui.agent, "stream_async", side_effect=Exception("Stream error")):
            responses = []
            async for response in mock_gui.get_streaming_response("Test message"):
                responses.append(response)

            assert len(responses) == 1
            assert "❌ **Error**" in responses[0]
            assert "Stream error" in responses[0]


class TestStrandsGUIMain:
    """Test main function of StrandsGUI."""

    @pytest.mark.asyncio
    async def test_main_success(self):
        """Test successful main function execution."""
        from gui import main

        with patch("gui.StrandsGUI") as mock_gui_class:
            mock_gui = Mock()
            mock_gui.initialize_config = AsyncMock(return_value=True)
            mock_gui.config = Mock()
            mock_gui.config.llm_provider = "openai"
            mock_gui.config.llm_choice = "gpt-4o"
            mock_gui.config.debug_mode = False
            mock_gui.agent = Mock()

            # Mock tool_names property properly
            type(mock_gui.agent).tool_names = PropertyMock(return_value=["tool1", "tool2"])

            mock_gui.create_interface = Mock()

            mock_interface = Mock()
            mock_interface.launch = Mock()
            mock_gui.create_interface.return_value = mock_interface

            mock_gui_class.return_value = mock_gui

            # Patch the launch to not actually start server
            with patch.object(mock_interface, "launch"):
                # This would normally run forever, so we need to mock the launch
                try:
                    await asyncio.wait_for(main(), timeout=0.1)
                except TimeoutError:
                    # Expected - main() runs indefinitely
                    pass

            mock_gui.initialize_config.assert_called_once()
            mock_gui.create_interface.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_config_failure(self, capsys):
        """Test main function with config failure."""
        from gui import main

        with patch("gui.StrandsGUI") as mock_gui_class:
            mock_gui = Mock()
            mock_gui.initialize_config = AsyncMock(return_value=False)
            mock_gui_class.return_value = mock_gui

            await main()

            mock_gui.initialize_config.assert_called_once()
            # Should print warning about config failure
            captured = capsys.readouterr()
            assert "Configuration initialization failed" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
