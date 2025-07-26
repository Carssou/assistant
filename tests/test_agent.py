"""
Unit tests for the PydanticAI Agent - following course pattern.

Simple tests that match the course structure.
"""

from unittest.mock import MagicMock, patch

import pytest

from agent.agent import AgentDeps, agent
from config.settings import AgentConfig


class TestAgent:
    """Test cases for the agent following course pattern."""

    def test_agent_exists(self):
        """Test that agent is created and accessible."""
        assert agent is not None
        assert agent._deps_type == AgentDeps

    def test_agent_deps_structure(self):
        """Test that AgentDeps has the expected fields."""
        # Check the dataclass has the right fields
        import dataclasses

        assert dataclasses.is_dataclass(AgentDeps)

        fields = {f.name for f in dataclasses.fields(AgentDeps)}
        expected_fields = {"config", "http_client", "langfuse_client", "vault_path"}
        assert fields == expected_fields

    def test_take_screenshot_tool(self):
        """Test screenshot tool is registered."""
        # Check the tool exists by looking at registered functions
        assert hasattr(agent, "_function_tools")
        tool_names = list(agent._function_tools.keys())
        assert "take_screenshot" in tool_names

    def test_take_region_screenshot_tool(self):
        """Test region screenshot tool is registered."""
        assert hasattr(agent, "_function_tools")
        tool_names = list(agent._function_tools.keys())
        assert "take_region_screenshot" in tool_names

    def test_get_screen_info_tool(self):
        """Test screen info tool is registered."""
        assert hasattr(agent, "_function_tools")
        tool_names = list(agent._function_tools.keys())
        assert "get_screen_info" in tool_names


class TestAgentTools:
    """Test individual tools following course pattern."""

    @pytest.mark.asyncio
    async def test_screenshot_tool_with_mock(self):
        """Test screenshot tool with mocked dependencies."""
        with patch("agent.tools.take_screenshot") as mock_screenshot:
            mock_screenshot.return_value = b"fake_image_data"

            from agent.tools import take_screenshot_tool
            from config.settings import load_config

            config = load_config()
            result = await take_screenshot_tool(config, 75)

            # Should return BinaryContent
            assert hasattr(result, "data")
            assert hasattr(result, "media_type")

    @pytest.mark.asyncio
    async def test_region_screenshot_tool(self):
        """Test region screenshot tool."""
        with patch("agent.tools.take_region_screenshot") as mock_screenshot:
            mock_screenshot.return_value = b"fake_region_data"

            from agent.tools import take_region_screenshot_tool

            result = await take_region_screenshot_tool(0, 0, 100, 100, 85)

            # Should return BinaryContent
            assert hasattr(result, "data")
            assert hasattr(result, "media_type")

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
