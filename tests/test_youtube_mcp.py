"""
Tests for YouTube MCP server integration.

This module tests the YouTube MCP server configuration and video processing utilities.
"""

import pytest
from unittest.mock import Mock

from config.settings import AgentConfig
from mcp_servers.configs import create_youtube_mcp_server
from tools.youtube import (
    YouTubeVideoManager, VideoInfo, VideoTranscript
)


class TestYouTubeMCPServer:
    """Test cases for YouTube MCP server configuration."""
    
    def test_youtube_server_creation(self):
        """Test that YouTube server is always created (no API key required)."""
        config = Mock(spec=AgentConfig)
        
        server = create_youtube_mcp_server(config)
        
        assert server is not None
        assert server.command == 'npx'
        assert server.args == ['-y', 'youtube-video-summarizer-mcp']
        assert not hasattr(server, 'env') or server.env is None


class TestYouTubeVideoManager:
    """Test cases for YouTube video management utilities."""
    
    def test_video_manager_initialization(self):
        """Test video manager initialization."""
        manager = YouTubeVideoManager()
        assert manager.default_language == "en"
        
        manager_es = YouTubeVideoManager(default_language="es")
        assert manager_es.default_language == "es"
    
    def test_extract_video_id(self):
        """Test video ID extraction from various URL formats."""
        manager = YouTubeVideoManager()
        
        # Standard watch URL
        video_id = manager.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
        
        # Short URL
        video_id = manager.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
        
        # Embed URL
        video_id = manager.extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
        
        # URL with additional parameters
        video_id = manager.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s")
        assert video_id == "dQw4w9WgXcQ"
        
        # Direct video ID
        video_id = manager.extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
        
        # Invalid URL
        video_id = manager.extract_video_id("https://example.com/video")
        assert video_id is None
        
        # Empty string
        video_id = manager.extract_video_id("")
        assert video_id is None
    
    def test_validate_youtube_url(self):
        """Test YouTube URL validation."""
        manager = YouTubeVideoManager()
        
        # Valid URLs
        assert manager.validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert manager.validate_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        assert manager.validate_youtube_url("dQw4w9WgXcQ")
        
        # Invalid URLs
        assert not manager.validate_youtube_url("https://example.com")
        assert not manager.validate_youtube_url("not a url")
        assert not manager.validate_youtube_url("")
    
    def test_normalize_youtube_url(self):
        """Test YouTube URL normalization."""
        manager = YouTubeVideoManager()
        
        # Various input formats should normalize to standard format
        inputs = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "dQw4w9WgXcQ"
        ]
        
        expected = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        for input_url in inputs:
            assert manager.normalize_youtube_url(input_url) == expected
        
        # Invalid URL should return None
        assert manager.normalize_youtube_url("https://example.com") is None
    
    def test_video_info_creation(self):
        """Test VideoInfo dataclass creation."""
        video_info = VideoInfo(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            description="Test description",
            duration="3:32",
            channel="Test Channel",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
        assert video_info.video_id == "dQw4w9WgXcQ"
        assert video_info.title == "Test Video"
        assert video_info.description == "Test description"
        assert video_info.duration == "3:32"
        assert video_info.channel == "Test Channel"
    
    def test_video_transcript_creation(self):
        """Test VideoTranscript dataclass creation."""
        transcript = VideoTranscript(
            video_id="dQw4w9WgXcQ",
            language="en",
            transcript_text="Hello world",
            auto_generated=False
        )
        
        assert transcript.video_id == "dQw4w9WgXcQ"
        assert transcript.language == "en"
        assert transcript.transcript_text == "Hello world"
        assert not transcript.auto_generated
        assert transcript.segments == []  # Default empty list
    
    def test_extract_key_points_from_summary(self):
        """Test key point extraction from summary."""
        manager = YouTubeVideoManager()
        
        # Summary with bullet points
        summary_bullets = """
        This video covers several important topics:
        - First key point about learning
        - Second important concept
        - Third crucial element
        Regular text without bullets.
        """
        
        points = manager.extract_key_points_from_summary(summary_bullets)
        assert len(points) == 3
        assert "First key point about learning" in points
        assert "Second important concept" in points
        assert "Third crucial element" in points
        
        # Summary with numbered list
        summary_numbered = """
        Here are the main points:
        1. Primary concept explanation
        2. Secondary important detail
        3. Final crucial takeaway
        """
        
        points = manager.extract_key_points_from_summary(summary_numbered)
        assert len(points) == 3
        assert "Primary concept explanation" in points
        
        # Summary without structured points
        summary_unstructured = """
        This video explains important concepts. The main idea is crucial for understanding.
        There are key elements to consider. The essential part is the conclusion.
        """
        
        points = manager.extract_key_points_from_summary(summary_unstructured)
        assert len(points) > 0  # Should find sentences with key indicators
    
    def test_get_video_context(self):
        """Test video context extraction for agent."""
        manager = YouTubeVideoManager()
        
        video_info = VideoInfo(
            title="How to Code in Python - Tutorial",
            description="Learn Python programming basics step by step",
            channel="Code Academy",
            duration="1:23:45",
            url="https://www.youtube.com/watch?v=example"
        )
        
        summary = "This tutorial covers Python basics including variables, functions, and loops."
        
        context = manager.get_video_context(video_info, summary)
        
        assert context["title"] == "How to Code in Python - Tutorial"
        assert context["channel"] == "Code Academy"
        assert context["duration"] == "1:23:45"
        assert context["summary"] == summary
        assert len(context["description"]) <= 300  # Truncated description
    
    def test_get_transcript_context(self):
        """Test transcript context extraction."""
        manager = YouTubeVideoManager()
        
        transcript = VideoTranscript(
            video_id="test123",
            language="en",
            transcript_text="This is a test transcript with multiple sentences. It contains important information.",
            auto_generated=False,
            segments=[{"start": 0, "text": "Hello"}, {"start": 5, "text": "World"}]
        )
        
        context = manager.get_transcript_context(transcript)
        
        assert context["language"] == "en"
        assert not context["auto_generated"]
        assert context["text_length"] > 0
        assert context["has_segments"]
        assert context["segment_count"] == 2
        assert len(context["text_preview"]) <= 500
    
    def test_format_duration(self):
        """Test duration formatting."""
        manager = YouTubeVideoManager()
        
        # Already formatted durations
        assert manager.format_duration("3:45") == "3:45"
        assert manager.format_duration("1:23:45") == "1:23:45"
        
        # Seconds to format
        assert manager.format_duration("225") == "3:45"  # 3 minutes 45 seconds
        assert manager.format_duration("3665") == "1:01:05"  # 1 hour 1 minute 5 seconds
        assert manager.format_duration("45") == "0:45"  # 45 seconds
        
        # Invalid input
        assert manager.format_duration("") == "Unknown"
        assert manager.format_duration("invalid") == "invalid"
    
    def test_create_structured_note_template(self):
        """Test structured note template creation."""
        manager = YouTubeVideoManager()
        
        video_info = VideoInfo(
            video_id="dQw4w9WgXcQ",
            title="Test Video Tutorial",
            description="A test video about learning",
            duration="5:30",
            channel="Test Channel",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
        transcript = VideoTranscript(
            video_id="dQw4w9WgXcQ",
            language="en",
            transcript_text="Hello, this is a test transcript.",
            auto_generated=False
        )
        
        summary = "This video explains testing concepts clearly."
        
        template = manager.create_structured_note_template(video_info, transcript, summary)
        
        assert "# Video: Test Video Tutorial" in template
        assert "Test Channel" in template
        assert "5:30" in template
        assert "## Summary" in template
        assert summary in template
        assert "## Notes" in template
        assert "## Action Items" in template
        assert "#video #youtube" in template
    
    
    def test_format_video_for_agent_response(self):
        """Test video formatting for agent response."""
        manager = YouTubeVideoManager()
        
        video_info = VideoInfo(
            title="Test Video",
            channel="Test Channel",
            duration="300",  # 5 minutes in seconds
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            description="Short description"
        )
        
        summary = "This is a test summary."
        
        response = manager.format_video_for_agent_response(video_info, summary)
        
        assert "**Test Video**" in response
        assert "Test Channel" in response
        assert "5:00" in response  # Formatted duration
        assert "**Summary:**" in response
        assert summary in response
        assert "**Description:**" in response


@pytest.mark.integration
class TestYouTubeIntegration:
    """Integration tests for YouTube MCP server (requires internet connection)."""
    
    def test_server_creation(self):
        """Test YouTube MCP server creation."""
        from config.settings import load_config
        
        config = load_config()
        server = create_youtube_mcp_server(config)
        
        assert server is not None
        assert server.command == 'npx'
        assert server.args == ['-y', 'youtube-video-summarizer-mcp']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])