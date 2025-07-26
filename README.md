# PydanticAI Productivity Agent

A PydanticAI-powered agent with integrated MCP servers for productivity tasks. The agent has access to multiple tools across note management, web search, task management, and video processing.

## Features

- **📝 Note Management**: Obsidian vault integration with 11+ note operations
- **🔍 Privacy-Focused Search**: SearXNG integration for secure web research
- **✅ Task Management**: Todoist integration for comprehensive task handling
- **🎥 Video Analysis**: Enhanced YouTube processing with intelligent summarization
- **👁️ Vision System**: Multi-model screenshot analysis (Claude, OpenAI, Amazon Nova) with ultra-wide monitor support
- **🔧 MCP Server Integration**: 4 reliable MCP servers with health monitoring
- **🛡️ Error Handling**: Graceful degradation when tools are unavailable
- **⚡ Performance**: Tool operations complete quickly with proper error recovery
- **🌐 Web Interface**: Gradio GUI with session memory and conversation history

## Requirements

- Python 3.8+
- Docker and Docker Compose (for SearXNG web search)
- Git

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/Carssou/assistant.git
cd assistant

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start SearXNG (Web Search)

```bash
# Start SearXNG Docker container for web search functionality
docker-compose up -d
```

This will start a local SearXNG instance at `http://localhost:8080` with JSON API enabled.

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

### 4. Test Configuration

```bash
# Test configuration and model setup
python main.py --config-test
```

### 5. Run the Application

```bash
# CLI interface (interactive mode)
python main.py

# Single query mode
python main.py --query "Hello, can you introduce yourself?"

# Multi-tool coordination examples
python main.py --query "Research AI agents and create comprehensive notes"
python main.py --query "Find MCP server resources and organize them in my knowledge base"

# Gradio GUI interface
python gui.py
```

## Usage Examples

The agent can use multiple tools to accomplish complex tasks:

### Research & Documentation

```bash
"Research the latest developments in transformer architectures and create study notes"
```

**Agent uses:** Web search → Note creation → Optional task creation

### Content Synthesis

```bash
"Find information about PydanticAI vs LangChain and create a comprehensive comparison"
```

**Agent uses:** Multiple searches → Note creation with comparison format

### Video Analysis

```bash
"Analyze this YouTube video about machine learning and create study materials"
```

**Agent uses:** Video processing → Study note creation

### Visual Assistance

```bash
"What's on my screen?" or "Can you see my screen?" or "Qu'est-ce que tu vois?"
```

**Agent uses:** Screenshot capture → Visual analysis → Detailed description (works with all models)

### Knowledge Organization

```bash
"Search for MCP server documentation and organize it in my knowledge base"
```

**Agent uses:** Search → Vault search → Note creation with connections

See [Usage Examples Documentation](docs/usage_examples.md) for more details.

## Configuration

### LLM Providers

- **AWS Bedrock**: Configure AWS credentials and region for Amazon Nova, Claude (gated), LLaMA, and other models
- **Anthropic Direct**: Direct Claude API access (no AWS account needed)
- **OpenAI**: GPT models with API key

### MCP Servers

1. **Obsidian**: Set `OBSIDIAN_VAULT_PATH` to your vault location
2. **SearXNG**: Requires Docker - run `docker-compose up -d` to start local instance
3. **Todoist**: Add your Todoist API token
4. **YouTube**: YouTube Data API v3 key recommended for full metadata (works without key using fallbacks)

#### SearXNG Setup

The project includes a pre-configured Docker setup for SearXNG:

```bash
# Start SearXNG
docker-compose up -d

# Check if running
curl http://localhost:8080

# Stop SearXNG
docker-compose down
```

The configuration automatically enables JSON API access required for the MCP server integration.

## Architecture

### Major Refactoring (July 2025)

This project underwent a comprehensive architectural refactoring to simplify the PydanticAI implementation and align it with framework best practices. The refactoring focused on removing unnecessary complexity and making the codebase more maintainable and learnable.

```
project/
├── agent/              # Simplified PydanticAI agent (refactored 2025-07-24)
│   ├── agent.py       # Clean agent following PydanticAI patterns - agent created at module level
│   ├── tools.py       # Tool implementations with specific parameter passing
│   └── prompts.py     # Dynamic system prompts with coordination logic
├── config/            # Configuration management
├── mcp_servers/       # MCP server configurations
├── utils/             # Shared utilities
│   ├── screen_capture.py     # Simplified screenshot functionality (50 lines, aspect ratio preservation)
│   ├── bedrock_vision.py     # Direct Bedrock API for Nova models (bypasses PydanticAI limitations)
│   ├── logger.py      # Langfuse integration
│   ├── server_monitor.py     # Health monitoring
│   └── graceful_degradation.py # Tool failure handling
├── tests/             # Simplified test structure matching new architecture
│   ├── test_agent.py  # Core agent functionality tests
│   ├── test_gui_integration.py # GUI integration tests
│   ├── test_real_integration.py # Real .env config tests
│   └── test_*.py      # Additional test modules
├── docs/              # Human-readable documentation
├── main.py            # CLI entry point
└── gui.py             # Gradio web interface
```

### Architectural Simplifications

**Before:**
- Complex factory functions for agent creation
- Separate `agent/dependencies.py` with factory patterns
- Tools receiving entire dependency objects
- Enterprise-style complexity patterns

**After (PydanticAI Best Practices):**
- Simple module-level agent creation: `agent = Agent(...)`
- Dependencies defined as simple `@dataclass` in `agent.py`
- Tools receive only specific parameters they need
- Clean, documentation-aligned patterns

### Agent Architecture

This is a simplified PydanticAI agent following framework best practices:

**Tool Access:**

- Agent has access to tools from 4 MCP servers plus integrated vision system
- Agent decides which tools to use based on context
- Natural language requests → appropriate tool calls
- Multi-model vision integration (Claude, OpenAI, Amazon Nova) with automatic fallback handling

**Error Handling:**

- Health monitoring for MCP servers
- Graceful degradation when tools are unavailable
- Alternative tool suggestions when primary tools fail

## Development

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config.py

# Test with verbose output
pytest tests/ -v
```

### Code Formatting

```bash
black .
```

### Development Commands

```bash
# Test configuration
python main.py --config-test

# Interactive CLI
python main.py

# Single query test
python main.py --query "test message"
```

## MCP Servers

This project integrates the following MCP servers:

- [obsidian-mcp-pydanticai](https://github.com/Carssou/obsidian-mcp-pydanticai) - Enhanced note management (our fork)
- [mcp-searxng](https://github.com/ihor-sokoliuk/mcp-searxng) - Privacy-focused web search
- [todoist-mcp-server](https://github.com/abhiz123/todoist-mcp-server) - Task management
- [youtube-video-summarizer-mcp-pydanticai](https://github.com/Carssou/youtube-video-summarizer-mcp-pydanticai) - Enhanced video analysis (our fork)

### Enhanced Forks

We've created enhanced versions of MCP servers to improve agent integration:

- **Obsidian Fork**: Fixed tool naming compatibility for PydanticAI
- **YouTube Fork**: Returns structured JSON data for intelligent agent analysis, supports both underscore and hyphen naming conventions, includes YouTube Data API v3 integration with multiple fallback strategies

## License

MIT License
