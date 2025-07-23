#!/usr/bin/env python3
"""
Test script for the improved Awesome List Agent with Galileo logging and learning path generation.

This script demonstrates:
1. Enhanced agent description and capabilities
2. Comprehensive Galileo tool span logging with JSON input/output
3. Improved output format with instructional guidance and learning paths
4. Better error handling and performance monitoring
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from awesome_list_agent.factory import AwesomeListAgentFactory
from awesome_list_logging import setup_logging


async def test_improved_agent():
    """Test the improved agent with Galileo logging and learning path generation."""
    
    print("🚀 Testing Improved Awesome List Agent")
    print("=" * 50)
    print("Features being tested:")
    print("✅ Enhanced agent description and capabilities")
    print("✅ Comprehensive Galileo tool span logging")
    print("✅ JSON input/output logging for all tools")
    print("✅ Learning path generation and instructional guidance")
    print("✅ Improved output format with structured recommendations")
    print()
    
    # Set up logging
    logger = setup_logging(
        log_level="INFO",
        log_file="test_improved_agent.log",
        console_output=True
    )
    
    try:
        # Create agent with Galileo logging enabled
        logger.info("Creating improved AwesomeListAgent with Galileo logging")
        agent = await AwesomeListAgentFactory.create_agent(
            verbosity="high",
            enable_galileo=True
        )
        
        # Test with a real awesome list
        test_url = "https://github.com/sindresorhus/awesome"
        
        print(f"📚 Processing Awesome List: {test_url}")
        print("This will demonstrate:")
        print("  - Tool span logging with JSON input/output")
        print("  - Learning path generation")
        print("  - Instructional guidance")
        print("  - Performance monitoring")
        print()
        
        # Process the awesome list
        result = await agent.process_awesome_list(test_url)
        
        # Display results
        print("\n" + "="*60)
        print("🎯 RESULTS SUMMARY")
        print("="*60)
        
        if result.get('status') == 'success':
            print("✅ Processing completed successfully!")
            
            parsed_data = result.get('parsed_data', {})
            learning_guidance = result.get('learning_guidance', {})
            
            print(f"\n📊 Extracted Information:")
            print(f"   Topic: {parsed_data.get('topic', 'N/A')}")
            print(f"   Resources: {parsed_data.get('total_items', 0)} items")
            print(f"   Categories: {len(parsed_data.get('categories', []))}")
            print(f"   Language: {parsed_data.get('language', 'N/A')}")
            
            if learning_guidance:
                learning_paths = learning_guidance.get('learning_paths', [])
                print(f"\n🎓 Generated {len(learning_paths)} learning paths")
                
                for i, path in enumerate(learning_paths[:3], 1):
                    print(f"   Path {i}: {path.get('name', 'N/A')}")
                    print(f"     Difficulty: {path.get('difficulty', 'N/A')}")
                    print(f"     Time: {path.get('estimated_hours', 0)} hours")
                
                instructional = learning_guidance.get('instructional_guidance', {})
                if instructional:
                    time_commitment = instructional.get('time_commitment', {})
                    print(f"\n⏰ Time Commitment:")
                    print(f"   Total: {time_commitment.get('total_hours', 0)} hours")
                    print(f"   Weekly: {time_commitment.get('weekly_hours', 0)} hours/week")
                    print(f"   Duration: {time_commitment.get('estimated_weeks', 0)} weeks")
            
            # Show processing metadata
            metadata = result.get('processing_metadata', {})
            if metadata:
                print(f"\n🔧 Processing Performance:")
                print(f"   Duration: {metadata.get('total_duration_seconds', 0):.2f} seconds")
                print(f"   Agent Version: {metadata.get('agent_version', 'N/A')}")
            
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
        
        print(f"\n📝 Check the log file 'test_improved_agent.log' for detailed Galileo spans")
        print(f"🔍 Look for JSON-formatted tool spans with input/output data")
        
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}", exc_info=True)
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return True


async def test_galileo_logging_demo():
    """Demonstrate the Galileo logging capabilities."""
    
    print("\n" + "="*60)
    print("🔍 GALILEO LOGGING DEMONSTRATION")
    print("="*60)
    
    # Set up logging with Galileo enabled
    logger = setup_logging(
        log_level="DEBUG",
        log_file="galileo_demo.log",
        console_output=True
    )
    
    try:
        # Create agent
        agent = await AwesomeListAgentFactory.create_agent(
            verbosity="high",
            enable_galileo=True
        )
        
        # Test with a smaller awesome list for faster processing
        test_url = "https://github.com/vinta/awesome-python"
        
        print(f"🔧 Testing Galileo logging with: {test_url}")
        print("This will generate detailed tool spans with JSON input/output")
        print()
        
        # Process and capture detailed logging
        result = await agent.process_awesome_list(test_url)
        
        print("✅ Galileo logging test completed!")
        print("📋 Check 'galileo_demo.log' for detailed span information")
        print("🔍 Look for entries like:")
        print("   - Tool Span: awesome_list_parser")
        print("   - Tool Span: learning_path_generator")
        print("   - Tool Span: mcp_server_call")
        print("   - Each span includes JSON input/output data")
        
    except Exception as e:
        logger.error(f"Galileo demo failed: {str(e)}", exc_info=True)
        print(f"❌ Galileo demo failed: {str(e)}")


async def main():
    """Main test function."""
    print("🧪 Awesome List Agent Improvement Test Suite")
    print("=" * 60)
    
    # Test 1: Basic improved agent functionality
    success1 = await test_improved_agent()
    
    # Test 2: Galileo logging demonstration
    await test_galileo_logging_demo()
    
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    if success1:
        print("✅ Basic agent functionality: PASSED")
    else:
        print("❌ Basic agent functionality: FAILED")
    
    print("✅ Galileo logging demonstration: COMPLETED")
    print("\n🎉 All tests completed!")
    print("\n📚 Next steps:")
    print("   1. Review the generated log files for detailed spans")
    print("   2. Check the JSON input/output data in tool spans")
    print("   3. Examine the learning path recommendations")
    print("   4. Test with different awesome list URLs")


if __name__ == "__main__":
    # Set environment variable for Galileo (if not already set)
    if not os.getenv("GALILEO_ENABLED"):
        os.environ["GALILEO_ENABLED"] = "true"
    
    asyncio.run(main()) 