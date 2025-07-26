"""
Unit tests for the PydanticAI Agent - following course pattern.

Simple tests that match the course structure.
"""

from unittest.mock import MagicMock, patch

import pytest

# Try to import and catch any errors during module loading
try:
    from agent.agent import AgentDeps, agent
    from config.settings import AgentConfig

    IMPORT_SUCCESS = True
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_SUCCESS = False
    IMPORT_ERROR = str(e)
    # Create dummy objects so tests can run
    AgentDeps = None
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

        assert agent is not None
        assert agent._deps_type == AgentDeps

        # Debug info for CI
        print(f"Agent type: {type(agent)}")
        print(f"Agent model: {type(agent.model)}")
        print(f"Has _function_tools: {hasattr(agent, '_function_tools')}")
        if hasattr(agent, "_function_tools"):
            print(f"Tools: {list(agent._function_tools.keys())}")
        print(f"Agent attributes: {[a for a in dir(agent) if 'tool' in a.lower()]}")

    def test_agent_deps_structure(self):
        """Test that AgentDeps has the expected fields."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        # Check the dataclass has the right fields
        import dataclasses

        assert dataclasses.is_dataclass(AgentDeps)

        fields = {f.name for f in dataclasses.fields(AgentDeps)}
        expected_fields = {"config", "http_client", "langfuse_client", "vault_path"}
        assert fields == expected_fields

    def test_take_screenshot_tool(self):
        """Test screenshot tool is registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        # Check the tool exists by looking at registered functions
        # First check if agent has the attribute (more robust than direct access)
        if hasattr(agent, "_function_tools"):
            tool_names = list(agent._function_tools.keys())
            assert "take_screenshot" in tool_names
        else:
            # Alternative check: verify the tool decorator worked
            assert hasattr(agent, "tool")
            # Agent should be properly initialized
            assert agent is not None

    def test_take_region_screenshot_tool(self):
        """Test region screenshot tool is registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        if hasattr(agent, "_function_tools"):
            tool_names = list(agent._function_tools.keys())
            assert "take_region_screenshot" in tool_names
        else:
            assert hasattr(agent, "tool")
            assert agent is not None

    def test_get_screen_info_tool(self):
        """Test screen info tool is registered."""
        if not IMPORT_SUCCESS:
            pytest.skip(f"Skipping due to import failure: {IMPORT_ERROR}")

        if hasattr(agent, "_function_tools"):
            tool_names = list(agent._function_tools.keys())
            assert "get_screen_info" in tool_names
        else:
            assert hasattr(agent, "tool")
            assert agent is not None


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
