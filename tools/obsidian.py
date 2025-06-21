"""
Obsidian tool wrappers for note management operations.

This module provides high-level functions for working with Obsidian notes
through the MCP server integration.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from agent.dependencies import AgentDependencies


logger = logging.getLogger(__name__)


class ObsidianTools:
    """
    High-level Obsidian operations wrapper.
    
    This class provides convenient methods for common Obsidian operations
    that can be used by the agent or other components.
    """
    
    def __init__(self, deps: AgentDependencies):
        """
        Initialize Obsidian tools.
        
        Args:
            deps: Agent dependencies containing configuration and clients
        """
        self.deps = deps
        self.config = deps.config
        self.logger = deps.logger
        self.vault_path = self.config.obsidian_vault_path
    
    def validate_vault_access(self) -> bool:
        """
        Validate that the Obsidian vault is accessible.
        
        Returns:
            True if vault is accessible, False otherwise
        """
        if not self.vault_path:
            self.logger.warning("No Obsidian vault path configured")
            return False
        
        if not self.vault_path.exists():
            self.logger.error(f"Obsidian vault path does not exist: {self.vault_path}")
            return False
        
        if not self.vault_path.is_dir():
            self.logger.error(f"Obsidian vault path is not a directory: {self.vault_path}")
            return False
        
        self.logger.info(f"Obsidian vault validated: {self.vault_path}")
        return True
    
    def get_vault_info(self) -> Dict[str, str]:
        """
        Get information about the configured vault.
        
        Returns:
            Dictionary with vault information
        """
        if not self.vault_path:
            return {"status": "not_configured", "message": "No vault path configured"}
        
        if not self.validate_vault_access():
            return {"status": "error", "message": f"Cannot access vault at {self.vault_path}"}
        
        # Count notes (markdown files)
        try:
            md_files = list(self.vault_path.rglob("*.md"))
            note_count = len(md_files)
            
            return {
                "status": "accessible",
                "path": str(self.vault_path),
                "note_count": str(note_count),
                "daily_notes_path": self.config.obsidian_daily_notes_path,
                "templates_path": self.config.obsidian_templates_path
            }
        except Exception as e:
            self.logger.error(f"Error getting vault info: {e}")
            return {"status": "error", "message": f"Error accessing vault: {str(e)}"}
    
    def get_note_path(self, note_name: str) -> Path:
        """
        Get the full path for a note file.
        
        Args:
            note_name: Name of the note (with or without .md extension)
            
        Returns:
            Path object for the note file
        """
        if not note_name.endswith('.md'):
            note_name += '.md'
        
        return self.vault_path / note_name
    
    def sanitize_note_name(self, name: str) -> str:
        """
        Sanitize a note name for file system compatibility.
        
        Args:
            name: Raw note name
            
        Returns:
            Sanitized note name
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        name = name.strip(' .')
        
        # Ensure the name isn't empty
        if not name:
            name = "untitled"
        
        return name
    
    def create_daily_note_name(self) -> str:
        """
        Create a daily note name with current date.
        
        Returns:
            Daily note filename
        """
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{today}.md"
    
    def format_note_content(self, title: str, content: str, tags: Optional[List[str]] = None) -> str:
        """
        Format note content with frontmatter and Obsidian-specific formatting.
        
        Args:
            title: Note title
            content: Note content
            tags: Optional list of tags
            
        Returns:
            Formatted note content with frontmatter
        """
        from datetime import datetime
        
        # Create frontmatter
        frontmatter = ["---"]
        frontmatter.append(f"title: {title}")
        frontmatter.append(f"created: {datetime.now().isoformat()}")
        
        if tags:
            frontmatter.append(f"tags: [{', '.join(tags)}]")
        
        frontmatter.append("---")
        frontmatter.append("")  # Empty line after frontmatter
        
        # Process content for Obsidian-specific formatting
        processed_content = self.process_obsidian_markdown(content)
        
        # Combine frontmatter and content
        full_content = "\n".join(frontmatter) + processed_content
        
        return full_content
    
    def process_obsidian_markdown(self, content: str) -> str:
        """
        Process content for Obsidian-specific markdown formatting.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Processed content with Obsidian-specific formatting
        """
        # Add proper line breaks if not present
        if not content.startswith('\n'):
            content = '\n' + content
        
        # Ensure proper spacing around headers
        import re
        content = re.sub(r'(\n)(#{1,6})\s*([^\n]+)', r'\1\1\2 \3\1', content)
        
        # Ensure proper spacing around code blocks
        content = re.sub(r'(\n)(```[^\n]*\n)', r'\1\1\2', content)
        content = re.sub(r'(\n```\n)', r'\1\1', content)
        
        # Convert internal links to Obsidian format [[link]]
        # This is a basic implementation - can be extended for more complex cases
        content = re.sub(r'\[([^\]]+)\]\(([^)]+\.md)\)', r'[[\2|\1]]', content)
        
        return content
    
    def create_wikilink(self, note_name: str, display_text: Optional[str] = None) -> str:
        """
        Create an Obsidian wikilink.
        
        Args:
            note_name: Name of the note to link to
            display_text: Optional display text for the link
            
        Returns:
            Formatted wikilink
        """
        if display_text:
            return f"[[{note_name}|{display_text}]]"
        return f"[[{note_name}]]"
    
    def create_tag_string(self, tags: List[str]) -> str:
        """
        Create a tag string for Obsidian notes.
        
        Args:
            tags: List of tag names
            
        Returns:
            Formatted tag string
        """
        # Obsidian supports both #tag and [[tag]] formats
        # Using #tag format by default
        return " ".join(f"#{tag.replace(' ', '_')}" for tag in tags)
    
    def extract_wikilinks(self, content: str) -> List[str]:
        """
        Extract all wikilinks from note content.
        
        Args:
            content: Note content with potential wikilinks
            
        Returns:
            List of linked note names
        """
        import re
        
        # Match [[note]] and [[note|display]] patterns
        pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(pattern, content)
        
        return [match.strip() for match in matches]
    
    def extract_tags_from_content(self, content: str) -> List[str]:
        """
        Extract hashtags from note content.
        
        Args:
            content: Note content with potential hashtags
            
        Returns:
            List of tag names (without # prefix)
        """
        import re
        
        # Match #tag patterns (excluding those in code blocks)
        pattern = r'(?:^|[^`])#([a-zA-Z0-9_-]+)(?:[^a-zA-Z0-9_-]|$)'
        matches = re.findall(pattern, content, re.MULTILINE)
        
        return list(set(matches))  # Remove duplicates
    
    def extract_note_metadata(self, content: str) -> Dict[str, str]:
        """
        Extract metadata from note frontmatter.
        
        Args:
            content: Note content with potential frontmatter
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        if not content.startswith('---'):
            return metadata
        
        try:
            # Find the end of frontmatter
            lines = content.split('\n')
            frontmatter_end = -1
            
            for i, line in enumerate(lines[1:], 1):  # Skip first ---
                if line.strip() == '---':
                    frontmatter_end = i
                    break
            
            if frontmatter_end == -1:
                return metadata
            
            # Parse frontmatter
            frontmatter_lines = lines[1:frontmatter_end]
            for line in frontmatter_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            
        except Exception as e:
            self.logger.warning(f"Error parsing frontmatter: {e}")
        
        return metadata


def create_obsidian_tools(deps: AgentDependencies) -> ObsidianTools:
    """
    Factory function to create Obsidian tools instance.
    
    Args:
        deps: Agent dependencies
        
    Returns:
        ObsidianTools instance
    """
    return ObsidianTools(deps)