#!/usr/bin/env python3
"""
Example usage of the Awesome List Agent CLI

This script demonstrates various ways to use the awesome_list_interface.py
with different Awesome List URLs and configuration options.
"""

import asyncio
import subprocess
import sys
from pathlib import Path

# Example Awesome List URLs to test with
EXAMPLE_URLS = [
    "https://github.com/sindresorhus/awesome",
    "https://github.com/vinta/awesome-python", 
    "https://github.com/sorrycc/awesome-javascript",
    "https://github.com/avelino/awesome-go",
    "https://github.com/rust-unofficial/awesome-rust",
    "https://github.com/akullpp/awesome-java",
    "https://github.com/markets/awesome-ruby",
]

def run_example(url: str, **kwargs):
    """Run the awesome list interface with a given URL and options."""
    cmd = ["python3", "awesome_list_interface.py"]
    
    # Add optional arguments
    if kwargs.get("log_level"):
        cmd.extend(["--log-level", kwargs["log_level"]])
    
    if kwargs.get("output_file"):
        cmd.extend(["--output-file", kwargs["output_file"]])
    
    if kwargs.get("log_file"):
        cmd.extend(["--log-file", kwargs["log_file"]])
    
    if kwargs.get("quiet"):
        cmd.append("--quiet")
    
    # Add the URL
    cmd.append(url)
    
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Command timed out after 60 seconds")
    except Exception as e:
        print(f"Error running command: {e}")
    
    print("-" * 80)

def main():
    """Run example demonstrations."""
    print("Awesome List Agent CLI - Examples")
    print("=" * 50)
    
    # Example 1: Basic usage
    print("\\n1. Basic Usage Example:")
    print("Processing the main Awesome list...")
    run_example(EXAMPLE_URLS[0])
    
    # Example 2: With DEBUG logging
    print("\\n2. Debug Logging Example:")
    print("Processing awesome-python with debug logs...")
    run_example(
        EXAMPLE_URLS[1], 
        log_level="DEBUG",
        output_file="results/awesome-python-debug.json"
    )
    
    # Example 3: Quiet mode with output file
    print("\\n3. Quiet Mode Example:")
    print("Processing awesome-javascript quietly...")
    run_example(
        EXAMPLE_URLS[2],
        quiet=True,
        output_file="results/awesome-javascript-quiet.json",
        log_file="logs/quiet-run.log"
    )
    
    print("\\nExamples completed!")
    print("\\nUsage patterns:")
    print("• Basic: python3 awesome_list_interface.py <url>")
    print("• Debug: python3 awesome_list_interface.py --log-level DEBUG <url>")
    print("• Save results: python3 awesome_list_interface.py --output-file results.json <url>")
    print("• Quiet mode: python3 awesome_list_interface.py --quiet --log-file app.log <url>")
    print("• Custom log file: python3 awesome_list_interface.py --log-file custom.log <url>")
    
    print("\\nTry these URLs:")
    for i, url in enumerate(EXAMPLE_URLS, 1):
        print(f"  {i}. {url}")

if __name__ == "__main__":
    # Create results directory
    Path("results").mkdir(exist_ok=True)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--run-examples":
        main()
    else:
        print("Awesome List Agent CLI - Usage Examples")
        print("=" * 50)
        print("\\nTo run all examples: python3 awesome_list_examples.py --run-examples")
        print("\\nOr use the CLI directly:")
        print("python3 awesome_list_interface.py <awesome_list_url>")
        print("\\nExample URLs to try:")
        for i, url in enumerate(EXAMPLE_URLS, 1):
            print(f"  {i}. {url}")
        print("\\nFor help: python3 awesome_list_interface.py --help")
