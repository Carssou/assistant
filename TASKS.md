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

### Task 1.3: First MCP Server Integration (Obsidian) ⚠️ PARTIALLY COMPLETED 2025-06-21

**Priority**: High
**Status**: ⚠️ INFRASTRUCTURE COMPLETE - AWAITING COMPATIBLE MCP SERVER

#### Subtasks:

- [x] Study `obsidian-mcp` server documentation and setup ✅ 2025-06-21
- [x] Implement MCPServerStdio connection for Obsidian ✅ 2025-06-21
- [x] Configure server with vault path: `npx -y obsidian-mcp /path/to/vault` ✅ 2025-06-21
- [x] Test connection and available tools ✅ 2025-06-21
- [x] Create wrapper functions for common Obsidian operations ✅ 2025-06-21
- [x] Add vault path validation and safety checks ✅ 2025-06-21
- [x] Test note operations (read, create, search) ✅ 2025-06-21
- [x] Handle Obsidian-specific markdown formatting ✅ 2025-06-21
- [ ] **BLOCKER**: Fix tool naming convention mismatch (requires forking obsidian-mcp)

#### Technical Implementation Status:

**✅ COMPLETED Infrastructure:**
- MCPServerStdio configuration and connection
- Agent integration with MCP servers (1 server detected)
- Complete tool wrapper functions with Obsidian-specific formatting
- Comprehensive unit tests (28 passing tests)
- Real integration tests with actual Obsidian vault
- Error handling and validation

**❌ BLOCKER Identified:**
- Tool naming mismatch: MCP server uses hyphens (`list-available-vaults`) but PydanticAI converts to underscores (`list_available_vaults`)
- All tool calls fail with "Unknown tool name" error
- Original obsidian-mcp package unmaintained (6 months without updates)

**🔧 SOLUTION IN PROGRESS:**
- Fork obsidian-mcp package to fix naming convention compatibility
- Maintain active fork with PydanticAI compatibility

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
- 11 tools registered (create-note, read-note, search-vault, etc.)
- Agent detects and lists all available tools
- Stdio communication established

**❌ Not Working:**
- Tool execution fails due to naming convention mismatch
- No functional note operations until server is fixed

#### Acceptance Criteria:

- [x] Agent can successfully connect to Obsidian MCP server ✅
- [ ] All basic note operations work correctly ❌ (naming mismatch)
- [x] Vault access is properly secured and validated ✅
- [x] Error handling covers common file operation failures ✅
- [ ] Agent can have meaningful conversations about note management ❌ (tools not executable)

---

## Phase 2: Multi-Server Integration

### Task 2.1: Web Search Integration (SearXNG MCP)

**Priority**: High

#### Subtasks:

- [ ] Set up SearXNG instance (if not already running)
- [ ] Study `mcp-searxng` server setup and configuration
- [ ] Integrate SearXNG MCP server as stdio process
- [ ] Test search functionality and result formatting
- [ ] Configure search parameters and result limits
- [ ] Add error handling for search failures
- [ ] Test privacy-focused search capabilities

#### Expected Capabilities:

- Web search through SearXNG instance
- Privacy-focused search without tracking
- Structured search results with metadata
- Integration with note creation for research

#### Acceptance Criteria:

- Agent can perform web searches via SearXNG
- Search results are properly formatted and useful
- Privacy features work as expected
- Search can be combined with note-taking workflows

---

### Task 2.2: Task Management Integration (Todoist)

**Priority**: Medium

#### Subtasks:

- [ ] Install Todoist MCP server: `npm install -g @abhiz123/todoist-mcp-server`
- [ ] Configure Todoist API token in environment
- [ ] Set up MCP server connection (SSH for now)
- [ ] Test task CRUD operations
- [ ] Implement task-note linking workflows
- [ ] Add due date and priority handling
- [ ] Handle Todoist API rate limits and errors

#### Expected Tools:

- create-task: Add new tasks to Todoist
- list-tasks: Retrieve tasks with filtering
- update-task: Modify existing tasks
- complete-task: Mark tasks as done
- delete-task: Remove tasks

#### Future Consideration:

- [ ] Research rebuilding as stdio server for better integration

#### Acceptance Criteria:

- Agent can manage Todoist tasks effectively
- Task operations are reliable and fast
- Integration handles API limitations gracefully
- Tasks can be created from conversations about notes or research

---

### Task 2.3: YouTube Video Processing

**Priority**: Medium

#### Subtasks:

- [ ] Study `youtube-video-summarizer-mcp` server setup
- [ ] Integrate YouTube MCP server as stdio process
- [ ] Test video URL parsing and validation
- [ ] Implement video summarization workflows
- [ ] Add transcript extraction capabilities
- [ ] Create note templates for video summaries
- [ ] Handle different video types and lengths
- [ ] Add error handling for private/unavailable videos

#### Expected Capabilities:

- Extract transcripts from YouTube videos
- Generate summaries of video content
- Create structured notes from video analysis
- Handle video metadata (title, duration, channel)

#### Acceptance Criteria:

- Agent can process YouTube URLs reliably
- Video summaries are meaningful and accurate
- Integration with note creation works smoothly
- Error handling covers common video access issues

---

### Task 2.4: Multi-Tool Coordination

**Priority**: Medium

#### Subtasks:

- [ ] Test agent with all MCP servers connected
- [ ] Create example workflows using multiple tools
- [ ] Implement tool coordination logic
- [ ] Add workflow templates for common use cases
- [ ] Test performance with multiple server connections
- [ ] Add monitoring for server health and connectivity
- [ ] Create graceful degradation when servers are unavailable

#### Example Workflows:

1. **Research & Note Creation**: Search web → create research note → generate follow-up tasks
2. **Video Learning**: Summarize YouTube video → create study notes → add to task list
3. **Information Synthesis**: Search multiple sources → create comprehensive note → organize in vault

#### Acceptance Criteria:

- All MCP servers work together reliably
- Multi-step workflows execute smoothly
- Agent can coordinate tools effectively
- Performance remains acceptable with all servers

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

### Task 1.4: Fork and Fix Obsidian MCP Server

**Priority**: High
**Status**: PENDING

#### Background:
The original `obsidian-mcp` package has a tool naming convention mismatch with PydanticAI:
- MCP server registers tools with hyphens: `list-available-vaults`
- PydanticAI converts them to underscores: `list_available_vaults`
- Package is unmaintained (6 months without updates)

#### Subtasks:

- [ ] Fork obsidian-mcp repository from https://github.com/StevenStavrakis/obsidian-mcp
- [ ] Identify and fix tool naming convention issues
- [ ] Test tool name compatibility with PydanticAI
- [ ] Publish fixed package or configure local usage
- [ ] Update project configuration to use working MCP server
- [ ] Verify all 11 tools work correctly
- [ ] Test end-to-end note operations through agent

#### Expected Fix:
Ensure MCP server accepts both naming conventions:
- `list-available-vaults` (original format)
- `list_available_vaults` (PydanticAI format)

#### Acceptance Criteria:

- [ ] Forked MCP server accepts PydanticAI tool name format
- [ ] All note operations work through agent conversation
- [ ] Real vault integration fully functional
- [ ] Agent can perform meaningful note management tasks

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
