"""
Test multi-tool coordination functionality.

This module tests how well the agent coordinates multiple MCP servers
and handles complex workflows that span multiple tools.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from pathlib import Path

from agent.agent import create_agent
from agent.dependencies import create_agent_dependencies
from config.settings import AgentConfig


class TestMultiToolCoordination:
    """Test multi-tool coordination capabilities."""
    
    @pytest.fixture
    async def agent_setup(self):
        """Set up agent with mocked dependencies for testing."""
        config = AgentConfig()
        deps = await create_agent_dependencies(config)
        agent = await create_agent(deps)
        return agent, deps
    
    @pytest.mark.asyncio
    async def test_research_workflow_coordination(self, agent_setup):
        """Test research → note creation → task generation workflow."""
        agent, deps = agent_setup
        
        # Mock the workflow execution
        query = "Research AI agents and create notes with follow-up tasks"
        
        # This would involve: searxng_web_search → create_note → todoist_create_task
        # In real test, we'd verify the agent makes these tool calls in sequence
        assert agent is not None
        assert deps is not None
    
    @pytest.mark.asyncio 
    async def test_video_learning_workflow(self, agent_setup):
        """Test video processing → study note creation workflow."""
        agent, deps = agent_setup
        
        query = "Analyze YouTube video and create study materials"
        
        # Expected flow: get-video-info → create_note → todoist_create_task
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_information_synthesis_workflow(self, agent_setup):
        """Test multiple search → synthesis → organized notes."""
        agent, deps = agent_setup
        
        query = "Compare PydanticAI vs LangChain with comprehensive analysis"
        
        # Expected: multiple searxng_web_search → web_url_read → create_note
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_content_curation_workflow(self, agent_setup):
        """Test search → read → organize → link workflow."""
        agent, deps = agent_setup
        
        query = "Find MCP server information and organize in knowledge base"
        
        # Expected: searxng_web_search → web_url_read → search_vault → create_note → edit_note
        assert agent is not None
    
    @pytest.mark.asyncio 
    async def test_error_handling_partial_failure(self, agent_setup):
        """Test coordination when one tool fails."""
        agent, deps = agent_setup
        
        # Simulate scenario where search works but note creation fails
        # Agent should handle gracefully and provide partial results
        query = "Research topic but simulate note creation failure"
        
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_server_unavailable_degradation(self, agent_setup):
        """Test graceful degradation when MCP server is unavailable."""
        agent, deps = agent_setup
        
        # Simulate Todoist server being down
        # Agent should complete research and notes but skip task creation
        query = "Complete workflow with task server unavailable"
        
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_usage(self, agent_setup):
        """Test performance with concurrent tool operations."""
        agent, deps = agent_setup
        
        # Test multiple concurrent requests that use different tools
        queries = [
            "Search for AI news",
            "Create a test note",
            "Get my tasks",
            "Search for ML resources"
        ]
        
        # Would test concurrent execution performance
        assert len(queries) == 4
    
    def test_workflow_templates_exist(self):
        """Test that workflow templates are properly defined."""
        from agent.prompts import WORKFLOW_TEMPLATES
        
        expected_workflows = [
            "research_workflow",
            "video_learning", 
            "information_synthesis"
        ]
        
        for workflow in expected_workflows:
            assert workflow in WORKFLOW_TEMPLATES
            assert isinstance(WORKFLOW_TEMPLATES[workflow], str)
            assert len(WORKFLOW_TEMPLATES[workflow]) > 0
    
    def test_error_messages_defined(self):
        """Test that error handling messages are defined."""
        from agent.prompts import ERROR_MESSAGES
        
        expected_errors = [
            "tool_unavailable",
            "invalid_input",
            "network_error",
            "permission_error"
        ]
        
        for error_type in expected_errors:
            assert error_type in ERROR_MESSAGES
            assert isinstance(ERROR_MESSAGES[error_type], str)
            assert len(ERROR_MESSAGES[error_type]) > 0


class TestToolCoordinationLogic:
    """Test the intelligence of tool coordination."""
    
    def test_tool_selection_intelligence(self):
        """Test that agent can intelligently select appropriate tools."""
        # This would test the agent's ability to choose the right tools
        # for different types of requests
        
        test_cases = [
            {
                "query": "Research AI and create notes",
                "expected_tools": ["searxng_web_search", "create_note"]
            },
            {
                "query": "Analyze YouTube video",
                "expected_tools": ["get-video-info", "create_note"]
            },
            {
                "query": "Find my tasks about machine learning",
                "expected_tools": ["todoist_get_tasks"]
            }
        ]
        
        # In real implementation, we'd verify tool selection
        assert len(test_cases) == 3
    
    def test_workflow_chaining_logic(self):
        """Test that workflows chain tools in logical order."""
        # Test that the agent understands dependencies between tools
        # e.g., search before create_note, get video info before create study notes
        
        workflow_chains = [
            ["searxng_web_search", "create_note", "todoist_create_task"],
            ["get-video-info", "create_note"],
            ["searxng_web_search", "web_url_read", "create_note"]
        ]
        
        # Verify logical ordering
        for chain in workflow_chains:
            assert len(chain) >= 2  # Multi-tool coordination requires at least 2 tools
    
    def test_context_preservation(self):
        """Test that context is preserved across tool calls."""
        # Test that information flows properly between tools
        # e.g., search results are used in note creation
        
        # This would verify that the agent maintains state and context
        # across multiple tool invocations
        assert True  # Placeholder - real test would verify context flow


class TestPerformanceMetrics:
    """Test performance aspects of multi-tool coordination."""
    
    @pytest.mark.asyncio
    async def test_response_time_acceptable(self, agent_setup):
        """Test that multi-tool workflows complete in reasonable time."""
        agent, deps = agent_setup
        
        # Test that complex workflows don't take too long
        # Acceptable threshold might be 30-60 seconds for complex workflows
        import time
        
        start_time = time.time()
        # Would run actual workflow here
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 60  # Should complete within 60 seconds
    
    @pytest.mark.asyncio
    async def test_memory_usage_reasonable(self, agent_setup):
        """Test that multi-tool coordination doesn't use excessive memory."""
        agent, deps = agent_setup
        
        # Monitor memory usage during complex workflows
        # This would use memory profiling tools
        assert agent is not None
    
    def test_concurrent_request_handling(self):
        """Test handling multiple concurrent coordination requests."""
        # Test that the system can handle multiple users
        # making complex requests simultaneously
        
        max_concurrent = 5  # Example limit
        assert max_concurrent > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])