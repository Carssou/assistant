"""
PydanticAI agent - following the exact course pattern.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
from langfuse import Langfuse
from pydantic_ai import Agent, RunContext

from agent.prompts import get_system_prompt
from agent.tools import (
    get_screen_info_tool,
    take_region_screenshot_tool,
    take_screenshot_tool,
)
from config.settings import AgentConfig, create_model_instance, load_config
from mcp_servers.configs import create_all_mcp_servers

# Load config
config = load_config()


@dataclass
class AgentDeps:
    """Simple dependency container - exactly like the course example."""

    config: AgentConfig
    http_client: httpx.AsyncClient
    langfuse_client: Langfuse | None
    vault_path: Path | None


# Create agent - exactly like the course
agent = Agent(
    create_model_instance(config),
    system_prompt=get_system_prompt(),
    deps_type=AgentDeps,
    mcp_servers=create_all_mcp_servers(config),
    retries=2,
)


@agent.tool
async def take_screenshot(ctx: RunContext[AgentDeps], quality: int = 75) -> str | Any:
    """Take a screenshot for visual analysis."""
    print("Calling take_screenshot tool")

    # Check if Nova model - use direct Bedrock API
    from utils.bedrock_vision import should_use_bedrock_direct

    if should_use_bedrock_direct(ctx.deps.config):
        from utils.bedrock_vision import analyze_full_screenshot_with_bedrock
        from utils.screen_capture import take_screenshot as take_screenshot_direct

        image_bytes = take_screenshot_direct(quality)
        analysis = await analyze_full_screenshot_with_bedrock(image_bytes, ctx.deps.config)
        return analysis

    return await take_screenshot_tool(ctx.deps.config, quality)


@agent.tool
async def take_region_screenshot(
    ctx: RunContext[AgentDeps],
    x: int,
    y: int,
    width: int,
    height: int,
    quality: int = 85,
) -> str | Any:
    """Take a screenshot of a specific region."""
    print("Calling take_region_screenshot tool")

    # Check if Nova model - use direct Bedrock API
    from utils.bedrock_vision import should_use_bedrock_direct

    if should_use_bedrock_direct(ctx.deps.config):
        from utils.bedrock_vision import analyze_region_screenshot_with_bedrock
        from utils.screen_capture import take_region_screenshot as take_region_screenshot_direct

        image_bytes = take_region_screenshot_direct(x, y, width, height, quality)
        analysis = await analyze_region_screenshot_with_bedrock(
            image_bytes, x, y, width, height, ctx.deps.config
        )
        return analysis

    return await take_region_screenshot_tool(x, y, width, height, quality)


@agent.tool
async def get_screen_info(ctx: RunContext[AgentDeps]) -> dict[str, Any]:
    """Get information about the current screen."""
    print("Calling get_screen_info tool")
    return await get_screen_info_tool()
