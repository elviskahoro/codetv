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
    """Agent specialized for processing Awesome Lists with comprehensive tool integration"""
    
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
        """Process an Awesome List URL to extract comprehensive information.

        Args:
            url: The URL of the Awesome List to process.

        Returns:
            A dictionary containing the parsed information and metadata.
        """
        import time
        start_time = time.time()
        
        # Start Galileo trace if logger supports it
        if hasattr(self.logger, 'start_trace'):
            self.logger.start_trace(f"process_awesome_list_{url.split('/')[-1]}")
        
        self.logger.info(f"Starting to process Awesome List URL: {url}")
        
        try:
            # Step 1: Parse the awesome list using our comprehensive parser
            self.logger.info("Executing comprehensive awesome list parser")
            
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
            
            self.logger.debug(f"Parser returned comprehensive data: {parsed_data}")
            
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
                self.logger.info(f"Extracted {len(parsed_data.get('youtube_metadata', []))} YouTube videos")
            
            # Combine all results into final result
            result = {
                "status": "success",
                "url": url,
                "parsed_data": parsed_data,
                "metadata": {
                    "total_items": parsed_data.get("total_items", 0),
                    "categories_count": len(parsed_data.get("categories", [])),
                    "youtube_videos_count": len(parsed_data.get("youtube_metadata", [])),
                    "processing_time": f"{(time.time() - start_time):.2f} seconds",
                    "trace_id": f"trace_{int(start_time)}" if hasattr(self.logger, 'start_trace') else "Not available"
                }
            }
            
            # Conclude trace with success
            if hasattr(self.logger, 'conclude_trace'):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Successfully processed {url}",
                    duration_ns=int(total_duration)
                )
            
            self.logger.info(f"Successfully completed processing of Awesome List: {url}")
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error processing Awesome List: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            # Conclude trace with error
            if hasattr(self.logger, 'conclude_trace'):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Error: {error_msg}",
                    duration_ns=int(total_duration)
                )
            
            return {
                "status": "error",
                "error": error_msg,
                "url": url
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
                if "comprehensive_summary" in result:
                    formatted_parts.append(f"Summary: {result['comprehensive_summary']}")
            else:
                formatted_parts.append(f"Tool '{tool_name}' encountered an error")
        
        return "\n".join(formatted_parts)

