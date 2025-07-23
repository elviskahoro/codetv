from .agent import Agent
from .tools.awesome_list_parser import AwesomeListParser
from .tools.youtube_metadata_tool import YouTubeMetadataTool
from .tools.web_scraping_tool import WebScrapingTool
from .tools.content_analysis_tool import ContentAnalysisTool
from typing import Any, Dict, List, Optional
import uuid
import logging
from datetime import datetime

class AwesomeListAgent(Agent):
    """Agent specialized for processing Awesome Lists and calling MCP servers"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up logger - use the injected logger or create a default one
        if self.logger:
            self.logger = self.logger
        else:
            self.logger = logging.getLogger("awesome_list_agent.AwesomeListAgent")
        
        # Log agent initialization
        self.logger.info("Initializing AwesomeListAgent")
        
        # Register all tools
        self._register_tools()
        
        # Set up Galileo hooks if logger supports it
        if hasattr(self.logger, '_setup_logger'):
            self.logger._setup_logger(self.logger)
    
    def _register_tools(self):
        """Register all available tools with the agent."""
        # Register the awesome list parser tool
        self.parser = AwesomeListParser()
        self.tool_registry.register(
            metadata=AwesomeListParser.get_metadata(),
            implementation=AwesomeListParser
        )
        self.logger.debug("Registered awesome_list_parser tool")
        
        # Register YouTube metadata tool
        self.youtube_tool = YouTubeMetadataTool()
        self.tool_registry.register(
            metadata=YouTubeMetadataTool.get_metadata(),
            implementation=YouTubeMetadataTool
        )
        self.logger.debug("Registered youtube_metadata_tool")
        
        # Register web scraping tool
        self.web_scraping_tool = WebScrapingTool()
        self.tool_registry.register(
            metadata=WebScrapingTool.get_metadata(),
            implementation=WebScrapingTool
        )
        self.logger.debug("Registered web_scraping_tool")
        
        # Register content analysis tool
        self.content_analysis_tool = ContentAnalysisTool()
        self.tool_registry.register(
            metadata=ContentAnalysisTool.get_metadata(),
            implementation=ContentAnalysisTool
        )
        self.logger.debug("Registered content_analysis_tool")

    async def process_awesome_list(self, url: str) -> Dict[str, Any]:
        """Process an Awesome List URL to extract key information and call MCP server.

        Args:
            url: The URL of the Awesome List to process.

        Returns:
            A dictionary containing the parsed information and MCP server result.
        """
        import time
        start_time = time.time()
        
        # Start Galileo trace if logger supports it
        if hasattr(self.logger, 'start_trace'):
            self.logger.start_trace(f"process_awesome_list_{url.split('/')[-1]}")
        
        self.logger.info(f"Starting to process Awesome List URL: {url}")
        
        try:
            # Step 1: Parse the awesome list using our tool
            self.logger.info("Executing awesome list parser")
            
            # Add tool span for parser execution
            if hasattr(self.logger, 'add_tool_span'):
                tool_start_time = time.time()
            
            parsed_data = await self.parser.execute(url)
            
            # Log tool execution span
            if hasattr(self.logger, 'add_tool_span'):
                tool_duration = (time.time() - tool_start_time) * 1_000_000_000  # Convert to nanoseconds
                self.logger.add_tool_span(
                    tool_name="awesome_list_parser",
                    inputs={"url": url},
                    outputs=parsed_data,
                    duration_ns=int(tool_duration),
                    success="error" not in parsed_data if isinstance(parsed_data, dict) else True
                )
            
            self.logger.debug(f"Parser returned data: {parsed_data}")
            
            # Check if parsing was successful
            if isinstance(parsed_data, dict) and "error" in parsed_data:
                self.logger.error(f"Parser failed with error: {parsed_data['error']}")
                
                # Conclude trace with error
                if hasattr(self.logger, 'conclude_trace'):
                    total_duration = (time.time() - start_time) * 1_000_000_000
                    self.logger.conclude_trace(
                        output=f"Error: {parsed_data['error']}", 
                        duration_ns=int(total_duration)
                    )
                
                return {
                    "status": "error",
                    "error": parsed_data["error"],
                    "url": url
                }
            
            # Log successful parsing
            if isinstance(parsed_data, dict):
                self.logger.info(f"Successfully parsed list - Topic: {parsed_data.get('topic', 'N/A')}")
                self.logger.info(f"Found {parsed_data.get('total_items', 0)} items")
                self.logger.info(f"Detected {len(parsed_data.get('categories', []))} categories")
            
            # Step 2: Call MCP server
            self.logger.info("Calling MCP server")
            
            # Add tool span for MCP server call
            if hasattr(self.logger, 'add_tool_span'):
                mcp_start_time = time.time()
            
            mcp_result = await self.call_mcp_server(url, parsed_data.get("context_summary", ""))
            
            # Log MCP server call span
            if hasattr(self.logger, 'add_tool_span'):
                mcp_duration = (time.time() - mcp_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="mcp_server_call",
                    inputs={"url": url, "context_summary": parsed_data.get("context_summary", "")},
                    outputs=mcp_result,
                    duration_ns=int(mcp_duration),
                    success=mcp_result.get("mcp_status") == "success"
                )
            
            self.logger.debug(f"MCP server result: {mcp_result}")
            
            # Combine parsed data with MCP result
            result = {
                "status": "success",
                "url": url,
                "parsed_data": parsed_data,
                "mcp_result": mcp_result
            }
            
            self.logger.info("Successfully completed processing Awesome List")
            
            # Conclude trace with success
            if hasattr(self.logger, 'conclude_trace'):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Successfully processed {parsed_data.get('total_items', 0)} items from {url}",
                    duration_ns=int(total_duration)
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Exception occurred while processing URL {url}: {str(e)}", exc_info=True)
            
            # Conclude trace with error
            if hasattr(self.logger, 'conclude_trace'):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Exception: {str(e)}", 
                    duration_ns=int(total_duration)
                )
            
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }

    async def call_mcp_server(self, url: str, context_summary: str) -> Dict[str, Any]:
        """Call the MCP server with the URL and context information.

        Args:
            url: The URL to send to the MCP server.
            context_summary: The extracted summary of the Awesome List.

        Returns:
            Result from the MCP server call.
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Calling MCP server with URL: {url}")
        self.logger.debug(f"Context summary length: {len(context_summary)} characters")
        
        # Add detailed Galileo logging for MCP server call
        if hasattr(self.logger, 'info'):
            self.logger.info(f"[Galileo] MCP Server Call - URL: {url}")
            self.logger.info(f"[Galileo] MCP Server Call - Context Summary Length: {len(context_summary)} chars")
        
        try:
            # This is a placeholder for actual MCP server integration
            # You would implement your actual MCP server calling logic here
            
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.1)  # Simulate network call
            
            result = {
                "mcp_status": "success",
                "message": f"MCP server processed URL: {url}",
                "context_received": context_summary,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log success with Galileo
            if hasattr(self.logger, 'info'):
                duration_ms = (time.time() - start_time) * 1000
                self.logger.info(f"[Galileo] MCP Server Call - Success - Duration: {duration_ms:.2f}ms")
            
            self.logger.info("MCP server call completed successfully")
            self.logger.debug(f"MCP server response: {result}")
            
            return result
            
        except Exception as e:
            # Log error with Galileo
            if hasattr(self.logger, 'error'):
                duration_ms = (time.time() - start_time) * 1000
                self.logger.error(f"[Galileo] MCP Server Call - Error - Duration: {duration_ms:.2f}ms - Error: {str(e)}")
            
            # Return error result
            return {
                "mcp_status": "error",
                "message": f"MCP server call failed: {str(e)}",
                "context_received": context_summary,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def _format_result(self, task: str, results: List[tuple[str, Dict[str, Any]]]) -> str:
        """Format the final result from tool executions.
        
        Args:
            task: The original task string
            results: List of (tool_name, result) tuples
            
        Returns:
            Formatted result string
        """
        if not results:
            return "No results from tool execution"
        
        formatted_parts = []
        for tool_name, result in results:
            if isinstance(result, dict) and "error" not in result:
                formatted_parts.append(f"Tool '{tool_name}' completed successfully")
                if "context_summary" in result:
                    formatted_parts.append(f"Summary: {result['context_summary']}")
            else:
                formatted_parts.append(f"Tool '{tool_name}' encountered an error")
        
        return "\n".join(formatted_parts)

