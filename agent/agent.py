"""
Main PydanticAI agent implementation.

This module contains the core agent setup following PydanticAI best practices.
"""

import asyncio
from typing import Optional, AsyncGenerator

from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelMessage

from agent.dependencies import AgentDependencies
from agent.prompts import get_system_prompt
from agent.tools import register_tools
from config.settings import AgentConfig, create_model_instance
from mcp_servers.configs import create_all_mcp_servers


# Global agent instance - will be configured during initialization
agent: Agent[AgentDependencies] = None


class ProductivityAgent:
    """
    Wrapper class for the PydanticAI agent with productivity tools.
    
    This class manages the agent lifecycle and provides convenience methods
    while following PydanticAI best practices.
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
        
        # Set up the agent with the model and MCP servers
        self._setup_agent()
        
        self.logger.info(f"Productivity agent initialized with {self.config.llm_provider} provider")
    
    def _setup_agent(self):
        """Set up the agent with model and MCP servers."""
        global agent
        
        # Create model instance
        model = create_model_instance(self.config)
        
        # Create MCP servers
        mcp_servers = create_all_mcp_servers(self.config)
        
        # Create the agent with proper MCP server integration
        agent = Agent(
            model=model,
            deps_type=AgentDependencies,
            system_prompt=get_system_prompt(),
            mcp_servers=mcp_servers,
            retries=2
        )
        
        # Register additional tools with the agent
        register_tools(agent)
        
        self.logger.info(f"Agent configured with {len(mcp_servers)} MCP servers")
    
    async def run_conversation(self, message: str, message_history: Optional[list[ModelMessage]] = None) -> str:
        """
        Run a single conversation turn.
        
        Args:
            message: User message
            message_history: Optional message history from previous conversations
            
        Returns:
            Agent response
        """
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
            result = None
            # Run with MCP servers in proper context
            # Check if agent has MCP servers using the private attribute
            if hasattr(agent, '_mcp_servers') and agent._mcp_servers:
                async with agent.run_mcp_servers():
                    result = await agent.run(
                        message, 
                        deps=self.deps,
                        message_history=message_history
                    )
            else:
                result = await agent.run(
                    message, 
                    deps=self.deps,
                    message_history=message_history
                )
            
            response = result.output
            
            # Log API usage
            self._log_conversation(message, result)
            
            # Log success to Langfuse
            if generation:
                generation.update(output=response)
                generation.end()
            
            return response
            
        except Exception as e:
            import traceback
            self.logger.error(f"Error in conversation: {e}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            
            error_msg = f"I encountered an error: {str(e)}"
            
            # Log error to Langfuse
            if generation:
                generation.update(output=error_msg, level="ERROR")
                generation.end()
            
            return error_msg
    
    def _log_conversation(self, message: str, result: AgentRunResult):
        """Log conversation details."""
        response = result.output

        print(f"[API REQUEST] Message: {message}")
        
        # Log tool calls
        for msg in result.new_messages():
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    normal_tools = ['take_screenshot', 'take_region_screenshot', 'get_screen_info']
                    if tool_call.tool_name in normal_tools:
                        print(f"[NORMAL TOOL] {tool_call.tool_name} called with: {tool_call.args}")
                    else:
                        print(f"[MCP TOOL] {tool_call.tool_name} called with: {tool_call.args}")
                        
            # Log tool results
            if hasattr(msg, 'content') and msg.content and len(str(msg.content)) > 100:
                print(f"[TOOL RESULT] {str(msg.content)[:200]}...")
    
    async def list_available_tools(self) -> dict:
        """
        List all available tools from MCP servers.
        
        Returns:
            Dictionary of server names and their available tools
        """
        tools_info = {}
        
        if not hasattr(agent, '_mcp_servers') or not agent._mcp_servers:
            return {"message": "No MCP servers configured"}
        
        for i, server in enumerate(agent._mcp_servers):
            server_name = f"server_{i}"
            try:
                tools_info[server_name] = {
                    "command": server.command,
                    "args": server.args,
                    "status": "configured"
                }
            except Exception as e:
                tools_info[server_name] = {
                    "command": server.command,
                    "args": server.args,
                    "status": f"error: {e}"
                }
        
        return tools_info
    
    @property
    def mcp_servers(self):
        """Get MCP servers from the underlying agent."""
        if hasattr(agent, '_mcp_servers'):
            return agent._mcp_servers
        return []
    
    def has_mcp_servers(self) -> bool:
        """Check if the agent has MCP servers configured."""
        return hasattr(agent, '_mcp_servers') and bool(agent._mcp_servers)
    
    def disable_mcp_servers(self):
        """Disable MCP servers by clearing the list."""
        global agent
        if hasattr(agent, '_mcp_servers'):
            agent._mcp_servers = []
    
    async def close(self):
        """Clean up agent resources."""
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
    productivity_agent = ProductivityAgent(deps)
    
    return productivity_agent
