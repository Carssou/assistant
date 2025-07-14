"""
PydanticAI agent implementation.
"""

from typing import Any

from pydantic_ai import Agent, RunContext

from agent.dependencies import AgentDependencies, create_agent_dependencies
from agent.prompts import get_system_prompt
from agent.tools import (
    get_screen_info_tool,
    take_region_screenshot_tool,
    take_screenshot_tool,
)
from config.settings import AgentConfig, create_model_instance, load_config
from mcp_servers.configs import create_all_mcp_servers


async def create_agent(
    config: AgentConfig | None = None,
) -> tuple[Agent[AgentDependencies], AgentDependencies]:
    """
    Create PydanticAI agent with dependencies.

    Args:
        config: Optional agent configuration. If None, loads from environment.

    Returns:
        Tuple of (agent, dependencies) - agent needs dependencies to be useful
    """
    if config is None:
        config = load_config()

    # Create dependencies first - agent needs them to be useful
    deps = await create_agent_dependencies(config)

    # Create model and MCP servers
    model = create_model_instance(config)
    mcp_servers = create_all_mcp_servers(config)

    # Create agent with proper typing
    agent = Agent(
        model,
        deps_type=AgentDependencies,
        system_prompt=get_system_prompt(),
        mcp_servers=mcp_servers,
        retries=2,  # Add retries for robustness
    )

    # Register tools following reference implementation pattern
    @agent.tool
    async def take_screenshot(ctx: RunContext[AgentDependencies], quality: int = 75) -> str | Any:
        """
        Take a screenshot for visual analysis and assistance.

        This tool captures the current screen and returns it as a base64-encoded image
        that can be analyzed by the AI. The image quality is automatically optimized
        based on the model being used to ensure efficient processing.

        Args:
            ctx: The context including agent dependencies
            quality: Image quality (1-100, default 75). Lower values for faster processing,
                    higher values for better detail. Automatically adjusted for smaller models.

        Returns:
            BinaryContent with image data for compatible models, or text analysis for Nova models
        """
        print("Calling take_screenshot tool")

        # Check if Nova model - use direct Bedrock API
        from utils.bedrock_vision import should_use_bedrock_direct

        if should_use_bedrock_direct(ctx.deps.config):
            print("Using direct Bedrock API for Nova model")
            from utils.bedrock_vision import analyze_full_screenshot_with_bedrock
            from utils.screen_capture import take_screenshot as take_screenshot_direct

            # Take screenshot and analyze directly with Bedrock
            image_bytes = take_screenshot_direct(quality)
            analysis = await analyze_full_screenshot_with_bedrock(image_bytes, ctx.deps.config)

            # For Nova, return the analysis directly instead of BinaryContent
            return analysis

        return await take_screenshot_tool(ctx.deps, quality)

    @agent.tool
    async def take_region_screenshot(
        ctx: RunContext[AgentDependencies],
        x: int,
        y: int,
        width: int,
        height: int,
        quality: int = 85,
    ) -> str | Any:
        """
        Take a screenshot of a specific rectangular region of the screen.

        This tool allows for precise capture of specific areas of the screen, useful
        when you need to focus on particular UI elements, windows, or screen regions
        without capturing the entire display.

        Args:
            ctx: The context including agent dependencies
            x: Left coordinate of the region (pixels from left edge)
            y: Top coordinate of the region (pixels from top edge)
            width: Width of the region in pixels
            height: Height of the region in pixels
            quality: Image quality (1-100, default 85)

        Returns:
            BinaryContent with image data of the specified region or text analysis for Nova models
        """
        print("Calling take_region_screenshot tool")

        # Check if Nova model - use direct Bedrock API
        from utils.bedrock_vision import should_use_bedrock_direct

        if should_use_bedrock_direct(ctx.deps.config):
            print("Using direct Bedrock API for Nova model (region screenshot)")
            from utils.bedrock_vision import analyze_region_screenshot_with_bedrock
            from utils.screen_capture import take_region_screenshot as take_region_screenshot_direct

            # Take region screenshot and analyze directly with Bedrock
            image_bytes = take_region_screenshot_direct(x, y, width, height, quality)
            analysis = await analyze_region_screenshot_with_bedrock(
                image_bytes, x, y, width, height, ctx.deps.config
            )

            # For Nova, return the analysis directly instead of BinaryContent
            return analysis

        return await take_region_screenshot_tool(ctx.deps, x, y, width, height, quality)

    @agent.tool
    async def get_screen_info(ctx: RunContext[AgentDependencies]) -> dict[str, Any]:
        """
        Get information about the current screen/desktop environment.

        This tool provides metadata about the user's display setup, including screen
        dimensions and cursor position. Useful for understanding the user's workspace
        and providing context-aware assistance.

        Args:
            ctx: The context including agent dependencies

        Returns:
            Dictionary containing:
            - screen_size: Tuple of (width, height) in pixels
            - cursor_position: Tuple of (x, y) coordinates of mouse cursor
            - timestamp: When the information was captured
        """
        print("Calling get_screen_info tool")
        return await get_screen_info_tool(ctx.deps)

    return agent, deps
