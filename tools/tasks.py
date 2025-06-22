"""
Todoist task management utilities and wrapper functions.

This module provides utility functions for working with Todoist tasks
through the MCP server integration, including task creation, management,
and coordination with other productivity tools.
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskPriority(int, Enum):
    """Todoist task priority levels."""
    
    LOW = 1
    NORMAL = 2  
    HIGH = 3
    URGENT = 4


@dataclass
class TaskInfo:
    """Structured task information."""
    
    id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    project_id: Optional[str] = None
    labels: List[str] = None
    completed: bool = False
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class TodoistTaskManager:
    """
    High-level task management utilities for Todoist integration.
    
    This class provides convenient methods for common task operations
    that can be used by the PydanticAI agent through MCP tools.
    """
    
    def __init__(self, default_project_id: Optional[str] = None):
        """
        Initialize the task manager.
        
        Args:
            default_project_id: Default project for new tasks
        """
        self.default_project_id = default_project_id
        
    def format_task_title(self, title: str) -> str:
        """
        Format and clean task title.
        
        Args:
            title: Raw task title
            
        Returns:
            Cleaned and formatted task title
        """
        # Remove extra whitespace and ensure proper capitalization
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
            
        # Ensure title doesn't exceed reasonable length
        if len(title) > 200:
            title = title[:197] + "..."
            
        return title
    
    def format_due_date(self, due_date: Optional[str]) -> Optional[str]:
        """
        Format due date for Todoist API.
        
        Args:
            due_date: Due date in various formats
            
        Returns:
            Formatted due date string or None
        """
        if not due_date:
            return None
            
        # If it's already a proper date string, return as-is
        if isinstance(due_date, str):
            # Handle common date formats
            try:
                # Try parsing common formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        parsed_date = datetime.strptime(due_date, fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
                        
                # If no format matches, return as-is (let Todoist handle it)
                return due_date
            except Exception:
                logger.warning(f"Could not parse due date: {due_date}")
                return due_date
                
        return str(due_date)
    
    def create_task_from_note_content(self, note_content: str, note_title: str) -> List[TaskInfo]:
        """
        Extract actionable tasks from note content.
        
        Args:
            note_content: Content of the note
            note_title: Title of the note
            
        Returns:
            List of extracted task information
        """
        tasks = []
        
        # Look for action items in common formats
        action_patterns = [
            "- [ ]",  # Markdown checkbox
            "TODO:",  # Explicit TODO
            "Action:",  # Action item
            "Next:",  # Next steps
        ]
        
        lines = note_content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check if line contains action patterns
            for pattern in action_patterns:
                if pattern in line:
                    # Extract task title
                    task_title = line.replace(pattern, "").strip()
                    if task_title:
                        task = TaskInfo(
                            title=task_title,
                            description=f"From note: {note_title}",
                            labels=["from-notes"]
                        )
                        tasks.append(task)
                    break
                    
        return tasks
    
    def create_research_tasks(self, topic: str, findings: List[str]) -> List[TaskInfo]:
        """
        Create follow-up tasks from research findings.
        
        Args:
            topic: Research topic
            findings: List of key findings
            
        Returns:
            List of research-related tasks
        """
        tasks = []
        
        # Create main follow-up task
        main_task = TaskInfo(
            title=f"Review research findings: {topic}",
            description="Analyze and synthesize research results",
            labels=["research", "review"]
        )
        tasks.append(main_task)
        
        # Create specific follow-up tasks for each finding
        for i, finding in enumerate(findings[:3]):  # Limit to 3 tasks
            task = TaskInfo(
                title=f"Follow up on: {finding[:50]}{'...' if len(finding) > 50 else ''}",
                description=f"Research topic: {topic}\nFinding: {finding}",
                labels=["research", "follow-up"]
            )
            tasks.append(task)
            
        return tasks
    
    def create_video_learning_tasks(self, video_title: str, video_url: str, 
                                  key_points: List[str]) -> List[TaskInfo]:
        """
        Create learning tasks from video content.
        
        Args:
            video_title: Title of the video
            video_url: URL of the video
            key_points: Key learning points
            
        Returns:
            List of learning-related tasks
        """
        tasks = []
        
        # Create main review task
        review_task = TaskInfo(
            title=f"Review video notes: {video_title}",
            description=f"Video: {video_url}\nReview and consolidate learning points",
            labels=["learning", "video", "review"]
        )
        tasks.append(review_task)
        
        # Create practice/application tasks for key points
        for point in key_points[:2]:  # Limit to 2 practice tasks
            if len(point) > 20:  # Only create tasks for substantial points
                task = TaskInfo(
                    title=f"Practice: {point[:40]}{'...' if len(point) > 40 else ''}",
                    description=f"From video: {video_title}\nApply learning: {point}",
                    labels=["learning", "practice", "video"]
                )
                tasks.append(task)
                
        return tasks
    
    def prioritize_task(self, task_title: str, description: str = "") -> TaskPriority:
        """
        Suggest priority level based on task content.
        
        Args:
            task_title: Task title
            description: Task description
            
        Returns:
            Suggested priority level
        """
        content = f"{task_title} {description}".lower()
        
        # Urgent keywords
        urgent_keywords = ["urgent", "asap", "emergency", "critical", "deadline today"]
        if any(keyword in content for keyword in urgent_keywords):
            return TaskPriority.URGENT
            
        # High priority keywords
        high_keywords = ["important", "priority", "deadline", "due soon", "meeting"]
        if any(keyword in content for keyword in high_keywords):
            return TaskPriority.HIGH
            
        # Low priority keywords
        low_keywords = ["someday", "maybe", "nice to have", "optional", "when time permits"]
        if any(keyword in content for keyword in low_keywords):
            return TaskPriority.LOW
            
        return TaskPriority.NORMAL
    
    def format_task_for_creation(self, task_info: TaskInfo) -> Dict[str, Any]:
        """
        Format task information for MCP server creation.
        
        Args:
            task_info: Task information
            
        Returns:
            Formatted task data for API
        """
        task_data = {
            "title": self.format_task_title(task_info.title)
        }
        
        if task_info.description:
            task_data["description"] = task_info.description
            
        if task_info.due_date:
            task_data["due_date"] = self.format_due_date(task_info.due_date)
            
        if task_info.priority != TaskPriority.NORMAL:
            task_data["priority"] = task_info.priority.value
            
        if task_info.project_id or self.default_project_id:
            task_data["project_id"] = task_info.project_id or self.default_project_id
            
        if task_info.labels:
            task_data["labels"] = task_info.labels
            
        return task_data
    
    def parse_natural_language_task(self, text: str) -> TaskInfo:
        """
        Parse natural language into structured task information.
        
        Args:
            text: Natural language task description
            
        Returns:
            Structured task information
        """
        # Extract due date patterns
        import re
        
        due_date = None
        priority = TaskPriority.NORMAL
        
        # Look for date patterns
        date_patterns = [
            r"due (\d{4}-\d{2}-\d{2})",
            r"by (\d{1,2}/\d{1,2}/\d{4})",
            r"deadline (\w+ \d{1,2})",
            r"(today|tomorrow|next week)"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text.lower())
            if match:
                due_date = match.group(1)
                # Remove date from title
                text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                break
        
        # Look for priority indicators
        if any(word in text.lower() for word in ["urgent", "asap", "critical"]):
            priority = TaskPriority.URGENT
        elif any(word in text.lower() for word in ["important", "high priority"]):
            priority = TaskPriority.HIGH
        elif any(word in text.lower() for word in ["low priority", "someday"]):
            priority = TaskPriority.LOW
            
        # Clean up the title
        title = text.strip()
        
        return TaskInfo(
            title=title,
            due_date=due_date,
            priority=priority
        )
    
    def suggest_labels_for_task(self, title: str, description: str = "") -> List[str]:
        """
        Suggest appropriate labels for a task based on content.
        
        Args:
            title: Task title
            description: Task description
            
        Returns:
            List of suggested labels
        """
        content = f"{title} {description}".lower()
        labels = []
        
        # Context-based labels
        if any(word in content for word in ["meeting", "call", "zoom"]):
            labels.append("meeting")
        if any(word in content for word in ["email", "message", "respond"]):
            labels.append("communication")
        if any(word in content for word in ["research", "investigate", "study"]):
            labels.append("research")
        if any(word in content for word in ["write", "document", "draft"]):
            labels.append("writing")
        if any(word in content for word in ["review", "check", "validate"]):
            labels.append("review")
        if any(word in content for word in ["buy", "purchase", "order"]):
            labels.append("shopping")
        if any(word in content for word in ["clean", "organize", "tidy"]):
            labels.append("organizing")
            
        return labels[:3]  # Limit to 3 labels