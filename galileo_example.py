#!/usr/bin/env python3
"""
Galileo Logging Example

This script demonstrates how to use Galileo observability with the agent framework.
It shows how to enable Galileo logging and what data gets captured.

To run this example:

1. Set up your .env file with Galileo credentials:
   ENABLE_GALILEO=true
   GALILEO_API_KEY=your_api_key
   GALILEO_PROJECT=your_project_name
   GALILEO_LOG_STREAM=your_log_stream_name
   OPENAI_API_KEY=your_openai_key

2. Run the script:
   python galileo_example.py

If Galileo is not configured, the system will fall back to console logging.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent_framework.config import AgentConfiguration
from agent_framework.factory import AgentFactory
from agent_framework.utils.galileo_logger import create_galileo_logger


class SimpleExampleAgent:
    """A simple example agent that demonstrates Galileo logging"""
    
    def __init__(self, llm_provider, logger):
        self.llm_provider = llm_provider
        self.logger = logger
    
    async def run_simple_task(self, task: str) -> str:
        """Run a simple task with Galileo logging"""
        
        # Start the agent (this will start a Galileo trace)
        self.logger.on_agent_start(task)
        
        try:
            # Create a simple prompt
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": task}
            ]
            
            # Generate response with Galileo logging
            response = await self.llm_provider.generate(
                messages,
                logger=self.logger
            )
            
            result = f"Task completed: {response.content}"
            
            # Log completion
            await self.logger.on_agent_done(result, [])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task failed: {str(e)}")
            raise


async def main():
    """Main function demonstrating Galileo logging"""
    
    print("🚀 Galileo Logging Example")
    print("=" * 50)
    
    # Check if Galileo is enabled
    enable_galileo = os.getenv("ENABLE_GALILEO", "false").lower() == "true"
    
    if enable_galileo:
        print("✅ Galileo logging is ENABLED")
        print(f"   Project: {os.getenv('GALILEO_PROJECT', 'Not set')}")
        print(f"   Log Stream: {os.getenv('GALILEO_LOG_STREAM', 'Not set')}")
    else:
        print("⚠️  Galileo logging is DISABLED")
        print("   Set ENABLE_GALILEO=true in your .env file to enable")
    
    print()
    
    # Create configuration
    config = AgentConfiguration.from_env(
        required_keys=["openai"],
        optional_keys={
            "galileo_api_key": "GALILEO_API_KEY",
            "galileo_project": "GALILEO_PROJECT",
            "galileo_log_stream": "GALILEO_LOG_STREAM"
        }
    )
    
    # Create factory
    factory = AgentFactory(config)
    
    # Get LLM provider
    llm_provider = factory.get_llm_provider()
    
    # Create logger (this will be Galileo logger if enabled)
    logger = create_galileo_logger("example-agent-001")
    
    # Create example agent
    agent = SimpleExampleAgent(llm_provider, logger)
    
    # Run a simple task
    task = "Explain the concept of machine learning in one sentence."
    print(f"📝 Running task: {task}")
    print()
    
    try:
        result = await agent.run_simple_task(task)
        print(f"✅ Result: {result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    print("🎉 Example completed!")
    
    if enable_galileo:
        print("📊 Check your Galileo console to see the logged traces and spans!")


if __name__ == "__main__":
    asyncio.run(main()) 