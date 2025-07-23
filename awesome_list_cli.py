#!/usr/bin/env python3
"""
Awesome List Agent CLI

A simple command-line interface for the Awesome List Agent that processes
Awesome Lists and generates learning paths with Galileo observability.
"""

import asyncio
import sys
import os
from typing import Optional
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from awesome_list_agent.awesome_list_agent import AwesomeListAgent
from awesome_list_agent.config import AgentConfiguration, EnvironmentError
from awesome_list_agent.utils.galileo_logger import GalileoAgentLogger

def setup_environment():
    """Set up environment variables and configuration."""
    load_dotenv()
    
    # Set default Galileo configuration if not already set
    if not os.getenv("GALILEO_API_KEY"):
        print("⚠️  Warning: GALILEO_API_KEY not found in environment variables.")
        print("   Galileo logging will be disabled. Set GALILEO_API_KEY to enable observability.")
    
    # Set default OpenAI configuration if not already set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY is required but not found.")
        print("   Please set OPENAI_API_KEY in your .env file or environment variables.")
        sys.exit(1)

def get_awesome_list_url() -> str:
    """Get the Awesome List URL from user input."""
    print("\n🚀 Awesome List Agent CLI")
    print("=" * 50)
    print("This tool will analyze an Awesome List and generate a learning path for you.")
    print("It will extract key information, assess difficulty levels, and provide")
    print("personalized learning recommendations with Galileo observability.\n")
    
    while True:
        url = input("📋 Please enter the Awesome List URL: ").strip()
        
        if not url:
            print("❌ URL cannot be empty. Please try again.")
            continue
            
        if not url.startswith(('http://', 'https://')):
            print("❌ Please enter a valid URL starting with http:// or https://")
            continue
            
        # Basic URL validation
        if 'github.com' in url or 'awesome' in url.lower():
            return url
        else:
            confirm = input("⚠️  This doesn't look like a typical Awesome List URL. Continue anyway? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                return url
            else:
                print("Please enter a different URL.")

def create_agent_config() -> AgentConfiguration:
    """Create agent configuration with Galileo logging enabled."""
    try:
        # Create configuration with required API keys
        config = AgentConfiguration.from_env(
            required_keys=["openai"],
            optional_keys={"galileo": None}
        )
        
        # Override to ensure Galileo logging is enabled
        config = config.with_overrides(
            enable_logging=True,
            verbosity="medium"  # Show informative output
        )
        
        return config
        
    except EnvironmentError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)

async def run_agent(url: str):
    """Run the Awesome List Agent with the given URL."""
    print(f"\n🔍 Processing Awesome List: {url}")
    print("⏳ This may take a few moments...\n")
    
    try:
        # Create configuration
        config = create_agent_config()
        
        # Set up Galileo logger
        galileo_logger = GalileoAgentLogger(agent_id="awesome_list_cli")
        
        # Create agent with Galileo logging
        agent = AwesomeListAgent(
            config=config,
            logger=galileo_logger
        )
        
        # Process the awesome list
        result = await agent.process_awesome_list(url)
        
        # Check if processing was successful
        if result.get("status") != "success":
            print(f"\n❌ Error processing Awesome List: {result.get('error', 'Unknown error')}")
            return
        
        # Display initial summary
        print("\n" + "=" * 60)
        print("📊 INITIAL ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Display basic information from parsed data
        if "parsed_data" in result:
            parsed_data = result["parsed_data"]
            print(f"\n📋 Topic: {parsed_data.get('topic', 'Awesome List Analysis')}")
            print(f"📚 Total Resources: {parsed_data.get('total_items', 0)}")
            print(f"📂 Categories Found: {len(parsed_data.get('categories', []))}")
            print(f"🎥 YouTube Videos: {len(parsed_data.get('youtube_metadata', []))}")
            
            # Display comprehensive summary if available
            if "comprehensive_summary" in parsed_data:
                print(f"\n📖 Summary: {parsed_data['comprehensive_summary']}")
            
            # Display processing metadata
            if "metadata" in result:
                metadata = result["metadata"]
                print(f"\n⏱️  Processing Time: {metadata.get('processing_time', 'Unknown')}")
        
        # Ask for user confirmation
        print("\n" + "=" * 60)
        while True:
            confirm = input("🤔 Are you ready to see the top 5 recommended YouTube videos? (yes/no): ").strip().lower()
            if confirm in ['yes', 'y']:
                break
            elif confirm in ['no', 'n']:
                print("\n👋 Thanks for using Awesome List Agent! Goodbye!")
                return
            else:
                print("❌ Please enter 'yes' or 'no'.")
        
        # Display top 5 recommended YouTube videos
        print("\n" + "=" * 60)
        print("🎬 TOP 5 RECOMMENDED YOUTUBE VIDEOS")
        print("=" * 60)
        
        if "parsed_data" in result and "youtube_metadata" in result["parsed_data"]:
            youtube_videos = result["parsed_data"]["youtube_metadata"]
            
            if not youtube_videos:
                print("\n❌ No YouTube videos found in this Awesome List.")
                return
            
            # Sort videos by view count and duration to get the most popular/valuable ones
            sorted_videos = sorted(
                youtube_videos, 
                key=lambda x: (x.get('view_count', 0), -(x.get('duration_seconds', 0))), 
                reverse=True
            )
            
            # Display top 5 videos
            top_5_videos = sorted_videos[:5]
            
            for i, video in enumerate(top_5_videos, 1):
                print(f"\n{i}. 🎥 {video.get('title', 'Unknown Title')}")
                print(f"   👤 Channel: {video.get('channel_name', 'Unknown Channel')}")
                print(f"   👀 Views: {video.get('view_count', 0):,}")
                print(f"   ⏱️  Duration: {video.get('duration_seconds', 0) // 60}:{video.get('duration_seconds', 0) % 60:02d}")
                print(f"   📅 Published: {video.get('published_date', 'Unknown')}")
                print(f"   🔗 Watch Now: {video.get('url', 'No URL available')}")
                
                # Add description if available
                if video.get('description'):
                    desc = video['description'][:100] + "..." if len(video['description']) > 100 else video['description']
                    print(f"   📝 {desc}")
        
        # Display additional analysis results
        print("\n" + "=" * 60)
        print("🎯 COMPREHENSIVE ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Display learning path
        if "learning_path" in result:
            learning_path = result["learning_path"]
            print(f"\n📚 Learning Path: {learning_path.get('title', 'Awesome List Learning Journey')}")
            print(f"🎯 Difficulty Level: {learning_path.get('difficulty', 'Intermediate')}")
            print(f"⏱️  Estimated Time: {learning_path.get('estimated_time', '2-4 weeks')}")
            print(f"📊 Total Resources: {learning_path.get('total_resources', 0)}")
            print(f"💻 Primary Language: {learning_path.get('primary_language', 'General')}")
            
            if "steps" in learning_path:
                print(f"\n📋 Learning Steps ({len(learning_path['steps'])} total):")
                for i, step in enumerate(learning_path["steps"], 1):
                    print(f"  {i}. {step.get('title', 'Learning step')}")
                    if step.get('description'):
                        print(f"     💡 {step['description']}")
                    if step.get('estimated_time'):
                        print(f"     ⏱️  {step['estimated_time']}")
                    if step.get('resources_count'):
                        print(f"     📚 ~{step['resources_count']} resources")
                    print()
        
        # Display instructional guidance
        if "instructional_guidance" in result:
            guidance = result["instructional_guidance"]
            print("🎓 Instructional Guidance:")
            print(f"   {guidance.get('summary', 'No guidance available')}")
            
            if "tips" in guidance:
                print("\n💡 Learning Tips:")
                for tip in guidance["tips"]:
                    print(f"   • {tip}")
            
            if "focus_areas" in guidance and guidance["focus_areas"]:
                print(f"\n🎯 Focus Areas:")
                for area in guidance["focus_areas"]:
                    print(f"   • {area}")
            
            if "recommended_starting_point" in guidance:
                print(f"\n🚀 Recommended Starting Point: {guidance['recommended_starting_point']}")
        
        # Display comprehensive summary from parsed data
        if "parsed_data" in result and "comprehensive_summary" in result["parsed_data"]:
            print(f"\n📖 Comprehensive Summary:")
            print(f"   {result['parsed_data']['comprehensive_summary']}")
        
        # Display processing metadata
        if "metadata" in result:
            metadata = result["metadata"]
            print(f"\n📊 Processing Summary:")
            print(f"   • Total items processed: {metadata.get('total_items', 'Unknown')}")
            print(f"   • Categories found: {metadata.get('categories_count', 'Unknown')}")
            print(f"   • YouTube videos analyzed: {metadata.get('youtube_videos_count', 'Unknown')}")
            print(f"   • Processing time: {metadata.get('processing_time', 'Unknown')}")
            print(f"   • Galileo trace ID: {metadata.get('trace_id', 'Not available')}")
        
        # Display MCP server status
        if "mcp_result" in result:
            mcp_result = result["mcp_result"]
            mcp_status = mcp_result.get("mcp_status", "unknown")
            if mcp_status == "success":
                print(f"\n🔗 MCP Server: ✅ Successfully processed")
            else:
                print(f"\n🔗 MCP Server: ⚠️  {mcp_result.get('message', 'Unknown status')}")
        
        print("\n✅ Processing complete! Check your Galileo dashboard for detailed observability data.")
        
    except Exception as e:
        print(f"\n❌ Error processing Awesome List: {str(e)}")
        print("Please check your internet connection and try again.")
        if hasattr(e, '__traceback__'):
            import traceback
            print("\nDetailed error information:")
            traceback.print_exc()

def main():
    """Main CLI entry point."""
    try:
        # Set up environment
        setup_environment()
        
        # Get URL from user
        url = get_awesome_list_url()
        
        # Run the agent
        asyncio.run(run_agent(url))
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Awesome List Agent.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 