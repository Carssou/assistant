"""
Main PydanticAI agent implementation.

This module contains the core agent setup and initialization.
"""

from typing import Optional

from pydantic_ai import Agent

from agent.dependencies import AgentDependencies
from agent.prompts import SYSTEM_PROMPT
from config.settings import AgentConfig, create_model_instance


class ProductivityAgent:
    """
    Main productivity agent class.
    
    This class encapsulates the PydanticAI agent with all its
    dependencies and configuration.
    """
    
    def __init__(self, dependencies: AgentDependencies):
        """
        Initialize the productivity agent.
        
        Args:
            dependencies: Agent dependencies container
        """
        self.deps = dependencies
        self.config = dependencies.config
        self.logger = dependencies.logger
        
        # Create the model instance
        self.model = create_model_instance(self.config)
        
        # Create the PydanticAI agent
        self.agent = Agent(
            model=self.model,
            deps_type=AgentDependencies,
            system_prompt=SYSTEM_PROMPT,
            retries=2
        )
        
        self.logger.info(f"Productivity agent initialized with {self.config.llm_provider} provider")
    
    async def run_conversation(self, message: str) -> str:
        """
        Run a single conversation turn.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        # Create Langfuse trace if client is available
        trace = None
        generation = None
        if self.deps.langfuse_client:
            trace_id = self.deps.langfuse_client.create_trace_id()
            generation = self.deps.langfuse_client.start_generation(
                name="agent_conversation",
                input=message,
                model=self.config.llm_choice,
                metadata={
                    "llm_provider": str(self.config.llm_provider),
                    "trace_id": trace_id
                }
            )
        
        try:
            result = await self.agent.run(message, deps=self.deps)
            response = result.data
            
            # Log successful completion to Langfuse
            if generation:
                generation.update(output=response)
                generation.end()
            
            return response
        except Exception as e:
            self.logger.error(f"Error in conversation: {e}")
            error_msg = f"I encountered an error: {str(e)}"
            
            # Log error to Langfuse
            if generation:
                generation.update(output=error_msg, level="ERROR")
                generation.end()
            
            return error_msg
    
    async def stream_conversation(self, message: str):
        """
        Stream a conversation response.
        
        Args:
            message: User message
            
        Yields:
            Response chunks as they arrive
        """
        # Create Langfuse trace if client is available
        generation = None
        if self.deps.langfuse_client:
            trace_id = self.deps.langfuse_client.create_trace_id()
            generation = self.deps.langfuse_client.start_generation(
                name="agent_streaming_conversation",
                input=message,
                model=self.config.llm_choice,
                metadata={
                    "llm_provider": str(self.config.llm_provider),
                    "streaming": True,
                    "trace_id": trace_id
                }
            )
        
        response_chunks = []
        try:
            async with self.agent.run_stream(message, deps=self.deps) as stream:
                async for chunk in stream:
                    response_chunks.append(str(chunk))
                    yield chunk
            
            # Log complete response to Langfuse
            if generation:
                full_response = "".join(response_chunks)
                generation.update(output=full_response)
                generation.end()
                
        except Exception as e:
            self.logger.error(f"Error in streaming conversation: {e}")
            error_msg = f"Error: {str(e)}"
            
            # Log error to Langfuse
            if generation:
                generation.update(output=error_msg, level="ERROR")
                generation.end()
            
            yield error_msg
    
    def get_conversation_history(self):
        """
        Get conversation history if available.
        
        Returns:
            Conversation history or empty list
        """
        # TODO: Implement conversation history storage
        return []
    
    async def close(self):
        """Clean up agent resources."""
        # Flush Langfuse data before closing
        if self.deps.langfuse_client:
            self.deps.langfuse_client.flush()
        await self.deps.close()


async def create_agent(config: Optional[AgentConfig] = None) -> ProductivityAgent:
    """
    Create and initialize a productivity agent.
    
    Args:
        config: Agent configuration (optional, loads from env if not provided)
        
    Returns:
        Initialized productivity agent
    """
    from agent.dependencies import create_agent_dependencies
    from config.settings import load_config
    
    if config is None:
        config = load_config()
    
    # Create dependencies
    deps = await create_agent_dependencies(config)
    
    # Create agent
    agent = ProductivityAgent(deps)
    
    return agent


def create_sync_agent(config: Optional[AgentConfig] = None) -> ProductivityAgent:
    """
    Create agent synchronously (for testing).
    
    Args:
        config: Agent configuration (optional)
        
    Returns:
        Productivity agent (note: some features may not work in sync mode)
    """
    from agent.dependencies import create_sync_dependencies
    from config.settings import load_config
    
    if config is None:
        config = load_config()
    
    # Create dependencies synchronously
    deps = create_sync_dependencies(config)
    
    # Create agent
    agent = ProductivityAgent(deps)
    
    return agent