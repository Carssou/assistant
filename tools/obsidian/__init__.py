"""
Obsidian vault management tools for PydanticAI.

This module provides native Python tools for interacting with Obsidian vaults,
replacing the MCP server approach for better performance and reliability.
"""

from .core import (
    create_obsidian_note,
    delete_obsidian_note,
    edit_obsidian_note,
    list_available_obsidian_vaults,
    read_obsidian_note,
)
from .search import (
    get_obsidian_tags_list,
    search_obsidian_vault,
)
from .tags import (
    add_obsidian_tags,
    remove_obsidian_tags,
    rename_obsidian_tag,
)

__all__ = [
    "create_obsidian_note",
    "read_obsidian_note",
    "edit_obsidian_note",
    "delete_obsidian_note",
    "list_available_obsidian_vaults",
    "search_obsidian_vault",
    "get_obsidian_tags_list",
    "add_obsidian_tags",
    "remove_obsidian_tags",
    "rename_obsidian_tag",
]
