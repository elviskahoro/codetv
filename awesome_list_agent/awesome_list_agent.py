from .agent import Agent
from .tools.awesome_list_parser import AwesomeListParser
from .tools.youtube_metadata_tool import YouTubeMetadataTool
from .tools.web_scraping_tool import WebScrapingTool
from .tools.content_analysis_tool import ContentAnalysisTool
from .tools.markdown_youtube_extractor_tool import MarkdownYouTubeExtractorTool
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

        # Register markdown YouTube extractor tool
        self.markdown_youtube_extractor_tool = MarkdownYouTubeExtractorTool()
        self.tool_registry.register(
            metadata=MarkdownYouTubeExtractorTool.metadata,
            implementation=MarkdownYouTubeExtractorTool
        )
        self.logger.debug("Registered markdown_youtube_extractor_tool")

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

                youtube_count = len(parsed_data.get('youtube_metadata', []))
                self.logger.info(f"🎥 Extracted {youtube_count} YouTube videos")
                if youtube_count > 0:
                    youtube_titles = [video.get('title', 'Unknown') for video in parsed_data.get('youtube_metadata', [])[:3]]
                    self.logger.info(f"📹 Sample YouTube videos: {', '.join(youtube_titles)}")

            # Combine all results into final result
            youtube_count = len(parsed_data.get("youtube_metadata", []))
            result = {
                "status": "success",
                "url": url,
                "parsed_data": parsed_data,
                "youtube_summary": {
                    "video_count": youtube_count,
                    "videos": parsed_data.get("youtube_metadata", [])[:5],  # Include first 5 videos
                    "total_views": sum(video.get("view_count", 0) for video in parsed_data.get("youtube_metadata", [])),
                    "avg_duration_minutes": sum(video.get("duration_seconds", 0) for video in parsed_data.get("youtube_metadata", [])) / max(youtube_count, 1) / 60
                },
                "metadata": {
                    "total_items": parsed_data.get("total_items", 0),
                    "categories_count": len(parsed_data.get("categories", [])),
                    "youtube_videos_count": youtube_count,
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

            # Clean up resources
            await self._cleanup_resources()

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

            # Clean up resources even on error
            await self._cleanup_resources()

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

    async def _cleanup_resources(self):
        """Clean up resources used by the agent."""
        try:
            # Clean up parser resources
            if hasattr(self, 'parser') and hasattr(self.parser, 'cleanup'):
                await self.parser.cleanup()

            # Clean up other tool resources
            for tool_name in ['youtube_tool', 'web_scraping_tool', 'content_analysis_tool', 'markdown_youtube_extractor_tool']:
                if hasattr(self, tool_name) and hasattr(getattr(self, tool_name), 'cleanup'):
                    await getattr(self, tool_name).cleanup()

        except Exception as e:
            self.logger.warning(f"Error during cleanup: {str(e)}")
