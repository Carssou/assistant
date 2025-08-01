"""
Core Obsidian file operations.
"""

from datetime import datetime

from .utils import (
    ensure_directory,
    ensure_markdown_extension,
    file_exists,
    get_vault_path,
    safe_join_path,
    validate_vault_path,
)


async def create_obsidian_note(filename: str, content: str, folder: str | None = None) -> str:
    """
    Create a new note in the specified vault.

    Args:
        vault: Vault name (currently unused, uses default vault)
        filename: Note filename (without path separators)
        content: Note content in markdown
        folder: Optional subfolder path relative to vault root

    Returns:
        Success message with file path

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

        # Create directory structure if needed
        target_dir = target_path.parent
        await ensure_directory(target_dir)

        # Check if file already exists
        if await file_exists(target_path):
            raise ValueError(f"Note already exists: {target_path.name}")

        # Write content to file
        try:
            target_path.write_text(content, encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to write note: {e}") from e

        # Return success message
        relative_path = target_path.relative_to(vault_path)
        return f"✅ Note created successfully: {relative_path}"

    except Exception as e:
        raise ValueError(f"Failed to create note: {e}") from e


async def read_obsidian_note(filename: str, folder: str | None = None) -> str:
    """
    Read the content of an existing note.

    Args:
        vault: Vault name
        filename: Note filename
        folder: Optional subfolder path

    Returns:
        Note content with metadata

    Raises:
        ValueError: If note doesn't exist or can't be read
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

        # Read content
        try:
            content = target_path.read_text(encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to read note: {e}") from e

        # Get file metadata
        stat = target_path.stat()
        file_size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)

        # Return content with metadata
        relative_path = target_path.relative_to(vault_path)
        metadata = f"\n\n📄 **File Info**: {relative_path} ({file_size:,} bytes, modified {modified_time.strftime('%Y-%m-%d %H:%M:%S')})"

        return f"{content}{metadata}"

    except Exception as e:
        raise ValueError(f"Failed to read note: {e}") from e


async def edit_obsidian_note(
    filename: str,
    content: str,
    folder: str | None = None,
    operation: str = "replace",
) -> str:
    """
    Edit an existing note.

    Args:
        vault: Vault name
        filename: Note filename
        content: New content
        folder: Optional subfolder path
        operation: Edit operation ("replace", "append", "prepend")

    Returns:
        Success message with operation details

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

        # Read existing content for backup and diff
        try:
            existing_content = target_path.read_text(encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to read existing note: {e}") from e

        # Determine new content based on operation
        if operation == "replace":
            new_content = content
        elif operation == "append":
            new_content = existing_content + "\n" + content
        elif operation == "prepend":
            new_content = content + "\n" + existing_content
        else:
            raise ValueError(
                f"Invalid operation: {operation}. Use 'replace', 'append', or 'prepend'"
            )

        # Create backup
        backup_path = target_path.with_suffix(
            f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        try:
            backup_path.write_text(existing_content, encoding="utf-8")
        except (OSError, RuntimeError):
            # Backup failed, but continue with edit
            pass

        # Write new content
        try:
            target_path.write_text(new_content, encoding="utf-8")
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to write note: {e}") from e

        # Calculate diff summary
        old_lines = len(existing_content.splitlines())
        new_lines = len(new_content.splitlines())
        line_diff = new_lines - old_lines

        # Return success message
        relative_path = target_path.relative_to(vault_path)
        diff_info = f"({line_diff:+d} lines)" if line_diff != 0 else "(no change in line count)"

        return f"✅ Note edited successfully ({operation}): {relative_path} {diff_info}"

    except Exception as e:
        raise ValueError(f"Failed to edit note: {e}") from e


async def delete_obsidian_note(filename: str, folder: str | None = None) -> str:
    """
    Delete an existing note.

    Args:
        vault: Vault name
        filename: Note filename
        folder: Optional subfolder path

    Returns:
        Success message

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

        # Get file info before deletion
        stat = target_path.stat()
        file_size = stat.st_size

        # Delete the file
        try:
            target_path.unlink()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to delete note: {e}") from e

        # Return success message
        relative_path = target_path.relative_to(vault_path)
        return f"🗑️ Note deleted successfully: {relative_path} ({file_size:,} bytes)"

    except Exception as e:
        raise ValueError(f"Failed to delete note: {e}") from e


async def list_available_obsidian_vaults() -> str:
    """
    List available Obsidian vaults.

    Args:

    Returns:
        List of available vaults
    """
    try:
        # For now, return the single configured vault
        # TODO: Support multiple vaults in config
        vault_path = get_vault_path()
        if not vault_path:
            return "❌ No Obsidian vault configured"
        vault_name = vault_path.name

        # Check vault status
        if not vault_path.exists():
            status = "❌ Path does not exist"
        elif not vault_path.is_dir():
            status = "❌ Not a directory"
        elif not (vault_path / ".obsidian").exists():
            status = "⚠️ Missing .obsidian config"
        else:
            # Count notes
            try:
                md_files = list(vault_path.rglob("*.md"))
                note_count = len(md_files)
                status = f"✅ {note_count} notes"
            except (OSError, RuntimeError):
                status = "✅ Valid vault"

        return f"📚 **Available Vaults**:\n\n- **{vault_name}**: {vault_path} - {status}"

    except Exception as e:
        return f"❌ Error listing vaults: {e}"
