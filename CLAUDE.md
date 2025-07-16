# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a PydanticAI-powered agent with integrated MCP servers for productivity tasks. The agent has access to tools from multiple MCP servers and can use them effectively based on user requests. The system features reliable MCP server integration with health monitoring and error handling.

## Architecture

### Core Components
- **Agent**: PydanticAI agent with MCP server integration and configurable LLM providers (AWS Bedrock, Anthropic Direct, OpenAI) ✅ REFACTORED
- **MCP Servers**: 4 integrated stdio-based servers (Obsidian, SearXNG, Todoist, YouTube) with health monitoring
- **Vision System**: Integrated screenshot capture and visual analysis with model-optimized compression
- **Dependencies**: Async HTTP client, Langfuse observability, and configuration management
- **Error Handling**: Graceful degradation when tools/servers are unavailable
- **GUI**: Gradio chat interface with session memory and conversation history ✅ COMPLETED

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
│   ├── screen_capture.py # Simplified screenshot utilities (50 lines, aspect ratio preservation)
│   ├── bedrock_vision.py # Direct Bedrock API for Nova models (bypasses PydanticAI limitations)
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
LLM_PROVIDER=aws|anthropic|openai
LLM_API_KEY=your_api_key_here
LLM_CHOICE=claude-3-5-sonnet-20241022|gpt-4o|amazon.nova-lite-v1:0|ollama|openrouter
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

#### PydanticAI Agent Refactor ✅ COMPLETED 2025-07-05
- **Core Architecture**: Complete refactor following PydanticAI best practices with proper Agent[AgentDependencies] typing
- **Tool Architecture**: Tools separated into `agent/tools.py` (logic) and `agent/agent.py` (@agent.tool decorators)
- **Reference Pattern Alignment**: Tool structure matches PydanticAI reference implementation with RunContext[AgentDependencies]
- **BinaryContent Integration**: Proper PydanticAI BinaryContent usage for screenshot tools across all models
- **Message History**: Fixed GUI integration with proper PydanticAI ModelMessage types
- **MCP Integration**: Proper MCPServerStdio implementation with context management
- **Test Coverage**: Comprehensive test suite with 96% pass rate (87/91 tests passing)
- **Real Integration**: Tests using actual .env configuration instead of mocks
- **Production Bug Fix**: Resolved critical "Expected code to be unreachable" error

#### Vision System Optimization ✅ COMPLETED 2025-07-05
- **Multi-Provider Support**: Screenshot analysis works with Claude (Anthropic), GPT-4o (OpenAI), and Nova (AWS Bedrock)
- **Aspect Ratio Preservation**: Fixed ultra-wide monitor support (6880x2880 → 1280x536) preventing image distortion
- **Token Optimization**: Reduced screenshot token usage from 31K+ to ~8-12K tokens through proper resizing
- **Bedrock Direct API**: Custom Nova integration bypassing PydanticAI BinaryContent limitations via `utils/bedrock_vision.py`
- **Model-Specific Handling**: Automatic quality adjustment for different model capabilities
- **Ultra-Wide Monitor Support**: Proper handling of 21:9 and wider aspect ratios without distortion
- **Language Agnostic**: Screenshot tools work regardless of user language (no keyword detection)
- **PydanticAI Tool Architecture**: Proper separation of tool logic with BinaryContent for cross-model compatibility

#### MCP Server Integration
- **Reliable Integration**: 4 MCP servers working together effectively
- **Tool Selection**: Agent selects appropriate tools based on request context  
- **Error Handling**: Graceful degradation when tools are unavailable
- **Health Monitoring**: Real-time MCP server status tracking with performance metrics
- **Performance**: Multi-tool tasks complete in 15-30 seconds

#### Gradio Web Interface
- **System Prompt Integration**: Fixed critical bug where system prompts weren't included with message history
- **Session Memory**: Maintains conversation context using PydanticAI's native history
- **Responsive Layout**: Full-width design that adapts to screen size
- **MCP Compatibility**: Handles MCP cancel scope errors gracefully
- **Configuration Display**: Shows current LLM provider, model, and vault info
- **Error Resilience**: Continues functioning when individual tools fail
- **Multi-Model Support**: Works correctly with all LLM providers (AWS, Anthropic, OpenAI)

### Example Usage Patterns
- **Research & Note**: "Research AI agents and create comprehensive notes" → Web search → Note creation → Optional tasks
- **Information Synthesis**: "Compare PydanticAI vs LangChain" → Multiple searches → Comparison note creation
- **Content Curation**: "Organize MCP server info in my knowledge base" → Search → Vault search → Organized note with connections
- **Video Learning**: "Analyze this YouTube video and create study materials" → Video processing → Study notes → Practice tasks
- **Project Planning**: "Plan a RAG system project" → Research → Project note → Task breakdown
- **Visual Analysis**: "What's on my screen?" → Screenshot capture → AI analysis → Detailed description (works with all models)
- **Multi-Language Support**: "Qu'est-ce que tu vois?" → Screenshot analysis → Response in user's language

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

#### Core Testing Commands
```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_agent.py                    # Core agent tests
pytest tests/test_real_integration.py         # Real integration tests
pytest tests/test_gui_integration.py          # GUI integration tests
pytest tests/test_multi_tool_coordination.py  # Multi-tool coordination tests

# Run with verbose output and show print statements
pytest tests/ -v -s

# Run tests with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test class or method
pytest tests/test_agent.py::TestAgent::test_agent_initialization -v
pytest tests/test_multi_tool_coordination.py::TestMultiToolCoordination -v
```

#### Quality Assurance Commands
```bash
# Run code formatting
black .

# Run linting
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Run type checking
mypy --ignore-missing-imports agent/ utils/ config/

# Run all quality checks in sequence
black . && ruff check --fix . && mypy --ignore-missing-imports agent/ utils/ config/ && pytest tests/ -v
```

#### Integration Testing
```bash
# Test configuration loading
python main.py --config-test

# Test MCP server integration
pytest tests/test_real_integration.py -v -s

# Test GUI functionality
python gui.py  # Then test via web interface at localhost:7860
```

#### Debugging and Development
```bash
# Run single test with detailed output
pytest tests/test_agent.py::TestAgent::test_agent_initialization -vv -s --tb=long

# Run tests with specific markers
pytest tests/ -m "not integration" -v  # Skip integration tests
pytest tests/ -m "asyncio" -v         # Run only async tests

# Run tests with failed tests first
pytest tests/ --failed-first -v
```

## Important Constraints

- Never assume external libraries are available - always check existing codebase
- Follow existing patterns for framework choice, naming, and architecture
- Prioritize stdio MCP servers over SSH connections for better integration
- Implement robust error handling for all external service connections
- Maintain clean separation between agent logic, GUI, and tool integrations

## Key Technical Achievements

### Vision System Breakthrough
This session successfully solved multiple critical issues with screenshot analysis:

1. **Model Hallucination Problem**: Fixed severe image distortion caused by forcing ultra-wide aspect ratios (21:9) into 16:9 dimensions
2. **Token Efficiency**: Reduced screenshot processing from 31K+ tokens to 8-12K tokens through proper aspect ratio preservation
3. **Cross-Model Compatibility**: Implemented Nova model support via direct Bedrock API calls when PydanticAI BinaryContent fails
4. **Architecture Alignment**: Refactored tool structure to match PydanticAI reference patterns while maintaining MCP integration

### Technical Implementation Details
- **Ultra-Wide Monitor Support**: Preserve original aspect ratio (6880x2880 → 1280x536) instead of forcing 16:9
- **Model-Specific Handling**: Detect Nova models and use `utils/bedrock_vision.py` for direct API calls
- **Tool Separation**: Tools in `agent/tools.py` return BinaryContent, wrapped by `@agent.tool` decorators in `agent/agent.py`
- **Error Resilience**: Graceful handling of vision API failures with meaningful error messages

### PydanticAI Architecture Patterns
The refactoring aligned the codebase with official PydanticAI patterns:

**Agent Structure** (`agent/agent.py`):
```python
# Tools registered inline with @agent.tool decorators
@agent.tool
async def take_screenshot(ctx: RunContext[AgentDependencies], quality: int = 75) -> BinaryContent:
    return await take_screenshot_tool(ctx.deps, quality)
```

**Tool Logic** (`agent/tools.py`):
```python
# Actual implementation separated from decorators
async def take_screenshot_tool(deps: AgentDependencies, quality: int = 75) -> BinaryContent:
    image_bytes = take_screenshot(quality)
    return BinaryContent(data=image_bytes, media_type="image/jpeg")
```

**Model-Specific Handling** (Nova bypass):
```python
# Direct Bedrock API when PydanticAI BinaryContent fails
if should_use_bedrock_direct(ctx.deps.config):
    analysis = await analyze_image_with_bedrock(image_bytes, prompt, ctx.deps.config)
    return analysis  # Return text instead of BinaryContent
```