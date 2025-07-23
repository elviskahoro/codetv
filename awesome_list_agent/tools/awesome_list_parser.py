"""Tool for parsing Awesome List URLs to extract metadata and context."""

import re
import asyncio
import aiohttp
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..tools.base import BaseTool
from ..tools.web_scraping_tool import WebScrapingTool
from ..tools.youtube_metadata_tool import YouTubeMetadataTool
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
            },
            "web_scraping_data": {
                "type": "object",
                "description": "Detailed web scraping results"
            },
            "youtube_metadata": {
                "type": "array",
                "items": {"type": "object"},
                "description": "YouTube metadata for video links found in the list"
            },
            "comprehensive_summary": {
                "type": "string",
                "description": "Comprehensive summary combining all extracted data"
            }
        }
    }


class AwesomeListParser(BaseTool):
    """Tool for parsing Awesome List URLs and extracting contextual information."""
    
    metadata = AwesomeListParserMetadata
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("awesome_list_agent.AwesomeListParser")
        
        # Initialize sub-tools
        self.web_scraping_tool = WebScrapingTool()
        self.youtube_metadata_tool = YouTubeMetadataTool()
    
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
        import time
        start_time = time.time()
        
        self.logger.info(f"Starting to parse Awesome List URL: {url}")
        
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                error_msg = "Invalid URL format. Must start with http:// or https://"
                self.logger.error(f"URL validation failed: {error_msg}")
                return ToolError(error=error_msg)
            
            self.logger.debug("URL validation passed")
            
            # Step 1: Basic parsing of the awesome list
            self.logger.info("Step 1: Basic parsing of awesome list content")
            
            # Add tool span for basic parsing
            if hasattr(self.logger, 'add_tool_span'):
                basic_start_time = time.time()
            
            basic_parsed_data = await self._parse_basic_content(url)
            
            # Log basic parsing span
            if hasattr(self.logger, 'add_tool_span'):
                basic_duration = (time.time() - basic_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="basic_content_parsing",
                    inputs={"url": url},
                    outputs=basic_parsed_data,
                    duration_ns=int(basic_duration),
                    success="error" not in basic_parsed_data if isinstance(basic_parsed_data, dict) else True
                )
            
            if isinstance(basic_parsed_data, dict) and "error" in basic_parsed_data:
                return basic_parsed_data
            
            # Step 2: Web scraping for detailed content analysis
            self.logger.info("Step 2: Web scraping for detailed content analysis")
            
            # Add tool span for web scraping
            if hasattr(self.logger, 'add_tool_span'):
                scraping_start_time = time.time()
            
            web_scraping_data = await self._perform_web_scraping(url)
            
            # Log web scraping span
            if hasattr(self.logger, 'add_tool_span'):
                scraping_duration = (time.time() - scraping_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="web_scraping_analysis",
                    inputs={"url": url},
                    outputs=web_scraping_data,
                    duration_ns=int(scraping_duration),
                    success="error" not in web_scraping_data if isinstance(web_scraping_data, dict) else True
                )
            
            # Step 3: Extract YouTube metadata from video links
            self.logger.info("Step 3: Extracting YouTube metadata from video links")
            
            # Add tool span for YouTube metadata extraction
            if hasattr(self.logger, 'add_tool_span'):
                youtube_start_time = time.time()
            
            youtube_metadata = await self._extract_youtube_metadata(basic_parsed_data, web_scraping_data)
            
            # Log YouTube metadata extraction span
            if hasattr(self.logger, 'add_tool_span'):
                youtube_duration = (time.time() - youtube_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="youtube_metadata_extraction",
                    inputs={"basic_data": basic_parsed_data, "web_data": web_scraping_data},
                    outputs={"youtube_metadata": youtube_metadata},
                    duration_ns=int(youtube_duration),
                    success=True
                )
            
            # Step 4: Combine all data and create comprehensive summary
            self.logger.info("Step 4: Creating comprehensive summary")
            
            # Add tool span for comprehensive summary creation
            if hasattr(self.logger, 'add_tool_span'):
                summary_start_time = time.time()
            
            comprehensive_result = await self._create_comprehensive_summary(
                basic_parsed_data, web_scraping_data, youtube_metadata, url
            )
            
            # Log comprehensive summary creation span
            if hasattr(self.logger, 'add_tool_span'):
                summary_duration = (time.time() - summary_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="comprehensive_summary_creation",
                    inputs={"basic_data": basic_parsed_data, "web_data": web_scraping_data, "youtube_data": youtube_metadata},
                    outputs=comprehensive_result,
                    duration_ns=int(summary_duration),
                    success="error" not in comprehensive_result if isinstance(comprehensive_result, dict) else True
                )
            
            # Log final results
            self.logger.info(f"Comprehensive parsing completed successfully")
            self.logger.debug(f"Extracted topic: {comprehensive_result.get('topic', 'N/A')}")
            self.logger.debug(f"Found {comprehensive_result.get('total_items', 0)} items")
            self.logger.debug(f"Detected {len(comprehensive_result.get('categories', []))} categories")
            self.logger.debug(f"Found {len(comprehensive_result.get('youtube_metadata', []))} YouTube videos")
            
            # Add overall tool execution span
            if hasattr(self.logger, 'add_tool_span'):
                total_duration = (time.time() - start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="awesome_list_parser_complete",
                    inputs={"url": url},
                    outputs=comprehensive_result,
                    duration_ns=int(total_duration),
                    success="error" not in comprehensive_result if isinstance(comprehensive_result, dict) else True
                )
            
            return comprehensive_result
            
        except Exception as e:
            error_msg = f"Unexpected error parsing Awesome List: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolError(error=error_msg)
    
    async def _parse_basic_content(self, url: str) -> Dict[str, Any]:
        """Parse basic content from the awesome list URL."""
        try:
            # Fetch the content
            self.logger.info("Fetching content from URL")
            session = await self._get_session()
            async with session.get(url) as response:
                self.logger.debug(f"HTTP response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch URL: HTTP {response.status}"
                    self.logger.error(error_msg)
                    return ToolError(error=error_msg)
                
                content = await response.text()
                content_length = len(content)
                self.logger.info(f"Successfully fetched content ({content_length} characters)")
            
            # Parse the content
            self.logger.info("Starting content parsing")
            parsed_data = await self._parse_content(content, url)
            
            return parsed_data
            
        except aiohttp.ClientError as e:
            error_msg = f"Network error while fetching URL: {str(e)}"
            self.logger.error(error_msg)
            return ToolError(error=error_msg)
    
    async def _perform_web_scraping(self, url: str) -> Dict[str, Any]:
        """Perform detailed web scraping of the awesome list."""
        import time
        start_time = time.time()
        
        try:
            self.logger.info("Starting web scraping analysis")
            
            # Add tool span for web scraping tool call
            if hasattr(self.logger, 'add_tool_span'):
                tool_start_time = time.time()
            
            # Use web scraping tool to get detailed content
            scraping_result = await self.web_scraping_tool.execute(
                url=url,
                extract_text=True,
                extract_links=True,
                extract_images=False,
                extract_metadata=True,
                max_links=100,  # Get more links for comprehensive analysis
                timeout=30
            )
            
            # Log web scraping tool span
            if hasattr(self.logger, 'add_tool_span'):
                tool_duration = (time.time() - tool_start_time) * 1_000_000_000
                self.logger.add_tool_span(
                    tool_name="web_scraping_tool",
                    inputs={"url": url, "extract_text": True, "extract_links": True, "max_links": 100},
                    outputs=scraping_result,
                    duration_ns=int(tool_duration),
                    success="error" not in scraping_result if isinstance(scraping_result, dict) else True
                )
            
            # Handle ToolError objects properly
            if hasattr(scraping_result, 'error'):
                error_msg = scraping_result.error
                self.logger.warning(f"Web scraping failed: {error_msg}")
                return {"error": error_msg}
            elif isinstance(scraping_result, dict) and "error" in scraping_result:
                self.logger.warning(f"Web scraping failed: {scraping_result['error']}")
                return {"error": scraping_result["error"]}
            
            self.logger.info(f"Web scraping completed - found {len(scraping_result.get('links', []))} links")
            return scraping_result
            
        except Exception as e:
            self.logger.error(f"Error during web scraping: {str(e)}")
            return {"error": str(e)}
    
    async def _extract_youtube_metadata(self, basic_data: Dict[str, Any], web_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract YouTube metadata from video links found in the awesome list."""
        import time
        start_time = time.time()
        
        try:
            youtube_metadata = []
            
            # Extract YouTube URLs from web scraping data
            youtube_urls = self._extract_youtube_urls(web_data)
            
            if not youtube_urls:
                self.logger.info("No YouTube URLs found in the awesome list")
                return youtube_metadata
            
            self.logger.info(f"Found {len(youtube_urls)} YouTube URLs to analyze")
            
            # Process each YouTube URL (limit to first 5 to avoid rate limiting)
            for i, youtube_url in enumerate(youtube_urls[:5]):
                try:
                    self.logger.debug(f"Processing YouTube URL {i+1}/{min(len(youtube_urls), 5)}: {youtube_url}")
                    
                    # Add tool span for YouTube metadata tool call
                    if hasattr(self.logger, 'add_tool_span'):
                        tool_start_time = time.time()
                    
                    metadata = await self.youtube_metadata_tool.execute(
                        url=youtube_url,
                        extract_comments=False  # Don't extract comments to keep it fast
                    )
                    
                    # Log YouTube metadata tool span
                    if hasattr(self.logger, 'add_tool_span'):
                        tool_duration = (time.time() - tool_start_time) * 1_000_000_000
                        self.logger.add_tool_span(
                            tool_name="youtube_metadata_tool",
                            inputs={"url": youtube_url, "extract_comments": False},
                            outputs=metadata,
                            duration_ns=int(tool_duration),
                            success="error" not in metadata if isinstance(metadata, dict) else True
                        )
                    
                    # Handle ToolError objects properly
                    if hasattr(metadata, 'error'):
                        self.logger.warning(f"Failed to extract metadata for YouTube URL {youtube_url}: {metadata.error}")
                        continue
                    elif isinstance(metadata, dict) and "error" not in metadata:
                        youtube_metadata.append(metadata)
                        self.logger.debug(f"Successfully extracted metadata for: {metadata.get('title', 'Unknown')}")
                    else:
                        self.logger.warning(f"Failed to extract metadata for YouTube URL: {youtube_url}")
                
                except Exception as e:
                    self.logger.warning(f"Error processing YouTube URL {youtube_url}: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully extracted metadata for {len(youtube_metadata)} YouTube videos")
            return youtube_metadata
            
        except Exception as e:
            self.logger.error(f"Error during YouTube metadata extraction: {str(e)}")
            return []
    
    def _extract_youtube_urls(self, web_data: Dict[str, Any]) -> List[str]:
        """Extract YouTube URLs from web scraping data and text content."""
        youtube_urls = []
        
        # YouTube URL patterns for comprehensive extraction
        youtube_patterns = [
            # Standard YouTube URLs
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&[\w=&-]*)?',
            r'https?://(?:www\.)?youtube\.com/embed/[\w-]+(?:\?[\w=&-]*)?',
            r'https?://(?:www\.)?youtube\.com/v/[\w-]+(?:\?[\w=&-]*)?',
            
            # YouTube short URLs
            r'https?://youtu\.be/[\w-]+(?:\?[\w=&-]*)?',
            
            # YouTube playlist URLs
            r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+(?:&[\w=&-]*)?',
            
            # YouTube channel URLs
            r'https?://(?:www\.)?youtube\.com/channel/[\w-]+(?:\?[\w=&-]*)?',
            r'https?://(?:www\.)?youtube\.com/c/[\w-]+(?:\?[\w=&-]*)?',
            r'https?://(?:www\.)?youtube\.com/@[\w-]+(?:\?[\w=&-]*)?',
        ]
        
        # Extract from web scraping links
        if "links" in web_data:
            for link in web_data["links"]:
                link_url = link.get("url", "")
                if link_url:
                    for pattern in youtube_patterns:
                        if re.match(pattern, link_url):
                            youtube_urls.append(link_url)
                            break
        
        # Extract from text content (markdown/HTML)
        if "text_content" in web_data:
            text_content = web_data["text_content"]
            
            # Search for URLs in the text using all patterns
            for pattern in youtube_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                youtube_urls.extend(matches)
            
            # Also search within markdown link syntax [text](url)
            markdown_link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
            markdown_links = re.findall(markdown_link_pattern, text_content)
            
            for _, url in markdown_links:
                for pattern in youtube_patterns:
                    if re.match(pattern, url, re.IGNORECASE):
                        youtube_urls.append(url)
                        break
            
            # Search within markdown image syntax ![alt](url)
            markdown_image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
            markdown_images = re.findall(markdown_image_pattern, text_content)
            
            for _, url in markdown_images:
                for pattern in youtube_patterns:
                    if re.match(pattern, url, re.IGNORECASE):
                        youtube_urls.append(url)
                        break
        
        return list(set(youtube_urls))  # Remove duplicates
    
    async def _create_comprehensive_summary(
        self, 
        basic_data: Dict[str, Any], 
        web_data: Dict[str, Any], 
        youtube_data: List[Dict[str, Any]], 
        url: str
    ) -> Dict[str, Any]:
        """Create a comprehensive summary combining all extracted data."""
        
        # Start with basic parsed data
        result = basic_data.copy()
        
        # Add web scraping data
        result["web_scraping_data"] = web_data
        
        # Add YouTube metadata
        result["youtube_metadata"] = youtube_data
        
        # Create comprehensive summary
        summary_parts = []
        
        # Basic information
        if "topic" in basic_data:
            summary_parts.append(f"This Awesome List focuses on {basic_data['topic']}.")
        
        if "description" in basic_data and basic_data["description"] != "No description available":
            summary_parts.append(basic_data["description"])
        
        # Web scraping insights
        if "error" not in web_data:
            if "links" in web_data:
                link_count = len(web_data["links"])
                summary_parts.append(f"The list contains {link_count} curated resources and links.")
            
            if "text_content" in web_data:
                text_length = len(web_data["text_content"])
                summary_parts.append(f"Total content length: {text_length} characters.")
        
        # YouTube insights
        if youtube_data:
            video_count = len(youtube_data)
            total_views = sum(video.get("view_count", 0) for video in youtube_data)
            avg_duration = sum(video.get("duration_seconds", 0) for video in youtube_data) / len(youtube_data)
            
            summary_parts.append(f"🎥 Found {video_count} YouTube videos with a total of {total_views:,} views.")
            summary_parts.append(f"📺 Average video duration: {avg_duration/60:.1f} minutes.")
            
            # Add sample video titles
            if video_count > 0:
                sample_titles = [video.get("title", "Unknown") for video in youtube_data[:3]]
                if sample_titles:
                    summary_parts.append(f"📹 Sample videos: {', '.join(sample_titles)}")
        else:
            summary_parts.append("📺 No YouTube videos found in this awesome list.")
        
        # Categories and structure
        if "categories" in basic_data and basic_data["categories"]:
            cat_count = len(basic_data["categories"])
            if cat_count <= 3:
                categories_text = ", ".join(basic_data["categories"])
            else:
                categories_text = f"{', '.join(basic_data['categories'][:3])}, and {cat_count - 3} other categories"
            summary_parts.append(f"Content is organized into {cat_count} categories: {categories_text}.")
        
        # Language information
        if "language" in basic_data and basic_data["language"] != "General":
            summary_parts.append(f"Primary programming language: {basic_data['language']}.")
        
        result["comprehensive_summary"] = " ".join(summary_parts)
        
        return result
    
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
        
        # Count HTML links (excluding navigation)
        html_links = len(re.findall(r'<a[^>]+href=[^>]*>([^<]+)</a>', content, re.IGNORECASE))
        
        # Use the higher count
        return max(md_links, html_links)
    
    def _detect_language(self, content: str, url: str) -> str:
        """Detect the primary programming language if applicable."""
        # Common programming languages to look for
        languages = {
            'javascript': ['javascript', 'js', 'node', 'npm', 'react', 'vue', 'angular'],
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy'],
            'java': ['java', 'spring', 'maven', 'gradle'],
            'go': ['golang', 'go', 'gin', 'beego'],
            'rust': ['rust', 'cargo', 'crates'],
            'php': ['php', 'laravel', 'symfony', 'composer'],
            'ruby': ['ruby', 'rails', 'gem'],
            'csharp': ['c#', 'csharp', '.net', 'dotnet'],
            'cpp': ['c++', 'cpp'],
            'swift': ['swift', 'ios', 'macos'],
            'kotlin': ['kotlin', 'android'],
            'typescript': ['typescript', 'ts']
        }
        
        content_lower = content.lower()
        url_lower = url.lower()
        
        # Check URL first
        for lang, keywords in languages.items():
            if any(keyword in url_lower for keyword in keywords):
                return lang.title()
        
        # Check content
        lang_scores = {}
        for lang, keywords in languages.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                lang_scores[lang] = score
        
        if lang_scores:
            best_lang = max(lang_scores, key=lang_scores.get)
            return best_lang.title()
        
        return "General"
    
    def _generate_context_summary(
        self, topic: str, description: str, categories: List[str], 
        total_items: int, language: str
    ) -> str:
        """Generate a contextual summary of the Awesome List."""
        summary_parts = [f"This is an Awesome List focused on {topic}."]
        
        if description != "No description available":
            summary_parts.append(description)
        
        if language != "General":
            summary_parts.append(f"It primarily covers {language} related resources.")
        
        if categories:
            if len(categories) <= 3:
                cat_text = ", ".join(categories)
            else:
                cat_text = f"{', '.join(categories[:3])}, and {len(categories) - 3} other categories"
            summary_parts.append(f"Main categories include: {cat_text}.")
        
        if total_items > 0:
            summary_parts.append(f"The list contains approximately {total_items} curated resources.")
        
        return " ".join(summary_parts)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
