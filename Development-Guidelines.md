# Development Guidelines

## Dependency Management Rules

### Package Manager Requirements
- **MANDATORY**: Use UV for all Python package operations
- **NEVER** use `pip` directly - always use `uv pip` commands
- UV provides faster, more reliable dependency resolution and package management

### Version Specification Policy
- **DISALLOWED**: Hard-pinned versions (e.g., `fastapi==0.110.0`)
- **REQUIRED**: Use minimum version specifiers with no upper bound (e.g., `fastapi>=0.110`)
- This ensures compatibility with newest versions while maintaining minimum requirements
- Exception: Only pin exact versions for security-critical packages when absolutely necessary

### Dependency Management Workflow

#### Adding New Packages
```bash
# Add a new package with minimum version
uv pip install "package_name>=minimum_version"

# Example: Adding FastAPI
uv pip install "fastapi>=0.110"

# For packages with extras
uv pip install "package_name[extra1,extra2]>=minimum_version"
```

#### Removing Packages
```bash
# Remove a package
uv pip uninstall package_name

# Remove multiple packages
uv pip uninstall package1 package2 package3
```

#### Synchronizing Dependencies
```bash
# Sync all dependencies from requirements.txt
uv pip sync requirements.txt

# Install all packages from requirements.txt
uv pip install -r requirements.txt
```

#### Dependency Health Checks
```bash
# Check for dependency conflicts and compatibility issues
uv pip check

# List installed packages and versions
uv pip list

# Show dependency tree
uv pip show --verbose package_name
```

### Maintenance Schedule
- **Weekly**: Run `uv pip check` to identify dependency conflicts
- **Monthly**: Review and update minimum version requirements
- **Before releases**: Ensure all dependencies use newest compatible versions

### Best Practices
1. Always test with newest compatible versions in development
2. Use virtual environments for isolation: `uv venv` and `source .venv/bin/activate`
3. Keep `requirements.txt` updated with all production dependencies
4. Document any version constraints with justification in comments
5. Regular dependency audits for security vulnerabilities

## Agent Reliability (Galileo) Integration Guidelines

### Conditional Integration Rules
- **Environment Flag**: All Galileo functionality must be gated behind the `ENABLE_GALILEO` environment variable
- **Graceful Fallback**: System must function normally when `ENABLE_GALILEO=false` or unset
- **Import Protection**: Use conditional imports to avoid dependency errors when Galileo is disabled

### Dependency Management for Galileo
- **Warning**: Galileo adds significant dependency weight to your application
- **Performance Impact**: Consider the impact on startup time, memory usage, and bundle size
- **Optional Installation**: Include Galileo in optional dependencies or separate requirements file
- **Version Specification**: Follow project standards: `galileo-sdk>=0.5.0` (no hard pinning)

#### Installation Commands
```bash
# Optional dependency installation (when needed)
uv pip install "galileo-sdk>=0.5.0"

# Or add to requirements-galileo.txt for optional features
echo "galileo-sdk>=0.5.0" >> requirements-galileo.txt
```

### Best-Practice Instrumentation Spots

#### Critical Instrumentation Points
1. **Before LLM Call** - Capture input context and parameters
2. **After LLM Call** - Log response, latency, and success/failure status
3. **Error Boundaries** - Track failures and exceptions in LLM interactions
4. **Token Usage** - Monitor token consumption and costs
5. **User Interactions** - Track user input patterns and satisfaction

#### Implementation Pattern
```python
# Example instrumentation wrapper
import os
from typing import Optional, Any, Dict

# Conditional import with fallback
try:
    if os.getenv('ENABLE_GALILEO', 'false').lower() == 'true':
        import galileo
        GALILEO_ENABLED = True
    else:
        GALILEO_ENABLED = False
except ImportError:
    GALILEO_ENABLED = False
    galileo = None

class LLMInstrumentation:
    @staticmethod
    def log_llm_call(prompt: str, model: str, **kwargs) -> Optional[str]:
        """Log LLM call initiation - BEFORE LLM call"""
        if not GALILEO_ENABLED:
            return None
        
        try:
            return galileo.log_prompt(
                prompt=prompt,
                model=model,
                metadata=kwargs
            )
        except Exception as e:
            # Graceful fallback - never break main flow
            print(f"Galileo logging failed: {e}")
            return None
    
    @staticmethod
    def log_llm_response(call_id: Optional[str], response: str, 
                        latency_ms: int, success: bool = True, 
                        error: Optional[str] = None) -> None:
        """Log LLM response - AFTER LLM call"""
        if not GALILEO_ENABLED or not call_id:
            return
        
        try:
            galileo.log_response(
                call_id=call_id,
                response=response,
                latency_ms=latency_ms,
                success=success,
                error=error
            )
        except Exception as e:
            # Graceful fallback - never break main flow
            print(f"Galileo response logging failed: {e}")

# Usage example
async def call_llm_with_instrumentation(prompt: str, model: str = "gpt-4"):
    # BEFORE LLM call instrumentation
    call_id = LLMInstrumentation.log_llm_call(prompt, model)
    
    start_time = time.time()
    try:
        # Your actual LLM call here
        response = await your_llm_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # AFTER LLM call instrumentation
        latency_ms = int((time.time() - start_time) * 1000)
        LLMInstrumentation.log_llm_response(
            call_id=call_id,
            response=response.choices[0].message.content,
            latency_ms=latency_ms,
            success=True
        )
        
        return response
        
    except Exception as e:
        # Error boundary instrumentation
        latency_ms = int((time.time() - start_time) * 1000)
        LLMInstrumentation.log_llm_response(
            call_id=call_id,
            response="",
            latency_ms=latency_ms,
            success=False,
            error=str(e)
        )
        raise
```

### Integration Checklist
- [ ] Environment variable `ENABLE_GALILEO` properly configured
- [ ] Conditional imports with graceful fallback implemented
- [ ] Before-LLM-call instrumentation added
- [ ] After-LLM-call instrumentation added
- [ ] Error boundary logging implemented
- [ ] Performance impact assessed and documented
- [ ] Fallback behavior tested when Galileo is disabled
- [ ] Dependencies added to optional requirements section

## LLM & MCP Interaction Best Practices

### Provider Architecture Guidelines

#### Abstract Provider Choice via Dependency Injection
- **Reuse Existing `OpenAIProvider`**: Leverage the current `OpenAIProvider` implementation as a foundation
- **Provider Abstraction**: Use dependency injection to abstract LLM provider choice at runtime
- **Factory Pattern**: Implement a provider factory that supports multiple LLM backends

```python
# agent_framework/llm/provider_factory.py
from typing import Dict, Type, Optional
from abc import ABC, abstractmethod
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .models import LLMConfig

class LLMProviderFactory:
    """Factory for creating LLM provider instances with DI support"""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAIProvider,
        # Add other providers here: "anthropic": AnthropicProvider, etc.
    }
    
    @classmethod
    def create_provider(
        cls, 
        provider_name: str, 
        config: LLMConfig,
        **kwargs
    ) -> LLMProvider:
        """Create provider instance based on configuration"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(config, **kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """Register a new provider type"""
        cls._providers[name] = provider_class

# app/dependencies.py - FastAPI DI integration
from fastapi import Depends
from agent_framework.llm.provider_factory import LLMProviderFactory
from agent_framework.llm.models import LLMConfig
from config.settings import get_settings

def get_llm_provider() -> LLMProvider:
    """Dependency injection for LLM provider"""
    settings = get_settings()
    config = LLMConfig(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens
    )
    
    return LLMProviderFactory.create_provider(
        provider_name=settings.llm_provider,  # "openai", "anthropic", etc.
        config=config
    )
```

### MCP Client Integration Rules

#### Accessing MCP Server with Retry & Exponential Back-off
- **Rule**: All MCP server access MUST use `mcp_client` with built-in retry logic
- **Exponential Back-off**: Implement exponential back-off with jitter for failed requests
- **Circuit Breaker**: Use circuit breaker pattern to prevent cascading failures

```python
# mcp_client/retry_client.py
import asyncio
import random
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from datetime import datetime, timedelta

T = TypeVar('T')

class CircuitBreakerState:
    """Circuit breaker state management"""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None
    
    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        elif self.state == "HALF_OPEN":
            self.state = "OPEN"

def with_retry_and_circuit_breaker(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """Decorator for retry logic with exponential back-off and circuit breaker"""
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        circuit_breaker = CircuitBreakerState()
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not circuit_breaker.can_execute():
                raise Exception("Circuit breaker is OPEN - requests blocked")
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    circuit_breaker.record_success()
                    return result
                    
                except Exception as e:
                    last_exception = e
                    circuit_breaker.record_failure()
                    
                    if attempt == max_retries:
                        break
                    
                    # Calculate delay with exponential back-off
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator

# mcp_client/client.py - Enhanced MCP client
class MCPClient:
    """MCP client with retry logic and circuit breaker"""
    
    def __init__(self, transport, default_timeout: float = 30.0):
        self.transport = transport
        self.default_timeout = default_timeout
    
    @with_retry_and_circuit_breaker(max_retries=3, base_delay=1.0)
    async def call_tool(
        self, 
        tool_name: str, 
        arguments: dict,
        timeout: Optional[float] = None
    ) -> Any:
        """Call MCP tool with retry and circuit breaker"""
        timeout = timeout or self.default_timeout
        
        try:
            async with asyncio.timeout(timeout):
                return await self.transport.call_tool(tool_name, arguments)
        except asyncio.TimeoutError:
            raise Exception(f"MCP tool call timeout after {timeout}s")
    
    @with_retry_and_circuit_breaker(max_retries=3, base_delay=1.0)
    async def list_resources(self, timeout: Optional[float] = None) -> Any:
        """List MCP resources with retry and circuit breaker"""
        timeout = timeout or self.default_timeout
        
        try:
            async with asyncio.timeout(timeout):
                return await self.transport.list_resources()
        except asyncio.TimeoutError:
            raise Exception(f"MCP resource listing timeout after {timeout}s")
```

### Streaming Requirements

#### Mandatory Streaming Pattern
- **Rule**: Use streaming (`async for` chunks) wherever possible
- **Fallback**: Provide non-streaming methods for compatibility but prefer streaming
- **Buffering**: Implement proper buffering for streaming responses

```python
# Enhanced OpenAI provider with mandatory streaming preference
class StreamingLLMProvider(LLMProvider):
    """LLM provider with streaming-first approach"""
    
    async def generate_with_preference(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
        prefer_streaming: bool = True
    ) -> Union[LLMResponse, AsyncGenerator[LLMResponse, None]]:
        """Generate response with streaming preference"""
        if prefer_streaming:
            return self.generate_stream(messages, config)
        else:
            return await self.generate(messages, config)
    
    async def process_streaming_response(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None,
        chunk_processor: Optional[Callable[[str], None]] = None
    ) -> str:
        """Process streaming response with chunk handling"""
        full_response = ""
        
        async for chunk in self.generate_stream(messages, config):
            if chunk.content:
                full_response += chunk.content
                
                # Optional chunk processing (e.g., real-time updates)
                if chunk_processor:
                    chunk_processor(chunk.content)
        
        return full_response

# Usage example with MCP integration
class AgentService:
    def __init__(self, llm_provider: LLMProvider, mcp_client: MCPClient):
        self.llm_provider = llm_provider
        self.mcp_client = mcp_client
    
    async def process_user_query_streaming(
        self, 
        query: str,
        stream_callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """Process user query with streaming LLM response"""
        
        # Prepare context from MCP resources (with retry)
        try:
            mcp_context = await self.mcp_client.list_resources()
        except Exception as e:
            # Graceful fallback when MCP is unavailable
            mcp_context = {"error": f"MCP unavailable: {e}"}
        
        # Prepare messages
        messages = [
            LLMMessage(role="system", content=f"Context: {mcp_context}"),
            LLMMessage(role="user", content=query)
        ]
        
        # Stream response with chunk processing
        full_response = ""
        async for chunk in self.llm_provider.generate_stream(messages):
            if chunk.content:
                full_response += chunk.content
                
                # Real-time streaming callback
                if stream_callback:
                    stream_callback(chunk.content)
        
        return full_response
```

### Timeout and Circuit Breaker Configuration

#### Default Timeout Settings
- **LLM Requests**: 30 seconds default, 120 seconds maximum
- **MCP Requests**: 10 seconds default, 30 seconds maximum  
- **Streaming Responses**: 300 seconds (5 minutes) for long generations

#### Circuit Breaker Configuration
- **Failure Threshold**: 5 consecutive failures before opening circuit
- **Recovery Timeout**: 60 seconds before attempting half-open state
- **Success Threshold**: 3 consecutive successes to close circuit from half-open

```python
# config/settings.py - Timeout and circuit breaker settings
from pydantic import BaseSettings

class Settings(BaseSettings):
    # LLM timeout settings
    llm_default_timeout: float = 30.0
    llm_max_timeout: float = 120.0
    llm_streaming_timeout: float = 300.0
    
    # MCP timeout settings
    mcp_default_timeout: float = 10.0
    mcp_max_timeout: float = 30.0
    
    # Circuit breaker settings
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_success_threshold: int = 3
    
    # Retry settings
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_exponential_base: float = 2.0
    
    class Config:
        env_file = ".env"
```

### Best Practices Summary

#### Implementation Checklist
- [ ] **Provider Abstraction**: Use DI factory pattern for LLM provider selection
- [ ] **MCP Retry Logic**: All MCP calls use retry with exponential back-off
- [ ] **Streaming First**: Prefer streaming responses (`async for` chunks)
- [ ] **Timeout Configuration**: Set appropriate timeouts for all operations
- [ ] **Circuit Breaker**: Implement circuit breaker pattern for external calls
- [ ] **Graceful Degradation**: Handle MCP/LLM failures without breaking user experience
- [ ] **Monitoring**: Log retry attempts, circuit breaker state changes, and timeouts
- [ ] **Resource Cleanup**: Properly close connections and clean up resources

#### Anti-Patterns to Avoid
- ❌ **Hard-coded Provider**: Directly instantiating specific LLM providers
- ❌ **No Retry Logic**: Making single-attempt calls to external services
- ❌ **Blocking Calls**: Using synchronous calls instead of async streaming
- ❌ **Infinite Timeouts**: Not setting reasonable timeout limits
- ❌ **Cascading Failures**: Allowing one service failure to break entire system
- ❌ **Resource Leaks**: Not properly closing connections or cleaning up resources

