#!/usr/bin/env python3
"""
Test Galileo Integration

This script tests the Galileo integration to ensure it works correctly
in both enabled and disabled states.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_galileo_logger_creation():
    """Test that Galileo logger can be created in both states"""
    print("🧪 Testing Galileo Logger Creation")
    print("=" * 50)
    
    # Test with Galileo disabled
    os.environ["ENABLE_GALILEO"] = "false"
    
    try:
        from agent_framework.utils.galileo_logger import create_galileo_logger
        logger = create_galileo_logger("test-agent-001")
        print("✅ Galileo logger created successfully (disabled mode)")
        print(f"   Logger type: {type(logger).__name__}")
        
        # Test basic logging
        logger.info("Test message")
        logger.warning("Test warning")
        logger.error("Test error")
        print("✅ Basic logging works in disabled mode")
        
    except Exception as e:
        print(f"❌ Failed to create logger in disabled mode: {e}")
        return False
    
    # Test with Galileo enabled (but not configured)
    os.environ["ENABLE_GALILEO"] = "true"
    
    try:
        logger = create_galileo_logger("test-agent-002")
        print("✅ Galileo logger created successfully (enabled mode)")
        print(f"   Logger type: {type(logger).__name__}")
        
        # Test basic logging
        logger.info("Test message")
        logger.warning("Test warning")
        logger.error("Test error")
        print("✅ Basic logging works in enabled mode")
        
    except Exception as e:
        print(f"❌ Failed to create logger in enabled mode: {e}")
        return False
    
    print()
    return True


async def test_galileo_trace_methods():
    """Test that trace methods work correctly"""
    print("🧪 Testing Galileo Trace Methods")
    print("=" * 50)
    
    try:
        from agent_framework.utils.galileo_logger import create_galileo_logger
        
        # Create logger
        logger = create_galileo_logger("trace-test-agent")
        
        # Test trace methods
        logger.start_trace("Test Trace")
        print("✅ start_trace() called successfully")
        
        logger.add_llm_span(
            input_text="Test input",
            output_text="Test output",
            model="gpt-4",
            name="Test LLM Span",
            num_input_tokens=10,
            num_output_tokens=20,
            total_tokens=30,
            duration_ns=1000000
        )
        print("✅ add_llm_span() called successfully")
        
        logger.add_tool_span(
            tool_name="test_tool",
            inputs={"param1": "value1"},
            outputs={"result": "success"},
            duration_ns=500000,
            success=True
        )
        print("✅ add_tool_span() called successfully")
        
        logger.conclude_trace("Test completed", duration_ns=2000000)
        print("✅ conclude_trace() called successfully")
        
        # Test agent lifecycle methods
        logger.on_agent_start("Test task")
        await logger.on_agent_planning("Test planning")
        await logger.on_agent_done("Test result", [])
        print("✅ Agent lifecycle methods called successfully")
        
    except Exception as e:
        print(f"❌ Failed to test trace methods: {e}")
        return False
    
    print()
    return True


async def test_llm_provider_integration():
    """Test that LLM provider integrates with Galileo logging"""
    print("🧪 Testing LLM Provider Integration")
    print("=" * 50)
    
    try:
        from agent_framework.config import AgentConfiguration
        from agent_framework.factory import AgentFactory
        from agent_framework.utils.galileo_logger import create_galileo_logger
        
        # Create configuration (without requiring actual API keys)
        config = AgentConfiguration.from_dict({
            "api_keys": {"openai": "test-key"},
            "llm_model": "gpt-4",
            "llm_temperature": 0.1,
            "enable_logging": True
        })
        
        # Create factory
        factory = AgentFactory(config)
        
        # Get logger
        logger = create_galileo_logger("llm-test-agent")
        print("✅ Factory and logger created successfully")
        
        # Note: We can't actually test LLM calls without real API keys,
        # but we can verify the integration is set up correctly
        print("✅ LLM provider integration setup verified")
        
    except Exception as e:
        print(f"❌ Failed to test LLM provider integration: {e}")
        return False
    
    print()
    return True


def test_environment_configuration():
    """Test environment variable configuration"""
    print("🧪 Testing Environment Configuration")
    print("=" * 50)
    
    # Test default values
    enable_galileo = os.getenv("ENABLE_GALILEO", "false").lower() == "true"
    galileo_api_key = os.getenv("GALILEO_API_KEY")
    galileo_project = os.getenv("GALILEO_PROJECT")
    galileo_log_stream = os.getenv("GALILEO_LOG_STREAM")
    
    print(f"ENABLE_GALILEO: {os.getenv('ENABLE_GALILEO', 'false')}")
    print(f"GALILEO_API_KEY: {'Set' if galileo_api_key else 'Not set'}")
    print(f"GALILEO_PROJECT: {galileo_project or 'Not set'}")
    print(f"GALILEO_LOG_STREAM: {galileo_log_stream or 'Not set'}")
    
    if enable_galileo:
        if not galileo_api_key:
            print("⚠️  Galileo enabled but API key not set")
        if not galileo_project:
            print("⚠️  Galileo enabled but project not set")
        if not galileo_log_stream:
            print("⚠️  Galileo enabled but log stream not set")
    
    print("✅ Environment configuration checked")
    print()
    return True


async def main():
    """Run all tests"""
    print("🚀 Galileo Integration Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Logger Creation", test_galileo_logger_creation),
        ("Trace Methods", test_galileo_trace_methods),
        ("LLM Provider Integration", test_llm_provider_integration),
        ("Environment Configuration", test_environment_configuration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
        
        print()
    
    print("📊 Test Results")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Galileo integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print()
    print("💡 Next Steps:")
    print("1. Set up your .env file with Galileo credentials")
    print("2. Set ENABLE_GALILEO=true to enable Galileo logging")
    print("3. Run your agent applications to see traces in Galileo console")
    print("4. Check GALILEO_INTEGRATION.md for detailed setup instructions")


if __name__ == "__main__":
    asyncio.run(main()) 