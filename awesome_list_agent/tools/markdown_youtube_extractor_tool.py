"""Tool for extracting YouTube URLs from markdown content scraped from URLs."""

import re
import asyncio
import aiohttp
import logging
import time
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from .base import BaseTool
from ..models import ToolMetadata, ToolError


class MarkdownYouTubeExtractorToolMetadata(ToolMetadata):
    """Metadata for the Markdown YouTube Extractor Tool."""
    
    name: str = "markdown_youtube_extractor_tool"
    description: str = "Scrapes markdown content from URLs and extracts YouTube URLs found within the content. This tool is essential for analyzing awesome lists and other markdown-based content to find video resources."
    tags: List[str] = ["markdown", "youtube", "content-extraction", "web-scraping", "url-parsing", "awesome-list"]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to scrape markdown content from",
                "pattern": r"^https?://.*"
            },
            "extract_video_ids": {
                "type": "boolean",
                "description": "Whether to also extract video IDs from YouTube URLs (default: true)",
                "default": True
            },
            "include_metadata": {
                "type": "boolean",
                "description": "Whether to include basic metadata about found videos (default: false)",
                "default": False
            },
            "max_urls": {
                "type": "integer",
                "description": "Maximum number of YouTube URLs to extract (default: 100)",
                "default": 100
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds (default: 30)",
                "default": 30
            }
        },
        "required": ["url"]
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "source_url": {
                "type": "string",
                "description": "The original URL that was scraped"
            },
            "markdown_content": {
                "type": "string",
                "description": "The scraped markdown content"
            },
            "content_length": {
                "type": "integer",
                "description": "Length of the markdown content in characters"
            },
            "youtube_urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of unique YouTube URLs found in the content"
            },
            "video_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of YouTube video IDs extracted from URLs"
            },
            "url_metadata": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "video_id": {"type": "string"},
                        "link_text": {"type": "string"},
                        "context": {"type": "string"},
                        "url_type": {"type": "string"}
                    }
                },
                "description": "Detailed metadata about each YouTube URL found"
            },
            "statistics": {
                "type": "object",
                "properties": {
                    "total_urls_found": {"type": "integer"},
                    "unique_video_ids": {"type": "integer"},
                    "url_types": {"type": "object"},
                    "content_analysis": {"type": "object"}
                },
                "description": "Statistics about the extraction process"
            },
            "extraction_summary": {
                "type": "string",
                "description": "Brief summary of what was extracted"
            }
        }
    }


class MarkdownYouTubeExtractorTool(BaseTool):
    """Tool for extracting YouTube URLs from markdown content scraped from URLs."""
    
    metadata = MarkdownYouTubeExtractorToolMetadata
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("awesome_list_agent.MarkdownYouTubeExtractorTool")
        
        # YouTube URL patterns for comprehensive extraction
        self.youtube_patterns = [
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
    
    async def execute(
        self,
        url: str,
        extract_video_ids: bool = True,
        include_metadata: bool = False,
        max_urls: int = 100,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Extract YouTube URLs from markdown content scraped from a URL.
        
        Args:
            url: The URL to scrape markdown content from
            extract_video_ids: Whether to also extract video IDs from YouTube URLs
            include_metadata: Whether to include basic metadata about found videos
            max_urls: Maximum number of YouTube URLs to extract
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing extracted YouTube URLs and metadata
        """
        start_time = time.perf_counter_ns()
        
        try:
            # Log tool execution start
            self.logger.info(f"Starting markdown YouTube extraction for URL: {url}")
            self.logger.debug(f"Options: extract_video_ids={extract_video_ids}, include_metadata={include_metadata}, max_urls={max_urls}")
            
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                error_msg = "Invalid URL format. Must start with http:// or https://"
                self.logger.error(f"URL validation failed: {error_msg}")
                return ToolError(error=error_msg)
            
            # Step 1: Scrape markdown content from URL
            self.logger.info("Step 1: Scraping markdown content from URL")
            markdown_content = await self._scrape_markdown_content(url, timeout)
            
            if isinstance(markdown_content, dict) and "error" in markdown_content:
                return markdown_content
            
            # Step 2: Extract YouTube URLs from markdown content
            self.logger.info("Step 2: Extracting YouTube URLs from markdown content")
            youtube_urls = self._extract_youtube_urls_from_markdown(markdown_content, max_urls)
            
            # Step 3: Extract video IDs if requested
            video_ids = []
            if extract_video_ids:
                self.logger.info("Step 3: Extracting video IDs from YouTube URLs")
                video_ids = self._extract_video_ids_from_urls(youtube_urls)
            
            # Step 4: Generate URL metadata if requested
            url_metadata = []
            if include_metadata:
                self.logger.info("Step 4: Generating URL metadata")
                url_metadata = self._generate_url_metadata(youtube_urls, markdown_content)
            
            # Step 5: Calculate statistics
            self.logger.info("Step 5: Calculating extraction statistics")
            statistics = self._calculate_statistics(youtube_urls, video_ids, markdown_content)
            
            # Step 6: Generate comprehensive result
            result = {
                "source_url": url,
                "markdown_content": markdown_content,
                "content_length": len(markdown_content),
                "youtube_urls": youtube_urls,
                "video_ids": video_ids,
                "url_metadata": url_metadata,
                "statistics": statistics,
                "extraction_summary": self._generate_extraction_summary(youtube_urls, video_ids, statistics)
            }
            
            # Calculate duration
            duration_ns = time.perf_counter_ns() - start_time
            
            # Log successful extraction
            self.logger.info(f"Successfully extracted {len(youtube_urls)} YouTube URLs from markdown content")
            self.logger.debug(f"Extraction completed in {duration_ns / 1_000_000:.2f}ms")
            
            # Add timing information
            result['extraction_time_ms'] = duration_ns / 1_000_000
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error during markdown YouTube extraction: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolError(error=error_msg)
    
    async def _scrape_markdown_content(self, url: str, timeout: int) -> str:
        """Scrape markdown content from a URL using Firecrawl-like approach."""
        try:
            self.logger.info("Fetching content from URL")
            session = await self._get_session()
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                self.logger.debug(f"HTTP response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch URL: HTTP {response.status}"
                    self.logger.error(error_msg)
                    return ToolError(error=error_msg)
                
                content = await response.text()
                content_length = len(content)
                self.logger.info(f"Successfully fetched content ({content_length} characters)")
            
            # Extract markdown content (simplified approach)
            # In a real implementation, you might use a more sophisticated markdown extractor
            markdown_content = self._extract_markdown_from_html(content)
            
            return markdown_content
            
        except aiohttp.ClientError as e:
            error_msg = f"Network error while fetching URL: {str(e)}"
            self.logger.error(error_msg)
            return ToolError(error=error_msg)
    
    def _extract_markdown_from_html(self, html_content: str) -> str:
        """Extract markdown-like content from HTML."""
        # This is a simplified implementation
        # In a real scenario, you might use a library like html2text or similar
        
        # Remove script and style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert common HTML elements to markdown-like format
        # Headers
        html_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Links
        html_content = re.sub(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', r'[\2](\1)', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Lists
        html_content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Paragraphs
        html_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
        html_content = html_content.strip()
        
        return html_content
    
    def _extract_youtube_urls_from_markdown(self, markdown_text: str, max_urls: int) -> List[str]:
        """Extract YouTube URLs from markdown text."""
        if not markdown_text:
            return []
        
        urls: Set[str] = set()
        
        # Search for URLs in the text using all patterns
        for pattern in self.youtube_patterns:
            matches = re.findall(pattern, markdown_text, re.IGNORECASE)
            urls.update(matches)
        
        # Also search within markdown link syntax [text](url)
        markdown_link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        markdown_links = re.findall(markdown_link_pattern, markdown_text)
        
        for _, url in markdown_links:
            for pattern in self.youtube_patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    urls.add(url)
        
        # Search within markdown image syntax ![alt](url)
        markdown_image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        markdown_images = re.findall(markdown_image_pattern, markdown_text)
        
        for _, url in markdown_images:
            for pattern in self.youtube_patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    urls.add(url)
        
        # Limit the number of URLs and return sorted list
        return sorted(list(urls))[:max_urls]
    
    def _extract_video_ids_from_urls(self, urls: List[str]) -> List[str]:
        """Extract YouTube video IDs from a list of YouTube URLs."""
        video_ids = []
        
        for url in urls:
            video_id = None
            
            # Standard watch URLs
            match = re.search(r'[?&]v=([^&]+)', url)
            if match:
                video_id = match.group(1)
            
            # Short URLs
            elif 'youtu.be/' in url:
                match = re.search(r'youtu\.be/([^?&]+)', url)
                if match:
                    video_id = match.group(1)
            
            # Embed URLs
            elif '/embed/' in url:
                match = re.search(r'/embed/([^?&]+)', url)
                if match:
                    video_id = match.group(1)
            
            # v/ URLs
            elif '/v/' in url:
                match = re.search(r'/v/([^?&]+)', url)
                if match:
                    video_id = match.group(1)
            
            if video_id and video_id not in video_ids:
                video_ids.append(video_id)
        
        return video_ids
    
    def _generate_url_metadata(self, urls: List[str], markdown_content: str) -> List[Dict[str, Any]]:
        """Generate metadata for each YouTube URL found."""
        metadata = []
        
        for url in urls:
            # Extract video ID
            video_id = None
            for pattern in [r'[?&]v=([^&]+)', r'youtu\.be/([^?&]+)', r'/embed/([^?&]+)', r'/v/([^?&]+)']:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    break
            
            # Determine URL type
            url_type = "video"
            if "playlist" in url:
                url_type = "playlist"
            elif "channel" in url or "/c/" in url or "/@" in url:
                url_type = "channel"
            elif "embed" in url:
                url_type = "embed"
            
            # Find link text and context
            link_text = ""
            context = ""
            
            # Look for markdown link containing this URL
            markdown_link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
            markdown_links = re.findall(markdown_link_pattern, markdown_content)
            
            for text, link_url in markdown_links:
                if link_url == url:
                    link_text = text
                    break
            
            # Extract context (text around the URL)
            url_index = markdown_content.find(url)
            if url_index != -1:
                start = max(0, url_index - 100)
                end = min(len(markdown_content), url_index + len(url) + 100)
                context = markdown_content[start:end].replace('\n', ' ').strip()
            
            metadata.append({
                "url": url,
                "video_id": video_id,
                "link_text": link_text,
                "context": context,
                "url_type": url_type
            })
        
        return metadata
    
    def _calculate_statistics(self, urls: List[str], video_ids: List[str], markdown_content: str) -> Dict[str, Any]:
        """Calculate statistics about the extraction process."""
        # Count URL types
        url_types = {}
        for url in urls:
            url_type = "video"
            if "playlist" in url:
                url_type = "playlist"
            elif "channel" in url or "/c/" in url or "/@" in url:
                url_type = "channel"
            elif "embed" in url:
                url_type = "embed"
            
            url_types[url_type] = url_types.get(url_type, 0) + 1
        
        # Content analysis
        content_analysis = {
            "total_lines": len(markdown_content.split('\n')),
            "total_words": len(markdown_content.split()),
            "has_markdown_links": bool(re.search(r'\[([^\]]*)\]\([^)]+\)', markdown_content)),
            "has_markdown_images": bool(re.search(r'!\[([^\]]*)\]\([^)]+\)', markdown_content)),
            "has_headings": bool(re.search(r'^#{1,6}\s+', markdown_content, re.MULTILINE))
        }
        
        return {
            "total_urls_found": len(urls),
            "unique_video_ids": len(video_ids),
            "url_types": url_types,
            "content_analysis": content_analysis
        }
    
    def _generate_extraction_summary(self, urls: List[str], video_ids: List[str], statistics: Dict[str, Any]) -> str:
        """Generate a summary of the extraction process."""
        summary_parts = [f"Successfully extracted {len(urls)} YouTube URLs from markdown content"]
        
        if video_ids:
            summary_parts.append(f"Found {len(video_ids)} unique video IDs")
        
        if statistics.get("url_types"):
            url_type_summary = []
            for url_type, count in statistics["url_types"].items():
                url_type_summary.append(f"{count} {url_type} URLs")
            summary_parts.append(f"URL types: {', '.join(url_type_summary)}")
        
        if statistics.get("content_analysis"):
            analysis = statistics["content_analysis"]
            summary_parts.append(f"Content analysis: {analysis['total_lines']} lines, {analysis['total_words']} words")
        
        return ". ".join(summary_parts) + "."
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close() 