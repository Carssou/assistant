"""
CLI interface for the Strands productivity agent.

This is the main entry point for running the agent in command-line mode
using Strands Agents' native conversation management.
"""

import asyncio
import logging
import sys

import click

from agent.agent import agent, mcp_servers
from config.settings import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("productivity_agent.log")],
)

logger = logging.getLogger(__name__)


async def run_interactive_session():
    """Run interactive CLI session with Strands agent."""
    logger.info("Starting interactive session")

    try:
        # Load configuration
        config = load_config()
        logger.info(
            f"Agent initialized with {config.llm_provider} provider using {config.llm_choice} model"
        )

        print(f"✅ Agent initialized with {config.llm_provider} provider")
        print(f"🛠️ Available tools: {len(agent.tool_names)}")
        print(f"💬 Conversation manager: {type(agent.conversation_manager).__name__}")
        print("\nReady to help with your productivity tasks!\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "q", ""]:
                    break

                # Get agent response using Strands native API
                print("Agent: ", end="", flush=True)

                try:
                    # Use MCP context managers for agent execution
                    def run_agent_query(agent, query):
                        return asyncio.run(agent.invoke_async(query))

                    if mcp_servers:
                        # Run within MCP contexts
                        contexts = []
                        try:
                            # Enter all MCP contexts
                            for mcp_client in mcp_servers:
                                contexts.append(mcp_client.__enter__())

                            # Run agent query
                            result = await agent.invoke_async(user_input)

                        finally:
                            # Exit all contexts
                            for mcp_client in mcp_servers:
                                try:
                                    mcp_client.__exit__(None, None, None)
                                except Exception as e:
                                    logger.warning(f"Error closing MCP client: {e}")
                    else:
                        # No MCP servers, run directly
                        result = await agent.invoke_async(user_input)

                    print(str(result))
                    logger.debug(f"Agent response: {str(result)[:100]}...")  # Log first 100 chars
                    print()

                except Exception as agent_error:
                    print(f"❌ Agent Error: {agent_error}")
                    logger.error(f"Agent error: {agent_error}")
                    print("Please try again.\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                logger.info("Interactive session ended by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"Error during conversation: {e}")
                print("Please try again.\n")

    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        logger.error(f"Failed to initialize agent: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


async def run_single_query(query: str):
    """Run a single query against the Strands agent."""
    logger.info(f"Running single query: {query}")

    try:
        # Load configuration
        config = load_config()
        logger.info(
            f"Agent initialized with {config.llm_provider} provider using {config.llm_choice} model"
        )

        # Get agent response using Strands native API with MCP context
        if mcp_servers:
            # Run within MCP contexts
            try:
                # Enter all MCP contexts
                for mcp_client in mcp_servers:
                    mcp_client.__enter__()

                # Run agent query
                result = await agent.invoke_async(query)

            finally:
                # Exit all contexts
                for mcp_client in mcp_servers:
                    try:
                        mcp_client.__exit__(None, None, None)
                    except Exception as e:
                        logger.warning(f"Error closing MCP client: {e}")
        else:
            # No MCP servers, run directly
            result = await agent.invoke_async(query)

        print(f"Response: {str(result)}")
        logger.info("Single query completed successfully")

    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Error in single query mode: {e}")
        sys.exit(1)


async def test_configuration():
    """Test configuration and model setup."""
    logger.info("Testing configuration")

    try:
        # Load and test configuration
        config = load_config()
        print("✅ Configuration loaded successfully")
        print(f"LLM Provider: {config.llm_provider}")
        print(f"Model: {config.llm_choice}")
        print(f"Debug Mode: {config.debug_mode}")
        logger.info(
            f"Configuration test successful - Provider: {config.llm_provider}, Model: {config.llm_choice}"
        )

        # Test model instance creation
        from config.settings import create_model_instance

        model_instance = create_model_instance(config)
        print(f"✅ Model instance created: {type(model_instance).__name__}")
        logger.info(f"Model instance created: {type(model_instance).__name__}")

        # Test agent initialization
        print(f"✅ Agent ready with {len(agent.tool_names)} tools")
        print(
            f"🛠️ Tools: {', '.join(list(agent.tool_names)[:5])}{'...' if len(agent.tool_names) > 5 else ''}"
        )
        logger.info(f"Agent initialized with {len(agent.tool_names)} tools")

        # Test a simple interaction
        print("\n🧪 Testing simple interaction...")
        result = await agent.invoke_async("Hello! Can you tell me what tools you have available?")
        print(f"✅ Agent response: {str(result)[:200]}...")
        logger.info("Configuration test completed successfully")

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        logger.error(f"Configuration test failed: {e}")
        sys.exit(1)


@click.command()
@click.option("--query", "-q", help="Run a single query instead of interactive mode")
@click.option("--config-test", is_flag=True, help="Test configuration and model setup")
def main(query: str = None, config_test: bool = False):
    """
    Strands Productivity Agent CLI.

    Run the agent in interactive mode or with a single query.
    """
    if config_test:
        # Configuration test mode
        asyncio.run(test_configuration())
    elif query:
        # Single query mode
        asyncio.run(run_single_query(query))
    else:
        # Interactive mode
        asyncio.run(run_interactive_session())


if __name__ == "__main__":
    main()
