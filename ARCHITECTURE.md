# Architecture and Directory Layout Guidelines

## Recommended Project Structure

The following standardized structure should be used for all projects to ensure consistency, maintainability, and clear separation of concerns:

```
project/
├─ app/                    # FastAPI endpoints & dependency injection
│  ├─ __init__.py
│  ├─ main.py             # FastAPI application entry point
│  ├─ dependencies.py     # DI container and dependency providers  
│  ├─ routers/           # API route handlers
│  │  ├─ __init__.py
│  │  ├─ agents.py       # Agent-related endpoints
│  │  ├─ mcp.py          # MCP server endpoints
│  │  └─ health.py       # Health check endpoints
│  └─ middleware/        # Custom middleware
│     ├─ __init__.py
│     ├─ auth.py
│     └─ logging.py
├─ agent_framework/       # LLM providers, agents, and tools
│  ├─ __init__.py
│  ├─ providers/         # LLM provider implementations
│  │  ├─ __init__.py
│  │  ├─ openai.py
│  │  ├─ anthropic.py
│  │  └─ base.py         # Abstract base provider
│  ├─ agents/            # Agent implementations
│  │  ├─ __init__.py
│  │  ├─ base.py         # Abstract base agent
│  │  └─ chat_agent.py
│  ├─ tools/             # Tool implementations
│  │  ├─ __init__.py
│  │  ├─ base.py         # Abstract base tool
│  │  └─ file_tools.py
│  └─ schemas/           # Pydantic models for agent framework
│     ├─ __init__.py
│     ├─ agent.py
│     ├─ tool.py
│     └─ provider.py
├─ mcp_client/           # Async client for MCP server
│  ├─ __init__.py
│  ├─ client.py          # Main MCP client implementation
│  ├─ transport/         # Transport layer implementations
│  │  ├─ __init__.py
│  │  ├─ base.py         # Abstract transport
│  │  ├─ stdio.py        # STDIO transport
│  │  └─ websocket.py    # WebSocket transport
│  ├─ schemas/           # MCP protocol schemas
│  │  ├─ __init__.py
│  │  ├─ messages.py
│  │  ├─ tools.py
│  │  └─ resources.py
│  └─ exceptions.py      # MCP-specific exceptions
├─ schemas/              # Shared Pydantic models
│  ├─ __init__.py
│  ├─ api.py            # API request/response models
│  ├─ config.py         # Configuration models
│  └─ common.py         # Common shared models
├─ services/             # Business logic layer
│  ├─ __init__.py
│  ├─ agent_service.py   # Agent coordination logic
│  ├─ mcp_service.py     # MCP integration logic
│  └─ auth_service.py    # Authentication logic
├─ config/               # Configuration management
│  ├─ __init__.py
│  ├─ settings.py        # Application settings
│  └─ logging.py         # Logging configuration
├─ tests/                # Test suite
│  ├─ __init__.py
│  ├─ conftest.py        # Pytest configuration
│  ├─ unit/              # Unit tests
│  │  ├─ test_agents.py
│  │  ├─ test_mcp_client.py
│  │  └─ test_services.py
│  ├─ integration/       # Integration tests
│  │  ├─ test_api.py
│  │  └─ test_mcp_integration.py
│  └─ fixtures/          # Test data and fixtures
│     ├─ __init__.py
│     └─ mock_data.py
├─ scripts/              # Utility scripts
│  ├─ setup.py          # Environment setup
│  ├─ migrate.py        # Database migrations
│  └─ seed_data.py      # Seed test data
├─ docs/                 # Documentation
│  ├─ api.md            # API documentation
│  ├─ deployment.md     # Deployment guide
│  └─ development.md    # Development setup
├─ .cursor-rules         # Cursor IDE rules
├─ pyproject.toml        # Python project configuration
├─ uv.lock              # UV lock file
├─ README.md            # Project overview
└─ .env.example         # Environment variables template
```

## Architecture Principles

### 1. Separation of Concerns

Each directory has a specific responsibility:

- **`app/`**: Web framework layer (FastAPI), routing, and dependency injection
- **`agent_framework/`**: Core agent functionality, LLM providers, and tools
- **`mcp_client/`**: MCP protocol implementation and transport layers
- **`schemas/`**: Data models and validation (Pydantic)
- **`services/`**: Business logic and orchestration
- **`config/`**: Application configuration and settings

### 2. Async-First Architecture

**REQUIREMENT**: All I/O operations MUST be asynchronous.

- Use `async`/`await` for all database operations
- Use `async`/`await` for all HTTP requests
- Use `async`/`await` for all file operations
- Use `asyncio` for concurrent operations
- Use `aiofiles` for file I/O
- Use `httpx` for HTTP client operations

Example:
```python
# ✅ Correct - Async I/O
async def fetch_data(client: httpx.AsyncClient) -> Dict[str, Any]:
    response = await client.get("/api/data")
    return response.json()

# ❌ Incorrect - Synchronous I/O
def fetch_data() -> Dict[str, Any]:
    response = requests.get("/api/data")
    return response.json()
```

### 3. Dependency Injection

Use FastAPI's dependency injection system for:
- Database connections
- External service clients
- Configuration objects
- Authentication/authorization

```python
# app/dependencies.py
from typing import AsyncGenerator
from fastapi import Depends
import httpx

async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client

# app/routers/agents.py
from fastapi import APIRouter, Depends
import httpx

router = APIRouter()

@router.get("/agents")
async def list_agents(client: httpx.AsyncClient = Depends(get_http_client)):
    # Use injected client
    pass
```

### 4. Schema-First Design

- Define all data structures using Pydantic models
- Place shared models in `schemas/`
- Use specific schema modules for each domain
- Validate all input/output data

```python
# schemas/agent.py
from pydantic import BaseModel, Field
from typing import List, Optional

class AgentRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    tools: List[str] = []

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
```

## Directory-Specific Guidelines

### `app/` - Web Framework Layer

- Keep route handlers thin - delegate to services
- Use dependency injection for all external dependencies
- Group related endpoints in separate router modules
- Implement proper error handling and status codes

### `agent_framework/` - Core Agent Logic

- Implement abstract base classes for extensibility
- Use the strategy pattern for different LLM providers
- Keep tool implementations stateless
- Use proper async patterns for LLM API calls

### `mcp_client/` - MCP Protocol

- Implement transport abstraction for different connection types
- Use proper async context managers for connections
- Handle protocol errors gracefully
- Implement connection pooling where appropriate

### `services/` - Business Logic

- Keep services focused on single responsibilities
- Use dependency injection for external dependencies
- Implement proper error handling and logging
- Make all service methods async

### `tests/` - Testing

- Maintain high test coverage (>80%)
- Use pytest with async support
- Create realistic fixtures and mock data
- Separate unit and integration tests

## Development Standards

### 1. Package Management

- Use UV for Python package management
- Avoid hard-pinning dependencies unless necessary
- Use the newest compatible versions of dependencies
- Keep `pyproject.toml` organized and well-documented

### 2. Code Quality

- Use type hints throughout the codebase
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Document complex business logic

### 3. Error Handling

- Use custom exception classes for domain-specific errors
- Implement proper error logging
- Return appropriate HTTP status codes
- Provide meaningful error messages to clients

### 4. Configuration

- Use environment variables for configuration
- Provide sensible defaults
- Validate configuration at startup
- Document all configuration options

## Example Implementation

```python
# services/agent_service.py
from typing import List, Optional
import asyncio
from agent_framework.agents.base import BaseAgent
from mcp_client.client import MCPClient
from schemas.agent import AgentRequest, AgentResponse

class AgentService:
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.agents: Dict[str, BaseAgent] = {}
    
    async def create_agent(self, request: AgentRequest) -> AgentResponse:
        """Create a new agent instance."""
        # Business logic here
        agent = await self._instantiate_agent(request)
        self.agents[agent.id] = agent
        
        return AgentResponse(
            id=agent.id,
            name=request.name,
            description=request.description,
            status="created",
            created_at=datetime.utcnow()
        )
    
    async def _instantiate_agent(self, request: AgentRequest) -> BaseAgent:
        """Helper method to create agent instance."""
        # Implementation details
        pass
```

This architecture ensures scalability, maintainability, and clear separation of concerns while adhering to modern Python async patterns and best practices.
