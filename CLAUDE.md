# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PydanticAI-powered agent with integrated MCP servers for productivity tasks. The agent has access to tools from multiple MCP servers and can use them effectively based on user requests. The system features reliable MCP server integration with health monitoring and error handling.

## Architecture

### Core Components
- **Agent**: PydanticAI agent with MCP server integration and configurable LLM providers (AWS Bedrock preferred, OpenAI fallback) ✅ REFACTORED
- **MCP Servers**: 4 integrated stdio-based servers (Obsidian, SearXNG, Todoist, YouTube) with health monitoring
- **Vision System**: Integrated screenshot capture and visual analysis with model-optimized compression
- **Dependencies**: Async HTTP client, Langfuse observability, and configuration management
- **Error Handling**: Graceful degradation when tools/servers are unavailable
- **GUI**: Gradio chat interface with streaming responses and session memory ✅ COMPLETED

### Project Structure
```
project/
├── .env.example
├── requirements.txt
├── main.py                # Entry point
├── gui.py                 # Gradio interface
├── config/
│   └── settings.py        # Pydantic configuration models
├── agent/
│   ├── agent.py          # Main PydanticAI agent (REFACTORED)
│   ├── tools.py          # Tool registration and definitions
│   ├── dependencies.py   # Dependency injection container
│   └── prompts.py        # System prompts and templates
├── mcp_servers/
│   └── configs.py        # MCP server configurations
├── tools/
│   └── __init__.py       # Tool utilities (MCP servers provide direct integration)
├── utils/
│   ├── logger.py         # Langfuse observability integration
│   ├── server_monitor.py # MCP server health monitoring
│   └── graceful_degradation.py # Tool failure handling
└── docs/
    └── usage_examples.md # Human-readable usage examples
```

## MCP Server Integration

### Configured Servers
1. **Obsidian MCP**: `npx -y obsidian-mcp-pydanticai /path/to/vault` (note management) - Our enhanced fork
2. **SearXNG MCP**: Privacy-focused web search via local SearXNG instance
3. **Todoist MCP**: Task management via stdio MCP server
4. **YouTube MCP**: Video analysis and intelligent summarization - Our enhanced fork with agent-friendly design

### Environment Variables
```env
# LLM Configuration
LLM_PROVIDER=aws|openai
LLM_API_KEY=your_api_key_here
LLM_CHOICE=claude-3-5-sonnet|gpt-4o
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# MCP Server Configuration
OBSIDIAN_VAULT_PATH=/path/to/your/vault
SEARXNG_BASE_URL=http://localhost:8080
TODOIST_API_TOKEN=your_todoist_api_token
YOUTUBE_API_KEY=your_youtube_api_key
```

## Development Guidelines

### Code Standards
- Follow PEP8 and use type hints throughout
- Use Pydantic models for data validation and configuration
- Format code with `black`
- Write Google-style docstrings for all functions
- Never create files longer than 500 lines - refactor into modules

### Testing Requirements
- Create Pytest unit tests for all new features in `/tests` folder
- Test structure should mirror main app structure
- Include tests for: expected use, edge cases, and failure scenarios
- Always test individual functions for agent tools
- Update existing tests when modifying logic

### Task Management
- Always read `PLANNING.md` at start of new conversations
- Check `TASKS.md` before starting work and add new tasks with dates
- Mark completed tasks immediately in `TASKS.md`
- Add discovered sub-tasks under "Discovered During Work" section

### Agent Development Patterns
- Use dependency injection container for shared resources:
```python
@dataclass
class AgentDependencies:
    http_client: AsyncClient
    config: AgentConfig
    logger: Logger
    vault_path: Path
```
- Implement graceful error handling and recovery
- Design for extensibility - easy addition of new MCP servers
- Maintain modular architecture for tool integration

## Common Workflows

### Adding New MCP Server
1. Add server configuration function to `mcp_servers/configs.py`
2. Update environment variables in `.env.example`
3. Add server to `create_all_mcp_servers()` function
4. Add integration tests
5. Tools are automatically available via MCP protocol

### System Features ✅ COMPLETED

#### PydanticAI Agent Refactor ✅ COMPLETED 2025-06-30
- **Core Architecture**: Complete refactor following PydanticAI best practices
- **Tool Organization**: All tools moved to `agent/tools.py` with `register_tools()` function
- **Message History**: Fixed GUI integration with proper PydanticAI ModelMessage types
- **MCP Integration**: Proper MCPServerStdio implementation with context management
- **Test Coverage**: Comprehensive test suite with 96% pass rate (87/91 tests passing)
- **Real Integration**: Tests using actual .env configuration instead of mocks
- **Production Bug Fix**: Resolved critical "Expected code to be unreachable" error

#### MCP Server Integration
- **Reliable Integration**: 4 MCP servers working together effectively
- **Tool Selection**: Agent selects appropriate tools based on request context  
- **Error Handling**: Graceful degradation when tools are unavailable
- **Health Monitoring**: Real-time MCP server status tracking with performance metrics
- **Performance**: Multi-tool tasks complete in 15-30 seconds

#### Gradio Web Interface
- **Streaming Responses**: Real-time progressive text streaming with proper formatting
- **Session Memory**: Maintains conversation context using PydanticAI's native history
- **Responsive Layout**: Full-width design that adapts to screen size
- **MCP Compatibility**: Handles MCP cancel scope errors gracefully
- **Configuration Display**: Shows current LLM provider, model, and vault info
- **Error Resilience**: Continues functioning when individual tools fail

### Example Usage Patterns
- **Research & Note**: "Research AI agents and create comprehensive notes" → Web search → Note creation → Optional tasks
- **Information Synthesis**: "Compare PydanticAI vs LangChain" → Multiple searches → Comparison note creation
- **Content Curation**: "Organize MCP server info in my knowledge base" → Search → Vault search → Organized note with connections
- **Video Learning**: "Analyze this YouTube video and create study materials" → Video processing → Study notes → Practice tasks
- **Project Planning**: "Plan a RAG system project" → Research → Project note → Task breakdown

## Development Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running
```bash
# Test configuration and model setup
python main.py --config-test

# Interactive CLI interface
python main.py

# Single query mode
python main.py --query "Hello, test message"

# Gradio GUI interface
python gui.py
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_agent.py          # Core agent tests
pytest tests/test_real_integration.py  # Real integration tests
pytest tests/test_gui_integration.py   # GUI integration tests

# Run with verbose output
pytest tests/ -v -s
```

## Important Constraints

- Never assume external libraries are available - always check existing codebase
- Follow existing patterns for framework choice, naming, and architecture
- Prioritize stdio MCP servers over SSH connections for better integration
- Implement robust error handling for all external service connections
- Maintain clean separation between agent logic, GUI, and tool integrations