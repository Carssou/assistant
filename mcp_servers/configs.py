"""
MCP server configurations for the PydanticAI agent.

This module provides factory functions for creating MCP server instances
for different productivity tools.
"""


from pydantic_ai.mcp import MCPServerStdio

from config.settings import AgentConfig


def create_obsidian_mcp_server(config: AgentConfig) -> MCPServerStdio | None:
    """
    Create Obsidian MCP server instance.

    Args:
        config: Agent configuration containing vault path

    Returns:
        MCPServerStdio instance or None if vault path not configured
    """
    if not config.obsidian_vault_path:
        return None

    vault_path = config.obsidian_vault_path

    # Skip validation for placeholder paths
    if str(vault_path) == "/path/to/your/vault":
        return None

    if not vault_path.exists():
        raise ValueError(f"Obsidian vault path does not exist: {vault_path}")

    return MCPServerStdio(
        command='npx',
        args=['-y', 'obsidian-mcp-pydanticai', str(vault_path)]
    )


def create_searxng_mcp_server(config: AgentConfig) -> MCPServerStdio | None:
    """
    Create SearXNG MCP server instance.

    Args:
        config: Agent configuration containing SearXNG settings

    Returns:
        MCPServerStdio instance or None if not configured
    """
    if not config.searxng_base_url:
        return None

    env = {'SEARXNG_URL': config.searxng_base_url}

    # Add authentication if configured
    if hasattr(config, 'searxng_username') and config.searxng_username:
        env['AUTH_USERNAME'] = config.searxng_username
    if hasattr(config, 'searxng_password') and config.searxng_password:
        env['AUTH_PASSWORD'] = config.searxng_password

    return MCPServerStdio(
        command='npx',
        args=['-y', 'mcp-searxng'],
        env=env
    )


def create_todoist_mcp_server(config: AgentConfig) -> MCPServerStdio | None:
    """
    Create Todoist MCP server instance.

    Args:
        config: Agent configuration containing Todoist settings

    Returns:
        MCPServerStdio instance or None if not configured
    """
    if not config.todoist_api_token:
        return None

    return MCPServerStdio(
        command='npx',
        args=['-y', '@abhiz123/todoist-mcp-server'],
        env={'TODOIST_API_TOKEN': config.todoist_api_token}
    )


def create_youtube_mcp_server(config: AgentConfig) -> MCPServerStdio | None:
    """
    Create YouTube MCP server instance.

    Args:
        config: Agent configuration containing YouTube settings

    Returns:
        MCPServerStdio instance or None if not configured
    """
    # YouTube MCP server doesn't require API key - it works without one
    # Always create the server as it provides video processing capabilities
    # Using our PydanticAI-compatible fork with underscore tool naming
    return MCPServerStdio(
        command='npx',
        args=['-y', 'youtube-video-summarizer-mcp-pydanticai']
    )


def create_all_mcp_servers(config: AgentConfig) -> list[MCPServerStdio]:
    """
    Create all configured MCP servers.

    Args:
        config: Agent configuration

    Returns:
        List of configured MCP server instances
    """
    servers = []

    # Add Obsidian server if configured
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
