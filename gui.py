"""
Gradio GUI interface for the productivity agent.

This module provides a web-based chat interface using Gradio with streaming support.
"""

import asyncio
import logging

import gradio as gr

from agent.agent import AgentDeps, agent
from config.settings import AgentConfig, load_config


class AgentGUI:
    """
    Gradio GUI wrapper for the productivity agent.

    Provides a web-based chat interface with streaming responses,
    configuration management, and session handling.
    """

    def __init__(self):
        """Initialize the GUI wrapper."""
        self.agent = agent  # Use the pre-created agent from course pattern
        self.deps = None
        self.config: AgentConfig | None = None
        self.conversation_history: list[dict[str, str]] = []
        self.mcp_context_active = False
        self.tool_calls_log = []

        # Set up console logging for tool calls
        self.setup_console_logging()

    def setup_console_logging(self):
        """Set up console logging for tool calls."""
        # Create console handler for tool calls
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        console_handler.setFormatter(formatter)

        # Add handler to agent.tools logger for console output
        tool_logger = logging.getLogger("agent.tools")
        tool_logger.addHandler(console_handler)
        tool_logger.setLevel(logging.INFO)
        tool_logger.propagate = False  # Don't propagate to root logger

    def process_uploaded_file(self, file_path: str) -> str:
        """Process uploaded file and provide content to agent."""
        if not file_path:
            return ""

        try:
            from pathlib import Path

            file_obj = Path(file_path)
            file_name = file_obj.name
            file_ext = file_obj.suffix.lower()

            # Read file content based on type
            if file_ext in [".txt", ".md", ".py", ".js", ".json"]:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            elif file_ext == ".pdf":
                content = f"[PDF file uploaded: {file_name} - PDF text extraction requires additional setup]"
            elif file_ext == ".docx":
                content = f"[Word document uploaded: {file_name} - DOCX processing requires additional setup]"
            else:
                content = f"[File uploaded: {file_name} - File type: {file_ext}]"

            return f"\n\n**📎 Uploaded File**: {file_name}\n```\n{content}\n```"

        except Exception as e:
            return f"\n\n❌ **File Error**: Could not read {file_path} - {str(e)}"

    async def initialize_agent(self) -> bool:
        """
        Initialize the agent dependencies following course pattern.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.config = load_config()

            # Create dependencies following course pattern
            import httpx

            from utils.logger import setup_agent_logging

            http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
            langfuse_client = setup_agent_logging(
                log_level=self.config.log_level,
                debug_mode=self.config.debug_mode,
                langfuse_secret_key=self.config.langfuse_secret_key,
                langfuse_public_key=self.config.langfuse_public_key,
                langfuse_host=self.config.langfuse_host,
            )

            self.deps = AgentDeps(
                config=self.config,
                http_client=http_client,
                langfuse_client=langfuse_client,
                vault_path=self.config.obsidian_vault_path,
            )

            return True
        except Exception as e:
            print(f"Failed to initialize agent dependencies: {e}")
            return False

    async def chat_response(self, message: str, history: list) -> tuple[list, str]:
        """
        Generate complete chat response with MCP error handling.

        Args:
            message: User message
            history: Conversation history

        Returns:
            Updated history with complete response
        """
        if not self.agent:
            history.append(
                {
                    "role": "assistant",
                    "content": "⚠️ **Agent Not Ready**: The AI agent isn't initialized.\n\n💡 *Try clicking 'Refresh Config' in the sidebar to reload the configuration.*",
                }
            )
            return history

        if not message.strip():
            history.append({"role": "assistant", "content": "Please enter a message."})
            return history

        try:
            # Convert GUI history to PydanticAI ModelMessage format
            from pydantic_ai.messages import (
                ModelRequest,
                ModelResponse,
                SystemPromptPart,
                TextPart,
                UserPromptPart,
            )

            from agent.prompts import get_system_prompt

            chat_history = []

            # CRITICAL: Always add system prompt at the start when message_history is provided
            # PydanticAI doesn't auto-include system prompt when message_history is provided
            system_prompt = get_system_prompt()
            chat_history.append(ModelRequest(parts=[SystemPromptPart(content=system_prompt)]))

            for msg in history:
                if msg["role"] == "user":
                    chat_history.append(
                        ModelRequest(parts=[UserPromptPart(content=msg["content"])])
                    )
                elif msg["role"] == "assistant":
                    chat_history.append(ModelResponse(parts=[TextPart(content=msg["content"])]))

            # Clear tool calls log before running agent
            self.tool_calls_log = []

            # First run - let agent decide if it needs tools
            if hasattr(self.agent, "_mcp_servers") and self.agent._mcp_servers:
                async with self.agent.run_mcp_servers():
                    print("🔧 Agent running with MCP servers available")
                    result = await self.agent.run(
                        message, deps=self.deps, message_history=chat_history
                    )
            else:
                print("🔧 Agent running without MCP servers")
                result = await self.agent.run(message, deps=self.deps, message_history=chat_history)

            response = result.output

            # Extract and clean up thinking content to avoid blank lines
            thinking_content = ""
            import re

            thinking_match = re.search(r"<thinking>(.*?)</thinking>", response, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                # Remove thinking tags from the main response to avoid blank lines
                response = re.sub(
                    r"<thinking>.*?</thinking>\s*", "", response, flags=re.DOTALL
                ).strip()

            # Log completion and track tool usage information
            tool_usage_text = "🔧 **Last Tools Used**: None (direct response)"
            try:
                if hasattr(result, "all_messages") and callable(result.all_messages):
                    tool_calls = []
                    for msg in result.all_messages():
                        if hasattr(msg, "parts"):
                            for part in msg.parts:
                                if hasattr(part, "tool_name"):
                                    tool_calls.append(part.tool_name)

                    if tool_calls:
                        unique_tools = list(set(tool_calls))  # Remove duplicates
                        tool_usage_text = f"🔧 **Last Tools Used**: {', '.join(unique_tools)}"
                        print(f"✅ Tools used: {', '.join(unique_tools)}")
                    else:
                        print("✅ No tools used")
                else:
                    print("✅ Response completed")
            except Exception:
                # Don't let logging failures break the response
                print("✅ Response completed")

            # Build the final response with thinking and tool info integrated
            final_response = response

            # Add thinking section if present
            if thinking_content:
                final_response = f"*{thinking_content}*\n\n────────\n{response}"

            # Add tool usage info at the end if tools were used
            if "None (direct response)" not in tool_usage_text:
                final_response += f"\n\n---\n\n{tool_usage_text}"

            history.append({"role": "assistant", "content": final_response})
            return history

        except Exception as e:
            # Let the agent handle its own errors - just re-raise
            raise e

    def _get_vault_name(self) -> str:
        """Extract vault name from full path."""
        vault_path = getattr(self.config, "obsidian_vault_path", None)
        if not vault_path:
            return "Not configured"

        from pathlib import Path

        return Path(vault_path).name

    def _format_provider_name(self) -> str:
        """Format provider name for display."""
        if not self.config or not self.config.llm_provider:
            return "Not configured"

        provider_str = str(self.config.llm_provider)
        if hasattr(self.config.llm_provider, "value"):
            provider_str = self.config.llm_provider.value
        else:
            provider_str = provider_str.split(".")[-1]

        # Provider name mapping for proper display
        provider_names = {
            "aws": "AWS",
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "google": "Google",
            "azure": "Azure",
            "huggingface": "Hugging Face",
            "cohere": "Cohere",
            "mistral": "Mistral",
            "groq": "Groq",
            "together": "Together AI",
            "replicate": "Replicate",
            "bedrock": "AWS Bedrock",
        }

        return provider_names.get(provider_str.lower(), provider_str.title())

    def validate_config(self) -> dict[str, bool]:
        """Validate current configuration and return status for each component."""
        if not self.config:
            return {}

        validation = {}

        # Validate LLM Provider
        validation["llm_provider"] = bool(self.config.llm_provider and self.config.llm_choice)

        # Validate Obsidian
        obsidian_path = getattr(self.config, "obsidian_vault_path", None)
        if obsidian_path:
            from pathlib import Path

            validation["obsidian"] = Path(obsidian_path).exists()
        else:
            validation["obsidian"] = False

        # Validate SearXNG
        searxng_url = getattr(self.config, "searxng_base_url", None)
        validation["searxng"] = bool(searxng_url and searxng_url.startswith("http"))

        # Validate Todoist
        todoist_token = getattr(self.config, "todoist_api_token", None)
        validation["todoist"] = bool(todoist_token)

        # Validate YouTube
        youtube_key = getattr(self.config, "youtube_api_key", None)
        validation["youtube"] = bool(youtube_key)

        return validation

    def get_config_info(self) -> str:
        """
        Get current configuration information with validation status.

        Returns:
            Formatted configuration string with status indicators
        """
        if not self.config:
            return "❌ **Configuration not loaded**"

        validation = self.validate_config()

        # Status indicators
        llm_status = "✅" if validation.get("llm_provider", False) else "❌"
        obsidian_status = "✅" if validation.get("obsidian", False) else "⚠️"
        searxng_status = "✅" if validation.get("searxng", False) else "⚠️"
        todoist_status = "✅" if validation.get("todoist", False) else "⚠️"
        youtube_status = "✅" if validation.get("youtube", False) else "⚠️"

        return f"""
**Current Configuration:**
{llm_status} **LLM Provider**: {self._format_provider_name()}/n
{llm_status} **Model**: {self.config.llm_choice}

**MCP Servers:**
{obsidian_status} **Obsidian Vault**: {self._get_vault_name()}/n
{searxng_status} **SearXNG URL**: {getattr(self.config, 'searxng_base_url', 'Not configured')}/n
{todoist_status} **Todoist**: {'Configured' if validation.get('todoist', False) else 'Not configured'}/n
{youtube_status} **YouTube**: {'Configured' if validation.get('youtube', False) else 'Not configured'}
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
            /* Make attachment button small */
            .attach-button {
                min-width: 40px !important;
                max-width: 40px !important;
                width: 40px !important;
                flex: none !important;
            }
            .attach-button button {
                min-width: 40px !important;
                max-width: 40px !important;
                width: 40px !important;
                padding: 4px !important;
                font-size: 16px !important;
            }
            /* Enhanced UI styling */
            .main-container {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }
            .chat-container {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 15px;
                box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
                backdrop-filter: blur(4px);
            }
            .config-panel {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
                backdrop-filter: blur(4px);
            }
            /* Loading indicator */
            .loading-indicator {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #3498db;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            /* Status indicators with better styling */
            .status-good { color: #27ae60; font-weight: bold; }
            .status-warning { color: #f39c12; font-weight: bold; }
            .status-error { color: #e74c3c; font-weight: bold; }
            /* Button enhancements */
            .gradio-button {
                transition: all 0.3s ease;
                border-radius: 8px;
            }
            .gradio-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            /* Input field enhancements */
            .gradio-textbox {
                border-radius: 10px;
                border: 2px solid #e0e0e0;
                transition: all 0.3s ease;
            }
            .gradio-textbox:focus {
                border-color: #3498db;
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.3);
            }
            """,
        ) as interface:

            # Enhanced header with better styling
            gr.HTML(
                """
                <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 20px; color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                    <h1 style="margin: 0; font-size: 2.5em; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">🤖 Productivity Agent</h1>
                    <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">Your intelligent AI assistant with access to notes, web search, tasks, and video analysis</p>
                </div>
                """
            )

            with gr.Row(elem_classes="main-container"):
                with gr.Column(scale=8, elem_classes="chat-container"):
                    # Main chat interface
                    chatbot = gr.Chatbot(
                        label="Chat with Agent",
                        height="70vh",
                        show_label=True,
                        container=True,
                        type="messages",
                        show_copy_button=True,
                        show_share_button=False,
                        render_markdown=True,
                    )

                    with gr.Row():
                        # Hidden file upload that opens explorer directly
                        file_upload = gr.File(
                            file_types=[".txt", ".md", ".pdf", ".docx", ".py", ".js", ".json"],
                            file_count="single",
                            visible=False,
                        )

                        msg = gr.Textbox(
                            label="Message",
                            placeholder="Ask me to search, take notes, manage tasks, or analyze videos...",
                            container=False,
                            scale=4,
                        )
                        # Small attachment button
                        attach_btn = gr.UploadButton(
                            "📎",
                            file_types=[".txt", ".md", ".pdf", ".docx", ".py", ".js", ".json"],
                            file_count="single",
                            size="sm",
                            elem_classes="attach-button",
                        )
                        submit = gr.Button("Send", variant="primary", scale=1)
                        clear = gr.Button("Clear", variant="secondary", scale=1)

                    # Small file indicator (shows when file is attached)
                    file_display = gr.Markdown("", visible=False, container=False)

                    # Loading indicator and progress feedback
                    loading_indicator = gr.HTML("", visible=False)
                    progress_text = gr.Markdown("", visible=False)

                with gr.Column(scale=2, elem_classes="config-panel"):
                    # Clean configuration header
                    gr.HTML(
                        "<h3 style='text-align: center; margin-bottom: 15px; color: #333;'>⚙️ Configuration</h3>"
                    )

                    config_display = gr.Markdown(self.get_config_info(), container=False)

                    with gr.Row():
                        refresh_config = gr.Button("Refresh", variant="secondary", size="sm")
                        validate_config = gr.Button("Validate", variant="primary", size="sm")

                    validation_results = gr.Markdown("", visible=False, container=False)

                    # Clean status section
                    gr.HTML(
                        "<h3 style='text-align: center; margin: 20px 0 10px 0; color: #333;'>📊 Status</h3>"
                    )
                    agent_status = gr.Markdown("🔴 **Agent**: Not initialized", container=False)

                    # Enhanced help with tabs or expandable sections
                    with gr.Accordion("📚 Getting Started Guide", open=False):
                        gr.Markdown(
                            """
                            ## 🚀 Quick Start

                            1. **Check Configuration**: Ensure your `.env` file is properly configured
                            2. **Validate Setup**: Click "Validate" to verify all services

                            """
                        )

                    with gr.Accordion("🔧 Troubleshooting", open=False):
                        gr.Markdown(
                            """
                            ## Common Issues & Solutions

                            ### ❌ Agent Not Responding
                            1. Check if agent status shows "Ready"
                            2. Click "Refresh Config" to reinitialize
                            3. Verify your `.env` file configuration

                            ### ⚠️ MCP Servers Not Working
                            1. Run "Validate Config" to check server status
                            2. Ensure required API keys are configured
                            3. Check that file paths exist (Obsidian vault)

                            ### 🐌 Slow Responses
                            - Large requests may take 15-30 seconds
                            - Vision analysis is processing intensive
                            - Try breaking complex requests into smaller parts

                            ### 📁 File Upload Issues
                            - Supported formats: .txt, .md, .pdf, .docx, .py, .js, .json
                            - Files are processed as context for your next message
                            - Large files may take longer to process

                            ## 🆘 Still Need Help?
                            - Check the validation report for specific issues
                            - Ensure all environment variables are correctly set
                            - Try restarting the interface if issues persist
                            """
                        )

                    with gr.Accordion("⚙️ Advanced Configuration", open=False):
                        gr.Markdown(
                            """
                            ## Environment Variables

                            ### Required for Core Functionality:
                            ```env
                            LLM_PROVIDER=aws|anthropic|openai
                            LLM_CHOICE=claude-3-5-sonnet-20241022|gpt-4o|amazon.nova-lite-v1:0
                            ```

                            ### Optional MCP Servers:
                            ```env
                            OBSIDIAN_VAULT_PATH=/path/to/your/vault
                            SEARXNG_BASE_URL=http://localhost:8080
                            TODOIST_API_TOKEN=your_todoist_api_token
                            YOUTUBE_API_KEY=your_youtube_api_key
                            ```

                            ### AWS Configuration (if using AWS Bedrock):
                            ```env
                            AWS_REGION=us-east-1
                            AWS_ACCESS_KEY_ID=your_access_key
                            AWS_SECRET_ACCESS_KEY=your_secret_key
                            ```

                            ## MCP Server Status Meanings:
                            - ✅ **Working**: Server is configured and accessible
                            - ⚠️ **Optional**: Server is not configured but not required
                            - ❌ **Issue**: Server configuration has problems
                            """
                        )

            # State for message passing
            msg_state = gr.State("")

            # Event handlers
            def add_user_message(message, history, uploaded_file=None):
                """Add user message to history, processing uploaded files if present."""
                final_message = message

                # Process uploaded file if present
                if uploaded_file is not None:
                    file_content = self.process_uploaded_file(uploaded_file)
                    final_message = f"{message}{file_content}"

                if not final_message.strip():
                    return "", history, "", None  # Return None to clear file upload

                history = history + [{"role": "user", "content": final_message}]
                return "", history, final_message, None  # Return message and clear file upload

            def get_response(message, history):
                """Get complete agent response."""
                import logging

                logging.info(f"GUI get_response called with message: {message}")

                if not message.strip():
                    return history

                # Create async event loop for response
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    logging.info("GUI about to call self.chat_response")
                    # Get complete response
                    updated_history = loop.run_until_complete(self.chat_response(message, history))
                    logging.info("GUI chat_response completed")
                    return updated_history
                except Exception as e:
                    # Enhanced error handling for GUI events
                    error_str = str(e).lower()
                    print(f"[GUI EVENT] Response error: {e}")
                    logging.error(f"GUI response error: {e}")
                    import traceback

                    traceback.print_exc()

                    # Categorized error display
                    if "config" in error_str or "initialization" in error_str:
                        error_msg = f"⚙️ **Configuration Error**: {str(e)}\n\n💡 *Check your configuration and try refreshing.*"
                    elif "timeout" in error_str:
                        error_msg = f"⏰ **Processing Timeout**: {str(e)}\n\n💡 *The request took too long. Try a simpler query.*"
                    else:
                        error_msg = f"❌ **Unexpected Error**: {str(e)}\n\n💡 *This may be a temporary issue. Try refreshing the configuration.*"

                    history.append({"role": "assistant", "content": error_msg})
                    return history
                finally:
                    loop.close()

            def show_loading():
                """Show loading indicator."""
                loading_html = """
                <div style="text-align: center; padding: 10px; background: #f8f9fa; border-radius: 10px; border-left: 4px solid #3498db;">
                    <div class="loading-indicator"></div>
                    <span style="margin-left: 10px; color: #3498db; font-weight: 500;">AI is thinking...</span>
                </div>
                """
                progress_msg = "🤖 **Processing your request...** \n\n⏱️ This may take a few moments depending on the complexity of your query."
                return gr.HTML(value=loading_html, visible=True), gr.Markdown(
                    value=progress_msg, visible=True
                )

            def clear_chat():
                """Clear chat history."""
                return (
                    [],
                    "",
                    "",
                    gr.Markdown(visible=False),
                    gr.HTML(visible=False),
                    gr.Markdown(visible=False),
                )  # Clear chat, message, file display, loading indicators

            async def refresh_config_info():
                """Refresh configuration display and reinitialize agent."""
                await self.initialize_agent()
                status = (
                    "🟢 **Agent**: Ready" if self.agent else "🔴 **Agent**: Failed to initialize"
                )
                return self.get_config_info(), status

            def validate_config_handler():
                """Handle configuration validation."""
                if not self.config:
                    return "❌ **No configuration loaded**\n\nPlease check your .env file and refresh the configuration."

                validation = self.validate_config()
                issues = []
                warnings = []

                # Check for critical issues
                if not validation.get("llm_provider", False):
                    issues.append(
                        "❌ **LLM Provider**: Missing or invalid provider/model configuration"
                    )

                # Check for optional but recommended settings
                if not validation.get("obsidian", False):
                    warnings.append("⚠️ **Obsidian**: Vault path not configured or inaccessible")
                if not validation.get("searxng", False):
                    warnings.append("⚠️ **SearXNG**: URL not configured")
                if not validation.get("todoist", False):
                    warnings.append("⚠️ **Todoist**: API token not configured")
                if not validation.get("youtube", False):
                    warnings.append("⚠️ **YouTube**: API key not configured")

                # Generate validation report
                report_lines = ["## Configuration Validation Report\n"]

                if not issues and not warnings:
                    report_lines.append("✅ **All systems operational!**\n")

                if issues:
                    report_lines.append("### ❌ Critical Issues")
                    report_lines.extend(issues)
                    report_lines.append("")
                    report_lines.append("*Fix these issues to ensure the agent works properly.*\n")

                if warnings:
                    report_lines.append("### ⚠️ Optional Components")
                    report_lines.extend(warnings)
                    report_lines.append("")
                    report_lines.append(
                        "*These are optional but enable additional functionality.*\n"
                    )

                report_lines.append("### 💡 Recommendations")
                if issues:
                    report_lines.append("- Check your .env file for missing or incorrect values")
                    report_lines.append("- Verify API keys and file paths are correct")
                    report_lines.append("- Click 'Refresh Config' after making changes")
                else:
                    report_lines.append("- Your configuration looks good!")
                    if warnings:
                        report_lines.append(
                            "- Consider configuring optional components for enhanced functionality"
                        )

                return "\n".join(report_lines)

            def handle_file_attached(file):
                """Handle when a file is attached via the upload button."""
                if file is not None:
                    from pathlib import Path

                    file_name = Path(file.name).name if hasattr(file, "name") else str(file)
                    return f"📎 **File attached**: {file_name}", gr.Markdown(visible=True), file
                else:
                    return "", gr.Markdown(visible=False), None

            # Event connections
            submit.click(
                add_user_message,
                inputs=[msg, chatbot, file_upload],
                outputs=[msg, chatbot, msg_state, file_upload],
                queue=False,
            ).then(get_response, inputs=[msg_state, chatbot], outputs=chatbot, queue=True)

            msg.submit(
                add_user_message,
                inputs=[msg, chatbot, file_upload],
                outputs=[msg, chatbot, msg_state, file_upload],
                queue=False,
            ).then(get_response, inputs=[msg_state, chatbot], outputs=chatbot, queue=True)

            clear.click(
                clear_chat,
                outputs=[
                    chatbot,
                    msg,
                    file_display,
                    file_display,
                    loading_indicator,
                    progress_text,
                ],
            )

            refresh_config.click(refresh_config_info, outputs=[config_display, agent_status])

            validate_config.click(validate_config_handler, outputs=[validation_results])

            # File attachment events
            attach_btn.upload(
                handle_file_attached,
                inputs=[attach_btn],
                outputs=[file_display, file_display, file_upload],
            )

            # Initialize on startup
            interface.load(refresh_config_info, outputs=[config_display, agent_status])

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

        # MCP servers will start/stop per chat message
        if hasattr(gui.agent, "_mcp_servers") and gui.agent._mcp_servers:
            print(f"🔗 MCP servers configured: {len(gui.agent._mcp_servers)} servers")
        else:
            print("ℹ️  No MCP servers configured")

        # Create and launch interface
        interface = gui.create_interface()

        print("🌐 Launching web interface...")
        print("💡 Open your browser to interact with the agent")

        # Launch with appropriate settings
        interface.launch(
            server_name="localhost",
            server_port=7860,
            share=False,
            debug=gui.config.debug_mode if gui.config else False,
            show_error=True,
            quiet=False,
        )
    else:
        print("⚠️  Agent initialization failed - check your configuration")
        print("The GUI will still start, but functionality may be limited")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
