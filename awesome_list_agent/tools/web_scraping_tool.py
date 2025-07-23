"""Tool for scraping web content and extracting structured information."""

import re
import asyncio
import aiohttp
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json

from .base import BaseTool
from ..models import ToolMetadata, ToolError


class WebScrapingToolMetadata(ToolMetadata):
    """Metadata for the Web Scraping Tool."""

    name: str = "web_scraping_tool"
    description: str = (
        "Scrapes web content from URLs and extracts structured information including text, links, images, and metadata"
    )
    tags: List[str] = [
        "web-scraping",
        "content-extraction",
        "html-parsing",
        "data-collection",
    ]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to scrape content from",
                "pattern": r"^https?://.*",
            },
            "extract_text": {
                "type": "boolean",
                "description": "Whether to extract text content (default: true)",
                "default": True,
            },
            "extract_links": {
                "type": "boolean",
                "description": "Whether to extract links (default: true)",
                "default": True,
            },
            "extract_images": {
                "type": "boolean",
                "description": "Whether to extract image information (default: false)",
                "default": False,
            },
            "extract_metadata": {
                "type": "boolean",
                "description": "Whether to extract meta tags (default: true)",
                "default": True,
            },
            "max_links": {
                "type": "integer",
                "description": "Maximum number of links to extract (default: 50)",
                "default": 50,
            },
            "max_images": {
                "type": "integer",
                "description": "Maximum number of images to extract (default: 20)",
                "default": 20,
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds (default: 30)",
                "default": 30,
            },
        },
        "required": ["url"],
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The URL that was scraped"},
            "title": {"type": "string", "description": "Page title"},
            "text_content": {"type": "string", "description": "Extracted text content"},
            "text_summary": {
                "type": "string",
                "description": "Brief summary of the text content",
            },
            "links": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "text": {"type": "string"},
                        "title": {"type": "string"},
                    },
                },
                "description": "Extracted links",
            },
            "images": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "src": {"type": "string"},
                        "alt": {"type": "string"},
                        "title": {"type": "string"},
                    },
                },
                "description": "Extracted images",
            },
            "metadata": {"type": "object", "description": "Page metadata (meta tags)"},
            "content_type": {
                "type": "string",
                "description": "Content type of the page",
            },
            "content_length": {
                "type": "integer",
                "description": "Length of the content in characters",
            },
            "scraping_summary": {
                "type": "string",
                "description": "Summary of what was extracted",
            },
        },
    }


class WebScrapingTool(BaseTool):
    """Tool for scraping web content and extracting structured information."""

    metadata = WebScrapingToolMetadata

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("awesome_list_agent.WebScrapingTool")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; AwesomeListAgent/1.0)"
                },
            )
        return self.session

    async def execute(
        self,
        url: str,
        extract_text: bool = True,
        extract_links: bool = True,
        extract_images: bool = False,
        extract_metadata: bool = True,
        max_links: int = 50,
        max_images: int = 20,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Scrape content from a web URL and extract structured information.

        Args:
            url: The URL to scrape content from
            extract_text: Whether to extract text content
            extract_links: Whether to extract links
            extract_images: Whether to extract image information
            extract_metadata: Whether to extract meta tags
            max_links: Maximum number of links to extract
            max_images: Maximum number of images to extract
            timeout: Request timeout in seconds

        Returns:
            Dictionary containing scraped content and extracted information
        """
        start_time = time.perf_counter_ns()

        try:
            # Log tool execution start
            self.logger.info(f"Starting web scraping for URL: {url}")
            self.logger.debug(
                f"Extraction options: text={extract_text}, links={extract_links}, images={extract_images}, metadata={extract_metadata}"
            )

            # Validate URL format
            if not url.startswith(("http://", "https://")):
                error_msg = "Invalid URL format. Must start with http:// or https://"
                self.logger.error(f"URL validation failed: {error_msg}")
                return ToolError(error=error_msg)

            # Fetch the content
            self.logger.info("Fetching content from URL")
            session = await self._get_session()

            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                self.logger.debug(f"HTTP response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch URL: HTTP {response.status}"
                    self.logger.error(error_msg)
                    return ToolError(error=error_msg)

                content = await response.text()
                content_length = len(content)
                content_type = response.headers.get("content-type", "unknown")

                self.logger.info(
                    f"Successfully fetched content ({content_length} characters, type: {content_type})"
                )

            # Parse the content
            self.logger.info("Parsing HTML content")
            soup = BeautifulSoup(content, "html.parser")

            # Extract information based on options
            result = {
                "url": url,
                "content_type": content_type,
                "content_length": content_length,
            }

            # Extract title
            title_tag = soup.find("title")
            result["title"] = (
                title_tag.get_text().strip() if title_tag else "No title found"
            )

            # Extract text content
            if extract_text:
                self.logger.debug("Extracting text content")
                text_content = self._extract_text_content(soup)
                result["text_content"] = text_content
                result["text_summary"] = self._generate_text_summary(text_content)

            # Extract links
            if extract_links:
                self.logger.debug("Extracting links")
                result["links"] = self._extract_links(soup, max_links)

            # Extract images
            if extract_images:
                self.logger.debug("Extracting images")
                result["images"] = self._extract_images(soup, max_images)

            # Extract metadata
            if extract_metadata:
                self.logger.debug("Extracting metadata")
                result["metadata"] = self._extract_metadata(soup)

            # Generate scraping summary
            result["scraping_summary"] = self._generate_scraping_summary(result)

            # Calculate duration
            duration_ns = time.perf_counter_ns() - start_time

            # Log successful scraping
            self.logger.info(f"Successfully scraped content from: {result['title']}")
            self.logger.debug(f"Scraping completed in {duration_ns / 1_000_000:.2f}ms")

            # Add timing information
            result["scraping_time_ms"] = duration_ns / 1_000_000

            return result

        except aiohttp.ClientError as e:
            error_msg = f"Network error while scraping URL: {str(e)}"
            self.logger.error(error_msg)
            return ToolError(error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during web scraping: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolError(error=error_msg)

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from the HTML."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text and clean it up
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        return text

    def _extract_links(
        self, soup: BeautifulSoup, max_links: int
    ) -> List[Dict[str, str]]:
        """Extract links from the HTML."""
        links = []

        for link in soup.find_all("a", href=True):
            if len(links) >= max_links:
                break

            href = link.get("href")
            text = link.get_text().strip()
            title = link.get("title", "")

            # Skip empty links and javascript links
            if href and not href.startswith("javascript:"):
                links.append({"url": href, "text": text, "title": title})

        return links

    def _extract_images(
        self, soup: BeautifulSoup, max_images: int
    ) -> List[Dict[str, str]]:
        """Extract image information from the HTML."""
        images = []

        for img in soup.find_all("img", src=True):
            if len(images) >= max_images:
                break

            src = img.get("src")
            alt = img.get("alt", "")
            title = img.get("title", "")

            if src:
                images.append({"src": src, "alt": alt, "title": title})

        return images

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from meta tags."""
        metadata = {}

        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")

            if name and content:
                metadata[name] = content

        return metadata

    def _generate_text_summary(self, text: str) -> str:
        """Generate a brief summary of the text content."""
        if not text:
            return "No text content found"

        # Take first 200 characters and add ellipsis if longer
        summary = text[:200].strip()
        if len(text) > 200:
            summary += "..."

        return summary

    def _generate_scraping_summary(self, result: Dict[str, Any]) -> str:
        """Generate a summary of what was scraped."""
        summary_parts = [
            f"Successfully scraped content from {result.get('title', 'Unknown page')}"
        ]

        if "text_content" in result:
            text_length = len(result["text_content"])
            summary_parts.append(f"Extracted {text_length} characters of text")

        if "links" in result:
            link_count = len(result["links"])
            summary_parts.append(f"Found {link_count} links")

        if "images" in result:
            image_count = len(result["images"])
            summary_parts.append(f"Found {image_count} images")

        if "metadata" in result:
            meta_count = len(result["metadata"])
            summary_parts.append(f"Extracted {meta_count} metadata fields")

        return ". ".join(summary_parts) + "."

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
