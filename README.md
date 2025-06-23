# Multi-Tool AI Agent

A PydanticAI-powered agent that intelligently coordinates multiple MCP servers for seamless productivity workflows. Unlike rigid workflow engines, this agent uses natural language to dynamically orchestrate tools based on user intent.

## Key Features

- **🔄 Multi-Tool Coordination**: Intelligent orchestration across all productivity tools
- **📝 Note Management**: Obsidian vault integration with 11+ note operations
- **🔍 Privacy-Focused Search**: SearXNG integration for secure web research
- **✅ Task Management**: Todoist integration for comprehensive task handling
- **🎥 Video Analysis**: Enhanced YouTube processing with intelligent summarization
- **🧠 AI-First Architecture**: Natural language coordination instead of rigid workflows
- **⚡ Performance**: Complex workflows complete in 15-30 seconds
- **🛡️ Graceful Degradation**: Automatic fallbacks when tools are unavailable
- **📊 Health Monitoring**: Real-time MCP server status tracking

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

# GUI interface (planned for future)
# python gui.py
```

## Multi-Tool Coordination Examples

The agent intelligently coordinates multiple tools based on your natural language requests:

### Research & Documentation
```bash
"Research the latest developments in transformer architectures and create study notes"
```
**What happens:** Web search → Analysis → Structured note creation → Optional follow-up tasks

### Content Curation
```bash
"Find information about PydanticAI vs LangChain and create a comprehensive comparison"
```
**What happens:** Multiple searches → Source analysis → Synthesis → Organized comparison note

### Learning Workflows
```bash
"Analyze this YouTube video about machine learning and create study materials"
```
**What happens:** Video processing → Key insights extraction → Study notes → Practice tasks

### Knowledge Integration
```bash
"Search for MCP server documentation and organize it in my knowledge base"
```
**What happens:** Search → Read sources → Check existing notes → Create organized content → Link connections

See [Multi-Tool Workflows Documentation](docs/multi_tool_workflows.md) for detailed examples.

## Configuration

### LLM Providers

- **AWS Bedrock** (preferred): Configure AWS credentials and region
- **OpenAI**: Set API key for fallback option

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

```
project/
├── agent/              # PydanticAI agent implementation
│   ├── agent.py       # Main agent with multi-tool coordination
│   ├── dependencies.py # Dependency injection container  
│   └── prompts.py     # Dynamic system prompts with coordination logic
├── config/            # Configuration management
├── mcp_servers/       # MCP server configurations
├── tools/             # Tool utilities and wrapper functions
├── utils/             # Shared utilities
│   ├── logger.py      # Langfuse integration
│   ├── server_monitor.py     # Health monitoring
│   └── graceful_degradation.py # Tool failure handling
├── tests/             # Comprehensive unit tests
├── docs/              # Human-readable documentation
│   └── multi_tool_workflows.md # Coordination examples
├── main.py            # CLI entry point
└── gui.py             # Gradio GUI (planned)
```

### AI-First Coordination

This agent uses **natural language coordination** instead of rigid workflow graphs:

**Traditional Approach (LangGraph):**
```python
# Must explicitly program every workflow path
workflow.add_edge("search", "create_note")
workflow.add_edge("create_note", "create_task")
# Breaks when you add new tools
```

**AI-First Approach (This Agent):**
```
"Research AI and create notes with follow-up tasks"
# Agent figures out optimal tool sequence automatically
# Works with any new MCP servers or novel requests
```

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