"""
Comprehensive test suite for Obsidian native tools.
"""

import asyncio
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from tools.obsidian.core import (
    create_obsidian_note,
    delete_obsidian_note,
    edit_obsidian_note,
    list_available_obsidian_vaults,
    read_obsidian_note,
)
from tools.obsidian.search import (
    get_obsidian_tags_list,
    search_obsidian_vault,
)
from tools.obsidian.tags import (
    add_obsidian_tags,
    remove_obsidian_tags,
    rename_obsidian_tag,
)
from tools.obsidian.utils import (
    ensure_directory,
    ensure_markdown_extension,
    extract_tags,
    file_exists,
    get_vault_path,
    matches_tag_pattern,
    normalize_tag,
    safe_join_path,
    validate_vault_path,
)


class TestObsidianTools:
    """Test suite for Obsidian native tools."""

    @pytest.fixture
    def mock_deps(self, tmp_path):
        """Create mock dependencies with temporary vault."""
        # Create temporary vault structure
        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()

        # Create .obsidian directory to make it a valid vault
        obsidian_dir = vault_path / ".obsidian"
        obsidian_dir.mkdir()

        # Create some test notes
        (vault_path / "test_note.md").write_text("# Test Note\n\nThis is a test note.")
        (vault_path / "tagged_note.md").write_text(
            """---
tags: ["ai", "testing"]
---

# Tagged Note

This note has #hashtags and frontmatter tags.
"""
        )

        # Create subdirectory with notes
        sub_dir = vault_path / "projects"
        sub_dir.mkdir()
        (sub_dir / "project_note.md").write_text("# Project Note\n\nProject content.")

        # Mock config
        mock_config = Mock()
        mock_config.obsidian_vault_path = str(vault_path)

        # Mock deps
        mock_deps = Mock()
        mock_deps.config = mock_config

        return mock_deps

    @pytest.mark.asyncio
    async def test_create_obsidian_note(self, mock_deps):
        """Test creating a new note."""
        result = await create_obsidian_note(
            mock_deps, "test_vault", "new_note", "# New Note\n\nThis is new content."
        )

        assert "Note created successfully" in result
        assert "new_note.md" in result

        # Verify file was created
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        new_file = vault_path / "new_note.md"
        assert new_file.exists()
        assert "This is new content." in new_file.read_text()

    @pytest.mark.asyncio
    async def test_create_note_with_folder(self, mock_deps):
        """Test creating a note in a subfolder."""
        result = await create_obsidian_note(
            mock_deps,
            "test_vault",
            "folder_note",
            "# Folder Note\n\nContent in folder.",
            folder="new_folder",
        )

        assert "Note created successfully" in result

        # Verify file was created in correct location
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        new_file = vault_path / "new_folder" / "folder_note.md"
        assert new_file.exists()

    @pytest.mark.asyncio
    async def test_create_duplicate_note_fails(self, mock_deps):
        """Test that creating a duplicate note fails."""
        with pytest.raises(ValueError, match="Note already exists"):
            await create_obsidian_note(mock_deps, "test_vault", "test_note", "Duplicate content")

    @pytest.mark.asyncio
    async def test_read_obsidian_note(self, mock_deps):
        """Test reading an existing note."""
        result = await read_obsidian_note(mock_deps, "test_vault", "test_note")

        assert "Test Note" in result
        assert "This is a test note." in result
        assert "File Info" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent_note_fails(self, mock_deps):
        """Test that reading a nonexistent note fails."""
        with pytest.raises(ValueError, match="Note not found"):
            await read_obsidian_note(mock_deps, "test_vault", "nonexistent")

    @pytest.mark.asyncio
    async def test_edit_obsidian_note_replace(self, mock_deps):
        """Test editing a note with replace operation."""
        result = await edit_obsidian_note(
            mock_deps,
            "test_vault",
            "test_note",
            "# Updated Note\n\nThis is updated content.",
            operation="replace",
        )

        assert "Note edited successfully (replace)" in result

        # Verify content was updated
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        note_file = vault_path / "test_note.md"
        content = note_file.read_text()
        assert "Updated Note" in content
        assert "updated content" in content

    @pytest.mark.asyncio
    async def test_edit_obsidian_note_append(self, mock_deps):
        """Test editing a note with append operation."""
        original_content = "# Test Note\n\nOriginal content."
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        note_file = vault_path / "append_test.md"
        note_file.write_text(original_content)

        result = await edit_obsidian_note(
            mock_deps, "test_vault", "append_test", "\n\nAppended content.", operation="append"
        )

        assert "Note edited successfully (append)" in result

        # Verify content was appended
        content = note_file.read_text()
        assert "Original content." in content
        assert "Appended content." in content

    @pytest.mark.asyncio
    async def test_delete_obsidian_note(self, mock_deps):
        """Test deleting a note."""
        # Create a note to delete
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        delete_file = vault_path / "to_delete.md"
        delete_file.write_text("# To Delete\n\nThis will be deleted.")

        result = await delete_obsidian_note(mock_deps, "test_vault", "to_delete")

        assert "Note deleted successfully" in result
        assert not delete_file.exists()

    @pytest.mark.asyncio
    async def test_list_available_obsidian_vaults(self, mock_deps):
        """Test listing available vaults."""
        result = await list_available_obsidian_vaults(mock_deps)

        assert "Available Vaults" in result
        assert "test_vault" in result
        assert "notes" in result

    @pytest.mark.asyncio
    async def test_search_obsidian_vault_content(self, mock_deps):
        """Test content search functionality."""
        result = await search_obsidian_vault(
            mock_deps, "test_vault", "test note", search_type="content"
        )

        assert "Search Results" in result
        assert "test_note.md" in result or "tagged_note.md" in result

    @pytest.mark.asyncio
    async def test_search_obsidian_vault_filename(self, mock_deps):
        """Test filename search functionality."""
        result = await search_obsidian_vault(
            mock_deps, "test_vault", "tagged", search_type="filename"
        )

        assert "Search Results" in result
        assert "tagged_note.md" in result

    @pytest.mark.asyncio
    async def test_search_obsidian_vault_tags(self, mock_deps):
        """Test tag search functionality."""
        result = await search_obsidian_vault(mock_deps, "test_vault", "ai", search_type="tag")

        assert "Search Results" in result
        assert "tagged_note.md" in result

    @pytest.mark.asyncio
    async def test_get_obsidian_tags_list(self, mock_deps):
        """Test getting tags list."""
        result = await get_obsidian_tags_list(mock_deps, "test_vault")

        assert "All Tags in Vault" in result
        assert "#ai" in result
        assert "#testing" in result
        assert "#hashtags" in result

    @pytest.mark.asyncio
    async def test_add_obsidian_tags(self, mock_deps):
        """Test adding tags to a note."""
        result = await add_obsidian_tags(
            mock_deps, "test_vault", "test_note", ["python", "tutorial"]
        )

        assert "Tags added" in result
        assert "#python" in result
        assert "#tutorial" in result

        # Verify tags were added to file
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        note_file = vault_path / "test_note.md"
        content = note_file.read_text()
        assert "python" in content
        assert "tutorial" in content

    @pytest.mark.asyncio
    async def test_remove_obsidian_tags(self, mock_deps):
        """Test removing tags from a note."""
        result = await remove_obsidian_tags(mock_deps, "test_vault", "tagged_note", ["ai"])

        assert "Tags removed" in result
        assert "#ai" in result

        # Verify tag was removed
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        note_file = vault_path / "tagged_note.md"
        content = note_file.read_text()
        # Should still have testing tag but not ai
        assert "testing" in content

    @pytest.mark.asyncio
    async def test_rename_obsidian_tag(self, mock_deps):
        """Test renaming a tag across the vault."""
        result = await rename_obsidian_tag(mock_deps, "test_vault", "testing", "qa")

        assert "Tag renamed" in result
        assert "testing" in result
        assert "qa" in result

        # Verify tag was renamed in file
        vault_path = Path(mock_deps.config.obsidian_vault_path)
        note_file = vault_path / "tagged_note.md"
        content = note_file.read_text()
        assert "qa" in content


class TestObsidianUtils:
    """Test utility functions."""

    def test_ensure_markdown_extension(self):
        """Test markdown extension addition."""
        assert ensure_markdown_extension("test") == "test.md"
        assert ensure_markdown_extension("test.md") == "test.md"
        assert ensure_markdown_extension("test.txt") == "test.txt.md"

    def test_normalize_tag(self):
        """Test tag normalization."""
        assert normalize_tag("#test") == "test"
        assert normalize_tag("  Test  ") == "test"
        assert normalize_tag("#Test-Tag") == "test-tag"

    def test_matches_tag_pattern(self):
        """Test tag pattern matching."""
        assert matches_tag_pattern("test", "test")
        assert matches_tag_pattern("test*", "testing")
        assert matches_tag_pattern("ai", "ai/machine-learning")
        assert not matches_tag_pattern("test", "testing")

    def test_extract_tags(self):
        """Test tag extraction from content."""
        content = """---
tags: ["ai", "testing"]
---

# Test Note

This has #hashtag and #another-tag in content.
"""
        tags = extract_tags(content)
        assert "ai" in tags
        assert "testing" in tags
        assert "hashtag" in tags
        assert "another-tag" in tags

    @pytest.mark.asyncio
    async def test_file_exists(self, tmp_path):
        """Test file existence check."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        assert await file_exists(test_file)
        assert not await file_exists(tmp_path / "nonexistent.txt")

    @pytest.mark.asyncio
    async def test_ensure_directory(self, tmp_path):
        """Test directory creation."""
        new_dir = tmp_path / "new" / "nested" / "dir"
        await ensure_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()


class TestObsidianSecurity:
    """Test security and validation."""

    @pytest.fixture
    def mock_deps_security(self, tmp_path):
        """Create mock deps for security testing."""
        vault_path = tmp_path / "secure_vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        mock_config = Mock()
        mock_config.obsidian_vault_path = str(vault_path)

        mock_deps = Mock()
        mock_deps.config = mock_config

        return mock_deps

    def test_validate_vault_path_security(self, tmp_path):
        """Test path traversal protection."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()

        # Valid path within vault
        valid_path = vault_path / "note.md"
        assert validate_vault_path(vault_path, valid_path)

        # Invalid path outside vault
        with pytest.raises(ValueError, match="Path outside vault"):
            invalid_path = tmp_path / "outside.md"
            validate_vault_path(vault_path, invalid_path)

    def test_safe_join_path_security(self, tmp_path):
        """Test safe path joining."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()

        # Valid join
        result = safe_join_path(vault_path, "folder", "note.md")
        assert "folder" in str(result)
        assert "note.md" in str(result)

        # Should strip dangerous characters
        result = safe_join_path(vault_path, "../../../etc", "passwd")
        assert ".." not in str(result)
        assert "etc" in str(result)

    @pytest.mark.asyncio
    async def test_filename_validation(self, mock_deps_security):
        """Test filename validation prevents path traversal."""
        with pytest.raises(ValueError, match="cannot contain path separators"):
            await create_obsidian_note(
                mock_deps_security, "vault", "../../../etc/passwd", "malicious content"
            )


class TestPerformanceAndReliability:
    """Test performance and reliability aspects."""

    @pytest.mark.asyncio
    async def test_large_vault_performance(self, tmp_path):
        """Test performance with larger vault."""
        # Create a larger test vault
        vault_path = tmp_path / "large_vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create 100 test notes
        for i in range(100):
            note_file = vault_path / f"note_{i:03d}.md"
            note_file.write_text(
                f"""---
tags: ["test", "performance", "note-{i}"]
---

# Test Note {i}

This is test note number {i} for performance testing.
Contains various keywords like performance, testing, benchmark.
"""
            )

        mock_config = Mock()
        mock_config.obsidian_vault_path = str(vault_path)
        mock_deps = Mock()
        mock_deps.config = mock_config

        # Test search performance
        import time

        start_time = time.time()

        result = await search_obsidian_vault(
            mock_deps, "vault", "performance", search_type="content"
        )

        end_time = time.time()
        search_time = end_time - start_time

        # Should complete in under 1 second for 100 notes
        assert search_time < 1.0
        assert "Search Results" in result

    @pytest.mark.asyncio
    async def test_error_handling(self, tmp_path):
        """Test error handling and graceful failures."""
        # Create invalid mock deps
        mock_config = Mock()
        mock_config.obsidian_vault_path = "/nonexistent/path"
        mock_deps = Mock()
        mock_deps.config = mock_config

        with pytest.raises(ValueError, match="does not exist"):
            await create_obsidian_note(mock_deps, "vault", "test", "content")

    @pytest.mark.asyncio
    async def test_unicode_and_special_characters(self, tmp_path):
        """Test handling of unicode and special characters."""
        # Create valid vault for unicode test
        vault_path = tmp_path / "unicode_vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        mock_config = Mock()
        mock_config.obsidian_vault_path = str(vault_path)
        mock_deps = Mock()
        mock_deps.config = mock_config

        result = await create_obsidian_note(
            mock_deps,
            "vault",
            "unicode_test",
            "# Unicode Test 🚀\n\nContent with émojis and spëcial characters: 测试",
        )

        assert "Note created successfully" in result

        # Verify unicode content is preserved
        read_result = await read_obsidian_note(mock_deps, "vault", "unicode_test")
        assert "🚀" in read_result
        assert "émojis" in read_result
        assert "测试" in read_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
