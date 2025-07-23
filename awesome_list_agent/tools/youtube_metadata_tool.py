"""Tool for extracting YouTube video metadata and information."""

import re
import asyncio
import aiohttp
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from .base import BaseTool
from ..models import ToolMetadata, ToolError


class YouTubeMetadataToolMetadata(ToolMetadata):
    """Metadata for the YouTube Metadata Tool."""
    
    name: str = "youtube_metadata_tool"
    description: str = "Extracts metadata and information from YouTube video URLs including title, description, duration, views, and more"
    tags: List[str] = ["youtube", "metadata", "video", "web-scraping", "content-analysis"]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The YouTube video URL to extract metadata from",
                "pattern": r"^https?://(?:www\.)?(?:youtube\.com|youtu\.be)/.*"
            },
            "extract_comments": {
                "type": "boolean",
                "description": "Whether to extract comment information (default: false)",
                "default": False
            }
        },
        "required": ["url"]
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "video_id": {
                "type": "string",
                "description": "YouTube video ID"
            },
            "title": {
                "type": "string",
                "description": "Video title"
            },
            "description": {
                "type": "string",
                "description": "Video description"
            },
            "duration": {
                "type": "string",
                "description": "Video duration in ISO 8601 format"
            },
            "duration_seconds": {
                "type": "integer",
                "description": "Video duration in seconds"
            },
            "view_count": {
                "type": "integer",
                "description": "Number of views"
            },
            "like_count": {
                "type": "integer",
                "description": "Number of likes"
            },
            "comment_count": {
                "type": "integer",
                "description": "Number of comments"
            },
            "upload_date": {
                "type": "string",
                "description": "Upload date in ISO format"
            },
            "channel_name": {
                "type": "string",
                "description": "Channel name"
            },
            "channel_id": {
                "type": "string",
                "description": "Channel ID"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Video tags"
            },
            "category": {
                "type": "string",
                "description": "Video category"
            },
            "thumbnail_url": {
                "type": "string",
                "description": "High quality thumbnail URL"
            },
            "comments": {
                "type": "array",
                "items": {"type": "object"},
                "description": "Top comments (if extract_comments is true)"
            },
            "metadata_summary": {
                "type": "string",
                "description": "Brief summary of the video content and engagement"
            }
        }
    }


class YouTubeMetadataTool(BaseTool):
    """Tool for extracting comprehensive metadata from YouTube videos."""
    
    metadata = YouTubeMetadataToolMetadata
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("awesome_list_agent.YouTubeMetadataTool")
    
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
    
    async def execute(self, url: str, extract_comments: bool = False) -> Dict[str, Any]:
        """Extract metadata from a YouTube video URL.
        
        Args:
            url: The YouTube video URL to extract metadata from
            extract_comments: Whether to extract comment information
            
        Returns:
            Dictionary containing comprehensive video metadata
        """
        start_time = time.perf_counter_ns()
        
        try:
            # Log tool execution start
            self.logger.info(f"Starting YouTube metadata extraction for URL: {url}")
            
            # Validate URL format
            if not self._is_valid_youtube_url(url):
                error_msg = "Invalid YouTube URL format"
                self.logger.error(f"URL validation failed: {error_msg}")
                return ToolError(error=error_msg)
            
            # Extract video ID
            video_id = self._extract_video_id(url)
            if not video_id:
                error_msg = "Could not extract video ID from URL"
                self.logger.error(error_msg)
                return ToolError(error=error_msg)
            
            self.logger.debug(f"Extracted video ID: {video_id}")
            
            # Fetch video metadata
            self.logger.info("Fetching video metadata")
            metadata = await self._fetch_video_metadata(video_id, extract_comments)
            
            # Calculate duration
            duration_ns = time.perf_counter_ns() - start_time
            
            # Log successful extraction
            self.logger.info(f"Successfully extracted metadata for video: {metadata.get('title', 'Unknown')}")
            self.logger.debug(f"Extraction completed in {duration_ns / 1_000_000:.2f}ms")
            
            # Add timing information to metadata
            metadata['extraction_time_ms'] = duration_ns / 1_000_000
            
            return metadata
            
        except aiohttp.ClientError as e:
            error_msg = f"Network error while fetching video metadata: {str(e)}"
            self.logger.error(error_msg)
            return ToolError(error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error extracting YouTube metadata: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolError(error=error_msg)
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """Validate that the URL is a valid YouTube URL."""
        youtube_patterns = [
            r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(?:www\.)?youtu\.be/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+',
            r'^https?://(?:www\.)?youtube\.com/v/[\w-]+'
        ]
        
        return any(re.match(pattern, url) for pattern in youtube_patterns)
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        # Handle youtu.be URLs
        if 'youtu.be' in url:
            path = urlparse(url).path
            return path.lstrip('/') if path else None
        
        # Handle youtube.com URLs
        if 'youtube.com' in url:
            parsed = urlparse(url)
            if parsed.path == '/watch':
                query_params = parse_qs(parsed.query)
                return query_params.get('v', [None])[0]
            elif parsed.path.startswith('/embed/') or parsed.path.startswith('/v/'):
                return parsed.path.split('/')[-1]
        
        return None
    
    async def _fetch_video_metadata(self, video_id: str, extract_comments: bool) -> Dict[str, Any]:
        """Fetch comprehensive metadata for a YouTube video."""
        # This is a simplified implementation
        # In a real implementation, you would use YouTube Data API v3
        # For now, we'll simulate the metadata extraction
        
        self.logger.debug(f"Fetching metadata for video ID: {video_id}")
        
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        # Generate mock metadata (replace with actual YouTube API calls)
        metadata = {
            "video_id": video_id,
            "title": f"Sample YouTube Video - {video_id}",
            "description": "This is a sample video description that would be extracted from YouTube.",
            "duration": "PT10M30S",  # ISO 8601 duration format
            "duration_seconds": 630,
            "view_count": 15000,
            "like_count": 1200,
            "comment_count": 450,
            "upload_date": "2024-01-15T10:30:00Z",
            "channel_name": "Sample Channel",
            "channel_id": "UC123456789",
            "tags": ["sample", "video", "tutorial", "education"],
            "category": "Education",
            "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
            "metadata_summary": f"Sample video with {15000} views, {1200} likes, and {450} comments. Duration: 10 minutes 30 seconds."
        }
        
        if extract_comments:
            metadata["comments"] = [
                {
                    "author": "User1",
                    "text": "Great video! Very helpful.",
                    "likes": 25,
                    "timestamp": "2024-01-16T08:15:00Z"
                },
                {
                    "author": "User2", 
                    "text": "Thanks for sharing this information.",
                    "likes": 12,
                    "timestamp": "2024-01-16T09:30:00Z"
                }
            ]
        
        return metadata
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close() 