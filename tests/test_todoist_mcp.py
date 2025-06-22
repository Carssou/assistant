"""
Tests for Todoist MCP server integration.

This module tests the Todoist MCP server configuration and connection.
"""

import pytest
import os
from unittest.mock import Mock

from config.settings import AgentConfig
from mcp_servers.configs import create_todoist_mcp_server
from tools.tasks import TodoistTaskManager, TaskInfo, TaskPriority


class TestTodoistMCPServer:
    """Test cases for Todoist MCP server configuration."""
    
    def test_todoist_server_creation_without_token(self):
        """Test that server returns None when no API token is provided."""
        config = Mock(spec=AgentConfig)
        config.todoist_api_token = None
        
        server = create_todoist_mcp_server(config)
        assert server is None
    
    def test_todoist_server_creation_with_token(self):
        """Test that server is created when API token is provided."""
        config = Mock(spec=AgentConfig)
        config.todoist_api_token = "test_token_123"
        
        server = create_todoist_mcp_server(config)
        
        assert server is not None
        assert server.command == 'npx'
        assert server.args == ['-y', '@abhiz123/todoist-mcp-server']
        assert server.env == {'TODOIST_API_TOKEN': 'test_token_123'}
    
    def test_todoist_server_creation_with_empty_token(self):
        """Test that server returns None for empty token."""
        config = Mock(spec=AgentConfig)
        config.todoist_api_token = ""
        
        server = create_todoist_mcp_server(config)
        assert server is None


class TestTodoistTaskManager:
    """Test cases for Todoist task management utilities."""
    
    def test_task_manager_initialization(self):
        """Test task manager initialization."""
        manager = TodoistTaskManager()
        assert manager.default_project_id is None
        
        manager_with_project = TodoistTaskManager(default_project_id="123")
        assert manager_with_project.default_project_id == "123"
    
    def test_format_task_title(self):
        """Test task title formatting."""
        manager = TodoistTaskManager()
        
        # Normal title
        assert manager.format_task_title("Test Task") == "Test Task"
        
        # Title with extra whitespace
        assert manager.format_task_title("  Test Task  ") == "Test Task"
        
        # Long title (should be truncated)
        long_title = "A" * 250
        formatted = manager.format_task_title(long_title)
        assert len(formatted) == 200
        assert formatted.endswith("...")
        
        # Empty title should raise error
        with pytest.raises(ValueError):
            manager.format_task_title("")
    
    def test_format_due_date(self):
        """Test due date formatting."""
        manager = TodoistTaskManager()
        
        # None input
        assert manager.format_due_date(None) is None
        
        # Valid date formats
        assert manager.format_due_date("2024-01-15") == "2024-01-15"
        assert manager.format_due_date("01/15/2024") == "2024-01-15"
        
        # Invalid format (should return as-is)
        assert manager.format_due_date("tomorrow") == "tomorrow"
    
    def test_prioritize_task(self):
        """Test task priority suggestion."""
        manager = TodoistTaskManager()
        
        # Urgent task
        assert manager.prioritize_task("URGENT fix the bug") == TaskPriority.URGENT
        assert manager.prioritize_task("Critical system failure") == TaskPriority.URGENT
        
        # High priority task
        assert manager.prioritize_task("Important meeting") == TaskPriority.HIGH
        assert manager.prioritize_task("Deadline tomorrow") == TaskPriority.HIGH
        
        # Low priority task
        assert manager.prioritize_task("Someday maybe task") == TaskPriority.LOW
        assert manager.prioritize_task("Optional nice to have") == TaskPriority.LOW
        
        # Normal priority task
        assert manager.prioritize_task("Regular task") == TaskPriority.NORMAL
    
    def test_suggest_labels_for_task(self):
        """Test label suggestion for tasks."""
        manager = TodoistTaskManager()
        
        # Meeting-related task
        labels = manager.suggest_labels_for_task("Schedule team meeting")
        assert "meeting" in labels
        
        # Research task
        labels = manager.suggest_labels_for_task("Research new framework")
        assert "research" in labels
        
        # Communication task
        labels = manager.suggest_labels_for_task("Send email to client")
        assert "communication" in labels
        
        # Multiple labels
        labels = manager.suggest_labels_for_task("Research and write meeting notes")
        assert len(labels) <= 3  # Should limit to 3 labels
    
    def test_parse_natural_language_task(self):
        """Test parsing natural language task descriptions."""
        manager = TodoistTaskManager()
        
        # Basic task
        task = manager.parse_natural_language_task("Buy groceries")
        assert task.title == "Buy groceries"
        assert task.priority == TaskPriority.NORMAL
        
        # Task with due date
        task = manager.parse_natural_language_task("Submit report due 2024-01-15")
        assert "Submit report" in task.title
        assert task.due_date == "2024-01-15"
        
        # Urgent task
        task = manager.parse_natural_language_task("URGENT: Fix production bug")
        assert task.priority == TaskPriority.URGENT
        
        # Task with relative date
        task = manager.parse_natural_language_task("Call client tomorrow")
        assert task.due_date == "tomorrow"
    
    def test_create_task_from_note_content(self):
        """Test extracting tasks from note content."""
        manager = TodoistTaskManager()
        
        note_content = """
        Meeting Notes:
        - [ ] Follow up with John
        - [ ] Review proposal
        TODO: Schedule next meeting
        Action: Send meeting notes to team
        """
        
        tasks = manager.create_task_from_note_content(note_content, "Team Meeting")
        
        assert len(tasks) == 4
        assert any("Follow up with John" in task.title for task in tasks)
        assert any("Review proposal" in task.title for task in tasks)
        assert any("Schedule next meeting" in task.title for task in tasks)
        assert any("Send meeting notes to team" in task.title for task in tasks)
        
        # All tasks should have the note reference
        for task in tasks:
            assert "from-notes" in task.labels
            assert "Team Meeting" in task.description
    
    def test_create_research_tasks(self):
        """Test creating research follow-up tasks."""
        manager = TodoistTaskManager()
        
        findings = [
            "Framework X has better performance",
            "Library Y is more popular",
            "Tool Z requires more setup",
            "Option A is cheaper",  # This should be excluded (limit 3)
        ]
        
        tasks = manager.create_research_tasks("Web Framework Comparison", findings)
        
        assert len(tasks) == 4  # 1 main + 3 follow-ups
        
        # Main task
        main_task = tasks[0]
        assert "Review research findings" in main_task.title
        assert "research" in main_task.labels
        
        # Follow-up tasks
        follow_up_tasks = tasks[1:]
        assert len(follow_up_tasks) == 3
        for task in follow_up_tasks:
            assert "follow-up" in task.labels
            assert "research" in task.labels
    
    def test_create_video_learning_tasks(self):
        """Test creating learning tasks from video content."""
        manager = TodoistTaskManager()
        
        key_points = [
            "Use dependency injection for better testability",
            "Implement proper error handling patterns",
            "Consider performance implications of async code"
        ]
        
        tasks = manager.create_video_learning_tasks(
            "Advanced Python Patterns",
            "https://youtube.com/watch?v=example",
            key_points
        )
        
        assert len(tasks) == 3  # 1 review + 2 practice tasks
        
        # Review task
        review_task = tasks[0]
        assert "Review video notes" in review_task.title
        assert "learning" in review_task.labels
        assert "video" in review_task.labels
        
        # Practice tasks
        practice_tasks = tasks[1:]
        assert len(practice_tasks) == 2
        for task in practice_tasks:
            assert "Practice:" in task.title
            assert "practice" in task.labels
    
    def test_format_task_for_creation(self):
        """Test formatting task data for API creation."""
        manager = TodoistTaskManager(default_project_id="default_123")
        
        task_info = TaskInfo(
            title="Test Task",
            description="Test description",
            due_date="2024-01-15",
            priority=TaskPriority.HIGH,
            labels=["test", "example"]
        )
        
        formatted = manager.format_task_for_creation(task_info)
        
        assert formatted["title"] == "Test Task"
        assert formatted["description"] == "Test description"
        assert formatted["due_date"] == "2024-01-15"
        assert formatted["priority"] == TaskPriority.HIGH.value
        assert formatted["project_id"] == "default_123"
        assert formatted["labels"] == ["test", "example"]
    
    def test_format_task_for_creation_minimal(self):
        """Test formatting minimal task data."""
        manager = TodoistTaskManager()
        
        task_info = TaskInfo(title="Simple Task")
        formatted = manager.format_task_for_creation(task_info)
        
        assert formatted["title"] == "Simple Task"
        assert "description" not in formatted
        assert "due_date" not in formatted
        assert "priority" not in formatted  # Normal priority not included
        assert "project_id" not in formatted
        assert "labels" not in formatted


@pytest.mark.integration
class TestTodoistIntegration:
    """Integration tests for Todoist MCP server (requires real API token)."""
    
    @pytest.mark.skipif(
        not os.getenv("TODOIST_API_TOKEN"),
        reason="TODOIST_API_TOKEN not set"
    )
    def test_server_connection(self):
        """Test actual connection to Todoist MCP server."""
        # This test would require actual MCP server testing
        # For now, just test that configuration is valid
        from config.settings import load_config
        
        config = load_config()
        if config.todoist_api_token:
            server = create_todoist_mcp_server(config)
            assert server is not None
            assert server.command == 'npx'
            assert server.env['TODOIST_API_TOKEN'] == config.todoist_api_token


if __name__ == "__main__":
    pytest.main([__file__, "-v"])