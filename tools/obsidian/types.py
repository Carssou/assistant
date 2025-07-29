"""
Type definitions for Obsidian tools.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, TypedDict


class FileOperationResult(TypedDict):
    """Result of a file operation."""

    success: bool
    message: str
    path: str
    operation: Literal["create", "read", "edit", "delete"]


class SearchMatch(TypedDict):
    """A search match result."""

    line: int
    text: str


@dataclass
class SearchResult:
    """Search result for a file with enhanced information."""

    file_path: str
    title: str
    match_type: Literal["content", "filename", "tag"]
    matches: list[dict[str, Any]]
    file_size: int | None = None
    modified_time: datetime | None = None


class SearchOperationResult(TypedDict):
    """Result of a search operation."""

    success: bool
    message: str
    results: list[SearchResult]
    total_matches: int
    matched_files: int


class VaultInfo(TypedDict):
    """Information about an Obsidian vault."""

    name: str
    path: str
    exists: bool
    is_valid: bool
