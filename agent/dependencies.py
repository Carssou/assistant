"""
Dependency injection container for the PydanticAI agent.

This module provides the AgentDependencies dataclass that contains
shared resources and configuration for the agent.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx
from langfuse import Langfuse

from config.settings import AgentConfig


@dataclass
class AgentDependencies:
    """
    Dependency injection container for agent shared resources.
    
    This follows PydanticAI patterns for dependency injection,
    providing access to configuration, HTTP client, logging, and
    other shared resources throughout the agent.
    Following the reference implementation pattern.
    """

    config: AgentConfig
    http_client: httpx.AsyncClient
    logger: logging.Logger
    langfuse_client: Langfuse | None = None
    vault_path: Path | None = None

    def __post_init__(self):
        """Post-initialization setup."""
        # Set vault path from config if available
        if self.config.obsidian_vault_path:
            self.vault_path = self.config.obsidian_vault_path

    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()
        if self.langfuse_client:
            self.langfuse_client.flush()


async def create_agent_dependencies(config: AgentConfig) -> AgentDependencies:
    """
    Create and initialize agent dependencies.
    
    Args:
        config: Agent configuration
        
    Returns:
        Initialized dependencies container
    """
    # Create HTTP client with timeout configuration
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),  # 30 second timeout
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=100)
    )

    # Set up logging
    from utils.logger import get_logger, setup_agent_logging

    langfuse_client = setup_agent_logging(
        log_level=config.log_level,
        debug_mode=config.debug_mode,
        langfuse_secret_key=config.langfuse_secret_key,
        langfuse_public_key=config.langfuse_public_key,
        langfuse_host=config.langfuse_host
    )

    logger = get_logger(__name__)

    # Create dependencies container
    deps = AgentDependencies(
        config=config,
        http_client=http_client,
        logger=logger,
        langfuse_client=langfuse_client
    )

    logger.info("Agent dependencies initialized successfully")
    if deps.langfuse_client:
        logger.info("Langfuse observability enabled")

    return deps


def create_sync_dependencies(config: AgentConfig) -> AgentDependencies:
    """
    Create dependencies synchronously (for testing or simple cases).
    
    Args:
        config: Agent configuration
        
    Returns:
        Dependencies container with sync HTTP client
    """
    # Note: This creates a sync version for testing
    # In production, use create_agent_dependencies

    from utils.logger import get_logger, setup_agent_logging

    langfuse_client = setup_agent_logging(
        log_level=config.log_level,
        debug_mode=config.debug_mode,
        langfuse_secret_key=config.langfuse_secret_key,
        langfuse_public_key=config.langfuse_public_key,
        langfuse_host=config.langfuse_host
    )

    logger = get_logger(__name__)

    # Create a simple async client for sync usage
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0)
    )

    return AgentDependencies(
        config=config,
        http_client=http_client,
        logger=logger,
        langfuse_client=langfuse_client
    )
