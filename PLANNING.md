# Multi-Purpose AI Agent Planning Document

## Project Overview

**Goal**: Create a PydanticAI-powered agent with a chat GUI that integrates specific MCP servers for productivity tasks. Start simple and iterate to add more capabilities.

## Architecture Overview

### Core Components

1. **Main Agent** (`main.py`)

   - PydanticAI Agent with selected MCP servers
   - LLM provider support (AWS Bedrock preferred, OpenAI fallback)
   - Environment-based configuration
   - Dependency injection for shared resources

2. **GUI Interface**

   - Gradio chat interface
   - Simple chat-based interaction
   - Configuration management
   - Real-time agent responses

3. **MCP Server Integration**
   - **Obsidian MCP**: `obsidian-mcp` stdio server for note management
   - **SearXNG MCP**: `mcp-searxng` stdio server for web search
   - **Todoist MCP**: `todoist-mcp-server` (SSH, potentially rebuild as stdio)
   - **YouTube MCP**: `youtube-video-summarizer-mcp` stdio server for video processing

### Agent Capabilities

Based on the selected MCP servers:

#### Primary Functions

- **Note Management** (Obsidian): Create, read, search, and organize vault notes
- **Web Search** (SearXNG): Privacy-focused search and information gathering
- **Task Management** (Todoist): Create, update, and manage tasks
- **Video Processing** (YouTube): Summarize YouTube videos and extract insights

#### Extensible Design

- Easy addition of new MCP servers
- Modular tool integration
- Scalable chat interface

## Technical Stack

### Core Framework

- **PydanticAI**: Main agent framework with MCP support
- **Python 3.10+**: Required for MCP integration
- **AsyncIO**: Asynchronous operations

### GUI Framework

- **Gradio**: Chat interface with built-in chat components for AI applications
- **Rich**: Enhanced console output for development

### MCP Servers (stdio transport)

```python
# Planned MCP server configurations
servers = [
    MCPServerStdio('npx', args=['-y', 'obsidian-mcp-pydanticai', vault_path]),  # stdio (fixed fork)
    MCPServerStdio('python', args=['searxng-mcp-server.py']),        # stdio
    MCPServerStdio('npx', args=['-y', '@abhiz123/todoist-mcp-server']),  # SSH (may rebuild)
    MCPServerStdio('python', args=['youtube-summarizer-mcp.py'])     # stdio
]
```

### Dependencies

- **HTTPX**: Async HTTP client
- **Logfire**: Optional instrumentation
- **dotenv**: Configuration management

## Environment Configuration

```env
# LLM Configuration
LLM_PROVIDER=aws|openai
LLM_BASE_URL=  # For OpenAI or custom endpoints
LLM_API_KEY=your_api_key_here
LLM_CHOICE=claude-3-5-sonnet|gpt-4o
AWS_REGION=us-east-1  # For AWS Bedrock
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Obsidian MCP Server Configuration
OBSIDIAN_VAULT_PATH=/path/to/your/vault
OBSIDIAN_DAILY_NOTES_PATH=Daily Notes  # Optional: subfolder for daily notes
OBSIDIAN_TEMPLATES_PATH=Templates      # Optional: templates folder

# SearXNG MCP Server Configuration
SEARXNG_BASE_URL=http://localhost:8080  # Your SearXNG instance URL
SEARXNG_API_KEY=your_searxng_api_key    # Optional: if your instance requires auth

# Todoist MCP Server Configuration
TODOIST_API_TOKEN=your_todoist_api_token
TODOIST_PROJECT_ID=your_default_project_id  # Optional: default project

# YouTube MCP Server Configuration
YOUTUBE_API_KEY=your_youtube_api_key         # Optional: for enhanced features
YOUTUBE_TRANSCRIPT_LANGUAGE=en              # Optional: default transcript language

# Optional: Development & Monitoring
LOG_LEVEL=INFO
LOGFIRE_TOKEN=your_logfire_token
DEBUG_MODE=false

# Optional: GUI Configuration
GUI_THEME=default                            # Gradio theme
GUI_PORT=7860                               # Default Gradio port
GUI_SHARE=false                             # Enable public sharing
```

## MCP Server Details

### 1. Obsidian MCP Server

- **Repository**: https://github.com/Carssou/obsidian-mcp-pydanticai (forked from StevenStavrakis/obsidian-mcp)
- **Type**: stdio server (no installation needed)
- **Configuration**: `npx -y obsidian-mcp-pydanticai /path/to/vault`
- **Expected Tools**: read-note, create-note, search-vault, edit-note, delete-note
- **Note**: Fixed for PydanticAI naming convention compatibility

### 2. SearXNG MCP Server

- **Repository**: https://github.com/ihor-sokoliuk/mcp-searxng
- **Type**: stdio server
- **Requires**: SearXNG instance running
- **Expected Tools**: web search with privacy focus

### 3. Todoist MCP Server

- **Repository**: https://github.com/abhiz123/todoist-mcp-server
- **Type**: SSH (may rebuild as stdio later)
- **Installation**: `npm install -g @abhiz123/todoist-mcp-server`
- **Expected Tools**: create-task, list-tasks, update-task, complete-task

### 4. YouTube Video Summarizer MCP

- **Repository**: https://github.com/nabid-pf/youtube-video-summarizer-mcp
- **Type**: stdio server
- **Expected Tools**: summarize-video, extract-transcript

## Agent Design Patterns

### Dependencies Container

```python
@dataclass
class AgentDeps:
    http_client: AsyncClient
    config: AgentConfig
    logger: Logger
    vault_path: Path
```

### System Prompt Strategy

- Define agent as productivity assistant with access to specific tools
- Clear tool usage guidelines
- Encourage natural conversation flow
- Handle multi-step operations gracefully

### Extensibility Pattern

- Easy MCP server addition through configuration
- Tool registration happens automatically via MCP protocol
- Modular design for adding new capabilities

## GUI Design

### Chat Interface Requirements

- **Real-time conversation**: Stream responses from agent
- **Tool visibility**: Show when agent is using tools (optional)
- **Configuration panel**: Manage environment variables and settings
- **Error handling**: Display errors gracefully
- **Session management**: Maintain conversation history

### GUI Framework Decision

Research current maintenance status:

- **Gradio**: Check recent commits, issues, community activity
- Choose based on active development and chat component quality

## Development Approach

### Start Simple, Iterate

1. **Core Agent**: Basic PydanticAI setup with one MCP server
2. **Add Servers**: Integrate remaining MCP servers one by one
3. **GUI Integration**: Add chat interface
4. **Polish**: Improve UX, error handling, configuration
5. **Extend**: Add new MCP servers as needed

### Learning Focus

- Understanding PydanticAI framework deeply
- MCP protocol and server integration
- Async Python patterns
- GUI framework best practices
- Agent orchestration patterns

## Project Structure

```
project/
├── .env.example
├── requirements.txt
├── main.py
├── gui.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── agent/
│   ├── __init__.py
│   ├── agent.py
│   ├── dependencies.py
│   └── prompts.py
├── mcp_servers/
│   ├── __init__.py
│   └── configs.py
├── tools/
│   ├── __init__.py
│   ├── obsidian.py
│   ├── search.py
│   ├── tasks.py
│   └── youtube.py
└── utils/
    ├── __init__.py
    └── logger.py
```

## Success Criteria

### Functional Requirements

- ✅ Chat with agent through GUI
- ✅ Create and search notes in Obsidian
- ✅ Search web via SearXNG
- ✅ Manage Todoist tasks
- ✅ Summarize YouTube videos
- ✅ Easy addition of new MCP servers

### Technical Requirements

- ✅ Robust error handling
- ✅ Clean configuration management
- ✅ Responsive chat interface
- ✅ Extensible architecture

### Learning Objectives

- ✅ Deep understanding of PydanticAI
- ✅ MCP protocol mastery
- ✅ Modern Python async patterns
- ✅ Agent orchestration skills

## Risk Mitigation

### MCP Server Dependencies

- **Issue**: External server maintenance and compatibility
- **Mitigation**: Document server versions, prepare to fork/rebuild if needed

### LLM Provider Support

- **Issue**: AWS Bedrock support in PydanticAI
- **Resolution**: ✅ Successfully integrated BedrockConverseModel with proper credential handling

### GUI Framework Choice

- **Issue**: Framework maintenance and feature support
- **Mitigation**: Quick evaluation of both options, easy to switch if needed

## Future Extensions

Once core system is working:

- Add more MCP servers (calendar, email, file management, etc.)
- Implement conversation memory and context
- Add multi-modal capabilities (image, document processing)
- Create custom MCP servers for specific needs
- Advanced workflow automation
- Voice interface integration
