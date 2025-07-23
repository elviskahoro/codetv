# Galileo Observability Integration

This document explains how to integrate Galileo observability into your agent framework applications for comprehensive monitoring, tracing, and debugging of LLM interactions and tool executions.

## What is Galileo?

Galileo is an observability platform designed specifically for AI applications. It provides:

- **Trace and Span Logging**: Track the flow of LLM calls and tool executions
- **Performance Metrics**: Monitor latency, token usage, and costs
- **Error Tracking**: Identify and debug issues in your AI applications
- **Visualization**: View traces and spans in an intuitive web interface

## Features

The Galileo integration in this agent framework provides:

### 🔍 **Automatic LLM Tracing**
- Logs all OpenAI API calls with input/output, token usage, and latency
- Captures structured data generation (function calling)
- Tracks errors and parsing failures

### 🛠️ **Tool Execution Monitoring**
- Monitors tool execution time and success/failure rates
- Logs tool inputs and outputs
- Tracks tool selection reasoning

### 📊 **Agent-Level Observability**
- Complete task execution traces
- Planning and reasoning logs
- Performance metrics across the entire agent workflow

### 🛡️ **Graceful Fallback**
- If Galileo is not configured, falls back to console logging
- No breaking changes to existing functionality
- Optional feature that can be enabled/disabled

## Setup Instructions

### 1. Install Dependencies

The Galileo SDK is already included in the requirements. If you need to install it separately:

```bash
pip install "galileo[openai]"
```

### 2. Environment Configuration

Create or update your `.env` file with Galileo credentials:

```ini
# Galileo Configuration
ENABLE_GALILEO=true
GALILEO_API_KEY=your_galileo_api_key_here
GALILEO_PROJECT=your_project_name_here
GALILEO_LOG_STREAM=your_log_stream_name_here

# OpenAI Configuration (required)
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Get Galileo Credentials

1. Sign up at [Galileo App](https://app.galileo.ai)
2. Create a new project
3. Generate an API key in the settings
4. Note your project name and log stream name

## Usage

### Basic Usage

The Galileo integration is automatically enabled when you set `ENABLE_GALILEO=true` in your environment. The framework will:

1. **Automatically create traces** for each agent task
2. **Log LLM spans** for all OpenAI API calls
3. **Track tool executions** with timing and results
4. **Provide fallback logging** if Galileo is unavailable

### Example Code

```python
import asyncio
from dotenv import load_dotenv
from agent_framework.config import AgentConfiguration
from agent_framework.factory import AgentFactory
from agent_framework.utils.galileo_logger import create_galileo_logger

# Load environment variables
load_dotenv()

async def main():
    # Create configuration
    config = AgentConfiguration.from_env(required_keys=["openai"])
    
    # Create factory (automatically uses Galileo logger if enabled)
    factory = AgentFactory(config)
    
    # Get LLM provider and logger
    llm_provider = factory.get_llm_provider()
    logger = create_galileo_logger("my-agent-001")
    
    # Your agent logic here...
    # All LLM calls and tool executions will be automatically logged

if __name__ == "__main__":
    asyncio.run(main())
```

### Manual Trace Control

For more granular control, you can manually manage traces:

```python
from agent_framework.utils.galileo_logger import GalileoAgentLogger

# Create Galileo logger
logger = GalileoAgentLogger("my-agent-001")

# Start a custom trace
logger.start_trace("Custom Task Trace")

# Your operations here...

# Conclude the trace
logger.conclude_trace("Task completed successfully")
```

## What Gets Logged

### LLM Spans

Each OpenAI API call creates a span with:

- **Input/Output**: Full prompt and response text
- **Model Information**: Model name and configuration
- **Token Usage**: Input, output, and total tokens
- **Performance**: Latency in nanoseconds
- **Metadata**: Agent ID, timestamp, etc.

### Tool Spans

Each tool execution creates a span with:

- **Tool Name**: Identifier for the tool
- **Inputs**: Parameters passed to the tool
- **Outputs**: Results returned by the tool
- **Success/Failure**: Execution status
- **Duration**: Execution time
- **Error Details**: Error messages if execution fails

### Agent Traces

Each agent task creates a trace containing:

- **Task Description**: What the agent was asked to do
- **Planning**: Agent's reasoning and planning process
- **Execution Steps**: Sequence of tool calls and LLM interactions
- **Final Result**: Completed task output
- **Total Duration**: End-to-end execution time

## Viewing Data in Galileo Console

1. **Navigate to your project** in the [Galileo Console](https://app.galileo.ai)
2. **Select your log stream** to see traces
3. **Click on any trace** to view detailed spans
4. **Explore metrics** in the Metrics tab for performance insights

### Trace View

The trace view shows:
- **Input/Output**: The original task and final result
- **Spans**: Individual LLM calls and tool executions
- **Timeline**: Visual representation of execution flow
- **Performance**: Latency breakdown by component

### Metrics View

The metrics view provides:
- **Latency Distribution**: Response time percentiles
- **Token Usage**: Input/output token trends
- **Error Rates**: Success/failure percentages
- **Cost Analysis**: Token usage and estimated costs

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENABLE_GALILEO` | Enable/disable Galileo logging | `false` |
| `GALILEO_API_KEY` | Your Galileo API key | Required if enabled |
| `GALILEO_PROJECT` | Project name in Galileo | Required if enabled |
| `GALILEO_LOG_STREAM` | Log stream name | Required if enabled |
| `GALILEO_CONSOLE_URL` | Custom Galileo console URL | Auto-detected |

### Logger Configuration

```python
# Create logger with custom project/log stream
logger = GalileoAgentLogger(
    agent_id="my-agent",
    project_name="custom-project",
    log_stream="custom-stream"
)
```

## Troubleshooting

### Common Issues

#### 1. Galileo Not Initializing

**Symptoms**: Console shows "Galileo SDK not available" or "GALILEO_API_KEY not found"

**Solutions**:
- Check that `ENABLE_GALILEO=true` in your `.env` file
- Verify `GALILEO_API_KEY` is set correctly
- Ensure `GALILEO_PROJECT` and `GALILEO_LOG_STREAM` are configured

#### 2. No Data in Galileo Console

**Symptoms**: Traces not appearing in the console

**Solutions**:
- Check your internet connection
- Verify API key permissions
- Ensure project and log stream names match exactly
- Check for error messages in console output

#### 3. Performance Impact

**Symptoms**: Application running slower with Galileo enabled

**Solutions**:
- Galileo logging is asynchronous and shouldn't significantly impact performance
- If issues persist, consider disabling for high-throughput scenarios
- Check network connectivity to Galileo servers

### Debug Mode

Enable debug logging to see detailed Galileo operations:

```python
import logging
logging.getLogger('galileo').setLevel(logging.DEBUG)
```

## Best Practices

### 1. **Use Descriptive Trace Names**

```python
# Good
logger.start_trace("Customer Support Query: Refund Request")

# Avoid
logger.start_trace("Task 1")
```

### 2. **Monitor Key Metrics**

Focus on these important metrics:
- **Latency**: Response time percentiles (P50, P95, P99)
- **Token Usage**: Input/output token ratios
- **Error Rates**: Success/failure percentages
- **Cost**: Token usage trends

### 3. **Set Up Alerts**

Configure alerts for:
- High error rates (>5%)
- Unusual latency spikes
- Excessive token usage
- Failed tool executions

### 4. **Regular Monitoring**

- Review traces daily for new patterns
- Monitor cost trends weekly
- Analyze error patterns monthly
- Update alert thresholds as needed

## Example: Complete Integration

Here's a complete example showing Galileo integration:

```python
#!/usr/bin/env python3
"""
Complete Galileo Integration Example
"""

import asyncio
import os
from dotenv import load_dotenv
from agent_framework.config import AgentConfiguration
from agent_framework.factory import AgentFactory
from agent_framework.utils.galileo_logger import create_galileo_logger

load_dotenv()

class GalileoAwareAgent:
    def __init__(self):
        # Create configuration
        self.config = AgentConfiguration.from_env(required_keys=["openai"])
        self.factory = AgentFactory(self.config)
        
        # Get dependencies
        self.llm_provider = self.factory.get_llm_provider()
        self.logger = create_galileo_logger("galileo-demo-agent")
    
    async def process_query(self, query: str) -> str:
        """Process a user query with full Galileo observability"""
        
        # Start trace (automatically called by logger.on_agent_start)
        self.logger.on_agent_start(query)
        
        try:
            # Create messages
            messages = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": query}
            ]
            
            # Generate response (automatically logged to Galileo)
            response = await self.llm_provider.generate(
                messages,
                logger=self.logger
            )
            
            result = response.content
            
            # Log completion (automatically concludes trace)
            await self.logger.on_agent_done(result, [])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {str(e)}")
            raise

async def main():
    # Check Galileo status
    enable_galileo = os.getenv("ENABLE_GALILEO", "false").lower() == "true"
    
    print(f"Galileo Status: {'✅ Enabled' if enable_galileo else '⚠️ Disabled'}")
    
    # Create agent
    agent = GalileoAwareAgent()
    
    # Process queries
    queries = [
        "What is machine learning?",
        "Explain quantum computing",
        "How does blockchain work?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Input: {query}")
        
        try:
            result = await agent.process_query(query)
            print(f"Output: {result[:100]}...")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\n🎉 All queries processed!")
    if enable_galileo:
        print("📊 Check your Galileo console for traces and metrics!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Support

For issues with the Galileo integration:

1. **Check the troubleshooting section** above
2. **Review Galileo documentation** at [docs.galileo.ai](https://docs.galileo.ai)
3. **Contact Galileo support** through their console
4. **Open an issue** in this repository for framework-specific problems

## Migration Guide

### From Console Logging Only

If you're currently using only console logging:

1. **Set up Galileo credentials** in your `.env` file
2. **Enable Galileo** by setting `ENABLE_GALILEO=true`
3. **No code changes required** - the integration is automatic
4. **Verify traces appear** in your Galileo console

### From Other Observability Tools

If you're migrating from other observability tools:

1. **Export existing data** from your current tool
2. **Set up Galileo** following the setup instructions
3. **Update environment variables** to use Galileo
4. **Test with a small subset** of your workload
5. **Gradually migrate** full production traffic

---

**Note**: This integration is designed to be backward compatible. Your existing code will continue to work whether Galileo is enabled or not. 