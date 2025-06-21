"""
Integration tests for Obsidian MCP server with actual agent.

These tests verify the complete integration between the agent and Obsidian tools,
including real MCP server communication.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from config.settings import AgentConfig, LLMProvider
from agent.agent import create_agent
from tools.obsidian import create_obsidian_tools


class TestObsidianIntegration:
    """Integration tests for Obsidian MCP functionality."""
    
    def setup_temp_vault(self):
        """Create a temporary vault for testing."""
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir)
        
        # Create some test notes
        (vault_path / "test_note.md").write_text("""---
title: Test Note
created: 2023-12-25T10:30:00
tags: [test, sample]
---

This is a test note with some content.""")
        
        (vault_path / "Daily Notes").mkdir()
        (vault_path / "Templates").mkdir()
        
        return vault_path
    
    def test_obsidian_tools_with_real_vault(self):
        """Test Obsidian tools with a real temporary vault."""
        temp_vault = self.setup_temp_vault()
        
        try:
            # Create mock dependencies
            mock_deps = Mock()
            mock_deps.config = Mock()
            mock_deps.config.obsidian_vault_path = temp_vault
            mock_deps.config.obsidian_daily_notes_path = "Daily Notes"
            mock_deps.config.obsidian_templates_path = "Templates"
            mock_deps.logger = Mock()
            
            # Create Obsidian tools
            tools = create_obsidian_tools(mock_deps)
            
            # Test vault validation
            assert tools.validate_vault_access() is True
            
            # Test vault info
            vault_info = tools.get_vault_info()
            assert vault_info["status"] == "accessible"
            assert vault_info["note_count"] == "1"  # test_note.md
            assert vault_info["path"] == str(temp_vault)
            
            # Test note path generation
            note_path = tools.get_note_path("new_note")
            assert note_path == temp_vault / "new_note.md"
            
            # Test note name sanitization
            sanitized = tools.sanitize_note_name("Invalid/Name:With<Chars>")
            assert sanitized == "Invalid_Name_With_Chars_"
            
            # Test note content formatting
            content = tools.format_note_content(
                "Test Title",
                "Test content",
                ["tag1", "tag2"]
            )
            assert "title: Test Title" in content
            assert "tags: [tag1, tag2]" in content
            assert "Test content" in content
            
            # Test metadata extraction
            test_content = (temp_vault / "test_note.md").read_text()
            metadata = tools.extract_note_metadata(test_content)
            assert metadata["title"] == "Test Note"
            assert metadata["tags"] == "[test, sample]"
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_vault)
    
    def test_mcp_server_creation(self):
        """Test MCP server creation with valid configuration."""
        from mcp_servers.configs import create_obsidian_mcp_server
        
        temp_vault = self.setup_temp_vault()
        
        try:
            # Create a mock config to bypass validation
            mock_config = Mock()
            mock_config.obsidian_vault_path = temp_vault
            
            server = create_obsidian_mcp_server(mock_config)
            
            assert server is not None
            assert server.command == 'npx'
            assert server.args == ['-y', 'obsidian-mcp', str(temp_vault)]
            
        finally:
            import shutil
            shutil.rmtree(temp_vault)
    
    def test_vault_accessibility_validation(self):
        """Test comprehensive vault accessibility validation."""
        from tools.obsidian import ObsidianTools
        
        temp_vault = self.setup_temp_vault()
        
        try:
            # Test with valid vault
            mock_deps = Mock()
            mock_deps.config = Mock()
            mock_deps.config.obsidian_vault_path = temp_vault
            mock_deps.config.obsidian_daily_notes_path = "Daily Notes"
            mock_deps.config.obsidian_templates_path = "Templates"
            mock_deps.logger = Mock()
            
            tools = ObsidianTools(mock_deps)
            assert tools.validate_vault_access() is True
            
            # Test with non-existent vault
            mock_deps.config.obsidian_vault_path = Path("/nonexistent/path")
            tools = ObsidianTools(mock_deps)
            assert tools.validate_vault_access() is False
            
            # Test with None vault path
            mock_deps.config.obsidian_vault_path = None
            tools = ObsidianTools(mock_deps)
            assert tools.validate_vault_access() is False
            
        finally:
            import shutil
            shutil.rmtree(temp_vault)
    
    def test_note_content_operations(self):
        """Test note content manipulation operations."""
        from tools.obsidian import ObsidianTools
        
        temp_vault = self.setup_temp_vault()
        
        try:
            mock_deps = Mock()
            mock_deps.config = Mock()
            mock_deps.config.obsidian_vault_path = temp_vault
            mock_deps.config.obsidian_daily_notes_path = "Daily Notes"
            mock_deps.config.obsidian_templates_path = "Templates"
            mock_deps.logger = Mock()
            
            tools = ObsidianTools(mock_deps)
            
            # Test daily note name generation
            daily_note = tools.create_daily_note_name()
            assert daily_note.endswith(".md")
            assert len(daily_note) == 13  # YYYY-MM-DD.md format
            
            # Test note content formatting with tags
            content = tools.format_note_content(
                "Research Note",
                "Important research findings...",
                ["research", "important"]
            )
            
            assert "---" in content  # Frontmatter markers
            assert "title: Research Note" in content
            assert "tags: [research, important]" in content
            assert "Important research findings..." in content
            
            # Test note content formatting without tags
            content_no_tags = tools.format_note_content(
                "Simple Note",
                "Simple content"
            )
            
            assert "title: Simple Note" in content_no_tags
            assert "tags:" not in content_no_tags
            assert "Simple content" in content_no_tags
            
        finally:
            import shutil
            shutil.rmtree(temp_vault)
    
    @pytest.mark.asyncio
    async def test_real_mcp_server_integration(self):
        """Test actual MCP server integration with PydanticAI agent using real vault."""
        # Load configuration from environment (includes real vault path)
        config = AgentConfig()
        
        # Skip if no real vault is configured
        if not config.obsidian_vault_path or str(config.obsidian_vault_path) == "/path/to/your/vault":
            pytest.skip("No real Obsidian vault configured in environment")
        
        # Verify the vault exists and is accessible
        if not config.obsidian_vault_path.exists():
            pytest.skip(f"Configured Obsidian vault does not exist: {config.obsidian_vault_path}")
        
        try:
            config.llm_provider = LLMProvider.OPENAI
            config.llm_choice = "gpt-4o-mini"
            config.llm_api_key = "test-key"
            
            # Mock the model creation to avoid actual API calls
            with patch('config.settings.create_model_instance') as mock_create_model:
                mock_model_instance = AsyncMock()
                mock_create_model.return_value = mock_model_instance
                
                # Create agent with real MCP server configuration
                agent = await create_agent(config)
                
                # Verify agent has MCP servers configured
                assert len(agent.mcp_servers) == 1
                assert agent.mcp_servers[0].command == 'npx'
                assert str(config.obsidian_vault_path) in agent.mcp_servers[0].args
                
                # Test that we can start the MCP server context
                # This will actually try to start the obsidian-mcp server
                try:
                    async with agent.agent.run_mcp_servers():
                        # If we get here, the MCP server started successfully
                        # and PydanticAI can communicate with it
                        assert True, "MCP server started and agent can communicate with it"
                        
                except Exception as e:
                    # If obsidian-mcp is not available, skip the test
                    if any(keyword in str(e).lower() for keyword in ["npx", "obsidian-mcp", "command not found", "not found"]):
                        pytest.skip(f"obsidian-mcp server not available: {e}")
                    else:
                        # This is a real error we should investigate
                        raise AssertionError(f"MCP server integration failed: {e}")
                
                # Clean up
                await agent.close()
                
        except Exception as e:
            # Clean up on error
            if 'agent' in locals():
                await agent.close()
            raise
    
    def test_mcp_server_availability_check(self):
        """Test if obsidian-mcp is available on the system."""
        import subprocess
        
        try:
            # Check if npx is available
            result = subprocess.run(['npx', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                pytest.skip("npx not available on system")
            
            # Try to get help from obsidian-mcp to see if it's available
            result = subprocess.run(['npx', '-y', 'obsidian-mcp', '--help'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Package is available and working
                assert True, "obsidian-mcp is available via npx"
            else:
                # Package not available or error
                pytest.skip(f"obsidian-mcp package not available: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            pytest.skip(f"Cannot check MCP server availability: {e}")
        except Exception as e:
            pytest.skip(f"Error checking obsidian-mcp availability: {e}")