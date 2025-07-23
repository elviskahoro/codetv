#!/usr/bin/env python3

import asyncio
import sys
import json
import argparse
import os
from datetime import datetime
from pathlib import Path
from awesome_list_agent.factory import AwesomeListAgentFactory
from awesome_list_logging import setup_logging

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process Awesome List URLs using the AwesomeListAgent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python awesome_list_interface.py https://github.com/sindresorhus/awesome
  python awesome_list_interface.py --log-level DEBUG --output-file results.json https://github.com/vinta/awesome-python
  python awesome_list_interface.py --enable-galileo https://github.com/sindresorhus/awesome
        """
    )
    
    parser.add_argument(
        "url",
        help="The Awesome List URL to process"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Specify custom log file path (default: auto-generated in logs/ directory)"
    )
    
    parser.add_argument(
        "--output-file",
        help="Save results to JSON file"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (logs still written to file)"
    )
    
    parser.add_argument(
        "--enable-galileo",
        action="store_true",
        help="Enable Galileo observability logging"
    )
    
    parser.add_argument(
        "--verbosity",
        choices=["none", "low", "high"],
        default="low",
        help="Set agent verbosity level (default: low)"
    )
    
    return parser.parse_args()

async def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(
        log_level=args.log_level,
        log_file=args.log_file,
        console_output=not args.quiet
    )
    
    # Log application start
    logger.info("=" * 60)
    logger.info("Starting Awesome List Agent CLI")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Input URL: {args.url}")
    logger.info(f"Log Level: {args.log_level}")
    logger.info(f"Verbosity: {args.verbosity}")
    logger.info(f"Galileo Enabled: {args.enable_galileo}")
    logger.info("=" * 60)
    
    if not args.quiet:
        print(f"\n🔍 Processing Awesome List URL: {args.url}")
        print(f"📝 Logging at {args.log_level} level")
        print(f"🔊 Verbosity: {args.verbosity}")
        if args.log_file:
            print(f"📄 Log file: {args.log_file}")
        if args.enable_galileo:
            print(f"📊 Galileo observability: ENABLED")
        else:
            print(f"📊 Galileo observability: DISABLED")
        print("-" * 50)
    
    try:
        # Initialize agent using factory with Galileo support
        logger.info("Initializing AwesomeListAgent with factory")
        agent = await AwesomeListAgentFactory.create_agent(
            verbosity=args.verbosity,
            enable_galileo=args.enable_galileo
        )
        
        # Process the URL
        logger.info(f"Starting to process URL: {args.url}")
        start_time = datetime.now()
        
        result = await agent.process_awesome_list(args.url)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Log results
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Result status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            logger.info("Successfully processed Awesome List")
            parsed_data = result.get('parsed_data', {})
            logger.info(f"Extracted topic: {parsed_data.get('topic', 'N/A')}")
            logger.info(f"Found {parsed_data.get('total_items', 0)} items")
            logger.info(f"Detected language: {parsed_data.get('language', 'N/A')}")
            logger.info(f"Categories: {len(parsed_data.get('categories', []))}")
        else:
            logger.error(f"Processing failed: {result.get('error', 'Unknown error')}")
        
        # Display results to user (if not quiet)
        if not args.quiet:
            display_results(result, processing_time)
        
        # Save to file if requested
        if args.output_file:
            save_results_to_file(result, args.output_file, logger)
        
        # Log completion
        logger.info("Application completed successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        if not args.quiet:
            print(f"\n❌ Error processing URL: {e}")
            print("Check the log file for detailed error information.")
        sys.exit(1)

def display_results(result: dict, processing_time: float):
    """Display results in a user-friendly format with learning guidance."""
    print(f"\n✅ Processing completed in {processing_time:.2f} seconds\n")
    
    if result.get('status') == 'error':
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    parsed_data = result.get('parsed_data', {})
    learning_guidance = result.get('learning_guidance', {})
    
    # Display basic information
    print("🎯 LEARNING PATH GENERATOR RESULTS")
    print("=" * 50)
    
    # Basic parsed information
    print("\n📊 RESOURCE ANALYSIS:")
    print("-" * 25)
    
    info_items = [
        ("Topic", parsed_data.get('topic', 'N/A')),
        ("Description", parsed_data.get('description', 'N/A')),
        ("Language", parsed_data.get('language', 'N/A')),
        ("Total Resources", parsed_data.get('total_items', 0)),
        ("Learning Categories", len(parsed_data.get('categories', []))),
    ]
    
    for label, value in info_items:
        print(f"{label:<20}: {value}")
    
    # Show categories if they exist
    categories = parsed_data.get('categories', [])
    if categories:
        print(f"\n📂 LEARNING CATEGORIES ({len(categories)}):")
        for i, category in enumerate(categories[:8], 1):  # Show first 8
            print(f"  {i:2d}. {category}")
        if len(categories) > 8:
            print(f"  ... and {len(categories) - 8} more categories")
    
    # Display learning guidance
    if learning_guidance:
        print(f"\n🎓 INSTRUCTIONAL GUIDANCE:")
        print("-" * 25)
        
        # Topic summary
        topic_summary = learning_guidance.get('topic_summary', '')
        if topic_summary:
            print(f"📝 {topic_summary}")
        
        # Recommended starting point
        starting_point = learning_guidance.get('recommended_starting_point', '')
        if starting_point:
            print(f"\n🚀 RECOMMENDED STARTING POINT:")
            print(f"   {starting_point}")
        
        # Learning paths
        learning_paths = learning_guidance.get('learning_paths', [])
        if learning_paths:
            print(f"\n🛤️  LEARNING PATHS ({len(learning_paths)}):")
            print("-" * 25)
            
            for i, path in enumerate(learning_paths[:5], 1):  # Show first 5 paths
                print(f"\n  Path {i}: {path.get('name', 'N/A')}")
                print(f"    Difficulty: {path.get('difficulty', 'N/A')}")
                print(f"    Estimated Time: {path.get('estimated_hours', 0)} hours")
                print(f"    Resources: {path.get('resources_count', 0)} items")
                
                # Show prerequisites if any
                prerequisites = path.get('prerequisites', [])
                if prerequisites:
                    print(f"    Prerequisites: {', '.join(prerequisites)}")
                
                # Show learning objectives
                objectives = path.get('learning_objectives', [])
                if objectives:
                    print(f"    Learning Objectives:")
                    for obj in objectives[:2]:  # Show first 2 objectives
                        print(f"      • {obj}")
        
        # Instructional guidance details
        instructional = learning_guidance.get('instructional_guidance', {})
        if instructional:
            print(f"\n📚 LEARNING APPROACH:")
            print("-" * 25)
            
            # Overview
            overview = instructional.get('overview', '')
            if overview:
                print(f"📖 {overview}")
            
            # Recommended approach
            approach = instructional.get('recommended_approach', '')
            if approach:
                print(f"\n💡 RECOMMENDED APPROACH:")
                print(f"   {approach}")
            
            # Skill levels
            skill_levels = instructional.get('skill_levels', {})
            if skill_levels:
                print(f"\n🎯 SKILL LEVEL RECOMMENDATIONS:")
                for level, resources in skill_levels.items():
                    if resources:
                        print(f"   {level.title()}: {', '.join(resources[:3])}")
                        if len(resources) > 3:
                            print(f"      ... and {len(resources) - 3} more")
            
            # Learning tips
            tips = instructional.get('learning_tips', [])
            if tips:
                print(f"\n💪 LEARNING TIPS:")
                for tip in tips[:4]:  # Show first 4 tips
                    print(f"   • {tip}")
            
            # Time commitment
            time_commitment = instructional.get('time_commitment', {})
            if time_commitment:
                print(f"\n⏰ TIME COMMITMENT:")
                print(f"   Total Hours: {time_commitment.get('total_hours', 0)} hours")
                print(f"   Weekly Commitment: {time_commitment.get('weekly_hours', 0)} hours/week")
                print(f"   Estimated Duration: {time_commitment.get('estimated_weeks', 0)} weeks")
                print(f"   Intensive Pace: {time_commitment.get('intensive_weeks', 0)} weeks")
    
    # Show context summary
    context_summary = parsed_data.get('context_summary', '')
    if context_summary:
        print(f"\n📋 CONTEXT SUMMARY:")
        print(f"{context_summary}")
    
    # Show processing metadata
    metadata = result.get('processing_metadata', {})
    if metadata:
        print(f"\n🔧 PROCESSING INFO:")
        print(f"   Agent Version: {metadata.get('agent_version', 'N/A')}")
        print(f"   Processing Time: {metadata.get('total_duration_seconds', 0):.2f} seconds")
        print(f"   Timestamp: {metadata.get('timestamp', 'N/A')}")
    
    print(f"\n🎉 Your personalized learning path is ready! Start with the recommended path and track your progress.")
    print(f"💡 Tip: Focus on hands-on practice and build projects to reinforce your learning.")

def save_results_to_file(result: dict, output_file: str, logger):
    """Save results to a JSON file."""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add metadata to results
        enhanced_result = {
            "timestamp": datetime.now().isoformat(),
            "url": result.get('url'),
            "processing_result": result
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_path}")
        print(f"\n💾 Results saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Failed to save results to file: {e}")
        print(f"\n⚠️  Failed to save results to file: {e}")

if __name__ == "__main__":
    asyncio.run(main())

