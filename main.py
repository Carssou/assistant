"""
CLI interface for the productivity agent.

This is the main entry point for running the agent in command-line mode.
"""

import asyncio
import logging
import sys

import click

from agent.agent import create_agent
from config.settings import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("productivity_agent.log")],
)
logger = logging.getLogger(__name__)


async def run_interactive_session():
    """Run an interactive chat session with the agent."""
    print("🤖 Productivity Agent - Interactive Mode")
    print("Type 'quit', 'exit', or 'q' to end the session")
    print("=" * 50)
    logger.info("Starting interactive session")

    try:
        # Load configuration and create agent
        config = load_config()
        agent, deps = await create_agent(config)

        print(f"✅ Agent initialized with {config.llm_provider} provider")
        logger.info(
            f"Agent initialized with {config.llm_provider} provider using {config.llm_choice} model"
        )

        print("Ready to help with your productivity tasks!\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                # Check for exit commands
                if user_input.lower() in ["quit", "exit", "q", ""]:
                    break

                # Get agent response
                print("Agent: ", end="", flush=True)
                if hasattr(agent, "_mcp_servers") and agent._mcp_servers:
                    async with agent.run_mcp_servers():
                        result = await agent.run(user_input, deps=deps)
                else:
                    result = await agent.run(user_input, deps=deps)

                print(result.output)
                logger.debug(f"Agent response: {result.output[:100]}...")  # Log first 100 chars
                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                logger.info("Interactive session ended by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"Error during conversation: {e}")
                print("Please try again.\n")

        # Clean up
        await deps.close()

    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        logger.error(f"Failed to initialize agent: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


async def run_single_query(query: str):
    """Run a single query against the agent."""
    try:
        config = load_config()
        agent, deps = await create_agent(config)

        print(f"Query: {query}")
        print("=" * 50)
        logger.info(f"Running single query: {query}")

        if hasattr(agent, "_mcp_servers") and agent._mcp_servers:
            async with agent.run_mcp_servers():
                result = await agent.run(query, deps=deps)
        else:
            result = await agent.run(query, deps=deps)

        print(f"Response: {result.output}")
        logger.info("Query completed successfully")

        await deps.close()

    except Exception as e:
        print(f"Error: {e}")
        logger.error(f"Error in single query mode: {e}")
        sys.exit(1)


@click.command()
@click.option("--query", "-q", help="Run a single query instead of interactive mode")
@click.option("--config-test", is_flag=True, help="Test configuration loading")
def main(query: str | None, config_test: bool):
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
            logger.info(
                f"Configuration test successful - Provider: {config.llm_provider}, Model: {config.llm_choice}"
            )

            # Test model creation
            from config.settings import create_model_instance

            model = create_model_instance(config)
            print(f"✅ Model instance created: {type(model).__name__}")
            logger.info(f"Model instance created: {type(model).__name__}")

        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            logger.error(f"Configuration test failed: {e}")
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
