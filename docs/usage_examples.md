# Usage Examples

This document shows how the PydanticAI agent uses multiple tools from different MCP servers to accomplish complex productivity tasks.

## How It Works

When you make a request like "Research AI agents and create notes," the agent:

1. **Understands the intent** - recognizes this needs research + note creation
2. **Selects appropriate tools** - chooses web search and note creation tools
3. **Executes tool calls** - runs tools in logical sequence based on context
4. **Maintains context** - passes information between tool calls

## Example Workflows

### Research & Note Creation
**What you say:** "Research the latest developments in AI agents and create a comprehensive note"

**What the agent does:**
1. Searches web for "AI agents latest developments" 
2. Searches for "multi-agent systems recent advances"
3. Analyzes and synthesizes the findings
4. Creates a structured research note with key insights
5. Optionally generates follow-up research tasks

**Tools used:** Web Search → Note Creation → Task Management

---

### Video Learning Pipeline
**What you say:** "Analyze this YouTube video about machine learning and create study materials"

**What the agent does:**
1. Extracts video transcript and metadata
2. Identifies key concepts and learning points
3. Creates structured study notes with clear sections
4. Adds practice tasks and review schedules
5. Links to related content in your vault

**Tools used:** Video Processing → Note Creation → Task Management

---

### Information Synthesis  
**What you say:** "Research PydanticAI vs LangChain and create a comprehensive comparison"

**What the agent does:**
1. Searches for "PydanticAI features and benefits"
2. Searches for "LangChain vs PydanticAI comparison" 
3. Reads key articles and documentation
4. Synthesizes findings into a coherent comparison
5. Creates well-organized note with proper structure
6. Identifies gaps for further research

**Tools used:** Web Search → URL Reading → Note Creation → Task Management

---

### Content Curation & Organization
**What you say:** "Find and organize information about MCP servers for my knowledge base"

**What the agent does:**
1. Searches for high-quality MCP server resources
2. Reads key articles and official documentation
3. Searches existing vault for related content
4. Creates organized notes with proper categorization
5. Links to existing knowledge and creates connections
6. Suggests organizational improvements

**Tools used:** Web Search → URL Reading → Vault Search → Note Creation → Note Editing

---

### Project Planning
**What you say:** "Help me plan a project to build a RAG system with proper documentation"

**What the agent does:**
1. Researches RAG system best practices and methodologies
2. Creates comprehensive project plan note with requirements
3. Breaks down project into actionable tasks with priorities
4. Sets rough timeline estimates
5. Adds initial tasks to task management system
6. Schedules regular review and milestone tasks

**Tools used:** Web Search → Note Creation → Task Management

---

### Learning Pathway Creation
**What you say:** "Create a learning plan for understanding transformer architectures"

**What the agent does:**
1. Searches for transformer architecture tutorials and resources
2. Identifies prerequisite knowledge and advanced topics
3. Creates structured learning pathway with milestones
4. Finds practical exercises and projects
5. Schedules study sessions and review periods
6. Adds progress tracking and assessment tasks

**Tools used:** Web Search → Note Creation → Task Management

## Key Benefits

### 🔄 **Tool Integration**
Information flows naturally between tool calls - search results become note content, which can inform task creation.

### 🧠 **Context Awareness** 
The agent adapts its tool usage based on what it finds. Tutorial content might trigger practice task creation, research papers might prompt source verification.

### ⚡ **Natural Interface**
Describe what you want in plain English. The agent selects appropriate tools based on the request.

### 🛡️ **Error Handling**
If a tool is unavailable, the agent can try alternative approaches or continue with available tools.

### 📈 **Extensible**
Add new MCP servers and the agent automatically has access to their tools.

## Performance

- **Typical completion time:** 15-30 seconds for multi-tool tasks
- **Tool selection:** Based on agent reasoning and context
- **Error handling:** Graceful degradation with monitoring
- **MCP integration:** Reliable stdio connections with health checks

## Agent Approach

This is a standard PydanticAI agent with multiple MCP servers:

**How it works:**
```
User request → Agent reasoning → Tool selection → Tool execution → Response
```

**Tool availability:**
- Tools are provided by MCP servers
- Agent has access to all available tools
- Agent selects tools based on request context
- Natural language interface handles complexity

This demonstrates effective MCP server integration with a single capable agent.