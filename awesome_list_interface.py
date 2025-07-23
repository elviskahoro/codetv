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
    """Display results in a user-friendly format."""
    print(f"\n✅ Processing completed in {processing_time:.2f} seconds\n")
    
    if result.get('status') == 'error':
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        return
    
    parsed_data = result.get('parsed_data', {})
    mcp_result = result.get('mcp_result', {})
    
    print("📊 PARSED INFORMATION:")
    print("-" * 30)
    
    info_items = [
        ("Topic", parsed_data.get('topic', 'N/A')),
        ("Description", parsed_data.get('description', 'N/A')),
        ("Language", parsed_data.get('language', 'N/A')),
        ("Total Items", parsed_data.get('total_items', 0)),
        ("Categories", len(parsed_data.get('categories', []))),
    ]
    
    for label, value in info_items:
        print(f"{label:<15}: {value}")
    
    # Show categories if they exist
    categories = parsed_data.get('categories', [])
    if categories:
        print(f"\n📂 CATEGORIES ({len(categories)}):")
        for i, category in enumerate(categories[:5], 1):  # Show first 5
            print(f"  {i}. {category}")
        if len(categories) > 5:
            print(f"  ... and {len(categories) - 5} more")
    
    # Show context summary
    context_summary = parsed_data.get('context_summary', '')
    if context_summary:
        print(f"\n📝 SUMMARY:")
        print(f"{context_summary}")
    
    # Show MCP result
    print(f"\n🔗 MCP SERVER RESULT:")
    print("-" * 30)
    print(f"Status: {mcp_result.get('mcp_status', 'N/A')}")
    print(f"Message: {mcp_result.get('message', 'N/A')}")
    print(f"Timestamp: {mcp_result.get('timestamp', 'N/A')}")

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

