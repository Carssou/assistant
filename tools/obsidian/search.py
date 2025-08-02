"""
Search functionality for Obsidian vaults.
"""

import re
from datetime import datetime
from pathlib import Path

from .types import SearchResult
from .utils import (
    extract_tags,
    get_all_markdown_files,
    get_vault_path,
    matches_tag_pattern,
    normalize_tag,
    safe_join_path,
)


async def search_obsidian_vault(
    query: str,
    search_type: str = "content",
    case_sensitive: bool = False,
    path: str | None = None,
    limit: int = 50,
) -> str:
    """
    Search for content in Obsidian vault.

    Args:
        query: Search query
        search_type: Type of search ("content", "filename", "tag")
        case_sensitive: Whether search is case sensitive
        path: Optional subfolder to limit search
        limit: Maximum number of results to return

    Returns:
        Formatted search results

    Raises:
        ValueError: If search fails
    """
    try:
        # Get vault path
        vault_path = get_vault_path()

        # Determine search directory
        search_dir = vault_path
        if path:
            search_dir = safe_join_path(vault_path, path)
            if not search_dir.exists():
                raise ValueError(f"Search path does not exist: {path}")

        # Get markdown files
        md_files = await get_all_markdown_files(vault_path, search_dir)

        if not md_files:
            return "📝 No markdown files found in search area"

        # Perform search based on type
        if search_type == "content":
            results = await _search_content(md_files, query, case_sensitive, vault_path)
        elif search_type == "filename":
            results = await _search_filename(md_files, query, case_sensitive, vault_path)
        elif search_type == "tag":
            results = await _search_tags(md_files, query, vault_path)
        else:
            raise ValueError(
                f"Invalid search type: {search_type}. Use 'content', 'filename', or 'tag'"
            )

        # Apply limit
        if limit > 0:
            results = results[:limit]

        # Format results
        return _format_search_results(results, query, search_type, len(md_files))

    except Exception as e:
        raise ValueError(f"Search failed: {e}") from e


async def _search_content(
    files: list[Path], query: str, case_sensitive: bool, vault_path: Path
) -> list[SearchResult]:
    """Search for content within files."""
    results = []

    # Prepare regex pattern
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        pattern = re.compile(query, flags)
    except re.error:
        # If regex fails, treat as literal string
        escaped_query = re.escape(query)
        pattern = re.compile(escaped_query, flags)

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()

            matches = []
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    # Get context lines
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 1)
                    context_lines = lines[context_start:context_end]

                    matches.append(
                        {
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "context": context_lines,
                        }
                    )

            if matches:
                relative_path = file_path.relative_to(vault_path)
                stat = file_path.stat()

                results.append(
                    SearchResult(
                        file_path=str(relative_path),
                        title=file_path.stem,
                        match_type="content",
                        matches=matches,
                        file_size=stat.st_size,
                        modified_time=datetime.fromtimestamp(stat.st_mtime),
                    )
                )

        except (OSError, RuntimeError, UnicodeDecodeError):
            # Skip files that can't be read
            continue

    return results


async def _search_filename(
    files: list[Path], query: str, case_sensitive: bool, vault_path: Path
) -> list[SearchResult]:
    """Search by filename."""
    results = []

    # Prepare search
    search_query = query if case_sensitive else query.lower()

    for file_path in files:
        filename = file_path.name if case_sensitive else file_path.name.lower()

        if search_query in filename:
            relative_path = file_path.relative_to(vault_path)
            stat = file_path.stat()

            results.append(
                SearchResult(
                    file_path=str(relative_path),
                    title=file_path.stem,
                    match_type="filename",
                    matches=[{"matched_filename": file_path.name, "query": query}],
                    file_size=stat.st_size,
                    modified_time=datetime.fromtimestamp(stat.st_mtime),
                )
            )

    return results


async def _search_tags(files: list[Path], tag_query: str, vault_path: Path) -> list[SearchResult]:
    """Search by tags."""
    results = []

    # Normalize tag query
    normalized_query = normalize_tag(tag_query)

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
            file_tags = extract_tags(content)

            matching_tags = []
            for tag in file_tags:
                if matches_tag_pattern(normalized_query, tag):
                    matching_tags.append(tag)

            if matching_tags:
                relative_path = file_path.relative_to(vault_path)
                stat = file_path.stat()

                results.append(
                    SearchResult(
                        file_path=str(relative_path),
                        title=file_path.stem,
                        match_type="tag",
                        matches=[
                            {
                                "matched_tags": matching_tags,
                                "all_tags": file_tags,
                                "query": tag_query,
                            }
                        ],
                        file_size=stat.st_size,
                        modified_time=datetime.fromtimestamp(stat.st_mtime),
                    )
                )

        except (OSError, RuntimeError, UnicodeDecodeError):
            # Skip files that can't be read
            continue

    return results


def _format_search_results(
    results: list[SearchResult], query: str, search_type: str, total_files: int
) -> str:
    """Format search results for display."""
    if not results:
        return f"🔍 No results found for '{query}' in {total_files:,} files"

    # Header
    result_count = len(results)
    header = f"🔍 **Search Results** ({result_count:,} matches in {total_files:,} files)\n"
    header += f"Query: `{query}` | Type: `{search_type}`\n\n"

    # Results
    formatted_results = []
    for i, result in enumerate(results, 1):
        if i > 20:  # Limit display to first 20 results
            remaining = len(results) - 20
            formatted_results.append(f"*... and {remaining} more results*")
            break

        formatted_results.append(_format_single_result(result, i))

    return header + "\n".join(formatted_results)


def _format_single_result(result: SearchResult, index: int) -> str:
    """Format a single search result."""
    # File info
    size_str = f"{result.file_size:,} bytes" if result.file_size else "unknown size"
    modified_str = (
        result.modified_time.strftime("%Y-%m-%d %H:%M") if result.modified_time else "unknown"
    )

    output = f"**{index}. {result.title}**\n"
    output += f"   📄 `{result.file_path}` ({size_str}, {modified_str})\n"

    # Match details
    if result.match_type == "content":
        match_count = len(result.matches)
        output += f"   🎯 {match_count} content match{'es' if match_count != 1 else ''}\n"

        # Show first few matches
        for _i, match in enumerate(result.matches[:3]):
            line_num = match.get("line_number", "?")
            line_content = match.get("line_content", "")[:100]
            output += f"   • L{line_num}: {line_content}\n"

        if len(result.matches) > 3:
            remaining = len(result.matches) - 3
            output += f"   • ... and {remaining} more matches\n"

    elif result.match_type == "filename":
        match = result.matches[0] if result.matches else {}
        output += f"   🎯 Filename match: `{match.get('matched_filename', '')}`\n"

    elif result.match_type == "tag":
        match = result.matches[0] if result.matches else {}
        matched_tags = match.get("matched_tags", [])
        all_tags = match.get("all_tags", [])

        output += f"   🏷️ Matched tags: {', '.join(f'#{tag}' for tag in matched_tags)}\n"
        if len(all_tags) > len(matched_tags):
            other_tags = [tag for tag in all_tags if tag not in matched_tags]
            output += f"   🏷️ Other tags: {', '.join(f'#{tag}' for tag in other_tags[:5])}\n"

    return output


async def get_obsidian_tags_list() -> str:
    """
    Get all unique tags used in the vault.

    Args:
        vault: Vault name

    Returns:
        Formatted list of all tags in the vault
    """
    try:
        # Get vault path
        vault_path = get_vault_path()

        # Get all markdown files
        md_files = await get_all_markdown_files(vault_path)

        if not md_files:
            return "📝 No markdown files found in vault"

        # Collect all tags
        all_tags = set()
        tag_counts = {}

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                file_tags = extract_tags(content)

                for tag in file_tags:
                    all_tags.add(tag)
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            except (OSError, RuntimeError, UnicodeDecodeError):
                continue

        if not all_tags:
            return f"🏷️ No tags found in {len(md_files):,} files"

        # Sort tags by usage count (descending)
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        # Format output
        output = f"🏷️ **All Tags in Vault** ({len(all_tags):,} unique tags in {len(md_files):,} files)\n\n"

        for _i, (tag, count) in enumerate(sorted_tags[:50]):  # Show top 50
            output += f"#{tag} ({count})\n"

        if len(sorted_tags) > 50:
            remaining = len(sorted_tags) - 50
            output += f"\n*... and {remaining} more tags*"

        return output

    except Exception as e:
        raise ValueError(f"Failed to get tags list: {e}") from e
