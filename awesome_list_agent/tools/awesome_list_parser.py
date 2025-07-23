"""Tool for parsing Awesome List URLs to extract metadata and context."""

import re
import asyncio
import aiohttp
import logging
import time
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..tools.base import BaseTool
from ..models import ToolMetadata, ToolError


class AwesomeListParserMetadata(BaseModel):
    """Metadata for the Awesome List Parser tool."""
    
    name: str = "awesome_list_parser"
    description: str = "Parses an Awesome List URL to extract general topic, categories, and contextual information"
    tags: List[str] = ["parsing", "awesome-list", "web-scraping", "metadata"]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the Awesome List to parse",
                "pattern": r"^https?://.*"
            }
        },
        "required": ["url"]
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The main topic/subject of the Awesome List"
            },
            "description": {
                "type": "string", 
                "description": "Description of what the list is about"
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Main categories found in the list"
            },
            "total_items": {
                "type": "integer",
                "description": "Number of items in the list"
            },
            "language": {
                "type": "string",
                "description": "Primary programming language if applicable"
            },
            "context_summary": {
                "type": "string",
                "description": "Brief summary of the list's purpose and content"
            }
        }
    }


class AwesomeListParser(BaseTool):
    """Tool for parsing Awesome List URLs and extracting contextual information."""
    
    metadata = AwesomeListParserMetadata
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("awesome_list_agent.AwesomeListParser")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; AwesomeListAgent/1.0)'
                }
            )
        return self.session
    
    async def execute(self, url: str) -> Dict[str, Any]:
        """Parse an Awesome List URL to extract metadata and context.
        
        Args:
            url: The URL of the Awesome List to parse
            
        Returns:
            Dictionary containing parsed information about the list
        """
        start_time = time.time()
        
        # Prepare input for logging
        tool_inputs = {"url": url}
        
        self.logger.info(f"Starting to parse Awesome List URL: {url}")
        
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                error_msg = "Invalid URL format. Must start with http:// or https://"
                self.logger.error(f"URL validation failed: {error_msg}")
                
                # Log tool span with error
                self._log_tool_span("awesome_list_parser", tool_inputs, None, 
                                  time.time() - start_time, False, error_msg)
                
                return ToolError(error=error_msg)
            
            self.logger.debug("URL validation passed")
            
            # Fetch the content
            self.logger.info("Fetching content from URL")
            fetch_start_time = time.time()
            
            session = await self._get_session()
            async with session.get(url) as response:
                self.logger.debug(f"HTTP response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch URL: HTTP {response.status}"
                    self.logger.error(error_msg)
                    
                    # Log tool span with error
                    self._log_tool_span("awesome_list_parser", tool_inputs, None,
                                      time.time() - start_time, False, error_msg)
                    
                    return ToolError(error=error_msg)
                
                content = await response.text()
                content_length = len(content)
                fetch_duration = time.time() - fetch_start_time
                
                self.logger.info(f"Successfully fetched content ({content_length} characters) in {fetch_duration:.2f}s")
            
            # Parse the content
            self.logger.info("Starting content parsing")
            parse_start_time = time.time()
            
            parsed_data = await self._parse_content(content, url)
            
            parse_duration = time.time() - parse_start_time
            total_duration = time.time() - start_time
            
            # Log parsing results
            if isinstance(parsed_data, dict):
                self.logger.info(f"Parsing completed successfully in {parse_duration:.2f}s")
                self.logger.debug(f"Extracted topic: {parsed_data.get('topic', 'N/A')}")
                self.logger.debug(f"Found {parsed_data.get('total_items', 0)} items")
                self.logger.debug(f"Detected {len(parsed_data.get('categories', []))} categories")
                self.logger.debug(f"Language: {parsed_data.get('language', 'N/A')}")
                
                # Log successful tool span with detailed output
                self._log_tool_span("awesome_list_parser", tool_inputs, parsed_data, 
                                  total_duration, True)
            else:
                # Log error tool span
                self._log_tool_span("awesome_list_parser", tool_inputs, parsed_data,
                                  total_duration, False, "Parsing failed")
            
            return parsed_data
            
        except aiohttp.ClientError as e:
            error_msg = f"Network error while fetching URL: {str(e)}"
            self.logger.error(error_msg)
            
            # Log tool span with error
            self._log_tool_span("awesome_list_parser", tool_inputs, None,
                              time.time() - start_time, False, error_msg)
            
            return ToolError(error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error parsing Awesome List: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            # Log tool span with error
            self._log_tool_span("awesome_list_parser", tool_inputs, None,
                              time.time() - start_time, False, error_msg)
            
            return ToolError(error=error_msg)
    
    def _log_tool_span(self, tool_name: str, inputs: Dict[str, Any], outputs: Optional[Dict[str, Any]], 
                      duration: float, success: bool, error: Optional[str] = None):
        """Log tool execution span with Galileo integration."""
        duration_ns = int(duration * 1_000_000_000)  # Convert to nanoseconds
        
        # Create span data for logging
        span_data = {
            "tool_name": tool_name,
            "inputs": self._sanitize_for_json(inputs),
            "outputs": self._sanitize_for_json(outputs) if outputs else None,
            "success": success,
            "error": error,
            "duration_ns": duration_ns,
            "duration_ms": duration * 1000
        }
        
        # Log as JSON for clarity
        try:
            span_json = json.dumps(span_data, indent=2, ensure_ascii=False)
            self.logger.info(f"Tool Span: {tool_name}", span_data=span_json, **span_data)
        except Exception as e:
            self.logger.error(f"Failed to serialize tool span data: {str(e)}")
        
        # If we have a logger with Galileo support, use it
        if hasattr(self.logger, 'add_tool_span'):
            try:
                self.logger.add_tool_span(
                    tool_name=tool_name,
                    inputs=inputs,
                    outputs=outputs,
                    duration_ns=duration_ns,
                    success=success,
                    error=error
                )
            except Exception as e:
                self.logger.error(f"Failed to add Galileo tool span: {str(e)}")
    
    def _sanitize_for_json(self, obj: Any) -> Any:
        """Sanitize an object for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    async def _parse_content(self, content: str, url: str) -> Dict[str, Any]:
        """Parse the HTML/Markdown content to extract list information.
        
        Args:
            content: The raw content of the page
            url: The original URL for context
            
        Returns:
            Parsed information about the Awesome List
        """
        # Extract title/topic
        topic = self._extract_topic(content, url)
        
        # Extract description
        description = self._extract_description(content)
        
        # Extract categories (headers)
        categories = self._extract_categories(content)
        
        # Count items (links)
        total_items = self._count_items(content)
        
        # Detect programming language
        language = self._detect_language(content, url)
        
        # Generate context summary
        context_summary = self._generate_context_summary(
            topic, description, categories, total_items, language
        )
        
        return {
            "topic": topic,
            "description": description,
            "categories": categories,
            "total_items": total_items,
            "language": language,
            "context_summary": context_summary
        }
    
    def _extract_topic(self, content: str, url: str) -> str:
        """Extract the main topic from title or URL."""
        # Try to extract from HTML title tag
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up common title patterns
            title = re.sub(r'^(awesome-?|Awesome\s+)', '', title, flags=re.IGNORECASE)
            if title:
                return title
        
        # Try to extract from first H1
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if h1_match:
            h1_text = h1_match.group(1).strip()
            h1_text = re.sub(r'^(awesome-?|Awesome\s+)', '', h1_text, flags=re.IGNORECASE)
            if h1_text:
                return h1_text
        
        # Try to extract from Markdown heading
        md_h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if md_h1_match:
            md_title = md_h1_match.group(1).strip()
            md_title = re.sub(r'^(awesome-?|Awesome\s+)', '', md_title, flags=re.IGNORECASE)
            if md_title:
                return md_title
        
        # Fall back to URL parsing
        url_parts = url.split('/')
        if 'awesome-' in url:
            for part in url_parts:
                if part.startswith('awesome-'):
                    return part.replace('awesome-', '').replace('-', ' ').title()
        
        return "Unknown Topic"
    
    def _extract_description(self, content: str) -> str:
        """Extract description from meta tags or content."""
        # Try meta description
        meta_desc = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', 
            content, re.IGNORECASE
        )
        if meta_desc:
            return meta_desc.group(1).strip()
        
        # Try first paragraph after title
        para_match = re.search(
            r'<h1[^>]*>[^<]+</h1>\s*<p[^>]*>([^<]+)</p>', 
            content, re.IGNORECASE | re.DOTALL
        )
        if para_match:
            return para_match.group(1).strip()
        
        # Try Markdown description (after first heading)
        md_desc = re.search(r'^#[^#\n]+\n\n([^\n]+)', content, re.MULTILINE)
        if md_desc:
            return md_desc.group(1).strip()
        
        return "No description available"
    
    def _extract_categories(self, content: str) -> List[str]:
        """Extract category headings from the content."""
        categories = []
        
        # HTML headings (h2, h3)
        html_headings = re.findall(
            r'<h[23][^>]*>([^<]+)</h[23]>', 
            content, re.IGNORECASE
        )
        categories.extend([h.strip() for h in html_headings if h.strip()])
        
        # Markdown headings (##, ###)
        md_headings = re.findall(r'^##[#]?\s+(.+)$', content, re.MULTILINE)
        categories.extend([h.strip() for h in md_headings if h.strip()])
        
        # Remove duplicates and common non-category headings
        categories = list(set(categories))
        skip_terms = {
            'contents', 'table of contents', 'contributing', 'license', 
            'awesome', 'related', 'similar', 'credits', 'acknowledgments'
        }
        categories = [c for c in categories if c.lower() not in skip_terms]
        
        return categories[:10]  # Limit to top 10 categories
    
    def _count_items(self, content: str) -> int:
        """Count approximate number of items/links in the list."""
        # Count markdown links
        md_links = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
        
        # Count HTML links
        html_links = len(re.findall(r'<a[^>]+href[^>]+>', content, re.IGNORECASE))
        
        # Count list items
        list_items = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        
        # Return the maximum count (likely the most accurate)
        return max(md_links, html_links, list_items)
    
    def _detect_language(self, content: str, url: str) -> str:
        """Detect the primary programming language from content or URL."""
        # Common programming languages to look for
        languages = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'java': ['java', 'spring', 'android'],
            'go': ['go', 'golang'],
            'rust': ['rust'],
            'cpp': ['cpp', 'c++', 'c plus plus'],
            'csharp': ['c#', 'csharp', '.net'],
            'php': ['php', 'laravel', 'wordpress'],
            'ruby': ['ruby', 'rails'],
            'swift': ['swift', 'ios'],
            'kotlin': ['kotlin'],
            'typescript': ['typescript', 'ts'],
            'scala': ['scala'],
            'r': ['r'],
            'matlab': ['matlab'],
            'julia': ['julia']
        }
        
        # Check URL first
        url_lower = url.lower()
        for lang, keywords in languages.items():
            if any(keyword in url_lower for keyword in keywords):
                return lang.title()
        
        # Check content
        content_lower = content.lower()
        for lang, keywords in languages.items():
            if any(keyword in content_lower for keyword in keywords):
                return lang.title()
        
        return "General"
    
    def _generate_context_summary(
        self, topic: str, description: str, categories: List[str], 
        total_items: int, language: str
    ) -> str:
        """Generate a contextual summary of the Awesome List."""
        summary_parts = []
        
        if topic and topic != "Unknown Topic":
            summary_parts.append(f"Comprehensive collection of {topic.lower()} resources")
        
        if language and language != "General":
            summary_parts.append(f"focused on {language} development")
        
        if total_items > 0:
            summary_parts.append(f"with {total_items} curated items")
        
        if categories:
            summary_parts.append(f"organized into {len(categories)} key areas")
        
        if description and description != "No description available":
            summary_parts.append(f"covering {description.lower()}")
        
        if not summary_parts:
            summary_parts.append("Curated collection of high-quality resources")
        
        summary = " ".join(summary_parts) + "."
        
        # Add learning context
        if categories:
            summary += f" Ideal for developers looking to master {topic.lower()} through structured learning paths."
        
        return summary
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
