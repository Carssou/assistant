"""
MCP server configurations for the Strands agent.

This module provides factory functions for creating MCP server instances
for different productivity tools using Strands native MCP integration.
"""

from mcp import StdioServerParameters, stdio_client
from strands.tools.mcp import MCPClient

from config.settings import AgentConfig


def create_obsidian_mcp_server(config: AgentConfig) -> None:
    """
    Obsidian MCP server disabled - using native tools instead.

    The Obsidian functionality is now implemented as native PydanticAI tools
    for better performance (sub-1-second vs 20+ second response times).
    """
    # Temporarily disabled - native tools are now used instead
    return None


def create_searxng_mcp_server(config: AgentConfig) -> MCPClient | None:
    """
    Create SearXNG MCP server instance using Strands.

    Args:
        config: Agent configuration containing SearXNG settings

    Returns:
        MCPClient instance or None if not configured
    """
    if not config.searxng_base_url:
        return None

    env = {"SEARXNG_URL": config.searxng_base_url}

    # Add authentication if configured
    if hasattr(config, "searxng_username") and config.searxng_username:
        env["AUTH_USERNAME"] = config.searxng_username
    if hasattr(config, "searxng_password") and config.searxng_password:
        env["AUTH_PASSWORD"] = config.searxng_password

    # Create Strands MCPClient with stdio transport
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(command="npx", args=["-y", "mcp-searxng"], env=env)
        )
    )


def create_todoist_mcp_server(config: AgentConfig) -> MCPClient | None:
    """
    Create Todoist MCP server instance using Strands.

    Args:
        config: Agent configuration containing Todoist settings

    Returns:
        MCPClient instance or None if not configured
    """
    if not config.todoist_api_token:
        return None

    # Create Strands MCPClient with stdio transport
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@abhiz123/todoist-mcp-server"],
                env={"TODOIST_API_TOKEN": config.todoist_api_token},
            )
        )
    )


def create_youtube_mcp_server(config: AgentConfig) -> MCPClient | None:
    """
    Create YouTube MCP server instance using Strands.

    Args:
        config: Agent configuration containing YouTube settings

    Returns:
        MCPClient instance or None if not configured
    """
    # YouTube MCP server doesn't require API key - it works without one
    # Always create the server as it provides video processing capabilities
    # Using standard YouTube MCP server (not PydanticAI fork)
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(command="npx", args=["-y", "youtube-video-summarizer-mcp"])
        )
    )


def create_all_mcp_servers(config: AgentConfig) -> list[MCPClient]:
    """
    Create all configured MCP servers using Strands.

    Args:
        config: Agent configuration

    Returns:
        List of configured Strands MCPClient instances
    """
    servers = []

    # Add Obsidian server if configured (currently disabled - using native tools)
    obsidian_server = create_obsidian_mcp_server(config)
    if obsidian_server:
        servers.append(obsidian_server)

    # Add other servers as they are implemented
    searxng_server = create_searxng_mcp_server(config)
    if searxng_server:
        servers.append(searxng_server)

    todoist_server = create_todoist_mcp_server(config)
    if todoist_server:
        servers.append(todoist_server)

    youtube_server = create_youtube_mcp_server(config)
    if youtube_server:
        servers.append(youtube_server)

    return servers
