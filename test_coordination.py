#!/usr/bin/env python3
"""
Multi-Tool Coordination Test Script

This script demonstrates and tests the multi-tool coordination capabilities
of the PydanticAI agent with multiple MCP servers.
"""

import asyncio
import time
from typing import List, Dict, Any

from agent.agent import create_agent
from agent.dependencies import create_agent_dependencies
from config.settings import AgentConfig


async def test_coordination_workflow(query: str, expected_tools: List[str]) -> Dict[str, Any]:
    """
    Test a coordination workflow with timing and tool usage tracking.
    
    Args:
        query: The user query to test
        expected_tools: List of tools expected to be used
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*60}")
    print(f"TESTING: {query}")
    print(f"Expected tools: {', '.join(expected_tools)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Create agent with all MCP servers
        agent = await create_agent()
        
        # Execute the query
        result = await agent.run_conversation(query)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✅ COMPLETED in {duration:.2f} seconds")
        print(f"Response: {result}")
        
        return {
            "success": True,
            "duration": duration,
            "response": result,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n❌ FAILED after {duration:.2f} seconds")
        print(f"Error: {str(e)}")
        
        return {
            "success": False,
            "duration": duration,
            "response": None,
            "error": str(e)
        }


async def run_coordination_tests():
    """Run all coordination workflow tests."""
    print("🤖 Multi-Tool Coordination Test Suite")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Simple Search & Note",
            "query": "Search for 'MCP servers' and create a quick reference note",
            "expected_tools": ["searxng_web_search", "create_note"]
        },
        {
            "name": "Research Synthesis",
            "query": "Research PydanticAI features and create a comprehensive feature overview",
            "expected_tools": ["searxng_web_search", "create_note"]
        },
        {
            "name": "Content Organization",
            "query": "Find information about agent frameworks and organize it in my knowledge base",
            "expected_tools": ["searxng_web_search", "search_vault", "create_note"]
        },
        {
            "name": "Learning Workflow",
            "query": "Explain multi-agent systems and create study notes with key concepts",
            "expected_tools": ["searxng_web_search", "create_note"]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Running: {test_case['name']}")
        result = await test_coordination_workflow(
            test_case["query"], 
            test_case["expected_tools"]
        )
        result["test_name"] = test_case["name"]
        results.append(result)
        
        # Brief pause between tests
        await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    total_time = sum(r["duration"] for r in results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"⏱️  Total time: {total_time:.2f} seconds")
    print(f"📊 Average time: {total_time/total:.2f} seconds per test")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test_name']}: {result['duration']:.2f}s")
        if result["error"]:
            print(f"   Error: {result['error']}")
    
    return results


async def demonstrate_coordination_features():
    """Demonstrate key coordination features."""
    print("\n🎯 Coordination Features Demonstration")
    print("=" * 60)
    
    features = [
        {
            "name": "Context Flow",
            "description": "Information flows between tools",
            "query": "Search for 'AI agent best practices' and create structured notes with the findings"
        },
        {
            "name": "Intelligent Synthesis", 
            "description": "Multiple sources combined intelligently",
            "query": "Research both 'MCP protocol' and 'PydanticAI agents' then create a comprehensive integration guide"
        },
        {
            "name": "Adaptive Workflow",
            "description": "Agent adapts workflow based on content",
            "query": "Help me understand transformer architecture - find resources and create a learning plan"
        },
        {
            "name": "Knowledge Integration",
            "description": "Links to existing knowledge base",
            "query": "Research prompt engineering techniques and connect them to my existing AI notes"
        }
    ]
    
    for feature in features:
        print(f"\n🔧 {feature['name']}")
        print(f"   {feature['description']}")
        print(f"   Query: {feature['query']}")
        
        # Run the demonstration
        result = await test_coordination_workflow(feature["query"], ["multiple_tools"])
        
        if result["success"]:
            print(f"   ✅ Demonstrated successfully")
        else:
            print(f"   ❌ Demonstration failed: {result['error']}")
        
        await asyncio.sleep(2)


if __name__ == "__main__":
    async def main():
        print("🚀 Starting Multi-Tool Coordination Tests")
        
        # Run coordination tests
        await run_coordination_tests()
        
        # Demonstrate coordination features
        await demonstrate_coordination_features()
        
        print("\n🎉 Multi-Tool Coordination Testing Complete!")
    
    asyncio.run(main())