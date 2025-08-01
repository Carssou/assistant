"""
Streamlit GUI for Strands Agents productivity assistant.

Modern streaming interface with native session management and MCP support.
"""

import asyncio
import logging

import streamlit as st

from agent.agent import agent_manager
from config.settings import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamlitGUI:
    """Streamlit interface for Strands agents with MCP support."""

    def __init__(self):
        """Initialize the Streamlit GUI."""
        self.agent_manager = agent_manager
        self.config = None

    async def initialize_config(self) -> bool:
        """Initialize configuration."""
        try:
            self.config = load_config()
            return True
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False

    async def get_streaming_response(self, message: str):
        """Get streaming response using Strands native streaming."""
        try:
            accumulated_text = ""
            async for chunk in self.agent_manager.stream_with_mcp(message):
                # Extract text from Strands streaming events
                if isinstance(chunk, dict):
                    if "event" in chunk:
                        event = chunk["event"]
                        if "contentBlockDelta" in event and "delta" in event["contentBlockDelta"]:
                            delta = event["contentBlockDelta"]["delta"]
                            if "text" in delta:
                                accumulated_text += delta["text"]
                                yield accumulated_text
                    elif "result" in chunk:
                        # Final result - extract complete text
                        result = chunk["result"]
                        if hasattr(result, "message") and result.message.get("content"):
                            content = result.message["content"]
                            if isinstance(content, list) and len(content) > 0:
                                if isinstance(content[0], dict) and "text" in content[0]:
                                    yield content[0]["text"]
        except Exception as e:
            yield f"❌ **Error**: {str(e)}"


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "gui" not in st.session_state:
        st.session_state.gui = StreamlitGUI()
    if "config_loaded" not in st.session_state:
        st.session_state.config_loaded = False


async def load_configuration():
    """Load configuration asynchronously."""
    if not st.session_state.config_loaded:
        success = await st.session_state.gui.initialize_config()
        st.session_state.config_loaded = success
        return success
    return True


def display_config_info():
    """Display configuration information in sidebar."""
    gui = st.session_state.gui

    if not gui.config:
        st.sidebar.error("❌ Configuration not loaded")
        return

    st.sidebar.success("✅ Configuration loaded")
    # Format provider name for display
    provider_str = str(gui.config.llm_provider)
    if hasattr(gui.config.llm_provider, "value"):
        provider_str = gui.config.llm_provider.value
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

    formatted_provider = provider_names.get(provider_str.lower(), provider_str.title())
    st.sidebar.write(f"**Provider:** {formatted_provider}")
    st.sidebar.write(f"**Model:** {gui.config.llm_choice}")

    # MCP server info
    mcp_count = len(gui.agent_manager.mcp_servers)
    native_tools = len(gui.agent_manager.native_agent.tool_names)
    mcp_tools = len(gui.agent_manager._mcp_tools)

    st.sidebar.write(f"**Tools:** {native_tools} native + {mcp_tools} MCP")
    st.sidebar.write(f"**MCP Servers:** {mcp_count}")

    # MCP status
    st.sidebar.write("**Status:** Ready")


def display_chat_history():
    """Display chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


async def handle_user_input(prompt: str):
    """Handle user input with streaming response."""
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display streaming assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            async for chunk in st.session_state.gui.get_streaming_response(prompt):
                full_response = chunk
                response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"❌ **Error**: {str(e)}"
            response_placeholder.markdown(full_response)

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Strands Agent", page_icon="🚀", layout="wide", initial_sidebar_state="expanded"
    )

    # Initialize session state
    initialize_session_state()

    # Header
    st.title("🚀 Strands Agent")
    st.markdown("AI productivity assistant with native MCP integration")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")

        # Load configuration
        if st.button("🔄 Refresh Config"):
            st.session_state.config_loaded = False

        # Display config info
        if asyncio.run(load_configuration()):
            display_config_info()
        else:
            st.error("Failed to load configuration")
            return

        # Controls
        st.header("Controls")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.gui.agent_manager.native_agent.messages.clear()
            st.rerun()

    # Main chat interface
    st.header("Chat")

    # Display chat history
    display_chat_history()

    # Chat input
    if prompt := st.chat_input("Ask me to search, take notes, manage tasks, or analyze content..."):
        # Use asyncio to handle the streaming response
        asyncio.run(handle_user_input(prompt))
        st.rerun()


if __name__ == "__main__":
    main()
