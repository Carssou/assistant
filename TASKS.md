# Development Tasks

## Phase 1: Foundation and Core Agent

### Task 1.1: Project Setup and Configuration ✅ COMPLETED 2025-06-21

**Priority**: High
**Status**: ✅ COMPLETED (13/13 completed)

#### Subtasks:

- [x] Create project structure following PydanticAI patterns ✅ 2025-06-21
- [x] Create `readme.md` ✅ 2025-06-21
- [x] Set up Python virtual environment using venv ✅ 2025-06-21
- [x] Install PydanticAI with MCP support ✅ 2025-06-21
- [x] Install Gradio for GUI ✅ 2025-06-21
- [x] Create comprehensive `.env.example` with all MCP server environment variables ✅ 2025-06-21
- [x] Create `requirements.txt` with exact dependencies and versions ✅ 2025-06-21
- [x] Create `.gitignore` file ✅ 2025-06-21
- [x] Initialize git repository and GitHub repo ✅ 2025-06-21
- [x] Set up configuration management with Pydantic models ✅ 2025-06-21
- [x] Add basic logging setup (using Langfuse) ✅ 2025-06-21
- [x] Create unit tests for configuration and logging ✅ 2025-06-21
- [x] Verify logging functionality with tests ✅ 2025-06-21

#### Files to Create:

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

#### Acceptance Criteria:

- [x] Clean project structure is set up ✅
- [x] Environment configuration works properly ✅ 
- [x] All dependencies install correctly ✅
- [x] Git repository created and pushed to GitHub ✅
- [x] Configuration management with Pydantic models implemented ✅
- [x] Basic logging is functional (verified with unit tests) ✅
- [x] Unit tests created and passing (24/24 tests pass) ✅

---

### Task 1.2: LLM Provider Setup and Agent Foundation ✅ COMPLETED 2025-06-21

**Priority**: High
**Status**: ✅ COMPLETED

#### Subtasks:

- [x] Research AWS Bedrock support in PydanticAI ✅ 2025-06-21
- [x] Implement LLM provider configuration (AWS preferred, OpenAI fallback) ✅ 2025-06-21
- [x] Create agent dependencies container ✅ 2025-06-21
- [x] Set up basic PydanticAI agent with system prompt ✅ 2025-06-21
- [x] Test agent initialization and basic conversation ✅ 2025-06-21
- [x] Add error handling and configuration validation ✅ 2025-06-21
- [x] Create simple CLI interface for testing ✅ 2025-06-21

#### Key Components:

```python
@dataclass
class AgentDependencies:  # Following PydanticAI patterns
    http_client: AsyncClient
    config: AgentConfig
    logger: Logger
    vault_path: Path

# Agent setup with configurable LLM provider
agent = Agent(
    model=get_model_string(config),  # AWS or OpenAI based on config
    deps_type=AgentDependencies,      # PydanticAI dependency injection
    system_prompt="You are a productivity assistant with access to notes, search, tasks, and video tools...",
    mcp_servers=[],  # Will populate in next tasks
    retries=2
)
```

#### Acceptance Criteria:

- [x] Agent can be configured with different LLM providers ✅
- [x] Basic conversation works without MCP servers ✅
- [x] Error handling is robust ✅
- [x] Configuration validation prevents common mistakes ✅

---

### Task 1.3: First MCP Server Integration (Obsidian) ✅ COMPLETED 2025-06-22

**Priority**: High
**Status**: ✅ COMPLETED

#### Subtasks:

- [x] Study `obsidian-mcp` server documentation and setup ✅ 2025-06-22
- [x] Implement MCPServerStdio connection for Obsidian ✅ 2025-06-22
- [x] Configure server with vault path: `npx -y obsidian-mcp-pydanticai /path/to/vault` ✅ 2025-06-22
- [x] Test connection and available tools ✅ 2025-06-22
- [x] Create wrapper functions for common Obsidian operations ✅ 2025-06-22
- [x] Add vault path validation and safety checks ✅ 2025-06-22
- [x] Test note operations (read, create, search) ✅ 2025-06-22
- [x] Handle Obsidian-specific markdown formatting ✅ 2025-06-22
- [x] Fix tool naming convention mismatch ✅ 2025-06-22

#### Technical Implementation Status:

**✅ COMPLETED Infrastructure:**
- MCPServerStdio configuration and connection
- Agent integration with MCP servers (1 server detected)
- Complete tool wrapper functions with Obsidian-specific formatting
- Comprehensive unit tests (28 passing tests)
- Real integration tests with actual Obsidian vault
- Error handling and validation
- Fork created and published as obsidian-mcp-pydanticai
- Tool naming convention fixed for PydanticAI compatibility
- End-to-end note operations fully functional

#### Expected Tools from obsidian-mcp:

- read-note / read_note: Read content of existing notes
- create-note / create_note: Create new notes with content
- search-vault / search_vault: Search across all notes
- edit-note / edit_note: Modify existing note content
- delete-note / delete_note: Remove notes from vault
- list-available-vaults / list_available_vaults: List configured vaults

#### Current Status:

**✅ Working:**
- MCP server starts successfully with real vault
- 11 tools registered (create_note, read_note, search_vault, etc.)
- Agent detects and lists all available tools
- Stdio communication established
- All tool executions work correctly
- End-to-end note operations functional

#### Acceptance Criteria:

- [x] Agent can successfully connect to Obsidian MCP server ✅
- [x] All basic note operations work correctly ✅
- [x] Vault access is properly secured and validated ✅
- [x] Error handling covers common file operation failures ✅
- [x] Agent can have meaningful conversations about note management ✅

---

## Phase 2: Multi-Server Integration

### Task 2.1: Web Search Integration (SearXNG MCP) ✅ COMPLETED 2025-06-22

**Priority**: High  
**Status**: ✅ COMPLETED

#### Subtasks:

- [x] Set up SearXNG instance (Docker) ✅ 2025-06-22
- [x] Study `mcp-searxng` server setup and configuration ✅ 2025-06-22
- [x] Integrate SearXNG MCP server as stdio process ✅ 2025-06-22
- [x] Test search functionality and result formatting ✅ 2025-06-22
- [x] Configure search parameters and result limits ✅ 2025-06-22
- [x] Add error handling for search failures ✅ 2025-06-22
- [x] Test privacy-focused search capabilities ✅ 2025-06-22

#### Expected Tools:

- [x] searxng_web_search: Execute web searches with advanced filtering ✅
- [x] web_url_read: Read and convert URL content to markdown ✅

#### Implementation Notes:

- ✅ Uses stdio MCP server with `npx -y mcp-searxng`
- ✅ Requires SEARXNG_URL environment variable (http://localhost:8080)
- ✅ Comprehensive search utility wrapper functions in tools/search.py
- ✅ Support for pagination, time filtering, language selection, safe search
- ✅ Research workflow generation and result categorization
- ✅ Integration with note creation and task management
- ✅ Dynamic date handling for current year searches
- ✅ Test coverage with 19 passing unit tests

#### Acceptance Criteria:

- [x] Agent can perform web searches via SearXNG ✅
- [x] Search results are properly formatted and useful ✅
- [x] Privacy features work as expected ✅
- [x] Search can be combined with note-taking workflows ✅

---

### Task 2.2: Task Management Integration (Todoist) ✅ COMPLETED 2025-06-22

**Priority**: Medium
**Status**: ✅ COMPLETED

#### Subtasks:

- [x] Install Todoist MCP server: Uses stdio with `npx -y @abhiz123/todoist-mcp-server` ✅ 2025-06-22
- [x] Configure Todoist API token in environment ✅ 2025-06-22
- [x] Set up MCP server connection (stdio, not SSH) ✅ 2025-06-22
- [x] Test task CRUD operations ✅ 2025-06-22
- [x] Implement task-note linking workflows ✅ 2025-06-22
- [x] Add due date and priority handling ✅ 2025-06-22
- [x] Handle Todoist API rate limits and error handling ✅ 2025-06-22

#### Expected Tools:

- [x] todoist_create_task: Add new tasks to Todoist ✅
- [x] todoist_get_tasks: Retrieve tasks with filtering ✅ 
- [x] todoist_update_task: Modify existing tasks ✅
- [x] todoist_delete_task: Remove tasks ✅

#### Implementation Notes:

- ✅ Uses stdio MCP server (not SSH as originally planned)
- ✅ Server runs with `npx -y @abhiz123/todoist-mcp-server`
- ✅ Requires TODOIST_API_TOKEN environment variable
- ✅ Comprehensive tool wrapper functions in tools/tasks.py
- ✅ Integration with note management and research workflows
- ✅ Natural language task parsing and priority suggestion
- ✅ Test coverage with 15 passing unit tests

#### Acceptance Criteria:

- [x] Agent can manage Todoist tasks effectively ✅
- [x] Task operations are reliable and fast ✅
- [x] Integration handles API limitations gracefully ✅
- [x] Tasks can be created from conversations about notes or research ✅

---

### Task 2.3: YouTube Video Processing ✅ COMPLETED 2025-06-22

**Priority**: Medium
**Status**: ✅ COMPLETED

#### Subtasks:

- [x] Study `youtube-video-summarizer-mcp` server setup ✅ 2025-06-22
- [x] Integrate YouTube MCP server as stdio process ✅ 2025-06-22
- [x] Test video URL parsing and validation ✅ 2025-06-22
- [x] Implement video summarization workflows ✅ 2025-06-22
- [x] Add transcript extraction capabilities ✅ 2025-06-22
- [x] Create note templates for video summaries ✅ 2025-06-22
- [x] Handle different video types and lengths ✅ 2025-06-22
- [x] Add error handling for private/unavailable videos ✅ 2025-06-22

#### Expected Tools:

- [x] get-video-info: Get basic information about a YouTube video ✅

#### Implementation Notes:

- ✅ Uses stdio MCP server with `npx -y youtube-video-summarizer-mcp`
- ✅ No API key required - works out of the box
- ✅ Comprehensive video processing utilities in tools/youtube.py (500+ lines)
- ✅ Support for video URL parsing, validation, and normalization
- ✅ Video summarization workflows and note creation templates
- ✅ Integration with task management and learning workflows
- ✅ Key point extraction and follow-up action suggestions
- ✅ Test coverage with 15 passing unit tests
- ✅ Support for multiple YouTube URL formats

#### Acceptance Criteria:

- [x] Agent can process YouTube URLs reliably ✅
- [x] Video summaries are meaningful and accurate ✅
- [x] Integration with note creation works smoothly ✅
- [x] Error handling covers common video access issues ✅

---

### Task 2.4: Multi-Tool Coordination ✅ COMPLETED 2025-06-23

**Priority**: Medium
**Status**: ✅ COMPLETED

#### Subtasks:

- [x] Test agent with all MCP servers connected ✅ 2025-06-23
- [x] Create example workflows using multiple tools ✅ 2025-06-23
- [x] Implement tool coordination logic ✅ 2025-06-23
- [x] Add workflow templates for common use cases ✅ 2025-06-23
- [x] Test performance with multiple server connections ✅ 2025-06-23
- [x] Add monitoring for server health and connectivity ✅ 2025-06-23
- [x] Create graceful degradation when servers are unavailable ✅ 2025-06-23

#### Implementation Status:

**✅ COMPLETED Infrastructure:**
- All 4 MCP servers (Obsidian, SearXNG, Todoist, YouTube) working together
- Intelligent tool coordination via enhanced agent prompts
- 6 comprehensive workflow templates implemented
- Performance testing: 15-30 second completion times for complex workflows
- Server health monitoring system with real-time status tracking
- Graceful degradation system with tool alternatives and fallback strategies
- Comprehensive documentation created in `/docs/multi_tool_workflows.md`

#### Example Workflows Successfully Tested:

1. **Research & Note Creation**: Search web → synthesize findings → create structured note → generate follow-up tasks
2. **Information Synthesis**: Multiple searches → cross-reference sources → comprehensive comparison note
3. **Content Curation**: Search → read sources → check existing vault → organize with connections
4. **Video Learning**: Process video → extract insights → create study notes → add practice tasks
5. **Project Planning**: Research best practices → create plan → break down tasks → schedule milestones
6. **Learning Pathways**: Find resources → sequence learning → create structured plan → track progress

#### Key Features Implemented:

- **🔄 Context Flow**: Information seamlessly flows between tools
- **🧠 Intelligent Coordination**: Agent chooses optimal tool sequences automatically
- **⚡ Performance**: Complex workflows complete in 15-30 seconds
- **🛡️ Graceful Degradation**: Automatic fallbacks when tools unavailable
- **📊 Health Monitoring**: Real-time MCP server status tracking
- **📚 Documentation**: Human-readable workflow examples and patterns

#### Acceptance Criteria:

- [x] All MCP servers work together reliably ✅
- [x] Multi-step workflows execute smoothly ✅
- [x] Agent can coordinate tools effectively ✅
- [x] Performance remains acceptable with all servers ✅
- [x] Natural language interface works intuitively ✅
- [x] System handles tool failures gracefully ✅

---

## Phase 3: GUI Development

### Task 3.1: Gradio GUI Setup and Implementation

**Priority**: High

#### Subtasks:

- [ ] Set up Gradio chat interface with streaming support
- [ ] Implement PydanticAI agent integration with Gradio
- [ ] Create configuration panel for environment variables
- [ ] Add session management for conversation history
- [ ] Implement real-time streaming of agent responses
- [ ] Add basic error display and handling in GUI
- [ ] Create file upload capabilities for note operations
- [ ] Add simple configuration validation in interface

#### Evaluation Criteria:

- **Maintenance**: Recent commits, active development, issue resolution
- **Chat Features**: Built-in chat components, customization options
- **Performance**: Response time, resource usage
- **Ease of Use**: Development experience, documentation quality

#### Acceptance Criteria:

- Framework choice is well-researched and justified
- Basic chat interface is functional
- Agent integration works smoothly
- Foundation is set for iterative improvement

---

### Task 3.2: Core Chat Interface Implementation

**Priority**: High

#### Subtasks:

- [ ] Create main chat interface with message history
- [ ] Implement real-time streaming of agent responses
- [ ] Add configuration panel for environment variables
- [ ] Create session management for conversation history
- [ ] Add basic error display and handling in GUI
- [ ] Implement file upload for relevant operations
- [ ] Add simple configuration validation in interface

#### Features:

```python
# Expected GUI components
- Chat input/output area
- Configuration sidebar/panel
- Session history management
- Error notification system
- Tool activity indicators (optional)
- File upload for note creation
```

#### Acceptance Criteria:

- Chat interface is responsive and user-friendly
- Agent responses stream naturally
- Configuration can be managed through GUI
- Error messages are clear and helpful
- Basic file operations work through interface

---

### Task 3.3: GUI Polish and Enhancement

**Priority**: Medium

#### Subtasks:

- [ ] Improve UI/UX design and layout
- [ ] Add loading indicators and progress feedback
- [ ] Implement conversation export functionality
- [ ] Add keyboard shortcuts for common actions
- [ ] Create help/documentation within the interface
- [ ] Add theme customization options
- [ ] Implement conversation search and filtering
- [ ] Add tool usage visualization (optional)

#### Acceptance Criteria:

- Interface is polished and professional
- User experience is smooth and intuitive
- Help documentation is accessible and useful
- Advanced features enhance usability without complexity

---

## Phase 4: Extension and Refinement

### Task 4.1: MCP Server Extensibility

**Priority**: Low

#### Subtasks:

- [ ] Create framework for easily adding new MCP servers
- [ ] Document process for integrating additional servers
- [ ] Create configuration templates for common server types
- [ ] Add dynamic server loading capabilities
- [ ] Implement server health monitoring and reconnection
- [ ] Create server-specific configuration validation

#### Acceptance Criteria:

- New MCP servers can be added with minimal code changes
- Server management is robust and reliable
- Documentation enables easy extension
- System handles server failures gracefully

---

### Task 1.4: Fork and Fix Obsidian MCP Server ✅ COMPLETED 2025-06-22

**Priority**: High
**Status**: ✅ COMPLETED

#### Background:
The original `obsidian-mcp` package has a tool naming convention mismatch with PydanticAI:
- MCP server registers tools with hyphens: `list-available-vaults`
- PydanticAI converts them to underscores: `list_available_vaults`
- Package is unmaintained (6 months without updates)

#### Subtasks:

- [x] Fork obsidian-mcp repository from https://github.com/StevenStavrakis/obsidian-mcp ✅ 2025-06-22
- [x] Create new package `obsidian-mcp-pydanticai` ✅ 2025-06-22
- [x] Update project configuration to use new package ✅ 2025-06-22
- [x] Identify and fix tool naming convention issues ✅ 2025-06-22
- [x] Test tool name compatibility with PydanticAI ✅ 2025-06-22
- [x] Publish fixed package to npm ✅ 2025-06-22
- [x] Verify all 11 tools work correctly ✅ 2025-06-22
- [x] Test end-to-end note operations through agent ✅ 2025-06-22

#### Package Information:
- **Repository**: https://github.com/Carssou/obsidian-mcp-pydanticai
- **Package Name**: `obsidian-mcp-pydanticai`
- **Configuration**: `npx -y obsidian-mcp-pydanticai /path/to/vault`

#### Expected Fix:
Ensure MCP server accepts both naming conventions:
- `list-available-vaults` (original format)
- `list_available_vaults` (PydanticAI format)

#### Acceptance Criteria:

- [x] Fork created and project configured to use new package ✅
- [x] Forked MCP server accepts PydanticAI tool name format ✅
- [x] All note operations work through agent conversation ✅
- [x] Real vault integration fully functional ✅
- [x] Agent can perform meaningful note management tasks ✅

---

### Task 4.2: Extended LLM Provider Support

**Priority**: Medium

#### Subtasks:

- [ ] Add support for Anthropic (Claude) models via anthropic provider
- [ ] Add support for Google Gemini models via google provider  
- [ ] Add support for Cohere models via cohere provider
- [ ] Add support for Groq models via groq provider
- [ ] Add support for Mistral models via mistral provider
- [ ] Update configuration to support all PydanticAI providers
- [ ] Create provider-specific configuration validation
- [ ] Add unit tests for all supported providers
- [ ] Update documentation with all provider options

#### Available PydanticAI Providers:
```
anthropic, bedrock, cohere, gemini, google, groq, mistral, openai
```

#### Acceptance Criteria:

- Users can choose from all major LLM providers
- Configuration validation works for each provider
- Provider switching is seamless through environment variables
- Documentation clearly explains setup for each provider

---

### Task 4.3: Advanced Agent Capabilities

**Priority**: Low

#### Subtasks:

- [ ] Implement conversation memory and context management
- [ ] Add workflow templates and automation
- [ ] Create intelligent tool selection and coordination
- [ ] Implement batch operations for efficiency
- [ ] Add content analysis and recommendation features
- [ ] Create custom prompt templates for different use cases

#### Acceptance Criteria:

- Agent provides more intelligent and contextual responses
- Workflow automation saves time on repetitive tasks
- Advanced features enhance productivity without complexity

---

### Task 4.4: Performance and Reliability

**Priority**: Medium

#### Subtasks:

- [ ] Optimize agent response times and resource usage
- [ ] Implement comprehensive error recovery strategies
- [ ] Add connection pooling and caching where appropriate
- [ ] Create performance monitoring and metrics
- [ ] Implement stress testing for multiple concurrent operations
- [ ] Add health checks and system monitoring

#### Acceptance Criteria:

- System performs well under normal and heavy usage
- Error recovery is automatic and graceful
- Performance metrics provide useful insights
- System reliability meets production standards

---

## Cross-Cutting Concerns

### Testing Strategy

- [ ] Unit tests for agent components and configuration
- [ ] Integration tests for MCP server connections
- [ ] End-to-end workflow testing
- [ ] GUI interaction testing
- [ ] Error scenario testing
- [ ] Performance and load testing

### Documentation

- [ ] User guide for setting up and using the agent
- [ ] Developer documentation for extending functionality
- [ ] MCP server integration guide
- [ ] Troubleshooting and FAQ documentation
- [ ] API documentation for internal components

### Security and Privacy

- [ ] Secure credential storage and management
- [ ] Input validation and sanitization
- [ ] Privacy controls for data handling
- [ ] Audit logging for security review
- [ ] Access control for sensitive operations

---

## Success Metrics

### Learning Objectives

- [ ] Deep understanding of PydanticAI framework and patterns
- [ ] Mastery of MCP protocol and server integration
- [ ] Proficiency with modern Python async programming
- [ ] Experience with agent orchestration and coordination
- [ ] GUI framework expertise for AI applications

### Functional Success

- [ ] All MCP servers integrate successfully
- [ ] Chat interface provides smooth user experience
- [ ] Agent handles multi-tool workflows effectively
- [ ] System is extensible for adding new capabilities
- [ ] Error handling and recovery work reliably

### Technical Quality

- [ ] Code is well-structured and maintainable
- [ ] Configuration management is robust
- [ ] Performance meets usability standards
- [ ] Documentation supports future development
- [ ] Architecture supports planned extensions
