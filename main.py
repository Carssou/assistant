"""
CLI interface for the productivity agent.

This is the main entry point for running the agent in command-line mode.
"""

import asyncio
import sys
from typing import Optional

import click

from agent.agent import create_agent
from config.settings import load_config


async def run_interactive_session():
    """Run an interactive chat session with the agent."""
    print("🤖 Productivity Agent - Interactive Mode")
    print("Type 'quit', 'exit', or 'q' to end the session")
    print("=" * 50)
    
    try:
        # Load configuration and create agent
        config = load_config()
        agent, deps = await create_agent(config)
        
        print(f"✅ Agent initialized with {config.llm_provider} provider")
        
        print("Ready to help with your productivity tasks!\n")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'q', '']:
                    break
                
                # Get agent response
                print("Agent: ", end="", flush=True)
                if hasattr(agent, '_mcp_servers') and agent._mcp_servers:
                    async with agent.run_mcp_servers():
                        result = await agent.run(user_input, deps=deps)
                else:
                    result = await agent.run(user_input, deps=deps)
                
                print(result.data)
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again.\n")
        
        # Clean up
        await deps.close()
        
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


async def run_single_query(query: str):
    """Run a single query against the agent."""
    try:
        config = load_config()
        agent, deps = await create_agent(config)
        
        print(f"Query: {query}")
        print("=" * 50)
        
        if hasattr(agent, '_mcp_servers') and agent._mcp_servers:
            async with agent.run_mcp_servers():
                result = await agent.run(query, deps=deps)
        else:
            result = await agent.run(query, deps=deps)
        
        print(f"Response: {result.data}")
        
        await deps.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


@click.command()
@click.option('--query', '-q', help='Run a single query instead of interactive mode')
@click.option('--config-test', is_flag=True, help='Test configuration loading')
def main(query: Optional[str], config_test: bool):
    """
    Productivity Agent CLI.
    
    Run the agent in interactive mode or execute a single query.
    """
    if config_test:
        # Test configuration loading
        try:
            config = load_config()
            print("✅ Configuration loaded successfully")
            print(f"LLM Provider: {config.llm_provider}")
            print(f"Model: {config.llm_choice}")
            print(f"Debug Mode: {config.debug_mode}")
            
            # Test model creation
            from config.settings import create_model_instance
            model = create_model_instance(config)
            print(f"✅ Model instance created: {type(model).__name__}")
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            sys.exit(1)
        return
    
    if query:
        # Single query mode
        asyncio.run(run_single_query(query))
    else:
        # Interactive mode
        asyncio.run(run_interactive_session())


if __name__ == "__main__":
    main()