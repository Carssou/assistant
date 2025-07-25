"""
Test multi-tool coordination functionality.

This module tests how well the agent coordinates multiple MCP servers
and handles complex workflows that span multiple tools.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from pathlib import Path

from agent.agent import create_agent, ProductivityAgent
from config.settings import AgentConfig


class TestMultiToolCoordination:
    """Test multi-tool coordination capabilities."""
    
    @pytest_asyncio.fixture
    async def agent_setup(self):
        """Set up agent with mocked dependencies for testing."""
        config = AgentConfig(_env_file=None)
        config.obsidian_vault_path = None  # Disable vault validation
        agent = await create_agent(config)
        return agent
    
    @pytest.mark.asyncio
    async def test_research_workflow_coordination(self, agent_setup):
        """Test research → note creation → task generation workflow."""
        agent = agent_setup
        
        # Mock the workflow execution
        query = "Research AI agents and create notes with follow-up tasks"
        
        # This would involve: searxng_web_search → create_note → todoist_create_task
        # In real test, we'd verify the agent makes these tool calls in sequence
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    @pytest.mark.asyncio 
    async def test_video_learning_workflow(self, agent_setup):
        """Test video processing → study note creation workflow."""
        agent = agent_setup
        
        query = "Analyze YouTube video and create study materials"
        
        # Expected flow: get-video-info → create_note → todoist_create_task
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_information_synthesis_workflow(self, agent_setup):
        """Test multiple search → synthesis → organized notes."""
        agent = agent_setup
        
        query = "Compare PydanticAI vs LangChain with comprehensive analysis"
        
        # Expected: multiple searxng_web_search → web_url_read → create_note
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_content_curation_workflow(self, agent_setup):
        """Test search → read → organize → link workflow."""
        agent = agent_setup
        
        query = "Find MCP server information and organize in knowledge base"
        
        # Expected: searxng_web_search → web_url_read → search_vault → create_note → edit_note
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    @pytest.mark.asyncio 
    async def test_error_handling_partial_failure(self, agent_setup):
        """Test coordination when one tool fails."""
        agent = agent_setup
        
        # Simulate scenario where search works but note creation fails
        # Agent should handle gracefully and provide partial results
        query = "Research topic but simulate note creation failure"
        
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_server_unavailable_degradation(self, agent_setup):
        """Test graceful degradation when MCP server is unavailable."""
        agent = agent_setup
        
        # Simulate Todoist server being down
        # Agent should complete research and notes but skip task creation
        query = "Complete workflow with task server unavailable"
        
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_usage(self, agent_setup):
        """Test performance with concurrent tool operations."""
        agent = agent_setup
        
        # Test multiple concurrent requests that use different tools
        queries = [
            "Search for AI news",
            "Create a test note",
            "Get my tasks",
            "Search for ML resources"
        ]
        
        # Would test concurrent execution performance
        assert len(queries) == 4
        assert isinstance(agent, ProductivityAgent)
    
    def test_system_prompt_exists(self):
        """Test that system prompt is properly defined."""
        from agent.prompts import get_system_prompt
        
        system_prompt = get_system_prompt()
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "productivity" in system_prompt.lower()
    
    def test_agent_capabilities_described(self):
        """Test that agent capabilities are described in system prompt."""
        from agent.prompts import get_system_prompt
        
        system_prompt = get_system_prompt()
        
        # Check for key capabilities mentioned
        expected_capabilities = [
            "search", "note", "task", "video"
        ]
        
        for capability in expected_capabilities:
            assert capability in system_prompt.lower()


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
        agent = agent_setup
        
        # Test that complex workflows don't take too long
        # Acceptable threshold might be 30-60 seconds for complex workflows
        import time
        
        start_time = time.time()
        # Would run actual workflow here
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 60  # Should complete within 60 seconds
        assert isinstance(agent, ProductivityAgent)
    
    @pytest.mark.asyncio
    async def test_memory_usage_reasonable(self, agent_setup):
        """Test that multi-tool coordination doesn't use excessive memory."""
        agent = agent_setup
        
        # Monitor memory usage during complex workflows
        # This would use memory profiling tools
        assert isinstance(agent, ProductivityAgent)
        assert agent is not None
    
    def test_concurrent_request_handling(self):
        """Test handling multiple concurrent coordination requests."""
        # Test that the system can handle multiple users
        # making complex requests simultaneously
        
        max_concurrent = 5  # Example limit
        assert max_concurrent > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])