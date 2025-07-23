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
        self.logger = logging.getLogger("awesome_list_agent.AwesomeListAgent")
        
        # Register all tools
        self.logger.info("Initializing AwesomeListAgent")
        
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
        self.logger.info(f"Starting to process Awesome List URL: {url}")
        
        try:
            # Parse the awesome list using our tool
            self.logger.info("Executing awesome list parser")
            parsed_data = await self.parser.execute(url)
            
            self.logger.debug(f"Parser returned data: {parsed_data}")
            
            # Check if parsing was successful
            if isinstance(parsed_data, dict) and "error" in parsed_data:
                self.logger.error(f"Parser failed with error: {parsed_data['error']}")
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
            
            # TODO: Implement MCP server call
            # Simulate MCP server call (you can replace this with actual MCP logic)
            self.logger.info("Calling MCP server")
            mcp_result = await self.call_mcp_server(url, parsed_data.get("context_summary", ""))
            self.logger.debug(f"MCP server result: {mcp_result}")
            
            # Combine parsed data with MCP result
            result = {
                "status": "success",
                "url": url,
                "parsed_data": parsed_data,
                "mcp_result": mcp_result
            }
            
            self.logger.info("Successfully completed processing Awesome List")
            return result
            
        except Exception as e:
            self.logger.error(f"Exception occurred while processing URL {url}: {str(e)}", exc_info=True)
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
        self.logger.info(f"Calling MCP server with URL: {url}")
        self.logger.debug(f"Context summary length: {len(context_summary)} characters")
        
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
        
        self.logger.info("MCP server call completed successfully")
        self.logger.debug(f"MCP server response: {result}")
        
        return result
    
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

