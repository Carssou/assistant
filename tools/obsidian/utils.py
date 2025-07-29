"""
Utility functions for Obsidian vault operations.
"""

import re
from pathlib import Path


def ensure_markdown_extension(filename: str) -> str:
    """Add .md extension if missing."""
    if not filename.endswith(".md"):
        return f"{filename}.md"
    return filename


def validate_vault_path(vault_path: Path, target_path: Path) -> bool:
    """
    Ensure target path is within vault (prevent directory traversal).

    Args:
        vault_path: Base vault directory
        target_path: Target file/directory path

    Returns:
        True if path is safe, False otherwise

    Raises:
        ValueError: If path is outside vault
    """
    try:
        # Resolve both paths to handle symlinks and relative paths
        vault_resolved = vault_path.resolve()
        target_resolved = target_path.resolve()

        # Check if target is within vault
        try:
            target_resolved.relative_to(vault_resolved)
            return True
        except ValueError as ve:
            raise ValueError(f"Path outside vault: {target_path}") from ve

    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}") from e


def safe_join_path(base: Path, *parts: str) -> Path:
    """
    Safely join paths with validation.

    Args:
        base: Base directory path
        *parts: Path components to join

    Returns:
        Safely joined path

    Raises:
        ValueError: If resulting path would be outside base
    """
    result = base
    for part in parts:
        # Remove any path separators and resolve
        clean_part = str(part).replace("..", "").replace("/", "").replace("\\", "")
        if clean_part:
            result = result / clean_part

    validate_vault_path(base, result)
    return result


def get_vault_path(deps) -> Path:
    """
    Get vault path from configuration.

    Args:
        deps: Agent dependencies

    Returns:
        Path to the vault

    Raises:
        ValueError: If vault not configured or doesn't exist
    """
    if not deps.config.obsidian_vault_path:
        raise ValueError("No Obsidian vault configured")

    vault_path = Path(deps.config.obsidian_vault_path)
    if not vault_path.exists():
        raise ValueError(f"Vault path does not exist: {vault_path}")

    if not vault_path.is_dir():
        raise ValueError(f"Vault path is not a directory: {vault_path}")

    # Check if it's a valid Obsidian vault
    obsidian_config = vault_path / ".obsidian"
    if not obsidian_config.exists():
        raise ValueError(f"Not a valid Obsidian vault (missing .obsidian): {vault_path}")

    return vault_path


async def file_exists(path: Path) -> bool:
    """Check if file exists asynchronously."""
    try:
        return path.exists() and path.is_file()
    except (OSError, RuntimeError):
        return False


async def ensure_directory(path: Path) -> None:
    """Ensure directory exists, creating if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Could not create directory {path}: {e}") from e


async def get_all_markdown_files(vault_path: Path, search_dir: Path | None = None) -> list[Path]:
    """
    Get all markdown files in vault or subdirectory.

    Args:
        vault_path: Base vault directory
        search_dir: Optional subdirectory to search (defaults to vault_path)

    Returns:
        List of markdown file paths
    """
    base_dir = search_dir if search_dir else vault_path
    if not base_dir.exists():
        return []

    markdown_files = []
    try:
        for md_file in base_dir.rglob("*.md"):
            if md_file.is_file():
                # Ensure file is within vault
                try:
                    validate_vault_path(vault_path, md_file)
                    markdown_files.append(md_file)
                except ValueError:
                    # Skip files outside vault
                    continue
    except (OSError, RuntimeError):
        # Handle permission errors gracefully
        pass

    return sorted(markdown_files)


def extract_tags(content: str) -> list[str]:
    """
    Extract tags from content (frontmatter + inline).

    Args:
        content: Note content

    Returns:
        List of unique tags
    """
    tags = set()

    # Extract from YAML frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        # Look for tags: [...] or tag: [...]
        tag_matches = re.findall(r"^(?:tags?|tag):\s*\[(.*?)\]", frontmatter, re.MULTILINE)
        for match in tag_matches:
            # Split by comma and clean up
            for tag in match.split(","):
                tag = tag.strip().strip("\"'")
                if tag:
                    tags.add(tag)

    # Extract inline hashtags
    inline_tags = re.findall(r"#([a-zA-Z0-9_/-]+)", content)
    tags.update(inline_tags)

    return sorted(tags)


def normalize_tag(tag: str) -> str:
    """Normalize tag format."""
    return tag.lower().strip("#").strip()


def matches_tag_pattern(pattern: str, tag: str) -> bool:
    """Check if tag matches search pattern."""
    normalized_pattern = normalize_tag(pattern)
    normalized_tag = normalize_tag(tag)

    # Support wildcard matching
    if "*" in normalized_pattern:
        pattern_regex = normalized_pattern.replace("*", ".*")
        return bool(re.match(f"^{pattern_regex}$", normalized_tag))

    # Exact match or hierarchical match
    return normalized_tag == normalized_pattern or normalized_tag.startswith(
        normalized_pattern + "/"
    )
