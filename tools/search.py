"""
Web search utilities and wrapper functions.

This module provides utility functions for working with web search
through the SearXNG MCP server integration, including search result
processing and coordination with other productivity tools.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, date

logger = logging.getLogger(__name__)


class SearchTimeRange(str, Enum):
    """Time range filters for search results."""
    
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL_TIME = "all"


class SafeSearchLevel(str, Enum):
    """Safe search levels for content filtering."""
    
    STRICT = "2"
    MODERATE = "1" 
    OFF = "0"


@dataclass
class SearchResult:
    """Structured search result information."""
    
    title: str = ""
    url: str = ""
    content: str = ""
    engine: str = ""
    score: float = 0.0
    category: str = ""
    published_date: Optional[str] = None
    
    def __post_init__(self):
        # Clean and validate data
        self.title = self.title.strip()
        self.url = self.url.strip()
        self.content = self.content.strip()


@dataclass
class SearchQuery:
    """Structured search query with parameters."""
    
    query: str
    language: str = "en"
    categories: List[str] = None
    engines: List[str] = None
    time_range: SearchTimeRange = SearchTimeRange.ALL_TIME
    safe_search: SafeSearchLevel = SafeSearchLevel.MODERATE
    page_no: int = 1
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = ["general"]
        if self.engines is None:
            self.engines = []


class SearXNGSearchManager:
    """
    High-level search management utilities for SearXNG integration.
    
    This class provides convenient methods for common search operations
    that can be used by the PydanticAI agent through MCP tools.
    """
    
    def __init__(self, default_language: str = "en"):
        """
        Initialize the search manager.
        
        Args:
            default_language: Default language for searches
        """
        self.default_language = default_language
        
    def format_search_query(self, query: str) -> str:
        """
        Format and optimize search query.
        
        Args:
            query: Raw search query
            
        Returns:
            Optimized search query
        """
        # Remove extra whitespace
        query = " ".join(query.split())
        
        # Basic query optimization
        if not query:
            raise ValueError("Search query cannot be empty")
            
        # Remove unnecessary characters that might break search
        query = re.sub(r'[<>{}]', '', query)
        
        return query.strip()
    
    def create_research_query(self, topic: str, specific_aspects: List[str] = None) -> List[SearchQuery]:
        """
        Create comprehensive research queries for a topic.
        
        Args:
            topic: Main research topic
            specific_aspects: Specific aspects to research
            
        Returns:
            List of optimized search queries
        """
        queries = []
        
        # Main topic query
        main_query = SearchQuery(
            query=f"{topic} overview",
            categories=["general"],
            time_range=SearchTimeRange.YEAR
        )
        queries.append(main_query)
        
        # Recent developments
        current_year = datetime.now().year
        recent_query = SearchQuery(
            query=f"{topic} latest developments {current_year}",
            categories=["general", "news"],
            time_range=SearchTimeRange.MONTH
        )
        queries.append(recent_query)
        
        # Academic/detailed information
        academic_query = SearchQuery(
            query=f"{topic} research study analysis",
            categories=["general", "science"],
            time_range=SearchTimeRange.YEAR
        )
        queries.append(academic_query)
        
        # Specific aspects if provided
        if specific_aspects:
            for aspect in specific_aspects[:3]:  # Limit to 3 aspects
                aspect_query = SearchQuery(
                    query=f"{topic} {aspect}",
                    categories=["general"],
                    time_range=SearchTimeRange.YEAR
                )
                queries.append(aspect_query)
        
        return queries
    
    def create_problem_solving_queries(self, problem: str) -> List[SearchQuery]:
        """
        Create queries focused on problem-solving.
        
        Args:
            problem: Problem description
            
        Returns:
            List of problem-solving search queries
        """
        queries = []
        
        # Direct solution search
        solution_query = SearchQuery(
            query=f"how to solve {problem}",
            categories=["general"],
            time_range=SearchTimeRange.YEAR
        )
        queries.append(solution_query)
        
        # Troubleshooting approach
        troubleshoot_query = SearchQuery(
            query=f"{problem} troubleshooting guide",
            categories=["general"],
            time_range=SearchTimeRange.YEAR
        )
        queries.append(troubleshoot_query)
        
        # Best practices
        practices_query = SearchQuery(
            query=f"{problem} best practices",
            categories=["general"],
            time_range=SearchTimeRange.YEAR
        )
        queries.append(practices_query)
        
        return queries
    
    def extract_key_information(self, search_results: List[SearchResult]) -> Dict[str, Any]:
        """
        Extract key information from search results.
        
        Args:
            search_results: List of search results
            
        Returns:
            Structured key information
        """
        if not search_results:
            return {"summary": "No search results found", "key_points": [], "sources": []}
        
        key_points = []
        sources = []
        
        for result in search_results[:10]:  # Process top 10 results
            # Extract key information from content
            if result.content:
                # Look for sentences that contain important information
                sentences = result.content.split('.')
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(sentence) > 20 and any(keyword in sentence.lower() for keyword in 
                                                ['important', 'key', 'main', 'primary', 'significant', 'critical']):
                        if sentence not in key_points:
                            key_points.append(sentence)
            
            # Collect unique sources
            if result.url and result.url not in [s['url'] for s in sources]:
                sources.append({
                    'title': result.title,
                    'url': result.url,
                    'engine': result.engine
                })
        
        # Create summary
        summary = f"Found {len(search_results)} results from {len(set(r.engine for r in search_results))} search engines."
        
        return {
            "summary": summary,
            "key_points": key_points[:5],  # Top 5 key points
            "sources": sources[:8],  # Top 8 sources
            "total_results": len(search_results)
        }
    
    def format_search_for_notes(self, query: str, search_results: List[SearchResult]) -> str:
        """
        Format search results for note creation.
        
        Args:
            query: Original search query
            search_results: Search results
            
        Returns:
            Formatted markdown content for notes
        """
        if not search_results:
            return f"# Search: {query}\n\nNo results found."
        
        content = f"# Search Results: {query}\n\n"
        content += f"*Search performed on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        
        # Summary
        key_info = self.extract_key_information(search_results)
        content += f"## Summary\n\n{key_info['summary']}\n\n"
        
        # Key points
        if key_info['key_points']:
            content += "## Key Points\n\n"
            for point in key_info['key_points']:
                content += f"- {point}\n"
            content += "\n"
        
        # Top results
        content += "## Top Results\n\n"
        for i, result in enumerate(search_results[:5], 1):
            content += f"### {i}. {result.title}\n"
            content += f"**Source:** {result.url}\n"
            content += f"**Engine:** {result.engine}\n\n"
            
            if result.content:
                # Truncate content if too long
                summary = result.content[:300]
                if len(result.content) > 300:
                    summary += "..."
                content += f"{summary}\n\n"
        
        # All sources
        if len(search_results) > 5:
            content += "## Additional Sources\n\n"
            for result in search_results[5:10]:
                content += f"- [{result.title}]({result.url}) ({result.engine})\n"
            content += "\n"
        
        # Tags for organization
        content += "## Tags\n\n"
        content += f"#search #research #{query.replace(' ', '-').lower()}\n"
        
        return content
    
    def suggest_follow_up_searches(self, original_query: str, 
                                 search_results: List[SearchResult]) -> List[str]:
        """
        Suggest follow-up searches based on results.
        
        Args:
            original_query: Original search query
            search_results: Search results from original query
            
        Returns:
            List of suggested follow-up search queries
        """
        suggestions = []
        
        if not search_results:
            # Suggest broader or alternative searches
            words = original_query.split()
            if len(words) > 2:
                suggestions.append(" ".join(words[:-1]))  # Remove last word
            suggestions.append(f"{original_query} tutorial")
            suggestions.append(f"{original_query} examples")
            return suggestions
        
        # Extract common terms from successful results
        all_content = " ".join([r.content for r in search_results[:5] if r.content])
        
        # Look for frequently mentioned related terms
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_content.lower())
        word_freq = {}
        for word in words:
            if word not in original_query.lower():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent terms
        frequent_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create follow-up queries
        for term, _ in frequent_terms:
            suggestions.append(f"{original_query} {term}")
        
        # Add specific follow-up types
        suggestions.append(f"{original_query} comparison")
        suggestions.append(f"{original_query} alternatives")
        suggestions.append(f"{original_query} pros and cons")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def categorize_search_results(self, search_results: List[SearchResult]) -> Dict[str, List[SearchResult]]:
        """
        Categorize search results by type/topic.
        
        Args:
            search_results: List of search results
            
        Returns:
            Dictionary of categorized results
        """
        categories = {
            "documentation": [],
            "tutorials": [],
            "news": [],
            "research": [],
            "tools": [],
            "forums": [],
            "other": []
        }
        
        for result in search_results:
            content_lower = (result.title + " " + result.content).lower()
            url_lower = result.url.lower()
            
            # Categorize based on content and URL patterns
            if any(term in content_lower for term in ["documentation", "docs", "api", "reference"]):
                categories["documentation"].append(result)
            elif any(term in content_lower for term in ["tutorial", "guide", "how to", "step by step"]):
                categories["tutorials"].append(result)
            elif any(term in url_lower for term in ["news", "blog", "article"]) or result.category == "news":
                categories["news"].append(result)
            elif any(term in content_lower for term in ["research", "study", "analysis", "paper"]):
                categories["research"].append(result)
            elif any(term in content_lower for term in ["tool", "software", "download", "github"]):
                categories["tools"].append(result)
            elif any(term in url_lower for term in ["forum", "stackoverflow", "reddit", "community"]):
                categories["forums"].append(result)
            else:
                categories["other"].append(result)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def create_search_summary_for_tasks(self, query: str, search_results: List[SearchResult]) -> List[str]:
        """
        Create actionable tasks based on search results.
        
        Args:
            query: Search query
            search_results: Search results
            
        Returns:
            List of suggested tasks
        """
        tasks = []
        
        if not search_results:
            tasks.append(f"Refine search for: {query}")
            return tasks
        
        # Categorize results
        categories = self.categorize_search_results(search_results)
        
        # Create tasks based on what was found
        if categories.get("documentation"):
            tasks.append(f"Review documentation for {query}")
        
        if categories.get("tutorials"):
            tasks.append(f"Follow tutorial on {query}")
        
        if categories.get("tools"):
            tasks.append(f"Evaluate tools related to {query}")
        
        if categories.get("research"):
            tasks.append(f"Deep dive into research on {query}")
        
        # Add general analysis task
        tasks.append(f"Analyze and synthesize findings on {query}")
        
        # Follow-up research
        follow_ups = self.suggest_follow_up_searches(query, search_results)
        if follow_ups:
            tasks.append(f"Research follow-up topic: {follow_ups[0]}")
        
        return tasks[:5]  # Limit to 5 tasks
    
    def format_search_for_agent_response(self, search_results: List[SearchResult]) -> str:
        """
        Format search results for agent response.
        
        Args:
            search_results: Search results
            
        Returns:
            Formatted response text
        """
        if not search_results:
            return "No search results found."
        
        response = f"Found {len(search_results)} search results:\n\n"
        
        for i, result in enumerate(search_results[:3], 1):
            response += f"{i}. **{result.title}**\n"
            response += f"   Source: {result.url}\n"
            if result.content:
                summary = result.content[:150]
                if len(result.content) > 150:
                    summary += "..."
                response += f"   {summary}\n"
            response += "\n"
        
        if len(search_results) > 3:
            response += f"...and {len(search_results) - 3} more results.\n"
        
        return response