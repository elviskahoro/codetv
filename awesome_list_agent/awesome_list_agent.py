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
        
        # Register markdown YouTube extractor tool (should be called early in workflow)
        self.markdown_youtube_extractor_tool = MarkdownYouTubeExtractorTool()
        self.tool_registry.register(
            metadata=MarkdownYouTubeExtractorTool.get_metadata(),
            implementation=MarkdownYouTubeExtractorTool
        )
        self.logger.debug("Registered markdown_youtube_extractor_tool")

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
            
            # Step 2: Generate learning path and instructional guidance
            self.logger.info("Generating learning path and instructional guidance")
            
            # Add tool span for learning path generation
            if hasattr(self.logger, 'add_tool_span'):
                learning_start_time = time.time()
            
            learning_path = await self._generate_learning_path(parsed_data)
            instructional_guidance = await self._generate_instructional_guidance(parsed_data)
            
            # Log learning path generation span
            if hasattr(self.logger, 'add_tool_span'):
                learning_duration = (time.time() - learning_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="learning_path_generation",
                    inputs={"parsed_data": parsed_data},
                    outputs={"learning_path": learning_path, "instructional_guidance": instructional_guidance},
                    duration_ns=int(learning_duration),
                    success=True
                )
            
            # TODO: Implement MCP server call. 
            # Step 3: Call MCP server for additional enrichment
            self.logger.info("Calling MCP server for content enrichment")
            
            # Add tool span for MCP server call
            if hasattr(self.logger, 'add_tool_span'):
                mcp_start_time = time.time()
            
            mcp_result = await self.call_mcp_server(url, parsed_data.get("comprehensive_summary", ""))
            
            # Log MCP server call span
            if hasattr(self.logger, 'add_tool_span'):
                mcp_duration = (time.time() - mcp_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="mcp_server_call",
                    inputs={"url": url, "comprehensive_summary": parsed_data.get("comprehensive_summary", "")},
                    outputs=mcp_result,
                    duration_ns=int(mcp_duration),
                    success=mcp_result.get("mcp_status") == "success"
                )
            
            self.logger.debug(f"MCP server result: {mcp_result}")
            

            #TODO: Implement MCP server call. 
            # Combine all results into comprehensive learning path
            result = {
                "status": "success",
                "url": url,
                "parsed_data": parsed_data,
                "learning_path": learning_path,
                "instructional_guidance": instructional_guidance,
                "mcp_result": mcp_result,
                "metadata": {
                    "total_items": parsed_data.get("total_items", 0),
                    "categories_count": len(parsed_data.get("categories", [])),
                    "youtube_videos_count": len(parsed_data.get("youtube_metadata", [])),
                    "processing_time": f"{(time.time() - start_time):.2f} seconds",
                    "trace_id": f"trace_{int(start_time)}" if hasattr(self.logger, 'start_trace') else "Not available"
                }
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

    async def _generate_learning_path(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured learning path based on the parsed awesome list data."""
        try:
            topic = parsed_data.get("topic", "Awesome List")
            categories = parsed_data.get("categories", [])
            total_items = parsed_data.get("total_items", 0)
            language = parsed_data.get("language", "General")
            youtube_videos = parsed_data.get("youtube_metadata", [])
            
            # Determine difficulty level based on content analysis
            difficulty = self._assess_difficulty(parsed_data)
            
            # Estimate time commitment
            estimated_time = self._estimate_time_commitment(total_items, len(youtube_videos), difficulty)
            
            # Create learning steps
            steps = []
            
            # Step 1: Foundation
            steps.append({
                "title": "Foundation Setup",
                "description": f"Start with basic {topic.lower()} concepts and tools",
                "estimated_time": "1-2 days",
                "resources_count": min(10, total_items // 4)
            })
            
            # Step 2: Core Concepts
            if categories:
                steps.append({
                    "title": "Core Concepts",
                    "description": f"Learn fundamental {topic.lower()} patterns and practices",
                    "estimated_time": "3-5 days",
                    "resources_count": min(20, total_items // 3)
                })
            
            # Step 3: Advanced Topics
            steps.append({
                "title": "Advanced Topics",
                "description": f"Explore specialized areas and advanced {topic.lower()} techniques",
                "estimated_time": "1-2 weeks",
                "resources_count": min(30, total_items // 2)
            })
            
            # Step 4: Practical Application
            steps.append({
                "title": "Practical Application",
                "description": f"Build projects using the learned {topic.lower()} concepts",
                "estimated_time": "1 week",
                "resources_count": min(15, total_items // 4)
            })
            
            # Step 5: Community Engagement
            steps.append({
                "title": "Community Engagement",
                "description": "Contribute back to the community and share knowledge",
                "estimated_time": "Ongoing",
                "resources_count": 5
            })
            
            return {
                "title": f"{topic} Learning Journey",
                "difficulty": difficulty,
                "estimated_time": estimated_time,
                "steps": steps,
                "total_resources": total_items,
                "youtube_videos": len(youtube_videos),
                "primary_language": language
            }
            
        except Exception as e:
            self.logger.error(f"Error generating learning path: {str(e)}")
            return {
                "title": "Learning Path",
                "difficulty": "Intermediate",
                "estimated_time": "2-4 weeks",
                "steps": [],
                "error": str(e)
            }
    
    async def _generate_instructional_guidance(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate instructional guidance based on the parsed data."""
        try:
            topic = parsed_data.get("topic", "Awesome List")
            categories = parsed_data.get("categories", [])
            language = parsed_data.get("language", "General")
            youtube_videos = parsed_data.get("youtube_metadata", [])
            web_data = parsed_data.get("web_scraping_data", {})
            
            # Create summary
            summary_parts = [f"This Awesome List covers a wide range of {topic.lower()} resources."]
            
            if language != "General":
                summary_parts.append(f"Focus on {language} related areas that align with your current projects.")
            
            if categories:
                summary_parts.append(f"Explore categories that match your skill level and interests.")
            
            summary = " ".join(summary_parts)
            
            # Generate learning tips
            tips = [
                "Start with tools and resources you'll use immediately in your projects",
                "Practice with small projects before tackling complex implementations",
                "Join community discussions to learn from others' experiences",
                "Keep a learning journal to track your progress and insights",
                "Don't try to learn everything at once - focus on one area at a time"
            ]
            
            # Add language-specific tips
            if language != "General":
                tips.append(f"Focus on {language} best practices and community standards")
            
            # Add video-specific tips if YouTube videos are available
            if youtube_videos:
                tips.append("Use the included video resources for visual learning and demonstrations")
                tips.append("Take notes while watching videos and practice the concepts shown")
            
            return {
                "summary": summary,
                "tips": tips,
                "focus_areas": categories[:5] if categories else [],
                "recommended_starting_point": categories[0] if categories else "General concepts"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating instructional guidance: {str(e)}")
            return {
                "summary": "Focus on areas that align with your current projects and skill level.",
                "tips": ["Start with basic concepts", "Practice regularly", "Join community discussions"],
                "focus_areas": [],
                "recommended_starting_point": "General concepts"
            }
    
    def _assess_difficulty(self, parsed_data: Dict[str, Any]) -> str:
        """Assess the difficulty level of the awesome list content."""
        try:
            categories = parsed_data.get("categories", [])
            total_items = parsed_data.get("total_items", 0)
            language = parsed_data.get("language", "General")
            youtube_videos = parsed_data.get("youtube_metadata", [])
            
            # Simple difficulty assessment based on content characteristics
            score = 0
            
            # More items = potentially more complex
            if total_items > 100:
                score += 2
            elif total_items > 50:
                score += 1
            
            # More categories = broader scope
            if len(categories) > 10:
                score += 2
            elif len(categories) > 5:
                score += 1
            
            # Specific language focus = more specialized
            if language != "General":
                score += 1
            
            # YouTube videos = more comprehensive
            if len(youtube_videos) > 5:
                score += 1
            
            # Determine difficulty based on score
            if score >= 4:
                return "Advanced"
            elif score >= 2:
                return "Intermediate"
            else:
                return "Beginner"
                
        except Exception as e:
            self.logger.error(f"Error assessing difficulty: {str(e)}")
            return "Intermediate"
    
    def _estimate_time_commitment(self, total_items: int, youtube_videos: int, difficulty: str) -> str:
        """Estimate the time commitment required for the learning path."""
        try:
            # Base time calculation
            base_time = total_items * 0.5  # 30 minutes per item on average
            
            # Add time for YouTube videos
            video_time = youtube_videos * 15  # 15 minutes per video on average
            
            total_minutes = base_time + video_time
            
            # Adjust based on difficulty
            if difficulty == "Advanced":
                total_minutes *= 1.5
            elif difficulty == "Beginner":
                total_minutes *= 0.8
            
            # Convert to weeks
            hours_per_week = 10  # Assuming 10 hours per week
            weeks = total_minutes / (hours_per_week * 60)
            
            if weeks < 1:
                return "1 week"
            elif weeks < 2:
                return "1-2 weeks"
            elif weeks < 4:
                return "2-4 weeks"
            elif weeks < 8:
                return "1-2 months"
            else:
                return "2-3 months"
                
        except Exception as e:
            self.logger.error(f"Error estimating time commitment: {str(e)}")
            return "2-4 weeks"

    # TODO: Implement MCP server call
    async def call_mcp_server(self, url: str, comprehensive_summary: str) -> Dict[str, Any]:
        """Call the MCP server with the URL and comprehensive summary information.

        Args:
            url: The URL to send to the MCP server.
            comprehensive_summary: The comprehensive summary of the Awesome List.

        Returns:
            Result from the MCP server call.
        """
        import time
        start_time = time.time()
        
        self.logger.info(f"Calling MCP server with URL: {url}")
        self.logger.debug(f"Comprehensive summary length: {len(comprehensive_summary)} characters")
        
        # Add detailed Galileo logging for MCP server call
        if hasattr(self.logger, 'info'):
            self.logger.info(f"[Galileo] MCP Server Call - URL: {url}")
            self.logger.info(f"[Galileo] MCP Server Call - Comprehensive Summary Length: {len(comprehensive_summary)} chars")
        
        try:
            # This is a placeholder for actual MCP server integration
            # You would implement your actual MCP server calling logic here
            
            # Simulate processing time
            import asyncio
            await asyncio.sleep(0.1)  # Simulate network call
            
            result = {
                "mcp_status": "success",
                "message": f"MCP server processed URL: {url}",
                "comprehensive_summary_received": comprehensive_summary,
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
                "comprehensive_summary_received": comprehensive_summary,
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
                if "comprehensive_summary" in result:
                    formatted_parts.append(f"Summary: {result['comprehensive_summary']}")
            else:
                formatted_parts.append(f"Tool '{tool_name}' encountered an error")
        
        return "\n".join(formatted_parts)

