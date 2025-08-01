"""
Strands Agents productivity agent with native MCP integration.
"""

from typing import Any

from strands import Agent, tool

from agent.prompts import get_system_prompt
from agent.tools import (
    get_screen_info_tool,
    take_region_screenshot_tool,
    take_screenshot_tool,
)
from config.settings import create_model_instance, load_config
from mcp_servers.configs import create_all_mcp_servers

# Load config
config = load_config()


# Vision tools
@tool
async def take_screenshot(quality: int = 75) -> str | Any:
    """Capture a screenshot of the entire screen for visual analysis.

    Use this tool when you need to see what's currently displayed on the user's screen.

    Args:
        quality (int, optional): Image quality 1-100, higher means better quality but larger file. Defaults to 75.

    Returns:
        For most models: image data that you can analyze visually
        For Nova models: text description of what's visible on screen
    """
    print("Calling take_screenshot tool")

    # Check if Nova model - use direct Bedrock API
    from utils.bedrock_vision import should_use_bedrock_direct

    if should_use_bedrock_direct(config):
        from utils.bedrock_vision import analyze_full_screenshot_with_bedrock
        from utils.screen_capture import take_screenshot as take_screenshot_direct

        image_bytes = take_screenshot_direct(quality)
        analysis = await analyze_full_screenshot_with_bedrock(image_bytes, config)
        return analysis

    return await take_screenshot_tool(config, quality)


@tool
async def take_region_screenshot(
    x: int,
    y: int,
    width: int,
    height: int,
    quality: int = 85,
) -> str | Any:
    """Capture a screenshot of a specific rectangular area on the screen.

    Use this when you need to focus on a particular region rather than the entire screen.

    Args:
        x (int): Left coordinate of the region in pixels
        y (int): Top coordinate of the region in pixels
        width (int): Width of the region in pixels
        height (int): Height of the region in pixels
        quality (int, optional): Image quality 1-100. Defaults to 85.

    Returns:
        For most models: image data of the specified region that you can analyze visually
        For Nova models: text description of what's visible in the specified screen region
    """
    print("Calling take_region_screenshot tool")

    # Check if Nova model - use direct Bedrock API
    from utils.bedrock_vision import should_use_bedrock_direct

    if should_use_bedrock_direct(config):
        from utils.bedrock_vision import analyze_region_screenshot_with_bedrock
        from utils.screen_capture import take_region_screenshot as take_region_screenshot_direct

        image_bytes = take_region_screenshot_direct(x, y, width, height, quality)
        analysis = await analyze_region_screenshot_with_bedrock(
            image_bytes, x, y, width, height, config
        )
        return analysis

    return await take_region_screenshot_tool(config, x, y, width, height, quality)


@tool
async def get_screen_info() -> dict[str, Any]:
    """Get technical information about the user's screen/display setup.

    Use this to understand screen dimensions, resolution, and display configuration.

    Returns:
        dict: Dictionary with screen width, height, resolution, and display properties
    """
    print("Calling get_screen_info tool")
    return await get_screen_info_tool()


# Obsidian tools (native implementation)
@tool
async def create_note(filename: str, content: str, folder: str = None) -> str:
    """Create a new markdown note in an Obsidian knowledge management vault.

    Use this to create new notes for storing information, ideas, or documentation.

    Args:
        filename (str): Note name without .md extension (e.g. 'My New Note')
        content (str): Markdown content for the note
        folder (str, optional): Subfolder path like 'Projects/AI'. Defaults to root.

    Returns:
        str: Success confirmation with the created file path
    """
    from tools.obsidian import create_obsidian_note

    return await create_obsidian_note(filename, content, folder)


@tool
async def read_note(filename: str, folder: str = None) -> str:
    """Read the markdown content of an existing Obsidian note.

    Use this to retrieve and view the contents of notes in the knowledge vault.

    Args:
        filename (str): Note name without .md extension (e.g. 'Meeting Notes')
        folder (str, optional): Subfolder path if note is in a subfolder

    Returns:
        str: Full markdown content of the note plus file metadata (size, modified date)
    """
    from tools.obsidian import read_obsidian_note

    return await read_obsidian_note(filename, folder)


@tool
async def edit_note(
    filename: str,
    content: str,
    folder: str = None,
    operation: str = "replace",
) -> str:
    """Modify the content of an existing Obsidian note with different edit operations.

    Use this to update, add to, or completely rewrite note content.

    Args:
        filename (str): Note name without .md extension
        content (str): New markdown content to add/replace
        folder (str, optional): Subfolder path if note is in a subfolder
        operation (str): Edit operation - 'replace' (overwrite), 'append' (add to end), 'prepend' (add to start). Defaults to 'replace'.

    Returns:
        str: Success confirmation with edit summary and line count changes
    """
    from tools.obsidian import edit_obsidian_note

    return await edit_obsidian_note(filename, content, folder, operation)


@tool
async def delete_note(filename: str, folder: str = None) -> str:
    """Permanently delete a note from the Obsidian vault.

    Use this to remove notes that are no longer needed. Creates backup before deletion.

    Args:
        filename (str): Note name without .md extension
        folder (str, optional): Subfolder path if note is in a subfolder

    Returns:
        str: Confirmation of deletion with file size information
    """
    from tools.obsidian import delete_obsidian_note

    return await delete_obsidian_note(filename, folder)


# Advanced Obsidian tools (Phase 2)
@tool
async def search_vault(
    query: str,
    search_type: str = "content",
    case_sensitive: bool = False,
    path: str = None,
    limit: int = 50,
) -> str:
    """Search through notes in an Obsidian vault using different search methods.

    Use this to find specific notes, content, or topics across the knowledge base.

    Args:
        query (str): Search term or phrase
        search_type (str): Search method - 'content' (search text), 'filename' (search titles), 'tag' (search tags). Defaults to 'content'.
        case_sensitive (bool): Whether search is case sensitive. Defaults to False.
        path (str, optional): Limit search to specific folder
        limit (int): Maximum results to return. Defaults to 50.

    Returns:
        str: Formatted list of matching notes with context and metadata
    """
    from tools.obsidian import search_obsidian_vault

    return await search_obsidian_vault(query, search_type, case_sensitive, path, limit)


@tool
async def get_tags_list() -> str:
    """List all tags used across notes in the Obsidian vault with usage statistics.

    Use this to understand the tag taxonomy and find popular topics in the knowledge base.

    Returns:
        str: Sorted list of all tags with usage counts, most popular first
    """
    from tools.obsidian import get_obsidian_tags_list

    return await get_obsidian_tags_list()


@tool
async def add_tags(
    filename: str,
    tags: list[str],
    folder: str = None,
) -> str:
    """Add new tags to an existing Obsidian note for better organization.

    Use this to categorize and organize notes with relevant topic tags.

    Args:
        filename (str): Note name without .md extension
        tags (list[str]): Tag names to add (e.g. ['ai', 'machine-learning'])
        folder (str, optional): Subfolder path if note is in a subfolder

    Returns:
        str: Confirmation with newly added tags and complete tag list for the note
    """
    from tools.obsidian import add_obsidian_tags

    return await add_obsidian_tags(filename, tags, folder)


@tool
async def remove_tags(
    filename: str,
    tags: list[str],
    folder: str = None,
) -> str:
    """Remove specific tags from an existing Obsidian note.

    Use this to clean up or reorganize note tags by removing outdated or incorrect ones.

    Args:
        filename (str): Note name without .md extension
        tags (list[str]): Tag names to remove (e.g. ['outdated', 'draft'])
        folder (str, optional): Subfolder path if note is in a subfolder

    Returns:
        str: Confirmation with removed tags and remaining tags on the note
    """
    from tools.obsidian import remove_obsidian_tags

    return await remove_obsidian_tags(filename, tags, folder)


@tool
async def rename_tag(old_tag: str, new_tag: str) -> str:
    """Rename a tag across all notes in the Obsidian vault (bulk operation).

    Use this to standardize tag naming or fix typos across the entire knowledge base.

    Args:
        old_tag (str): Current tag name to replace
        new_tag (str): New tag name to use instead

    Returns:
        str: Summary of changes with count of affected notes and file list
    """
    from tools.obsidian import rename_obsidian_tag

    return await rename_obsidian_tag(old_tag, new_tag)


# Define native tools list
native_tools = [
    take_screenshot,
    take_region_screenshot,
    get_screen_info,
    create_note,
    read_note,
    edit_note,
    delete_note,
    search_vault,
    get_tags_list,
    add_tags,
    remove_tags,
    rename_tag,
]


# MCP-aware agent manager for persistent sessions
class MCPAgentManager:
    """Manager for Strands agents with MCP support following proper context patterns."""

    def __init__(self):
        self.mcp_servers = create_all_mcp_servers(config)
        self.native_agent = Agent(
            model=create_model_instance(config),
            system_prompt=get_system_prompt(),
            tools=native_tools,
        )
        self._mcp_tools = None
        self._discover_mcp_tools()
        print(f"MCPAgentManager initialized with {len(self.mcp_servers)} MCP servers")

    def _discover_mcp_tools(self):
        """Discover MCP tools once and cache them."""
        if not self.mcp_servers:
            self._mcp_tools = []
            return

        self._mcp_tools = []
        for mcp_client in self.mcp_servers:
            try:
                with mcp_client:
                    mcp_tools = mcp_client.list_tools_sync()
                    self._mcp_tools.extend(mcp_tools)
            except Exception as e:
                print(f"Warning: Failed to discover tools from MCP server: {e}")

    def _create_mcp_agent(self):
        """Create agent with all tools (native + MCP)."""
        all_tools = native_tools.copy()
        all_tools.extend(self._mcp_tools)

        return Agent(
            model=create_model_instance(config), system_prompt=get_system_prompt(), tools=all_tools
        )

    async def invoke_with_mcp(self, message: str) -> str:
        """Invoke agent with proper MCP context management."""
        if not self.mcp_servers:
            return await self.native_agent.invoke_async(message)

        # Enter all MCP contexts for this conversation
        contexts = []
        try:
            for mcp_client in self.mcp_servers:
                mcp_client.__enter__()
                contexts.append(mcp_client)

            # Create agent with cached tools
            agent = self._create_mcp_agent()
            return await agent.invoke_async(message)

        finally:
            for mcp_client in reversed(contexts):
                try:
                    mcp_client.__exit__(None, None, None)
                except Exception as e:
                    print(f"Warning: Error closing MCP client: {e}")

    async def stream_with_mcp(self, message: str):
        """Stream response from agent with proper MCP context management."""
        if not self.mcp_servers:
            async for chunk in self.native_agent.stream_async(message):
                yield chunk
            return

        # Use MCP contexts but keep agent persistent for streaming
        contexts = []
        try:
            for mcp_client in self.mcp_servers:
                mcp_client.__enter__()
                contexts.append(mcp_client)

            # Use the persistent agent or create one
            if not hasattr(self, "_mcp_agent") or self._mcp_agent is None:
                self._mcp_agent = self._create_mcp_agent()

            # Stream from the persistent agent
            async for chunk in self._mcp_agent.stream_async(message):
                yield chunk

        finally:
            for mcp_client in reversed(contexts):
                try:
                    mcp_client.__exit__(None, None, None)
                except Exception as e:
                    print(f"Warning: Error closing MCP client: {e}")


# Create the global agent manager
agent_manager = MCPAgentManager()
