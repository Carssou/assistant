"""
MCP server configurations for the PydanticAI agent.

This module provides factory functions for creating MCP server instances
for different productivity tools.
"""

from pathlib import Path
from typing import List, Optional

from pydantic_ai.mcp import MCPServerStdio

from config.settings import AgentConfig


def create_obsidian_mcp_server(config: AgentConfig) -> Optional[MCPServerStdio]:
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
    if not vault_path.exists():
        raise ValueError(f"Obsidian vault path does not exist: {vault_path}")
    
    return MCPServerStdio(
        command='npx',
        args=['-y', 'obsidian-mcp-pydanticai', str(vault_path)]
    )


def create_searxng_mcp_server(config: AgentConfig) -> Optional[MCPServerStdio]:
    """
    Create SearXNG MCP server instance.
    
    Args:
        config: Agent configuration containing SearXNG settings
        
    Returns:
        MCPServerStdio instance or None if not configured
    """
    # TODO: Implement SearXNG MCP server configuration
    # Will be implemented in Task 2.1
    return None


def create_todoist_mcp_server(config: AgentConfig) -> Optional[MCPServerStdio]:
    """
    Create Todoist MCP server instance.
    
    Args:
        config: Agent configuration containing Todoist settings
        
    Returns:
        MCPServerStdio instance or None if not configured
    """
    # TODO: Implement Todoist MCP server configuration
    # Will be implemented in Task 2.2
    return None


def create_youtube_mcp_server(config: AgentConfig) -> Optional[MCPServerStdio]:
    """
    Create YouTube MCP server instance.
    
    Args:
        config: Agent configuration containing YouTube settings
        
    Returns:
        MCPServerStdio instance or None if not configured
    """
    # TODO: Implement YouTube MCP server configuration
    # Will be implemented in Task 2.3
    return None


def create_all_mcp_servers(config: AgentConfig) -> List[MCPServerStdio]:
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