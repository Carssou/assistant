"""
Gradio GUI interface for the productivity agent.

This module provides a web-based chat interface using Gradio with streaming support.
"""

import asyncio
from typing import AsyncGenerator, Optional, List, Tuple
import gradio as gr

from agent.agent import create_agent, ProductivityAgent
from config.settings import load_config, AgentConfig


class AgentGUI:
    """
    Gradio GUI wrapper for the productivity agent.
    
    Provides a web-based chat interface with streaming responses,
    configuration management, and session handling.
    """
    
    def __init__(self):
        """Initialize the GUI wrapper."""
        self.agent: Optional[ProductivityAgent] = None
        self.config: Optional[AgentConfig] = None
        self.conversation_history: List[Tuple[str, str]] = []
        
    async def initialize_agent(self) -> bool:
        """
        Initialize the agent with current configuration.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.config = load_config()
            self.agent = await create_agent(self.config)
            return True
        except Exception as e:
            print(f"Failed to initialize agent: {e}")
            return False
    
    async def chat_response(
        self, 
        message: str, 
        history: List
    ) -> AsyncGenerator[List, None]:
        """
        Generate streaming chat response with MCP error handling.
        
        Args:
            message: User message
            history: Conversation history
            
        Yields:
            Updated history with streaming response
        """
        if not self.agent:
            history.append({"role": "assistant", "content": "Error: Agent not initialized. Please check configuration."})
            yield history
            return
        
        if not message.strip():
            history.append({"role": "assistant", "content": "Please enter a message."})
            yield history
            return
        
        # Add empty assistant message that we'll update
        history.append({"role": "assistant", "content": ""})
        
        try:
            # Stream from agent with MCP error handling
            async for chunk in self.agent.stream_conversation(message):
                history[-1]["content"] = chunk
                yield history
            
            # Log final complete response
            print(f"\n[FINAL RESPONSE]:\n{history[-1]['content']}\n{'='*50}")
        except Exception as e:
            # Handle MCP cancel scope errors gracefully
            error_str = str(e).lower()
            if "cancel scope" in error_str or "different task" in error_str:
                # Log but don't fail - this is a known MCP threading issue
                print(f"MCP context warning (continuing normally): {e}")
                # If we got some content before the error, keep it
                if history[-1]["content"]:
                    yield history
                else:
                    history[-1]["content"] = "Response completed (MCP context warning)"
                    yield history
            else:
                # Other errors should be shown to user
                history[-1]["content"] = f"Error: {str(e)}"
                yield history
    
    def _get_vault_name(self) -> str:
        """Extract vault name from full path."""
        vault_path = getattr(self.config, 'obsidian_vault_path', None)
        if not vault_path:
            return 'Not configured'
        
        from pathlib import Path
        return Path(vault_path).name
    
    def _format_provider_name(self) -> str:
        """Format provider name for display."""
        if not self.config or not self.config.llm_provider:
            return 'Not configured'
        
        provider_str = str(self.config.llm_provider)
        if hasattr(self.config.llm_provider, 'value'):
            provider_str = self.config.llm_provider.value
        else:
            provider_str = provider_str.split('.')[-1]
        
        # Provider name mapping for proper display
        provider_names = {
            'aws': 'AWS',
            'openai': 'OpenAI',
            'anthropic': 'Anthropic',
            'google': 'Google',
            'azure': 'Azure',
            'huggingface': 'Hugging Face',
            'cohere': 'Cohere',
            'mistral': 'Mistral',
            'groq': 'Groq',
            'together': 'Together AI',
            'replicate': 'Replicate',
            'bedrock': 'AWS Bedrock'
        }
        
        return provider_names.get(provider_str.lower(), provider_str.title())
    
    def get_config_info(self) -> str:
        """
        Get current configuration information.
        
        Returns:
            Formatted configuration string
        """
        if not self.config:
            return "Configuration not loaded"
        
        return f"""
**Current Configuration:**
- LLM Provider: {self._format_provider_name()}
- Model: {self.config.llm_choice}
- Debug Mode: {self.config.debug_mode}
- Obsidian Vault: {self._get_vault_name()}
- SearXNG URL: {getattr(self.config, 'searxng_base_url', 'Not configured')}
"""
    
    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface.
        
        Returns:
            Configured Gradio Blocks interface
        """
        with gr.Blocks(
            title="Productivity Agent",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 100% !important;
                width: 100% !important;
                margin: 0 !important;
                padding: 20px !important;
            }
            .chat-message {
                padding: 10px;
                margin: 5px 0;
                border-radius: 10px;
            }
            """
        ) as interface:
            
            gr.Markdown(
                """
                # 🤖 Productivity Agent
                
                Your AI assistant with access to notes, web search, tasks, and video analysis.
                """
            )
            
            with gr.Row():
                with gr.Column(scale=8):
                    # Main chat interface
                    chatbot = gr.Chatbot(
                        label="Chat with Agent",
                        height="70vh",
                        show_label=True,
                        container=True,
                        type="messages",
                        show_copy_button=True,
                        show_share_button=False,
                        render_markdown=True
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Message",
                            placeholder="Ask me to search, take notes, manage tasks, or analyze videos...",
                            container=False,
                            scale=4
                        )
                        submit = gr.Button("Send", variant="primary", scale=1)
                        clear = gr.Button("Clear", variant="secondary", scale=1)
                
                with gr.Column(scale=2):
                    # Configuration panel
                    gr.Markdown("### Configuration")
                    
                    config_display = gr.Markdown(
                        self.get_config_info(),
                        label="Current Config"
                    )
                    
                    refresh_config = gr.Button("Refresh Config", variant="secondary")
                    
                    # Status indicators
                    gr.Markdown("### Status")
                    
                    agent_status = gr.Markdown(
                        "🔴 **Agent**: Not initialized",
                        label="Agent Status"
                    )
                    
                    # Help section
                    gr.Markdown("### Usage Examples")
                    gr.Markdown("""
                    **Research & Notes:**
                    - "Research latest AI developments and create notes"
                    - "Search for productivity tools and organize findings"
                    
                    **Task Management:**
                    - "Show my current Todoist tasks" 
                    - "Add task to review documentation by Friday"
                    
                    **Video Learning:**
                    - "Analyze this YouTube video: [URL]"
                    - "Create study notes from this tutorial"
                    
                    **Web Search:**
                    - "Find recent news about AI developments"
                    - "Search for Python best practices"
                    """)
            
            # State for message passing
            msg_state = gr.State("")
            
            # Streaming event handlers
            def add_user_message(message, history):
                """Add user message to history."""
                if not message.strip():
                    return "", history, ""
                history = history + [{"role": "user", "content": message}]
                return "", history, message  # Return message as third output
            
            def stream_response(message, history):
                """Stream agent response."""
                if not message.strip():
                    return history
                
                # Create async event loop for streaming
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Create async generator
                    async_gen = self.chat_response(message, history)
                    
                    # Stream the response
                    while True:
                        try:
                            updated_history = loop.run_until_complete(async_gen.__anext__())
                            yield updated_history
                        except StopAsyncIteration:
                            break
                        except Exception as e:
                            # Log unexpected errors but don't break streaming
                            print(f"Streaming error: {e}")
                            break
                finally:
                    loop.close()
            
            def clear_chat():
                """Clear chat history."""
                self.conversation_history = []
                return [], ""
            
            async def refresh_config_info():
                """Refresh configuration display."""
                await self.initialize_agent()
                status = "🟢 **Agent**: Ready" if self.agent else "🔴 **Agent**: Failed to initialize"
                return self.get_config_info(), status
            
            # Streaming event connections
            submit.click(
                add_user_message,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot, msg_state],
                queue=False
            ).then(
                stream_response,
                inputs=[msg_state, chatbot],
                outputs=chatbot,
                queue=True
            )
            
            msg.submit(
                add_user_message,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot, msg_state],
                queue=False
            ).then(
                stream_response,
                inputs=[msg_state, chatbot],
                outputs=chatbot,
                queue=True
            )
            
            clear.click(
                clear_chat,
                outputs=[chatbot, msg]
            )
            
            refresh_config.click(
                refresh_config_info,
                outputs=[config_display, agent_status]
            )
            
            # Initialize on startup
            interface.load(
                refresh_config_info,
                outputs=[config_display, agent_status]
            )
        
        return interface


async def main():
    """Main function to run the GUI."""
    print("🚀 Starting Productivity Agent GUI...")
    
    # Create GUI instance
    gui = AgentGUI()
    
    # Initialize agent
    print("📡 Initializing agent...")
    success = await gui.initialize_agent()
    
    if success:
        print("✅ Agent initialized successfully")
        print(f"🔧 Provider: {gui.config.llm_provider}")
        print(f"🧠 Model: {gui.config.llm_choice}")
    else:
        print("⚠️  Agent initialization failed - check your configuration")
        print("The GUI will still start, but functionality may be limited")
    
    # Create and launch interface
    interface = gui.create_interface()
    
    print("🌐 Launching web interface...")
    print("💡 Open your browser to interact with the agent")
    
    # Launch with appropriate settings
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        debug=gui.config.debug_mode if gui.config else False,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
