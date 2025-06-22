# Multi-Purpose AI Agent

A PydanticAI-powered agent with a Gradio chat GUI that integrates multiple MCP servers for productivity tasks.

## Features

- **Note Management**: Obsidian vault integration for creating, reading, and searching notes
- **Web Search**: Privacy-focused search through SearXNG
- **Task Management**: Todoist integration for task CRUD operations
- **Video Processing**: YouTube video summarization and transcript extraction
- **Chat Interface**: Gradio-based GUI with streaming responses
- **Configurable LLM**: Support for AWS Bedrock and OpenAI providers

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

# GUI interface (coming soon)
python gui.py
```

## Configuration

### LLM Providers

- **AWS Bedrock** (preferred): Configure AWS credentials and region
- **OpenAI**: Set API key for fallback option

### MCP Servers

1. **Obsidian**: Set `OBSIDIAN_VAULT_PATH` to your vault location
2. **SearXNG**: Requires Docker - run `docker-compose up -d` to start local instance
3. **Todoist**: Add your Todoist API token
4. **YouTube**: Optional API key for enhanced features

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
├── agent/          # PydanticAI agent implementation
├── config/         # Configuration management
├── mcp_servers/    # MCP server configurations
├── tools/          # Tool wrappers for each service
├── utils/          # Shared utilities
├── tests/          # Unit tests
├── main.py         # CLI entry point
└── gui.py          # Gradio GUI
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

- [obsidian-mcp](https://github.com/StevenStavrakis/obsidian-mcp) - Note management
- [mcp-searxng](https://github.com/ihor-sokoliuk/mcp-searxng) - Web search
- [todoist-mcp-server](https://github.com/abhiz123/todoist-mcp-server) - Task management
- [youtube-video-summarizer-mcp](https://github.com/nabid-pf/youtube-video-summarizer-mcp) - Video processing

## License

MIT License