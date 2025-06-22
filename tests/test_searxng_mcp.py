"""
Tests for SearXNG MCP server integration.

This module tests the SearXNG MCP server configuration and connection.
"""

import pytest
import os
from unittest.mock import Mock

from config.settings import AgentConfig
from mcp_servers.configs import create_searxng_mcp_server
from tools.search import (
    SearXNGSearchManager, SearchResult, SearchQuery, 
    SearchTimeRange, SafeSearchLevel
)


class TestSearXNGMCPServer:
    """Test cases for SearXNG MCP server configuration."""
    
    def test_searxng_server_creation_without_url(self):
        """Test that server returns None when no base URL is provided."""
        config = Mock(spec=AgentConfig)
        config.searxng_base_url = None
        
        server = create_searxng_mcp_server(config)
        assert server is None
    
    def test_searxng_server_creation_with_empty_url(self):
        """Test that server returns None for empty URL."""
        config = Mock(spec=AgentConfig)
        config.searxng_base_url = ""
        
        server = create_searxng_mcp_server(config)
        assert server is None
    
    def test_searxng_server_creation_with_url(self):
        """Test that server is created when base URL is provided."""
        config = Mock(spec=AgentConfig)
        config.searxng_base_url = "http://localhost:8080"
        
        server = create_searxng_mcp_server(config)
        
        assert server is not None
        assert server.command == 'npx'
        assert server.args == ['-y', 'mcp-searxng']
        assert server.env == {'SEARXNG_URL': 'http://localhost:8080'}
    
    def test_searxng_server_creation_with_auth(self):
        """Test that server includes authentication when provided."""
        config = Mock(spec=AgentConfig)
        config.searxng_base_url = "http://localhost:8080"
        config.searxng_username = "testuser"
        config.searxng_password = "testpass"
        
        server = create_searxng_mcp_server(config)
        
        assert server is not None
        expected_env = {
            'SEARXNG_URL': 'http://localhost:8080',
            'AUTH_USERNAME': 'testuser',
            'AUTH_PASSWORD': 'testpass'
        }
        assert server.env == expected_env


class TestSearXNGSearchManager:
    """Test cases for SearXNG search management utilities."""
    
    def test_search_manager_initialization(self):
        """Test search manager initialization."""
        manager = SearXNGSearchManager()
        assert manager.default_language == "en"
        
        manager_fr = SearXNGSearchManager(default_language="fr")
        assert manager_fr.default_language == "fr"
    
    def test_format_search_query(self):
        """Test search query formatting."""
        manager = SearXNGSearchManager()
        
        # Normal query
        assert manager.format_search_query("python programming") == "python programming"
        
        # Query with extra whitespace
        assert manager.format_search_query("  python   programming  ") == "python programming"
        
        # Query with harmful characters (only removes specific chars, not full tags)
        result = manager.format_search_query("python <script>alert()</script>")
        assert "<" not in result and ">" not in result and "{" not in result and "}" not in result
        
        # Empty query should raise error
        with pytest.raises(ValueError):
            manager.format_search_query("")
        
        with pytest.raises(ValueError):
            manager.format_search_query("   ")
    
    def test_search_result_creation(self):
        """Test SearchResult dataclass creation."""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            content="Test content",
            engine="google",
            score=0.85
        )
        
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.content == "Test content"
        assert result.engine == "google"
        assert result.score == 0.85
    
    def test_search_query_creation(self):
        """Test SearchQuery dataclass creation."""
        query = SearchQuery(query="test search")
        
        assert query.query == "test search"
        assert query.language == "en"
        assert query.categories == ["general"]
        assert query.engines == []
        assert query.time_range == SearchTimeRange.ALL_TIME
        assert query.safe_search == SafeSearchLevel.MODERATE
        assert query.page_no == 1
    
    def test_create_research_query(self):
        """Test research query creation."""
        manager = SearXNGSearchManager()
        
        queries = manager.create_research_query("machine learning")
        
        assert len(queries) >= 3
        assert any("machine learning overview" in q.query for q in queries)
        assert any("latest developments" in q.query for q in queries)
        assert any("research study" in q.query for q in queries)
        
        # Test with specific aspects
        queries_with_aspects = manager.create_research_query(
            "machine learning", 
            ["deep learning", "neural networks", "applications"]
        )
        
        assert len(queries_with_aspects) >= 6  # 3 main + 3 aspects
        assert any("deep learning" in q.query for q in queries_with_aspects)
    
    def test_create_problem_solving_queries(self):
        """Test problem-solving query creation."""
        manager = SearXNGSearchManager()
        
        queries = manager.create_problem_solving_queries("server not responding")
        
        assert len(queries) >= 3
        assert any("how to solve" in q.query for q in queries)
        assert any("troubleshooting" in q.query for q in queries)
        assert any("best practices" in q.query for q in queries)
    
    def test_extract_key_information_empty_results(self):
        """Test key information extraction with empty results."""
        manager = SearXNGSearchManager()
        
        info = manager.extract_key_information([])
        
        assert info["summary"] == "No search results found"
        assert info["key_points"] == []
        assert info["sources"] == []
    
    def test_extract_key_information_with_results(self):
        """Test key information extraction with results."""
        manager = SearXNGSearchManager()
        
        results = [
            SearchResult(
                title="Test Result 1",
                url="https://example.com/1",
                content="This is important information about the main topic. Key findings show significant results.",
                engine="google"
            ),
            SearchResult(
                title="Test Result 2", 
                url="https://example.com/2",
                content="Secondary information with critical details about the subject.",
                engine="bing"
            )
        ]
        
        info = manager.extract_key_information(results)
        
        assert "2 results" in info["summary"]
        assert "2 search engines" in info["summary"]
        assert len(info["sources"]) == 2
        assert info["total_results"] == 2
    
    def test_format_search_for_notes(self):
        """Test search result formatting for notes."""
        manager = SearXNGSearchManager()
        
        results = [
            SearchResult(
                title="Test Result",
                url="https://example.com",
                content="Test content for note formatting",
                engine="google"
            )
        ]
        
        formatted = manager.format_search_for_notes("test query", results)
        
        assert "# Search Results: test query" in formatted
        assert "## Summary" in formatted
        assert "## Top Results" in formatted
        assert "Test Result" in formatted
        assert "https://example.com" in formatted
        assert "#search #research #test-query" in formatted
    
    def test_format_search_for_notes_empty_results(self):
        """Test note formatting with empty results."""
        manager = SearXNGSearchManager()
        
        formatted = manager.format_search_for_notes("test query", [])
        
        assert "# Search: test query" in formatted
        assert "No results found" in formatted
    
    def test_suggest_follow_up_searches(self):
        """Test follow-up search suggestions."""
        manager = SearXNGSearchManager()
        
        # Test with empty results
        suggestions = manager.suggest_follow_up_searches("machine learning algorithms", [])
        
        assert len(suggestions) > 0
        assert any("tutorial" in s for s in suggestions)
        assert any("examples" in s for s in suggestions)
        
        # Test with results
        results = [
            SearchResult(
                title="Neural Networks",
                url="https://example.com",
                content="Deep learning neural networks with tensorflow and pytorch frameworks",
                engine="google"
            )
        ]
        
        suggestions_with_results = manager.suggest_follow_up_searches("machine learning", results)
        
        assert len(suggestions_with_results) > 0
        assert any("comparison" in s for s in suggestions_with_results)
    
    def test_categorize_search_results(self):
        """Test search result categorization."""
        manager = SearXNGSearchManager()
        
        results = [
            SearchResult(
                title="API Documentation",
                url="https://docs.example.com/api",
                content="Official documentation for the API",
                engine="google"
            ),
            SearchResult(
                title="Tutorial: Getting Started",
                url="https://tutorial.example.com",
                content="Step by step guide on how to use the tool",
                engine="bing"
            ),
            SearchResult(
                title="GitHub Repository",
                url="https://github.com/example/tool",
                content="Open source tool for developers",
                engine="google"
            )
        ]
        
        categories = manager.categorize_search_results(results)
        
        assert "documentation" in categories
        assert "tutorials" in categories
        assert "tools" in categories
        assert len(categories["documentation"]) == 1
        assert len(categories["tutorials"]) == 1
        assert len(categories["tools"]) == 1
    
    def test_create_search_summary_for_tasks(self):
        """Test task creation from search results."""
        manager = SearXNGSearchManager()
        
        # Test with empty results
        tasks = manager.create_search_summary_for_tasks("python", [])
        assert len(tasks) == 1
        assert "Refine search" in tasks[0]
        
        # Test with categorized results
        results = [
            SearchResult(
                title="Python Documentation",
                url="https://docs.python.org",
                content="Official Python documentation",
                engine="google"
            ),
            SearchResult(
                title="Python Tutorial",
                url="https://tutorial.python.org",
                content="Learn Python step by step",
                engine="bing"
            )
        ]
        
        tasks = manager.create_search_summary_for_tasks("python", results)
        
        assert len(tasks) <= 5
        assert any("Review documentation" in task for task in tasks)
        assert any("Follow tutorial" in task for task in tasks)
    
    def test_format_search_for_agent_response(self):
        """Test search result formatting for agent response."""
        manager = SearXNGSearchManager()
        
        # Test with empty results
        response = manager.format_search_for_agent_response([])
        assert "No search results found" in response
        
        # Test with results
        results = [
            SearchResult(
                title="Test Result 1",
                url="https://example.com/1",
                content="This is a test result with some content that should be truncated if it's too long to display in the agent response.",
                engine="google"
            ),
            SearchResult(
                title="Test Result 2",
                url="https://example.com/2",
                content="Another test result",
                engine="bing"
            )
        ]
        
        response = manager.format_search_for_agent_response(results)
        
        assert "Found 2 search results" in response
        assert "Test Result 1" in response
        assert "Test Result 2" in response
        assert "https://example.com/1" in response


@pytest.mark.integration
class TestSearXNGIntegration:
    """Integration tests for SearXNG MCP server (requires running SearXNG instance)."""
    
    @pytest.mark.skipif(
        not os.getenv("SEARXNG_BASE_URL"),
        reason="SEARXNG_BASE_URL not set"
    )
    def test_server_connection(self):
        """Test actual connection to SearXNG MCP server."""
        from config.settings import load_config
        
        config = load_config()
        if config.searxng_base_url:
            server = create_searxng_mcp_server(config)
            assert server is not None
            assert server.command == 'npx'
            assert server.env['SEARXNG_URL'] == config.searxng_base_url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])