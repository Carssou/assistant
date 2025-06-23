# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PydanticAI-powered agent with a Gradio chat GUI that integrates multiple MCP servers for productivity tasks. The agent combines note management (Obsidian), web search (SearXNG), task management (Todoist), and video processing (YouTube) capabilities.

## Architecture

### Core Components
- **Agent**: PydanticAI agent with MCP server integration and configurable LLM providers (AWS Bedrock preferred, OpenAI fallback)
- **GUI**: Gradio chat interface with streaming responses and configuration management
- **MCP Servers**: Multiple stdio-based servers for different productivity tools
- **Dependencies**: Async HTTP client, logging, and configuration management

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
│   ├── agent.py          # Main PydanticAI agent
│   ├── dependencies.py   # Dependency injection container
│   └── prompts.py        # System prompts and templates
├── mcp_servers/
│   └── configs.py        # MCP server configurations
├── tools/
│   └── __init__.py       # Tool utilities (MCP servers provide direct integration)
└── utils/
    └── logger.py         # Logging configuration
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

### Multi-Tool Coordination Examples
- **Research & Note**: Search web → agent analyzes results → creates structured research note → generates follow-up tasks
- **Video Learning**: Get YouTube video data → agent summarizes content → creates study notes with proper titles → adds tasks if needed
- **Information Synthesis**: Search multiple sources → agent synthesizes information → creates comprehensive note → organizes in vault with tags

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

# Gradio GUI (planned for future implementation)
# python gui.py
```

### Testing
```bash
pytest tests/
pytest tests/test_specific_module.py  # Single test file
```

## Important Constraints

- Never assume external libraries are available - always check existing codebase
- Follow existing patterns for framework choice, naming, and architecture
- Prioritize stdio MCP servers over SSH connections for better integration
- Implement robust error handling for all external service connections
- Maintain clean separation between agent logic, GUI, and tool integrations