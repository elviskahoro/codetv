"""Tool for extracting YouTube URLs from markdown content scraped from URLs."""

import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from firecrawl.firecrawl import FirecrawlApp
from src.extract_youtube_urls import extract_youtube_urls_from_markdown

from .base import BaseTool
from ..models import ToolMetadata, ToolError


def firecrawl_markdown(
    url: str,
) -> str:
    api_key: str = "fc-95ddf7f5c64f4e1e814f03567183dc16"
    app: Any = FirecrawlApp(api_key=api_key)
    scrape_data = app.scrape_url(
        url,
        params={
            "onlyMainContent": True,
        },
    )
    markdown = scrape_data.get("markdown", "")
    print(markdown)
    return markdown


class MarkdownYouTubeExtractorToolMetadata(ToolMetadata):
    """Metadata for the Markdown YouTube Extractor Tool."""

    name: str = "markdown_youtube_extractor_tool"
    description: str = (
        "Scrapes markdown content from URLs and extracts YouTube URLs found within the content. This tool is essential for analyzing awesome lists and other markdown-based content to find video resources."
    )
    tags: List[str] = [
        "markdown",
        "youtube",
        "content-extraction",
        "web-scraping",
        "url-parsing",
        "awesome-list",
    ]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to scrape markdown content from",
            },
            "extract_video_ids": {
                "type": "boolean",
                "description": "Whether to also extract video IDs from YouTube URLs",
                "default": True,
            },
            "include_metadata": {
                "type": "boolean",
                "description": "Whether to include basic metadata about found videos",
                "default": False,
            },
            "max_urls": {
                "type": "integer",
                "description": "Maximum number of YouTube URLs to extract",
                "default": 100,
            },
        },
        "required": ["url"],
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "youtube_urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of extracted YouTube URLs",
            },
            "video_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of extracted YouTube video IDs",
            },
            "url_count": {
                "type": "integer",
                "description": "Total number of YouTube URLs found",
            },
            "source_url": {
                "type": "string",
                "description": "The original URL that was scraped",
            },
        },
    }


class MarkdownYouTubeExtractorTool(BaseTool):
    """Tool for extracting YouTube URLs from markdown content scraped from URLs."""

    metadata = MarkdownYouTubeExtractorToolMetadata

    def __init__(self):
        self.logger = logging.getLogger(
            "awesome_list_agent.MarkdownYouTubeExtractorTool"
        )
        self.api_key = "fc-95ddf7f5c64f4e1e814f03567183dc16"

    def _validate_url(self, url: str) -> bool:
        """Validate that the URL is properly formatted."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _scrape_markdown_content(self, url: str) -> str:
        """Scrape markdown content from a URL using Firecrawl."""
        try:
            self.logger.info(f"Scraping markdown content from URL: {url}")

            app = FirecrawlApp(api_key=self.api_key)
            scrape_data = app.scrape_url(
                url,
                params={
                    "onlyMainContent": True,
                },
            )

            markdown = scrape_data.get("markdown", "")
            self.logger.info(
                f"Successfully scraped {len(markdown)} characters of markdown content"
            )

            return markdown

        except Exception as e:
            error_msg = f"Error scraping markdown from URL {url}: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    async def execute(
        self,
        url: str,
        extract_video_ids: bool = True,
        include_metadata: bool = False,
        max_urls: int = 100,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Extract YouTube URLs from markdown content scraped from a URL.

        Args:
            url: The URL to scrape markdown content from
            extract_video_ids: Whether to also extract video IDs from YouTube URLs
            include_metadata: Whether to include basic metadata about found videos
            max_urls: Maximum number of YouTube URLs to extract
            timeout: Request timeout in seconds (not used with Firecrawl but kept for compatibility)

        Returns:
            Dictionary containing extracted YouTube URLs and metadata
        """
        try:
            # Validate URL
            if not self._validate_url(url):
                error_msg = f"Invalid URL format: {url}"
                self.logger.error(error_msg)
                return ToolError(error=error_msg)

            # Scrape markdown content using Firecrawl
            markdown_content = self._scrape_markdown_content(url)

            if not markdown_content:
                self.logger.warning("No markdown content found")
                return {
                    "youtube_urls": [],
                    "video_ids": [],
                    "url_count": 0,
                    "source_url": url,
                }

            # Extract YouTube URLs from markdown
            youtube_urls = extract_youtube_urls_from_markdown(markdown_content)

            # Limit the number of URLs if specified
            if max_urls and len(youtube_urls) > max_urls:
                youtube_urls = youtube_urls[:max_urls]
                self.logger.info(f"Limited results to {max_urls} URLs")

            result = {
                "youtube_urls": youtube_urls,
                "url_count": len(youtube_urls),
                "source_url": url,
            }

            # Extract video IDs if requested
            if extract_video_ids:
                from src.extract_youtube_urls import extract_video_ids_from_urls

                video_ids = extract_video_ids_from_urls(youtube_urls)
                result["video_ids"] = video_ids

            # Add metadata if requested
            if include_metadata:
                result["metadata"] = {
                    "markdown_length": len(markdown_content),
                    "extraction_timestamp": time.time(),
                    "firecrawl_used": True,
                }

            self.logger.info(
                f"Successfully extracted {len(youtube_urls)} YouTube URLs from {url}"
            )
            return result

        except Exception as e:
            error_msg = f"Error executing YouTube URL extraction: {str(e)}"
            self.logger.error(error_msg)
            return ToolError(error=error_msg)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No cleanup needed for Firecrawl-based implementation
        pass
