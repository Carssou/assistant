# Strands Agents Productivity Assistant

A Strands Agents-powered productivity assistant with native MCP integration and multi-tool coordination. The agent seamlessly combines native tools with MCP servers for optimal performance and flexibility.

## Features

- **📝 Note Management**: Native Obsidian vault integration with 10 optimized note operations
- **🔍 Privacy-Focused Search**: SearXNG integration for secure web research
- **✅ Task Management**: Todoist integration for comprehensive task handling
- **🎥 Video Analysis**: Enhanced YouTube processing with intelligent summarization
- **👁️ Vision System**: Multi-model screenshot analysis (Claude, OpenAI, Amazon Nova) with ultra-wide monitor support
- **⚡ Strands Architecture**: Native MCP integration with automatic tool discovery and health monitoring
- **🛡️ Error Handling**: Graceful degradation when tools are unavailable
- **🌐 Modern Interface**: Streamlit GUI with real-time streaming and session management
- **🔧 Model Flexibility**: Easy switching between AWS Bedrock, Anthropic, and OpenAI providers

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

Required configuration:
```env
# LLM Configuration
LLM_PROVIDER=aws|anthropic|openai
LLM_CHOICE=claude-3-5-sonnet-20241022|gpt-4o|amazon.nova-lite-v1:0

# MCP Server Configuration  
OBSIDIAN_VAULT_PATH=/path/to/your/vault
SEARXNG_BASE_URL=http://localhost:8080
TODOIST_API_TOKEN=your_todoist_api_token
YOUTUBE_API_KEY=your_youtube_api_key
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

# Streamlit GUI interface (recommended)
python streamlit_gui.py
```

## Usage Examples

The agent uses Strands' native multi-tool coordination to accomplish complex tasks:

### Research & Documentation

```bash
"Research the latest developments in transformer architectures and create study notes"
```

**Agent uses:** Web search → Note creation → Optional task creation

### Content Synthesis

```bash
"Find information about Strands Agents vs LangChain and create a comprehensive comparison"
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

## Architecture

### Strands Agents Implementation

This project has been fully migrated to Strands Agents architecture, providing:

- **Native MCP Integration**: Seamless MCP server discovery and tool registration
- **Multi-Model Support**: Easy switching between AWS Bedrock, Anthropic, and OpenAI
- **Streaming Responses**: Real-time response streaming with proper event handling
- **Tool Flexibility**: Simple `@tool` decorators for rapid development

```
project/
├── agent/                  # Strands Agents implementation
│   ├── agent.py           # Main agent with native MCP integration
│   ├── tools.py           # Native tool implementations  
│   └── prompts.py         # System prompts and templates
├── tools/                  # Native tool implementations for optimal performance
│   └── obsidian/          # High-performance native Obsidian operations
│       ├── core.py        # CRUD operations (create, read, edit, delete)
│       ├── search.py      # Advanced search and tags functionality
│       ├── tags.py        # Tag management operations
│       └── utils.py       # Security and path validation utilities
├── config/                 # Configuration management
├── mcp_servers/            # MCP server configurations (SearXNG, Todoist, YouTube)
├── utils/                  # Shared utilities
│   ├── screen_capture.py  # Screenshot functionality with aspect ratio preservation
│   ├── bedrock_vision.py  # Direct Bedrock API for Nova models
│   ├── logger.py          # Langfuse integration
│   └── server_monitor.py  # Health monitoring
├── tests/                  # Comprehensive test suite
├── streamlit_gui.py        # Modern Streamlit interface
└── main.py                # CLI entry point
```

### Hybrid Tool Architecture

**Native Tools (High Performance):**
- **Obsidian**: 10 optimized operations using `@tool` decorators
- **Vision System**: Screenshot capture and analysis
- **Screen Info**: Display configuration utilities

**MCP Servers (External Services):**
- **SearXNG**: Privacy-focused web search
- **Todoist**: Task management and organization
- **YouTube**: Video analysis and summarization

### Strands Advantages

**Model Flexibility:**
- Seamless provider switching (AWS ↔ Anthropic ↔ OpenAI)
- Model-specific optimizations (Nova direct API, etc.)
- Dynamic model selection based on task requirements

**Native MCP Support:**
- Automatic MCP server discovery
- Built-in health monitoring
- Simplified configuration
- Tool hot-reloading for development

**Streaming & Performance:**
- Real-time response streaming
- Native event handling
- Persistent agent sessions
- Optimized tool execution

## Configuration

### LLM Providers

- **AWS Bedrock**: Configure AWS credentials and region for Amazon Nova, Claude, and other models
- **Anthropic Direct**: Direct Claude API access (no AWS account needed)  
- **OpenAI**: GPT models with API key

### Tool Configuration

1. **Obsidian (Native)**: Set `OBSIDIAN_VAULT_PATH` to your vault location
2. **SearXNG (MCP)**: Requires Docker - run `docker-compose up -d` to start local instance
3. **Todoist (MCP)**: Add your Todoist API token
4. **YouTube (MCP)**: YouTube Data API v3 key recommended for full metadata

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

## Development

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agent.py

# Test with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check --fix .

# Type checking
mypy --ignore-missing-imports agent/ utils/ config/
```

### Development Commands

```bash
# Test configuration
python main.py --config-test

# Interactive CLI
python main.py

# Single query test
python main.py --query "test message"

# Streamlit GUI (development)
streamlit run streamlit_gui.py
```

## Tool Integrations

### Native Tools (Strands @tool)
- **Obsidian**: Native Strands implementation with 10 optimized operations
  - Core: create, read, edit, delete notes
  - Advanced: search, tag management, bulk operations
  - Performance: Sub-second response times, no MCP overhead
- **Vision**: Screenshot capture and multi-model analysis
- **Screen Info**: Display configuration and technical details

### MCP Servers (Native Integration)
- [mcp-searxng](https://github.com/ihor-sokoliuk/mcp-searxng) - Privacy-focused web search
- [todoist-mcp-server](https://github.com/abhiz123/todoist-mcp-server) - Task management
- [youtube-video-summarizer-mcp-pydanticai](https://github.com/Carssou/youtube-video-summarizer-mcp-pydanticai) - Enhanced video analysis (our fork)

### Performance Optimization

**Why Native vs MCP?**
- **Native Tools**: Critical operations (note management, vision) run directly using Strands `@tool` decorators
- **MCP Servers**: External services benefit from MCP's standardization and Strands' native integration
- **Result**: Optimal performance for local operations while maintaining MCP ecosystem benefits

## Migration from PydanticAI

This project was successfully migrated from PydanticAI to Strands Agents, achieving:

✅ **100% Feature Parity**: All functionality preserved  
✅ **Performance Maintained**: No regression in operation speed  
✅ **Enhanced Capabilities**: Native MCP integration, better streaming  
✅ **Simplified Architecture**: Cleaner `@tool` patterns, less boilerplate  
✅ **Modern Interface**: Streamlit GUI with real-time streaming  

Key improvements:
- Native MCP integration (no custom workarounds)
- Model-agnostic architecture with easy provider switching
- Real-time streaming responses
- Simplified tool development with `@tool` decorators
- Better error handling and graceful degradation

## License

MIT License