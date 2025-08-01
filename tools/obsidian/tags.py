"""
Tag management functionality for Obsidian vaults.
"""

import re
from datetime import datetime

from .utils import (
    ensure_markdown_extension,
    extract_tags,
    file_exists,
    get_all_markdown_files,
    get_vault_path,
    normalize_tag,
    safe_join_path,
    validate_vault_path,
)


async def add_obsidian_tags(filename: str, tags: list[str], folder: str | None = None) -> str:
    """
    Add tags to an existing note.

    Args:
        filename: Note filename
        tags: List of tags to add
        folder: Optional subfolder path

    Returns:
        Success message with updated tags

    Raises:
        ValueError: If operation fails
    """
    try:
        # Get vault path
        vault_path = get_vault_path()

        # Validate filename
        if "/" in filename or "\\" in filename:
            raise ValueError(
                "Filename cannot contain path separators - use the 'folder' parameter instead"
            )

        # Ensure .md extension
        sanitized_filename = ensure_markdown_extension(filename)

        # Construct target path
        if folder:
            target_path = safe_join_path(vault_path, folder, sanitized_filename)
        else:
            target_path = vault_path / sanitized_filename

        # Validate path is within vault
        validate_vault_path(vault_path, target_path)

        # Check if file exists
        if not await file_exists(target_path):
            raise ValueError(f"Note not found: {filename}")

        # Read existing content
        try:
            content = target_path.read_text(encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to read note: {e}") from e

        # Parse existing tags
        existing_tags = set(extract_tags(content))

        # Normalize new tags
        normalized_new_tags = []
        for tag in tags:
            normalized = normalize_tag(tag)
            if normalized and normalized not in existing_tags:
                normalized_new_tags.append(normalized)

        if not normalized_new_tags:
            return "📝 No new tags to add (all tags already exist)"

        # Update content with new tags
        updated_content = _add_tags_to_content(content, normalized_new_tags)

        # Create backup
        backup_path = target_path.with_suffix(
            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        try:
            backup_path.write_text(content, encoding="utf-8")
        except (OSError, RuntimeError):
            # Backup failed, but continue
            pass

        # Write updated content
        try:
            target_path.write_text(updated_content, encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to write updated note: {e}") from e

        # Return success message
        relative_path = target_path.relative_to(vault_path)
        all_tags = existing_tags.union(set(normalized_new_tags))

        return (
            f"🏷️ Tags added to {relative_path}: {', '.join(f'#{tag}' for tag in normalized_new_tags)}\n"
            + f"📝 Total tags: {', '.join(f'#{tag}' for tag in sorted(all_tags))}"
        )

    except Exception as e:
        raise ValueError(f"Failed to add tags: {e}") from e


async def remove_obsidian_tags(filename: str, tags: list[str], folder: str | None = None) -> str:
    """
    Remove tags from an existing note.

    Args:
        filename: Note filename
        tags: List of tags to remove
        folder: Optional subfolder path

    Returns:
        Success message with remaining tags

    Raises:
        ValueError: If operation fails
    """
    try:
        # Get vault path
        vault_path = get_vault_path()

        # Validate filename
        if "/" in filename or "\\" in filename:
            raise ValueError(
                "Filename cannot contain path separators - use the 'folder' parameter instead"
            )

        # Ensure .md extension
        sanitized_filename = ensure_markdown_extension(filename)

        # Construct target path
        if folder:
            target_path = safe_join_path(vault_path, folder, sanitized_filename)
        else:
            target_path = vault_path / sanitized_filename

        # Validate path is within vault
        validate_vault_path(vault_path, target_path)

        # Check if file exists
        if not await file_exists(target_path):
            raise ValueError(f"Note not found: {filename}")

        # Read existing content
        try:
            content = target_path.read_text(encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to read note: {e}") from e

        # Parse existing tags
        existing_tags = set(extract_tags(content))

        # Normalize tags to remove
        normalized_remove_tags = []
        for tag in tags:
            normalized = normalize_tag(tag)
            if normalized and normalized in existing_tags:
                normalized_remove_tags.append(normalized)

        if not normalized_remove_tags:
            return "📝 No matching tags to remove"

        # Update content by removing tags
        updated_content = _remove_tags_from_content(content, normalized_remove_tags)

        # Create backup
        backup_path = target_path.with_suffix(
            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        try:
            backup_path.write_text(content, encoding="utf-8")
        except (OSError, RuntimeError):
            # Backup failed, but continue
            pass

        # Write updated content
        try:
            target_path.write_text(updated_content, encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to write updated note: {e}") from e

        # Return success message
        relative_path = target_path.relative_to(vault_path)
        remaining_tags = existing_tags - set(normalized_remove_tags)

        result = f"🗑️ Tags removed from {relative_path}: {', '.join(f'#{tag}' for tag in normalized_remove_tags)}\n"
        if remaining_tags:
            result += f"📝 Remaining tags: {', '.join(f'#{tag}' for tag in sorted(remaining_tags))}"
        else:
            result += "📝 No tags remaining"

        return result

    except Exception as e:
        raise ValueError(f"Failed to remove tags: {e}") from e


async def rename_obsidian_tag(old_tag: str, new_tag: str) -> str:
    """
    Rename a tag across the entire vault.

    Args:
        old_tag: Current tag name
        new_tag: New tag name

    Returns:
        Success message with affected files count

    Raises:
        ValueError: If operation fails
    """
    try:
        # Get vault path
        vault_path = get_vault_path()

        # Normalize tags
        old_normalized = normalize_tag(old_tag)
        new_normalized = normalize_tag(new_tag)

        if not old_normalized:
            raise ValueError("Invalid old tag name")
        if not new_normalized:
            raise ValueError("Invalid new tag name")
        if old_normalized == new_normalized:
            raise ValueError("Old and new tag names are the same")

        # Get all markdown files
        md_files = await get_all_markdown_files(vault_path)

        if not md_files:
            return "📝 No markdown files found in vault"

        # Find files containing the old tag
        affected_files = []
        total_replacements = 0

        for file_path in md_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                file_tags = extract_tags(content)

                if old_normalized in file_tags:
                    # Replace the tag in content
                    updated_content, replacements = _replace_tag_in_content(
                        content, old_normalized, new_normalized
                    )

                    if replacements > 0:
                        # Create backup
                        backup_path = file_path.with_suffix(
                            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        )
                        try:
                            backup_path.write_text(content, encoding="utf-8")
                        except (OSError, RuntimeError):
                            # Backup failed, but continue
                            pass

                        # Write updated content
                        file_path.write_text(updated_content, encoding="utf-8")

                        relative_path = file_path.relative_to(vault_path)
                        affected_files.append(str(relative_path))
                        total_replacements += replacements

            except (OSError, RuntimeError, UnicodeDecodeError):
                # Skip files that can't be processed
                continue

        if not affected_files:
            return f"🏷️ No files found containing tag: #{old_normalized}"

        # Return success message
        result = f"✅ Tag renamed from #{old_normalized} to #{new_normalized}\n"
        result += f"📊 Updated {len(affected_files)} files ({total_replacements} replacements)\n\n"
        result += "**Affected files:**\n"

        for i, file_path in enumerate(affected_files[:10], 1):
            result += f"{i}. {file_path}\n"

        if len(affected_files) > 10:
            result += f"... and {len(affected_files) - 10} more files"

        return result

    except Exception as e:
        raise ValueError(f"Failed to rename tag: {e}") from e


def _add_tags_to_content(content: str, tags: list[str]) -> str:
    """Add tags to content, updating frontmatter if it exists."""
    if not tags:
        return content

    # Check if content has YAML frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

    if frontmatter_match:
        # Update existing frontmatter
        frontmatter = frontmatter_match.group(1)
        remaining_content = content[frontmatter_match.end() :]

        # Look for existing tags field
        tag_pattern = r"^(tags?|tag):\s*(\[.*?\]|\S+.*?)$"
        tag_match = re.search(tag_pattern, frontmatter, re.MULTILINE)

        if tag_match:
            # Update existing tags
            existing_line = tag_match.group(0)
            field_name = tag_match.group(1)

            # Parse existing tags
            existing_tags_str = tag_match.group(2)
            if existing_tags_str.startswith("[") and existing_tags_str.endswith("]"):
                # Array format
                existing_content = existing_tags_str[1:-1]
                existing_tags = [
                    tag.strip().strip("\"'") for tag in existing_content.split(",") if tag.strip()
                ]
            else:
                # String format
                existing_tags = [existing_tags_str.strip()]

            # Combine tags
            all_tags = existing_tags + tags
            tag_list = ", ".join(f'"{tag}"' for tag in all_tags)
            new_tags_line = f"{field_name}: [{tag_list}]"

            # Replace in frontmatter
            updated_frontmatter = frontmatter.replace(existing_line, new_tags_line)
        else:
            # Add new tags field
            tag_list = ", ".join(f'"{tag}"' for tag in tags)
            updated_frontmatter = frontmatter + f"\ntags: [{tag_list}]"

        return f"---\n{updated_frontmatter}\n---\n{remaining_content}"
    else:
        # No frontmatter - add it
        tag_list = ", ".join(f'"{tag}"' for tag in tags)
        new_frontmatter = f"---\ntags: [{tag_list}]\n---\n"
        return new_frontmatter + content


def _remove_tags_from_content(content: str, tags_to_remove: list[str]) -> str:
    """Remove tags from content."""
    if not tags_to_remove:
        return content

    # Remove from frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        remaining_content = content[frontmatter_match.end() :]

        # Update frontmatter tags
        tag_pattern = r"^(tags?|tag):\s*(\[.*?\]|\S+.*?)$"
        tag_match = re.search(tag_pattern, frontmatter, re.MULTILINE)

        if tag_match:
            existing_line = tag_match.group(0)
            field_name = tag_match.group(1)
            existing_tags_str = tag_match.group(2)

            # Parse existing tags
            if existing_tags_str.startswith("[") and existing_tags_str.endswith("]"):
                existing_content = existing_tags_str[1:-1]
                existing_tags = [
                    tag.strip().strip("\"'") for tag in existing_content.split(",") if tag.strip()
                ]
            else:
                existing_tags = [existing_tags_str.strip()]

            # Remove specified tags
            remaining_tags = [tag for tag in existing_tags if tag not in tags_to_remove]

            if remaining_tags:
                tag_list = ", ".join(f'"{tag}"' for tag in remaining_tags)
                new_tags_line = f"{field_name}: [{tag_list}]"
                updated_frontmatter = frontmatter.replace(existing_line, new_tags_line)
            else:
                # Remove the entire tags line
                updated_frontmatter = frontmatter.replace(existing_line, "")
                # Clean up empty lines
                updated_frontmatter = re.sub(r"\n\s*\n", "\n", updated_frontmatter).strip()

            if updated_frontmatter.strip():
                content = f"---\n{updated_frontmatter}\n---\n{remaining_content}"
            else:
                content = remaining_content
        else:
            content = f"---\n{frontmatter}\n---\n{remaining_content}"

    # Remove inline hashtags
    for tag in tags_to_remove:
        # Remove hashtag versions
        content = re.sub(rf"#\b{re.escape(tag)}\b", "", content, flags=re.IGNORECASE)
        # Clean up extra spaces
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"^\s+|\s+$", "", content, flags=re.MULTILINE)

    return content


def _replace_tag_in_content(content: str, old_tag: str, new_tag: str) -> tuple[str, int]:
    """Replace a tag in content and return the updated content and replacement count."""
    replacements = 0

    # Replace in frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        remaining_content = content[frontmatter_match.end() :]

        # Replace in tags arrays/lists
        old_frontmatter = frontmatter

        # Replace quoted versions
        frontmatter = re.sub(
            rf'(["\']){re.escape(old_tag)}\1', rf"\1{new_tag}\1", frontmatter, flags=re.IGNORECASE
        )

        # Replace unquoted versions in tag lists
        frontmatter = re.sub(
            rf"\b{re.escape(old_tag)}\b", new_tag, frontmatter, flags=re.IGNORECASE
        )

        if frontmatter != old_frontmatter:
            replacements += 1
            content = f"---\n{frontmatter}\n---\n{remaining_content}"

    # Replace inline hashtags
    old_content = content
    content = re.sub(rf"#\b{re.escape(old_tag)}\b", f"#{new_tag}", content, flags=re.IGNORECASE)

    if content != old_content:
        replacements += content.count(f"#{new_tag}") - old_content.count(f"#{new_tag}")

    return content, replacements
