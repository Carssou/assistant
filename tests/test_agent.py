"""
Unit tests for the Strands Agent.

Updated tests for Strands Agents framework.
"""

from unittest.mock import MagicMock, patch

import pytest

# Try to import and catch any errors during module loading
try:
    from agent.agent import agent_manager
    from config.settings import AgentConfig

    IMPORT_SUCCESS = True
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)
    # Create dummy objects so tests can run
    agent = None
    AgentConfig = None


class TestAgent:
    """Test cases for the agent following course pattern."""

    def test_import_success(self):
        """Test that imports worked correctly."""
        print(f"Import success: {IMPORT_SUCCESS}")
        if not IMPORT_SUCCESS:
            print(f"Import error: {IMPORT_ERROR}")
        assert IMPORT_SUCCESS, f"Failed to import agent modules: {IMPORT_ERROR}"

    def test_agent_exists(self):
        """Test that agent is created and accessible."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        assert agent_manager is not None
        assert agent_manager.native_agent is not None

        # Debug info for CI
        print(f"Agent manager type: {type(agent_manager)}")
        print(f"Native agent type: {type(agent_manager.native_agent)}")
        print(f"Agent model: {type(agent_manager.native_agent.model)}")
        print(f"Has tool_names: {hasattr(agent_manager.native_agent, 'tool_names')}")
        if hasattr(agent_manager.native_agent, "tool_names"):
            print(f"Tools: {agent_manager.native_agent.tool_names}")
        print(
            f"Agent attributes: {[a for a in dir(agent_manager.native_agent) if 'tool' in a.lower()]}"
        )

    def test_agent_has_tools(self):
        """Test that agent has tools registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        # Check that agent has tools
        assert hasattr(agent_manager.native_agent, "tool_names")
        assert len(agent_manager.native_agent.tool_names) > 0

        # Check that we have the expected tools
        expected_tools = ["take_screenshot", "create_note", "read_note"]

        for expected_tool in expected_tools:
            assert (
                expected_tool in agent_manager.native_agent.tool_names
            ), f"Missing tool: {expected_tool}"

    def test_take_screenshot_tool(self):
        """Test screenshot tool is registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        assert "take_screenshot" in agent_manager.native_agent.tool_names

    def test_take_region_screenshot_tool(self):
        """Test region screenshot tool is registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        assert "take_region_screenshot" in agent_manager.native_agent.tool_names

    def test_get_screen_info_tool(self):
        """Test screen info tool is registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        assert "get_screen_info" in agent_manager.native_agent.tool_names


class TestAgentTools:
    """Test individual tools following course pattern."""

    @pytest.mark.asyncio
    async def test_screenshot_tool_with_mock(self):
        """Test screenshot tool with mocked dependencies."""
        with patch("agent.tools.take_screenshot") as mock_screenshot:
            mock_screenshot.return_value = b"fake_image_data"

            from agent.tools import take_screenshot_tool
            from config.settings import AgentConfig, LLMProvider

            # Create test config directly to avoid validation issues
            config = AgentConfig(
                llm_provider=LLMProvider.AWS,
                llm_choice="claude-3-5-sonnet-20241022",
                obsidian_vault_path=None,
                _env_file=None,
            )
            result = await take_screenshot_tool(config, 75)

            # Should return base64 string
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_region_screenshot_tool(self):
        """Test region screenshot tool."""
        with patch("agent.tools.take_region_screenshot") as mock_screenshot:
            mock_screenshot.return_value = b"fake_region_data"

            from agent.tools import take_region_screenshot_tool

            result = await take_region_screenshot_tool(0, 0, 100, 100, 85)

            # Should return base64 string
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_screen_info_tool(self):
        """Test screen info tool."""
        with (
            patch("agent.tools.get_screen_size") as mock_size,
            patch("agent.tools.get_cursor_position") as mock_cursor,
        ):

            mock_size.return_value = (1920, 1080)
            mock_cursor.return_value = (100, 200)

            from agent.tools import get_screen_info_tool

            result = await get_screen_info_tool()

            # Should return dict with expected keys
            assert isinstance(result, dict)
            assert "screen_size" in result
            assert "cursor_position" in result
            assert "timestamp" in result
