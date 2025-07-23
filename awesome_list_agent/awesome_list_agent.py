from .agent import Agent
from .tools.awesome_list_parser import AwesomeListParser
from .tools.youtube_metadata_tool import YouTubeMetadataTool
from .tools.web_scraping_tool import WebScrapingTool
from .tools.content_analysis_tool import ContentAnalysisTool
from typing import Any, Dict, List, Optional
import uuid
import logging
from datetime import datetime
import time
import json

class AwesomeListAgent(Agent):
    """
    Awesome List Learning Path Agent
    
    This specialized agent transforms Awesome Lists on GitHub into structured, personalized learning paths.
    It analyzes curated resource collections to extract key information, categorize content,
    and generate instructional guidance for effective learning.
    
    Key Capabilities:
    - Parse and analyze Awesome List repositories
    - Extract metadata, categories, and resource counts
    - Identify programming languages and technologies
    - Generate contextual summaries and learning recommendations
    - Provide structured learning path guidance
    
    The agent is designed to help developers of all different skill levels navigate curated resource collections
    and create personalized learning journeys based on their interests and skill levels.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up logger - use the injected logger or create a default one
        if self.logger:
            self.logger = self.logger
        else:
            self.logger = logging.getLogger("awesome_list_agent.AwesomeListAgent")
        
        # Log agent initialization
        self.logger.info("Initializing AwesomeListAgent - Learning Path Generator")
        
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
        """
        Process an Awesome List URL to extract key information and generate learning guidance.

        This method transforms a curated resource collection into a structured learning path
        with instructional guidance and personalized recommendations.

        Args:
            url: The URL of the Awesome List to process.

        Returns:
            A dictionary containing:
            - Parsed information about the list
            - Learning path recommendations
            - Instructional guidance
            - Resource categorization
            - Personalized learning suggestions
        """
        start_time = time.time()
        
        # Start Galileo trace if logger supports it
        if hasattr(self.logger, 'start_trace'):
            trace_name = f"awesome_list_learning_path_{url.split('/')[-1]}"
            self.logger.start_trace(trace_name)
        
        self.logger.info(f"Starting to process Awesome List URL: {url}")
        self.logger.info("Transforming curated resources into structured learning path")
        
        try:
            # Step 1: Parse the awesome list using our tool
            self.logger.info("Executing awesome list parser to extract metadata and structure")
            
            # Add tool span for parser execution
            tool_start_time = time.time()
            
            parsed_data = await self.parser.execute(url)
            
            # Log tool execution span with detailed JSON
            tool_duration = (time.time() - tool_start_time) * 1_000_000_000  # Convert to nanoseconds
            if hasattr(self.logger, 'add_tool_span'):
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
                self.logger.info(f"Found {parsed_data.get('total_items', 0)} curated resources")
                self.logger.info(f"Detected {len(parsed_data.get('categories', []))} learning categories")
                self.logger.info(f"Primary technology: {parsed_data.get('language', 'N/A')}")
            
            # Step 2: Generate learning path and instructional guidance
            self.logger.info("Generating learning path recommendations and instructional guidance")
            
            # Add tool span for learning path generation
            learning_start_time = time.time()
            
            learning_guidance = await self._generate_learning_guidance(parsed_data)
            
            # Log learning path generation span
            learning_duration = (time.time() - learning_start_time) * 1_000_000_000
            if hasattr(self.logger, 'add_tool_span'):
                self.logger.add_tool_span(
                    tool_name="learning_path_generator",
                    inputs={"parsed_data": parsed_data},
                    outputs=learning_guidance,
                    duration_ns=int(learning_duration),
                    success=True
                )
            # TODO: Implement MCP server call. 
            # Step 3: Call MCP server for additional enrichment
            self.logger.info("Calling MCP server for content enrichment")
            
            # Add tool span for MCP server call
            mcp_start_time = time.time()
            
            mcp_result = await self.call_mcp_server(url, parsed_data.get("context_summary", ""))
            
            # Log MCP server call span
            mcp_duration = (time.time() - mcp_start_time) * 1_000_000_000
            if hasattr(self.logger, 'add_tool_span'):
                self.logger.add_tool_span(
                    tool_name="mcp_server_call",
                    inputs={"url": url, "context_summary": parsed_data.get("context_summary", "")},
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
                "learning_guidance": learning_guidance,
                "mcp_result": mcp_result,
                "processing_metadata": {
                    "total_duration_seconds": time.time() - start_time,
                    "timestamp": datetime.now().isoformat(),
                    "agent_version": "1.0.0"
                }
            }
            
            self.logger.info("Successfully completed learning path generation")
            self.logger.info(f"Generated {len(learning_guidance.get('learning_paths', []))} learning paths")
            
            # Conclude trace with success
            if hasattr(self.logger, 'conclude_trace'):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.conclude_trace(
                    output=f"Successfully generated learning path for {parsed_data.get('total_items', 0)} resources from {url}",
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

    async def _generate_learning_guidance(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive learning guidance and path recommendations.
        
        Args:
            parsed_data: Parsed data from the awesome list
            
        Returns:
            Dictionary containing learning guidance, paths, and recommendations
        """
        topic = parsed_data.get('topic', 'Unknown Topic')
        categories = parsed_data.get('categories', [])
        total_items = parsed_data.get('total_items', 0)
        language = parsed_data.get('language', 'General')
        description = parsed_data.get('description', '')
        
        # Generate learning paths based on categories
        learning_paths = []
        for i, category in enumerate(categories[:5], 1):  # Focus on top 5 categories
            learning_paths.append({
                "path_id": f"path_{i}",
                "name": f"{category} Learning Path",
                "description": f"Comprehensive learning path for {category.lower()}",
                "difficulty": self._assess_difficulty(category, language),
                "estimated_hours": self._estimate_learning_time(category, total_items),
                "prerequisites": self._identify_prerequisites(category, language),
                "resources_count": max(1, total_items // len(categories)),
                "learning_objectives": self._generate_learning_objectives(category)
            })
        
        # Generate instructional guidance
        instructional_guidance = {
            "overview": f"This curated collection contains {total_items} high-quality resources for learning {topic.lower()}. "
                       f"The resources are organized into {len(categories)} key areas, providing a comprehensive "
                       f"learning experience for developers at all skill levels.",
            "recommended_approach": self._generate_recommended_approach(topic, categories, language),
            "skill_levels": {
                "beginner": self._identify_beginner_resources(categories),
                "intermediate": self._identify_intermediate_resources(categories),
                "advanced": self._identify_advanced_resources(categories)
            },
            "learning_tips": self._generate_learning_tips(topic, language),
            "time_commitment": self._calculate_time_commitment(total_items, categories)
        }
        
        return {
            "learning_paths": learning_paths,
            "instructional_guidance": instructional_guidance,
            "topic_summary": f"Comprehensive learning resources for {topic} with {total_items} curated items across {len(categories)} categories",
            "recommended_starting_point": self._recommend_starting_point(categories, language)
        }
    
    def _assess_difficulty(self, category: str, language: str) -> str:
        """Assess the difficulty level of a learning category."""
        advanced_keywords = ['advanced', 'expert', 'master', 'professional', 'enterprise']
        beginner_keywords = ['beginner', 'intro', 'basics', 'fundamentals', 'getting started']
        
        category_lower = category.lower()
        
        if any(keyword in category_lower for keyword in advanced_keywords):
            return "Advanced"
        elif any(keyword in category_lower for keyword in beginner_keywords):
            return "Beginner"
        else:
            return "Intermediate"
    
    def _estimate_learning_time(self, category: str, total_items: int) -> int:
        """Estimate learning time in hours for a category."""
        base_hours = 10  # Base hours per category
        items_factor = min(total_items / 100, 2)  # Scale with number of items
        return int(base_hours * items_factor)
    
    def _identify_prerequisites(self, category: str, language: str) -> List[str]:
        """Identify prerequisites for a learning category."""
        prerequisites = []
        
        if language.lower() != 'general':
            prerequisites.append(f"Basic understanding of {language}")
        
        if 'advanced' in category.lower():
            prerequisites.append("Intermediate programming experience")
        elif 'framework' in category.lower():
            prerequisites.append("Basic programming concepts")
        
        return prerequisites
    
    def _generate_learning_objectives(self, category: str) -> List[str]:
        """Generate learning objectives for a category."""
        return [
            f"Understand core concepts of {category.lower()}",
            f"Apply {category.lower()} in practical scenarios",
            f"Build confidence with {category.lower()} tools and techniques"
        ]
    
    def _generate_recommended_approach(self, topic: str, categories: List[str], language: str) -> str:
        """Generate recommended learning approach."""
        return (
            f"Start with the fundamentals and gradually progress to more advanced topics. "
            f"Focus on hands-on practice and real-world applications. "
            f"Consider your current skill level and choose resources accordingly. "
            f"Allocate dedicated time for each category and track your progress."
        )
    
    def _identify_beginner_resources(self, categories: List[str]) -> List[str]:
        """Identify beginner-friendly resource categories."""
        return [cat for cat in categories if any(keyword in cat.lower() 
                for keyword in ['beginner', 'intro', 'basics', 'fundamentals'])]
    
    def _identify_intermediate_resources(self, categories: List[str]) -> List[str]:
        """Identify intermediate-level resource categories."""
        return [cat for cat in categories if not any(keyword in cat.lower() 
                for keyword in ['beginner', 'advanced', 'expert', 'intro', 'basics'])]
    
    def _identify_advanced_resources(self, categories: List[str]) -> List[str]:
        """Identify advanced-level resource categories."""
        return [cat for cat in categories if any(keyword in cat.lower() 
                for keyword in ['advanced', 'expert', 'master', 'professional'])]
    
    def _generate_learning_tips(self, topic: str, language: str) -> List[str]:
        """Generate learning tips for the topic."""
        tips = [
            "Set clear learning goals and track your progress",
            "Practice regularly with hands-on exercises",
            "Join community discussions and forums",
            "Build projects to apply your knowledge",
            "Review and revisit concepts periodically"
        ]
        
        if language.lower() != 'general':
            tips.append(f"Focus on {language}-specific best practices and patterns")
        
        return tips
    
    def _calculate_time_commitment(self, total_items: int, categories: List[str]) -> Dict[str, Any]:
        """Calculate recommended time commitment."""
        total_hours = sum(self._estimate_learning_time(cat, total_items) for cat in categories[:5])
        
        return {
            "total_hours": total_hours,
            "weekly_hours": min(10, max(5, total_hours // 8)),  # 5-10 hours per week
            "estimated_weeks": max(4, total_hours // 8),  # At least 4 weeks
            "intensive_weeks": max(2, total_hours // 15)  # Intensive pace
        }
    
    def _recommend_starting_point(self, categories: List[str], language: str) -> str:
        """Recommend a starting point for learning."""
        beginner_cats = self._identify_beginner_resources(categories)
        
        if beginner_cats:
            return f"Start with '{beginner_cats[0]}' to build a solid foundation"
        elif categories:
            return f"Begin with '{categories[0]}' and progress systematically"
        else:
            return "Review all available resources and choose based on your current skill level"

    # TODO: Implement MCP server call
    async def call_mcp_server(self, url: str, context_summary: str) -> Dict[str, Any]:
        """Call the MCP server with the URL and context information.

        Args:
            url: The URL to send to the MCP server.
            context_summary: The extracted summary of the Awesome List.

        Returns:
            Result from the MCP server call.
        """
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
            Formatted result string with learning guidance
        """
        if not results:
            return "No results from tool execution"
        
        formatted_parts = []
        for tool_name, result in results:
            if isinstance(result, dict) and "error" not in result:
                formatted_parts.append(f"✅ Tool '{tool_name}' completed successfully")
                if "context_summary" in result:
                    formatted_parts.append(f"📝 Summary: {result['context_summary']}")
                if "learning_guidance" in result:
                    guidance = result["learning_guidance"]
                    formatted_parts.append(f"🎯 Learning Paths: {len(guidance.get('learning_paths', []))} paths generated")
                    formatted_parts.append(f"📚 Instructional Guidance: {guidance.get('topic_summary', 'N/A')}")
            else:
                formatted_parts.append(f"❌ Tool '{tool_name}' encountered an error")
        
        return "\n".join(formatted_parts)

