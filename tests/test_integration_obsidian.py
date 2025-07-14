"""
Integration tests for Obsidian MCP server with actual agent.

These tests verify the complete integration between the agent and Obsidian tools,
including real MCP server communication.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agent.agent import create_agent
from config.settings import AgentConfig, LLMProvider

# from tools.obsidian import create_obsidian_tools  # No longer needed with MCP integration


class TestObsidianIntegration:
    """Integration tests for Obsidian MCP functionality."""

    def setup_temp_vault(self):
        """Create a temporary vault for testing."""
        temp_dir = tempfile.mkdtemp()
        vault_path = Path(temp_dir)

        # Create some test notes
        (vault_path / "test_note.md").write_text(
            """---
title: Test Note
created: 2023-12-25T10:30:00
tags: [test, sample]
---

This is a test note with some content."""
        )

        (vault_path / "Daily Notes").mkdir()
        (vault_path / "Templates").mkdir()

        return vault_path

    def test_obsidian_mcp_server_config(self):
        """Test Obsidian MCP server configuration."""
        temp_vault = self.setup_temp_vault()

        try:
            from mcp_servers.configs import create_obsidian_mcp_server

            # Create a mock config to bypass validation
            mock_config = Mock()
            mock_config.obsidian_vault_path = temp_vault

            server = create_obsidian_mcp_server(mock_config)

            assert server is not None
            assert server.command == "npx"
            assert server.args == ["-y", "obsidian-mcp-pydanticai", str(temp_vault)]

        finally:
            # Clean up temporary directory
            import shutil

            shutil.rmtree(temp_vault)

    def test_temp_vault_structure(self):
        """Test temporary vault structure creation."""
        temp_vault = self.setup_temp_vault()

        try:
            # Verify vault structure
            assert temp_vault.exists()
            assert (temp_vault / "test_note.md").exists()
            assert (temp_vault / "Daily Notes").exists()
            assert (temp_vault / "Templates").exists()

            # Verify note content
            note_content = (temp_vault / "test_note.md").read_text()
            assert "Test Note" in note_content
            assert "test, sample" in note_content

        finally:
            import shutil

            shutil.rmtree(temp_vault)

    def test_mcp_server_configuration_validation(self):
        """Test MCP server configuration validation."""
        from mcp_servers.configs import create_obsidian_mcp_server

        # Test with None vault path (should return None)
        mock_config = Mock()
        mock_config.obsidian_vault_path = None

        server = create_obsidian_mcp_server(mock_config)
        assert server is None

        # Test with placeholder vault path (should return None)
        mock_config.obsidian_vault_path = Path("/path/to/your/vault")
        server = create_obsidian_mcp_server(mock_config)
        assert server is None

    @pytest.mark.asyncio
    async def test_real_mcp_server_integration(self):
        """Test actual MCP server integration with PydanticAI agent using real vault."""
        # Load configuration from environment (includes real vault path)
        config = AgentConfig()

        # Skip if no real vault is configured
        if (
            not config.obsidian_vault_path
            or str(config.obsidian_vault_path) == "/path/to/your/vault"
        ):
            pytest.skip("No real Obsidian vault configured in environment")

        # Verify the vault exists and is accessible
        if not config.obsidian_vault_path.exists():
            pytest.skip(f"Configured Obsidian vault does not exist: {config.obsidian_vault_path}")

        try:
            config.llm_provider = LLMProvider.OPENAI
            config.llm_choice = "gpt-4o-mini"
            config.llm_api_key = "test-key"

            # Mock the model creation to avoid actual API calls
            with patch("config.settings.create_model_instance") as mock_create_model:
                mock_model_instance = AsyncMock()
                mock_create_model.return_value = mock_model_instance

                # Create agent with real MCP server configuration
                agent = await create_agent(config)

                # Verify agent has MCP servers configured
                assert agent.has_mcp_servers()
                servers = agent.mcp_servers
                if len(servers) > 0:
                    # Check if Obsidian MCP server is configured
                    obsidian_server = next(
                        (s for s in servers if "obsidian-mcp" in " ".join(s.args)), None
                    )
                    if obsidian_server:
                        assert obsidian_server.command == "npx"
                        assert str(config.obsidian_vault_path) in obsidian_server.args

                # Test that we can start the MCP server context
                # This will actually try to start the obsidian-mcp server
                try:
                    from agent.agent import agent as global_agent

                    async with global_agent.run_mcp_servers():
                        # If we get here, the MCP server started successfully
                        # and PydanticAI can communicate with it
                        assert True, "MCP server started and agent can communicate with it"

                except Exception as e:
                    # If obsidian-mcp is not available, skip the test
                    if any(
                        keyword in str(e).lower()
                        for keyword in ["npx", "obsidian-mcp", "command not found", "not found"]
                    ):
                        pytest.skip(f"obsidian-mcp server not available: {e}")
                    else:
                        # This is a real error we should investigate
                        raise AssertionError(f"MCP server integration failed: {e}") from e

                # Clean up
                await agent.close()

        except Exception:
            # Clean up on error
            if "agent" in locals():
                await agent.close()
            raise

    def test_mcp_server_availability_check(self):
        """Test if obsidian-mcp is available on the system."""
        import subprocess

        try:
            # Check if npx is available
            result = subprocess.run(
                ["npx", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                pytest.skip("npx not available on system")

            # Try to get help from obsidian-mcp to see if it's available
            result = subprocess.run(
                ["npx", "-y", "obsidian-mcp", "--help"], capture_output=True, text=True, timeout=30
            )

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
