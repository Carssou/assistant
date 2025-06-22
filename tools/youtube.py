"""
YouTube video processing utilities and wrapper functions.

This module provides utility functions for working with YouTube videos
through the MCP server integration, including video summarization,
transcript extraction, and coordination with other productivity tools.
"""

import logging
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Structured video information."""
    
    video_id: str = ""
    title: str = ""
    description: str = ""
    duration: str = ""
    channel: str = ""
    upload_date: Optional[str] = None
    view_count: Optional[str] = None
    url: str = ""
    thumbnail_url: str = ""
    
    def __post_init__(self):
        # Clean and validate data
        self.title = self.title.strip()
        self.description = self.description.strip()
        self.channel = self.channel.strip()


@dataclass
class VideoTranscript:
    """Structured video transcript information."""
    
    video_id: str = ""
    language: str = "en"
    transcript_text: str = ""
    segments: List[Dict[str, Any]] = None
    auto_generated: bool = False
    
    def __post_init__(self):
        if self.segments is None:
            self.segments = []


class YouTubeVideoManager:
    """
    High-level video management utilities for YouTube integration.
    
    This class provides convenient methods for common video operations
    that can be used by the PydanticAI agent through MCP tools.
    """
    
    def __init__(self, default_language: str = "en"):
        """
        Initialize the video manager.
        
        Args:
            default_language: Default language for transcripts
        """
        self.default_language = default_language
        
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.
        
        Args:
            url: YouTube URL in various formats
            
        Returns:
            Video ID or None if not found
        """
        # Remove whitespace
        url = url.strip()
        
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/.*[?&]v=([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def validate_youtube_url(self, url: str) -> bool:
        """
        Validate if URL is a valid YouTube URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid YouTube URL
        """
        video_id = self.extract_video_id(url)
        return video_id is not None
    
    def normalize_youtube_url(self, url: str) -> Optional[str]:
        """
        Normalize YouTube URL to standard format.
        
        Args:
            url: YouTube URL in any format
            
        Returns:
            Normalized YouTube URL or None if invalid
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            return None
        
        return f"https://www.youtube.com/watch?v={video_id}"
    
    def create_video_summary_note(self, video_info: VideoInfo, 
                                transcript: VideoTranscript,
                                summary: str,
                                key_points: List[str] = None) -> str:
        """
        Create a formatted note from video summary.
        
        Args:
            video_info: Video information
            transcript: Video transcript
            summary: Generated summary
            key_points: List of key points
            
        Returns:
            Formatted markdown content for notes
        """
        if key_points is None:
            key_points = []
        
        content = f"# Video Summary: {video_info.title}\n\n"
        
        # Video metadata
        content += "## Video Information\n\n"
        content += f"**Channel:** {video_info.channel}\n"
        content += f"**Duration:** {video_info.duration}\n"
        content += f"**URL:** {video_info.url}\n"
        if video_info.upload_date:
            content += f"**Upload Date:** {video_info.upload_date}\n"
        if video_info.view_count:
            content += f"**Views:** {video_info.view_count}\n"
        content += f"**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Summary
        content += "## Summary\n\n"
        content += f"{summary}\n\n"
        
        # Key points
        if key_points:
            content += "## Key Points\n\n"
            for point in key_points:
                content += f"- {point}\n"
            content += "\n"
        
        # Video description (if not too long)
        if video_info.description and len(video_info.description) < 500:
            content += "## Video Description\n\n"
            content += f"{video_info.description}\n\n"
        
        # Transcript information
        if transcript.transcript_text:
            content += "## Transcript Information\n\n"
            content += f"**Language:** {transcript.language}\n"
            content += f"**Auto-generated:** {'Yes' if transcript.auto_generated else 'No'}\n"
            content += f"**Length:** {len(transcript.transcript_text)} characters\n\n"
            
            # Include excerpt of transcript (first 300 chars)
            if len(transcript.transcript_text) > 300:
                content += "### Transcript Excerpt\n\n"
                content += f"{transcript.transcript_text[:300]}...\n\n"
        
        # Tags for organization
        content += "## Tags\n\n"
        content += f"#video #youtube #summary #{video_info.channel.replace(' ', '-').lower()}\n"
        
        return content
    
    def extract_key_points_from_summary(self, summary: str) -> List[str]:
        """
        Extract key points from a video summary.
        
        Args:
            summary: Video summary text
            
        Returns:
            List of key points
        """
        key_points = []
        
        # Look for bullet points or numbered lists
        lines = summary.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check for bullet points or numbered items
            if (line.startswith('- ') or line.startswith('* ') or 
                re.match(r'^\d+\.\s', line)):
                # Extract the point without the marker
                point = re.sub(r'^[-*]\s*|\d+\.\s*', '', line).strip()
                if len(point) > 10:  # Only substantial points
                    key_points.append(point)
        
        # If no structured points found, look for sentences with key indicators
        if not key_points:
            sentences = summary.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if any(keyword in sentence.lower() for keyword in 
                      ['important', 'key', 'main', 'significant', 'crucial', 'essential']):
                    if len(sentence) > 20:
                        key_points.append(sentence)
        
        return key_points[:8]  # Limit to 8 key points
    
    def get_video_context(self, video_info: VideoInfo, summary: str) -> Dict[str, str]:
        """
        Provide context about the video for the agent to make intelligent decisions.
        
        Args:
            video_info: Video information
            summary: Video summary
            
        Returns:
            Structured context for agent decision-making
        """
        return {
            "title": video_info.title,
            "channel": video_info.channel,
            "duration": video_info.duration,
            "description": video_info.description[:300],  # First 300 chars
            "summary": summary,
            "url": video_info.url
        }
    
    def create_structured_note_template(self, video_info: VideoInfo, 
                                       transcript: VideoTranscript,
                                       summary: str) -> str:
        """
        Create a structured note template that the agent can customize.
        
        Args:
            video_info: Video information
            transcript: Video transcript
            summary: Video summary
            
        Returns:
            Basic structured template for agent enhancement
        """
        template = f"# Video: {video_info.title}\n\n"
        template += f"**Channel:** {video_info.channel}\n"
        template += f"**Duration:** {self.format_duration(video_info.duration)}\n"
        template += f"**URL:** {video_info.url}\n"
        template += f"**Date Processed:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        template += f"## Summary\n\n{summary}\n\n"
        template += f"## Notes\n\n[Agent will add key insights and takeaways here]\n\n"
        template += f"## Action Items\n\n[Agent will suggest relevant follow-up actions]\n\n"
        template += f"## Tags\n\n#video #youtube\n"
        
        return template
    
    def format_duration(self, duration_str: str) -> str:
        """
        Format video duration for display.
        
        Args:
            duration_str: Duration string from API
            
        Returns:
            Formatted duration string
        """
        if not duration_str:
            return "Unknown"
        
        # If already formatted (HH:MM:SS or MM:SS), return as-is
        if ':' in duration_str:
            return duration_str
        
        # If it's a number of seconds
        try:
            total_seconds = int(duration_str)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        except (ValueError, TypeError):
            return duration_str
    
    
    def get_transcript_context(self, transcript: VideoTranscript) -> Dict[str, Any]:
        """
        Provide transcript context for agent analysis.
        
        Args:
            transcript: Video transcript
            
        Returns:
            Structured transcript information
        """
        return {
            "language": transcript.language,
            "auto_generated": transcript.auto_generated,
            "text_length": len(transcript.transcript_text),
            "text_preview": transcript.transcript_text[:500] if transcript.transcript_text else "",
            "has_segments": bool(transcript.segments),
            "segment_count": len(transcript.segments) if transcript.segments else 0
        }
    
    def format_video_for_agent_response(self, video_info: VideoInfo,
                                      summary: str = None) -> str:
        """
        Format video information for agent response.
        
        Args:
            video_info: Video information
            summary: Optional summary text
            
        Returns:
            Formatted response text
        """
        response = f"**{video_info.title}**\n"
        response += f"Channel: {video_info.channel}\n"
        response += f"Duration: {self.format_duration(video_info.duration)}\n"
        response += f"URL: {video_info.url}\n\n"
        
        if summary:
            response += f"**Summary:**\n{summary}\n\n"
        
        if video_info.description and len(video_info.description) < 200:
            response += f"**Description:**\n{video_info.description}\n"
        
        return response