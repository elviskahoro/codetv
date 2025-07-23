from .agent import Agent
from .tools.awesome_list_parser import AwesomeListParser
from .tools.youtube_metadata_tool import YouTubeMetadataTool
from .tools.web_scraping_tool import WebScrapingTool
from .tools.content_analysis_tool import ContentAnalysisTool
from .llm.models import LLMMessage
from .tools.markdown_youtube_extractor_tool import MarkdownYouTubeExtractorTool
from typing import Any, Dict, List, Optional
import uuid
import logging
from datetime import datetime


class AwesomeListAgent(Agent):
    """Agent specialized for processing Awesome Lists with comprehensive tool integration"""

    # Comprehensive system prompt describing the agent's purpose and capabilities
    SYSTEM_PROMPT = """You are the AwesomeListAgent, a specialized AI agent designed to process and analyze "Awesome Lists" - curated collections of resources, tools, libraries, and learning materials typically found on GitHub and other platforms.

## Your Core Mission
Your primary purpose is to extract, analyze, and provide comprehensive insights from Awesome Lists, which are community-curated collections that serve as valuable learning resources and tool directories.

## What You Do
1. **Parse Awesome Lists**: Extract structured data from markdown-based Awesome Lists including categories, items, descriptions, and links
2. **Web Scraping Analysis**: Perform comprehensive content analysis of the Awesome List pages to understand context and structure
3. **YouTube Integration**: Automatically detect and extract metadata from YouTube videos referenced in the lists
4. **Content Analysis**: Provide insights about the quality, relevance, and organization of the content
5. **Metadata Extraction**: Gather comprehensive metadata about the list, its items, and external resources

## Your Specialized Tools
- **Awesome List Parser**: Extracts structured data from markdown Awesome Lists
- **Web Scraping Tool**: Analyzes web content, extracts text, links, and metadata
- **YouTube Metadata Tool**: Fetches detailed information about YouTube videos (title, views, duration, etc.)
- **Content Analysis Tool**: Provides insights and analysis of the content quality and relevance

## Your Output Format
You provide comprehensive results including:
- Parsed structured data from the Awesome List
- Web scraping analysis with text content and link extraction
- Enhanced YouTube video metadata with engagement metrics
- Content analysis and insights
- Processing metadata and performance metrics

## Your Approach
- Be thorough and comprehensive in your analysis
- Focus on extracting maximum value from the Awesome List content
- Provide both raw data and meaningful insights
- Handle errors gracefully and provide detailed error information
- Log all operations for observability and debugging

## When to Use Each Tool
- Use the Awesome List Parser for initial structured extraction
- Use Web Scraping for comprehensive content analysis
- Use the Markdown YouTube Extractor tool for extracting youtube links and metadata
- Use Content Analysis Tool for quality assessment and insights

You are designed to be the ultimate tool for processing and understanding Awesome Lists, making them more accessible and valuable for users seeking curated learning resources."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up logger - use the injected logger or create a default one
        if self.logger:
            self.logger = self.logger
        else:
            self.logger = logging.getLogger("awesome_list_agent.AwesomeListAgent")

        # Log agent initialization with system prompt context
        self.logger.info(
            "Initializing AwesomeListAgent with specialized Awesome List processing capabilities"
        )
        self.logger.info(f"Agent ID: {self.agent_id}")
        self.logger.info(
            "System Purpose: Process and analyze Awesome Lists with comprehensive tool integration"
        )

        # Log agent initialization
        self.logger.info("Initializing AwesomeListAgent")

        # Register all tools
        self._register_tools()

        # Set up Galileo hooks if logger supports it
        if hasattr(self.logger, "_setup_logger"):
            self.logger._setup_logger(self.logger)

    def get_system_prompt(self) -> str:
        """Return the specialized system prompt for this agent."""
        return self.SYSTEM_PROMPT

    @classmethod
    def get_agent_description(cls) -> str:
        """Return a user-friendly description of what this agent does."""
        return """The AwesomeListAgent is a specialized AI agent designed to process and analyze "Awesome Lists" -
curated collections of resources, tools, libraries, and learning materials typically found on GitHub and other platforms.

Key Capabilities:
• Parse structured data from markdown-based Awesome Lists
• Extract categories, items, descriptions, and links
• Perform comprehensive web scraping analysis
• Automatically detect and extract YouTube video metadata
• Provide content analysis and quality insights
• Generate comprehensive reports with processing metrics

This agent is perfect for:
- Researching and analyzing curated resource lists
- Extracting structured data from community-curated collections
- Understanding the scope and quality of learning resources
- Building datasets from Awesome Lists
- Creating summaries and insights from curated content"""

    def get_agent_info(self) -> Dict[str, Any]:
        """Return comprehensive information about this agent instance."""
        return {
            "agent_type": "AwesomeListAgent",
            "agent_id": self.agent_id,
            "description": self.get_agent_description(),
            "capabilities": [
                "Awesome List parsing and structured data extraction",
                "Web scraping and content analysis",
                "YouTube metadata extraction and analysis",
                "Content quality assessment and insights",
                "Comprehensive reporting and metrics",
            ],
            "registered_tools": [
                tool.name for tool in self.tool_registry.get_all_tools().values()
            ],
            "system_prompt_length": len(self.SYSTEM_PROMPT),
            "verbosity_level": self.config.verbosity.value,
            "has_llm_provider": self.llm_provider is not None,
            "has_logger": self.logger is not None,
        }

    def _create_planning_prompt(self, task: str) -> List[LLMMessage]:
        """Create a specialized planning prompt for Awesome List processing tasks.

        This overrides the base agent's planning prompt to include our specialized
        system prompt that describes the agent's purpose and capabilities.
        """
        # Get the base tools description
        tools_description = "\n".join(
            [
                f"Tool: {tool.name}\n"
                f"Description: {tool.description}\n"
                f"Tags: {', '.join(tool.tags)}\n"
                f"Input Schema: {tool.input_schema}\n"
                f"Output Schema: {tool.output_schema}\n"
                for tool in self.tool_registry.get_all_tools().values()
            ]
        )

        # Create specialized system prompt for Awesome List processing
        system_prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            "## Task Planning Instructions\n"
            "You are an intelligent task planning system specialized for Awesome List processing. "
            "Your role is to analyze Awesome List processing tasks and create detailed execution plans.\n\n"
            "You MUST provide a complete response with ALL of the following components:\n\n"
            "1. input_analysis: A thorough analysis of the Awesome List processing requirements and constraints\n"
            "2. available_tools: List of all Awesome List processing tools that could potentially be used\n"
            "3. tool_capabilities: A mapping of each available tool to its key capabilities for Awesome List processing\n"
            "4. execution_plan: A list of steps, where each step has:\n"
            "   - tool: The name of the tool to use\n"
            "   - reasoning: Why this tool was chosen for this Awesome List processing step\n"
            "5. requirements_coverage: How each Awesome List processing requirement is covered by which tools\n"
            "6. chain_of_thought: Your step-by-step reasoning process for Awesome List analysis\n\n"
            f"Available Tools:\n{tools_description}\n\n"
            "Your response MUST be a JSON object with this EXACT structure:\n"
            "{\n"
            '  "input_analysis": "detailed analysis of the Awesome List processing task",\n'
            '  "available_tools": ["tool1", "tool2"],\n'
            '  "tool_capabilities": {\n'
            '    "tool1": ["capability1", "capability2"],\n'
            '    "tool2": ["capability3"]\n'
            "  },\n"
            '  "execution_plan": [\n'
            '    {"tool": "tool1", "reasoning": "why tool1 is used for Awesome List processing"},\n'
            '    {"tool": "tool2", "reasoning": "why tool2 is used for Awesome List processing"}\n'
            "  ],\n"
            '  "requirements_coverage": {\n'
            '    "requirement1": ["tool1"],\n'
            '    "requirement2": ["tool1", "tool2"]\n'
            "  },\n"
            '  "chain_of_thought": [\n'
            '    "step 1 reasoning for Awesome List analysis",\n'
            '    "step 2 reasoning for Awesome List analysis"\n'
            "  ]\n"
            "}\n\n"
            "Ensure ALL fields are present and properly formatted. Missing fields will cause errors."
        )

        return [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(
                role="user",
                content=f"Awesome List Processing Task: {task}\n\nAnalyze this Awesome List processing task and create a complete execution plan with ALL required fields.",
            ),
        ]

    def _register_tools(self):
        """Register all available tools with the agent."""
        # Register the awesome list parser tool
        self.parser = AwesomeListParser()
        self.tool_registry.register(
            metadata=AwesomeListParser.get_metadata(), implementation=AwesomeListParser
        )
        self.logger.debug("Registered awesome_list_parser tool")

        # Register YouTube metadata tool
        self.youtube_tool = YouTubeMetadataTool()
        self.tool_registry.register(
            metadata=YouTubeMetadataTool.get_metadata(),
            implementation=YouTubeMetadataTool,
        )
        self.logger.debug("Registered youtube_metadata_tool")

        # Register web scraping tool
        self.web_scraping_tool = WebScrapingTool()
        self.tool_registry.register(
            metadata=WebScrapingTool.get_metadata(), implementation=WebScrapingTool
        )
        self.logger.debug("Registered web_scraping_tool")

        # Register content analysis tool
        self.content_analysis_tool = ContentAnalysisTool()
        self.tool_registry.register(
            metadata=ContentAnalysisTool.get_metadata(),
            implementation=ContentAnalysisTool,
        )
        self.logger.debug("Registered content_analysis_tool")

        # Register markdown YouTube extractor tool
        self.markdown_youtube_extractor_tool = MarkdownYouTubeExtractorTool()
        self.tool_registry.register(
            metadata=MarkdownYouTubeExtractorTool.get_metadata(),
            implementation=MarkdownYouTubeExtractorTool,
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
        if hasattr(self.logger, "start_trace"):
            self.logger.start_trace(f"process_awesome_list_{url.split('/')[-1]}")

        # Log agent purpose and system prompt context
        self.logger.info("🎯 AwesomeListAgent Starting Processing")
        self.logger.info(
            "📋 Agent Purpose: Process and analyze Awesome Lists with comprehensive tool integration"
        )
        self.logger.info(f"🔗 Processing URL: {url}")
        self.logger.info(f"🆔 Agent ID: {self.agent_id}")
        self.logger.info(
            f"📊 System Prompt Length: {len(self.SYSTEM_PROMPT)} characters"
        )

        self.logger.info(f"Starting to process Awesome List URL: {url}")

        try:
            # Step 1: Explicitly call web scraping tool for comprehensive content analysis
            self.logger.info("Step 1: Executing explicit web scraping analysis")

            # Add tool span for explicit web scraping execution
            if hasattr(self.logger, "add_tool_span"):
                web_scraping_start_time = time.time()

            # Explicitly call web scraping tool from the main agent
            web_scraping_result = await self.web_scraping_tool.execute(
                url=url,
                extract_text=True,
                extract_links=True,
                extract_images=False,
                extract_metadata=True,
                max_links=100,  # Get comprehensive link analysis
                timeout=30,
            )

            # Log explicit web scraping tool execution span
            if hasattr(self.logger, "add_tool_span"):
                web_scraping_duration = (
                    time.time() - web_scraping_start_time
                ) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="explicit_web_scraping_tool",
                    inputs={
                        "url": url,
                        "extract_text": True,
                        "extract_links": True,
                        "max_links": 100,
                    },
                    outputs=web_scraping_result,
                    duration_ns=int(web_scraping_duration),
                    success=(
                        "error" not in web_scraping_result
                        if isinstance(web_scraping_result, dict)
                        else True
                    ),
                )

            # Log web scraping results
            if (
                isinstance(web_scraping_result, dict)
                and "error" not in web_scraping_result
            ):
                self.logger.info(f"✅ Explicit web scraping completed successfully")
                self.logger.info(
                    f"📄 Found {len(web_scraping_result.get('text_content', ''))} characters of text"
                )
                self.logger.info(
                    f"🔗 Extracted {len(web_scraping_result.get('links', []))} links"
                )
                self.logger.info(
                    f"📊 Found {len(web_scraping_result.get('metadata', {}))} metadata fields"
                )
            else:
                self.logger.warning(
                    f"⚠️ Explicit web scraping encountered issues: {web_scraping_result.get('error', 'Unknown error')}"
                )

            # Step 2: Parse the awesome list using our comprehensive parser
            self.logger.info("Step 2: Executing comprehensive awesome list parser")

            # Add tool span for parser execution
            if hasattr(self.logger, "add_tool_span"):
                parser_start_time = time.time()

            # Step 1: Parse the awesome list using our comprehensive parser
            self.logger.info("Executing comprehensive awesome list parser")

            # Add tool span for parser execution
            if hasattr(self.logger, "add_tool_span"):
                tool_start_time = time.time()

            parsed_data = await self.parser.execute(url)

            # Log tool execution span
            if hasattr(self.logger, "add_tool_span"):
                parser_duration = (
                    time.time() - parser_start_time
                ) * 1_000_000_000  # Convert to nanoseconds
                self.logger.add_tool_span(
                    tool_name="awesome_list_parser",
                    inputs={"url": url},
                    outputs=parsed_data,
                    duration_ns=int(parser_duration),
                    success=(
                        "error" not in parsed_data
                        if isinstance(parsed_data, dict)
                        else True
                    ),
                )

            self.logger.debug(f"Parser returned comprehensive data: {parsed_data}")

            # Check if parsing was successful
            if isinstance(parsed_data, dict) and "error" in parsed_data:
                self.logger.error(f"Parser failed with error: {parsed_data['error']}")

                # Conclude trace with error
                if hasattr(self.logger, "conclude_trace"):
                    total_duration = (time.time() - start_time) * 1_000_000_000
                    self.logger.conclude_trace(
                        output=f"Error: {parsed_data['error']}",
                        duration_ns=int(total_duration),
                    )

                return {"status": "error", "error": parsed_data["error"], "url": url}

            # Log successful parsing
            if isinstance(parsed_data, dict):
                self.logger.info(
                    f"Successfully parsed list - Topic: {parsed_data.get('topic', 'N/A')}"
                )
                self.logger.info(f"Found {parsed_data.get('total_items', 0)} items")
                self.logger.info(
                    f"Detected {len(parsed_data.get('categories', []))} categories"
                )

                youtube_count = len(parsed_data.get("youtube_metadata", []))
                self.logger.info(f"🎥 Extracted {youtube_count} YouTube videos")
                if youtube_count > 0:
                    youtube_titles = [
                        video.get("title", "Unknown")
                        for video in parsed_data.get("youtube_metadata", [])[:3]
                    ]
                    self.logger.info(
                        f"📹 Sample YouTube videos: {', '.join(youtube_titles)}"
                    )

            # Step 3: Explicitly call YouTube metadata tool for any YouTube links found
            self.logger.info("Step 3: Executing explicit YouTube metadata extraction")

            # Extract YouTube URLs from web scraping results
            youtube_urls = []
            if isinstance(web_scraping_result, dict) and "links" in web_scraping_result:
                for link in web_scraping_result["links"]:
                    if isinstance(link, dict) and "url" in link:
                        url_str = link["url"]
                        if "youtube.com" in url_str or "youtu.be" in url_str:
                            youtube_urls.append(url_str)

            # Also check parsed data for YouTube URLs
            if isinstance(parsed_data, dict) and "youtube_metadata" in parsed_data:
                for video in parsed_data.get("youtube_metadata", []):
                    if isinstance(video, dict) and "url" in video:
                        youtube_urls.append(video["url"])

            # Remove duplicates
            youtube_urls = list(set(youtube_urls))

            self.logger.info(
                f"🔍 Found {len(youtube_urls)} unique YouTube URLs to process"
            )

            # Process each YouTube URL to get detailed metadata
            enhanced_youtube_metadata = []
            if youtube_urls:
                for youtube_url in youtube_urls[
                    :10
                ]:  # Limit to first 10 to avoid overwhelming
                    try:
                        self.logger.info(f"🎬 Processing YouTube URL: {youtube_url}")

                        # Add tool span for YouTube metadata execution
                        if hasattr(self.logger, "add_tool_span"):
                            youtube_start_time = time.time()

                        youtube_result = await self.youtube_tool.execute(youtube_url)

                        # Log tool execution span
                        if hasattr(self.logger, "add_tool_span"):
                            youtube_duration = (
                                time.time() - youtube_start_time
                            ) * 1_000_000_000
                            self.logger.add_tool_span(
                                tool_name="youtube_metadata_tool",
                                inputs={"url": youtube_url},
                                outputs=youtube_result,
                                duration_ns=int(youtube_duration),
                                success=(
                                    "error" not in youtube_result
                                    if isinstance(youtube_result, dict)
                                    else True
                                ),
                            )

                        if (
                            isinstance(youtube_result, dict)
                            and "error" not in youtube_result
                        ):
                            enhanced_youtube_metadata.append(youtube_result)
                            self.logger.info(
                                f"✅ Successfully processed YouTube video: {youtube_result.get('title', 'Unknown')}"
                            )
                        else:
                            self.logger.warning(
                                f"⚠️ Failed to process YouTube URL: {youtube_url}"
                            )

                    except Exception as e:
                        self.logger.error(
                            f"❌ Error processing YouTube URL {youtube_url}: {str(e)}"
                        )

            # Update the parsed data with enhanced YouTube metadata
            if enhanced_youtube_metadata:
                if isinstance(parsed_data, dict):
                    parsed_data["youtube_metadata"] = enhanced_youtube_metadata
                    self.logger.info(
                        f"🎬 Enhanced YouTube metadata with {len(enhanced_youtube_metadata)} videos"
                    )

            # Combine all results into final result
            youtube_count = len(parsed_data.get("youtube_metadata", []))
            result = {
                "status": "success",
                "url": url,
                "parsed_data": parsed_data,
                "explicit_web_scraping": {
                    "status": (
                        "success"
                        if isinstance(web_scraping_result, dict)
                        and "error" not in web_scraping_result
                        else "error"
                    ),
                    "data": web_scraping_result,
                    "summary": {
                        "text_length": (
                            len(web_scraping_result.get("text_content", ""))
                            if isinstance(web_scraping_result, dict)
                            else 0
                        ),
                        "links_count": (
                            len(web_scraping_result.get("links", []))
                            if isinstance(web_scraping_result, dict)
                            else 0
                        ),
                        "metadata_count": (
                            len(web_scraping_result.get("metadata", {}))
                            if isinstance(web_scraping_result, dict)
                            else 0
                        ),
                    },
                },
                "youtube_summary": {
                    "video_count": youtube_count,
                    "videos": parsed_data.get("youtube_metadata", [])[
                        :5
                    ],  # Include first 5 videos
                    "total_views": sum(
                        video.get("view_count", 0)
                        for video in parsed_data.get("youtube_metadata", [])
                    ),
                    "avg_duration_minutes": sum(
                        video.get("duration_seconds", 0)
                        for video in parsed_data.get("youtube_metadata", [])
                    )
                    / max(youtube_count, 1)
                    / 60,
                },
                "metadata": {
                    "total_items": parsed_data.get("total_items", 0),
                    "categories_count": len(parsed_data.get("categories", [])),
                    "youtube_videos_count": youtube_count,
                    "processing_time": f"{(time.time() - start_time):.2f} seconds",
                    "trace_id": (
                        f"trace_{int(start_time)}"
                        if hasattr(self.logger, "start_trace")
                        else "Not available"
                    ),
                },
            }

            # Conclude trace with success
            if hasattr(self.logger, "conclude_trace"):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Successfully processed {url}",
                    duration_ns=int(total_duration),
                )

            self.logger.info(
                f"Successfully completed processing of Awesome List: {url}"
            )

            # Clean up resources
            await self._cleanup_resources()

            return result

        except Exception as e:
            error_msg = f"Unexpected error processing Awesome List: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            # Conclude trace with error
            if hasattr(self.logger, "conclude_trace"):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Error: {error_msg}", duration_ns=int(total_duration)
                )

            # Clean up resources even on error
            await self._cleanup_resources()

            return {"status": "error", "error": error_msg, "url": url}

    async def _format_result(
        self, task: str, results: List[tuple[str, Dict[str, Any]]]
    ) -> str:
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
                    formatted_parts.append(
                        f"Summary: {result['comprehensive_summary']}"
                    )
            else:
                formatted_parts.append(f"Tool '{tool_name}' encountered an error")

        return "\n".join(formatted_parts)

    async def _cleanup_resources(self):
        """Clean up resources used by the agent."""
        try:
            # Clean up parser resources
            if hasattr(self, "parser") and hasattr(self.parser, "cleanup"):
                await self.parser.cleanup()

            # Clean up other tool resources
            for tool_name in [
                "youtube_tool",
                "web_scraping_tool",
                "content_analysis_tool",
                "markdown_youtube_extractor_tool",
            ]:
                if hasattr(self, tool_name) and hasattr(
                    getattr(self, tool_name), "cleanup"
                ):
                    await getattr(self, tool_name).cleanup()

        except Exception as e:
            self.logger.warning(f"Error during cleanup: {str(e)}")

    async def extract_youtube_from_markdown(self, url: str) -> Dict[str, Any]:
        """Extract YouTube URLs from markdown content using the MarkdownYouTubeExtractorTool.

        This function specifically uses the MarkdownYouTubeExtractorTool to:
        1. Scrape markdown content from the given URL using Firecrawl
        2. Extract all YouTube URLs found in the markdown
        3. Return structured data about the YouTube videos found

        Args:
            url: The URL containing markdown content to analyze for YouTube links

        Returns:
            Dict containing:
            - status: "success" or "error"
            - url: The original URL processed
            - youtube_urls: List of YouTube URLs found
            - youtube_count: Number of YouTube URLs found
            - markdown_content: The scraped markdown content (if successful)
            - error: Error message (if failed)
            - processing_metadata: Information about the extraction process
        """
        import time

        start_time = time.time()

        # Log the start of YouTube extraction from markdown
        self.logger.info(f"🎬 Starting YouTube extraction from markdown content at: {url}")
        self.logger.info(f"🔧 Using MarkdownYouTubeExtractorTool for specialized extraction")

        # Start Galileo trace if logger supports it
        if hasattr(self.logger, "start_trace"):
            self.logger.start_trace(f"extract_youtube_from_markdown_{url.split('/')[-1]}")

        try:
            # Add tool span for markdown YouTube extractor execution
            if hasattr(self.logger, "add_tool_span"):
                tool_start_time = time.time()

            # Execute the MarkdownYouTubeExtractorTool
            self.logger.info("🔍 Executing MarkdownYouTubeExtractorTool...")
            extraction_result = await self.markdown_youtube_extractor_tool.execute(url=url)

            # Log tool execution span
            if hasattr(self.logger, "add_tool_span"):
                tool_duration = (time.time() - tool_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="markdown_youtube_extractor_tool",
                    inputs={"url": url},
                    outputs=extraction_result,
                    duration_ns=int(tool_duration),
                    success=(
                        "error" not in extraction_result
                        if isinstance(extraction_result, dict)
                        else True
                    ),
                )

            # Check if extraction was successful
            if isinstance(extraction_result, dict) and "error" in extraction_result:
                error_msg = f"MarkdownYouTubeExtractorTool failed: {extraction_result['error']}"
                self.logger.error(error_msg)

                # Conclude trace with error
                if hasattr(self.logger, "conclude_trace"):
                    total_duration = (time.time() - start_time) * 1_000_000_000
                    self.logger.conclude_trace(
                        output=f"Error: {error_msg}",
                        duration_ns=int(total_duration),
                    )

                return {
                    "status": "error",
                    "url": url,
                    "error": error_msg,
                    "youtube_urls": [],
                    "youtube_count": 0,
                    "processing_metadata": {
                        "processing_time": f"{(time.time() - start_time):.2f} seconds",
                        "tool_used": "MarkdownYouTubeExtractorTool",
                        "success": False
                    }
                }

            # Extract YouTube URLs from the result
            youtube_urls = []
            markdown_content = ""

            if isinstance(extraction_result, dict):
                youtube_urls = extraction_result.get("youtube_urls", [])
                markdown_content = extraction_result.get("markdown_content", "")

                # Log successful extraction
                self.logger.info(f"✅ Successfully extracted {len(youtube_urls)} YouTube URLs")
                self.logger.info(f"📄 Processed {len(markdown_content)} characters of markdown content")

                # Log sample YouTube URLs found
                if youtube_urls:
                    sample_urls = youtube_urls[:3]  # Show first 3 URLs
                    self.logger.info(f"🎥 Sample YouTube URLs found: {sample_urls}")

            # Create comprehensive result
            result = {
                "status": "success",
                "url": url,
                "youtube_urls": youtube_urls,
                "youtube_count": len(youtube_urls),
                "markdown_content": markdown_content,
                "extraction_details": extraction_result,
                "processing_metadata": {
                    "processing_time": f"{(time.time() - start_time):.2f} seconds",
                    "tool_used": "MarkdownYouTubeExtractorTool",
                    "success": True,
                    "markdown_length": len(markdown_content),
                    "trace_id": (
                        f"trace_{int(start_time)}"
                        if hasattr(self.logger, "start_trace")
                        else "Not available"
                    ),
                }
            }

            # Conclude trace with success
            if hasattr(self.logger, "conclude_trace"):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Successfully extracted {len(youtube_urls)} YouTube URLs from {url}",
                    duration_ns=int(total_duration),
                )

            self.logger.info(f"🎯 Completed YouTube extraction from markdown: {url}")
            return result

        except Exception as e:
            error_msg = f"Unexpected error during YouTube extraction from markdown: {str(e)}"
            self.logger.error(error_msg, exc_info=True)

            # Conclude trace with error
            if hasattr(self.logger, "conclude_trace"):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Error: {error_msg}",
                    duration_ns=int(total_duration),
                )

            return {
                "status": "error",
                "url": url,
                "error": error_msg,
                "youtube_urls": [],
                "youtube_count": 0,
                "processing_metadata": {
                    "processing_time": f"{(time.time() - start_time):.2f} seconds",
                    "tool_used": "MarkdownYouTubeExtractorTool",
                    "success": False
                }
            }
