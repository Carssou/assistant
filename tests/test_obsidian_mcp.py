"""
Unit tests for Obsidian MCP server integration.

Tests the MCP server configuration, connection, and tool wrappers.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from config.settings import AgentConfig, LLMProvider
from mcp_servers.configs import create_obsidian_mcp_server, create_all_mcp_servers
from tools.obsidian import ObsidianTools, create_obsidian_tools
from agent.dependencies import AgentDependencies


class TestObsidianMCPServer:
    """Test Obsidian MCP server configuration."""
    
    def test_create_obsidian_mcp_server_no_vault_path(self):
        """Test MCP server creation with no vault path."""
        config = AgentConfig(obsidian_vault_path=None)
        server = create_obsidian_mcp_server(config)
        assert server is None
    
    def test_create_obsidian_mcp_server_nonexistent_path(self):
        """Test MCP server creation with nonexistent vault path."""
        # Create a mock config to bypass validation
        config = Mock()
        config.obsidian_vault_path = Path("/nonexistent/path")
        
        with pytest.raises(ValueError, match="Obsidian vault path does not exist"):
            create_obsidian_mcp_server(config)
    
    @patch('pathlib.Path.exists')
    def test_create_obsidian_mcp_server_valid_path(self, mock_exists):
        """Test MCP server creation with valid vault path."""
        mock_exists.return_value = True
        vault_path = Path("/mock/vault/path")
        
        # Create a mock config to bypass validation
        config = Mock()
        config.obsidian_vault_path = vault_path
        
        server = create_obsidian_mcp_server(config)
        
        assert server is not None
        assert server.command == 'npx'
        assert server.args == ['-y', 'obsidian-mcp', str(vault_path)]
    
    @patch('pathlib.Path.exists')
    def test_create_all_mcp_servers_with_obsidian(self, mock_exists):
        """Test creating all MCP servers with Obsidian configured."""
        mock_exists.return_value = True
        
        # Create a mock config to bypass validation
        config = Mock()
        config.obsidian_vault_path = Path("/mock/vault")
        
        servers = create_all_mcp_servers(config)
        
        assert len(servers) == 1  # Only Obsidian implemented
        assert servers[0].command == 'npx'
    
    def test_create_all_mcp_servers_no_config(self):
        """Test creating all MCP servers with no configuration."""
        config = AgentConfig()
        servers = create_all_mcp_servers(config)
        assert len(servers) == 0


class TestObsidianTools:
    """Test Obsidian tool wrappers."""
    
    def setup_method(self):
        """Set up test dependencies."""
        self.mock_config = Mock()
        self.mock_config.obsidian_vault_path = Path("/mock/vault")
        self.mock_config.obsidian_daily_notes_path = "Daily Notes"
        self.mock_config.obsidian_templates_path = "Templates"
        
        self.mock_logger = Mock()
        
        self.mock_deps = Mock(spec=AgentDependencies)
        self.mock_deps.config = self.mock_config
        self.mock_deps.logger = self.mock_logger
        
        self.obsidian_tools = ObsidianTools(self.mock_deps)
    
    def test_init(self):
        """Test ObsidianTools initialization."""
        assert self.obsidian_tools.deps == self.mock_deps
        assert self.obsidian_tools.config == self.mock_config
        assert self.obsidian_tools.logger == self.mock_logger
        assert self.obsidian_tools.vault_path == Path("/mock/vault")
    
    def test_validate_vault_access_no_path(self):
        """Test vault validation with no path configured."""
        self.mock_config.obsidian_vault_path = None
        tools = ObsidianTools(self.mock_deps)
        
        result = tools.validate_vault_access()
        
        assert result is False
        self.mock_logger.warning.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_validate_vault_access_nonexistent(self, mock_exists):
        """Test vault validation with nonexistent path."""
        mock_exists.return_value = False
        
        result = self.obsidian_tools.validate_vault_access()
        
        assert result is False
        self.mock_logger.error.assert_called_once()
    
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.exists')
    def test_validate_vault_access_not_directory(self, mock_exists, mock_is_dir):
        """Test vault validation with file instead of directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = False
        
        result = self.obsidian_tools.validate_vault_access()
        
        assert result is False
        self.mock_logger.error.assert_called_once()
    
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.exists')
    def test_validate_vault_access_valid(self, mock_exists, mock_is_dir):
        """Test vault validation with valid directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        result = self.obsidian_tools.validate_vault_access()
        
        assert result is True
        self.mock_logger.info.assert_called_once()
    
    def test_get_vault_info_no_config(self):
        """Test get_vault_info with no vault configured."""
        self.mock_config.obsidian_vault_path = None
        tools = ObsidianTools(self.mock_deps)
        
        info = tools.get_vault_info()
        
        assert info["status"] == "not_configured"
        assert "No vault path configured" in info["message"]
    
    @patch('pathlib.Path.exists')
    def test_get_vault_info_inaccessible(self, mock_exists):
        """Test get_vault_info with inaccessible vault."""
        mock_exists.return_value = False
        
        info = self.obsidian_tools.get_vault_info()
        
        assert info["status"] == "error"
        assert "Cannot access vault" in info["message"]
    
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.is_dir')
    @patch('pathlib.Path.exists')
    def test_get_vault_info_accessible(self, mock_exists, mock_is_dir, mock_rglob):
        """Test get_vault_info with accessible vault."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_rglob.return_value = [Path("note1.md"), Path("note2.md")]
        
        info = self.obsidian_tools.get_vault_info()
        
        assert info["status"] == "accessible"
        assert info["path"] == "/mock/vault"
        assert info["note_count"] == "2"
        assert info["daily_notes_path"] == "Daily Notes"
        assert info["templates_path"] == "Templates"
    
    def test_get_note_path(self):
        """Test note path generation."""
        path1 = self.obsidian_tools.get_note_path("test_note")
        path2 = self.obsidian_tools.get_note_path("test_note.md")
        
        assert path1 == Path("/mock/vault/test_note.md")
        assert path2 == Path("/mock/vault/test_note.md")
    
    def test_sanitize_note_name(self):
        """Test note name sanitization."""
        test_cases = [
            ("Valid Name", "Valid Name"),
            ("Name with <invalid> chars", "Name with _invalid_ chars"),
            ("  Name with spaces  ", "Name with spaces"),
            (".hidden.name.", "hidden.name"),
            ("", "untitled"),
            ("Name/with\\path:chars", "Name_with_path_chars")
        ]
        
        for input_name, expected in test_cases:
            result = self.obsidian_tools.sanitize_note_name(input_name)
            assert result == expected
    
    @patch('datetime.datetime')
    def test_create_daily_note_name(self, mock_datetime):
        """Test daily note name creation."""
        mock_datetime.now.return_value.strftime.return_value = "2023-12-25"
        
        name = self.obsidian_tools.create_daily_note_name()
        
        assert name == "2023-12-25.md"
    
    @patch('datetime.datetime')
    def test_format_note_content(self, mock_datetime):
        """Test note content formatting."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-12-25T10:30:00"
        
        content = self.obsidian_tools.format_note_content(
            "Test Note", 
            "This is the content",
            ["tag1", "tag2"]
        )
        
        assert "title: Test Note" in content
        assert "created: 2023-12-25T10:30:00" in content
        assert "tags: [tag1, tag2]" in content
        assert "This is the content" in content
        assert content.startswith("---")
    
    def test_extract_note_metadata(self):
        """Test metadata extraction from frontmatter."""
        content = """---
title: Test Note
created: 2023-12-25T10:30:00
tags: [tag1, tag2]
---

This is the content."""
        
        metadata = self.obsidian_tools.extract_note_metadata(content)
        
        assert metadata["title"] == "Test Note"
        assert metadata["created"] == "2023-12-25T10:30:00"
        assert metadata["tags"] == "[tag1, tag2]"
    
    def test_extract_note_metadata_no_frontmatter(self):
        """Test metadata extraction without frontmatter."""
        content = "Just plain content without frontmatter."
        
        metadata = self.obsidian_tools.extract_note_metadata(content)
        
        assert metadata == {}
    
    def test_create_obsidian_tools_factory(self):
        """Test ObsidianTools factory function."""
        tools = create_obsidian_tools(self.mock_deps)
        
        assert isinstance(tools, ObsidianTools)
        assert tools.deps == self.mock_deps
    
    def test_obsidian_markdown_formatting(self):
        """Test Obsidian-specific markdown formatting."""
        # Test wikilink creation
        wikilink = self.obsidian_tools.create_wikilink("My Note")
        assert wikilink == "[[My Note]]"
        
        wikilink_with_display = self.obsidian_tools.create_wikilink("My Note", "Custom Display")
        assert wikilink_with_display == "[[My Note|Custom Display]]"
        
        # Test tag string creation
        tag_string = self.obsidian_tools.create_tag_string(["research", "important notes"])
        assert tag_string == "#research #important_notes"
        
        # Test wikilink extraction
        content_with_links = "This links to [[Note 1]] and [[Note 2|Display Text]]."
        extracted_links = self.obsidian_tools.extract_wikilinks(content_with_links)
        assert extracted_links == ["Note 1", "Note 2"]
        
        # Test tag extraction
        content_with_tags = "This has #tag1 and #tag2 but not `#code_tag` in code."
        extracted_tags = self.obsidian_tools.extract_tags_from_content(content_with_tags)
        assert "tag1" in extracted_tags
        assert "tag2" in extracted_tags
        assert "code_tag" not in extracted_tags
    
    def test_process_obsidian_markdown(self):
        """Test markdown processing for Obsidian."""
        # Test header spacing
        content = "# Header\nSome content"
        processed = self.obsidian_tools.process_obsidian_markdown(content)
        assert "\n\n# Header\n" in processed
        
        # Test markdown link conversion
        content = "Check [this note](other_note.md) for details."
        processed = self.obsidian_tools.process_obsidian_markdown(content)
        assert "[[other_note.md|this note]]" in processed
        
        # Test that content starts with newline
        content = "Regular content"
        processed = self.obsidian_tools.process_obsidian_markdown(content)
        assert processed.startswith("\n")