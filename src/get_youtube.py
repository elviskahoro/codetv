from __future__ import annotations

import json
from typing import Any

import yt_dlp
from yt_dlp import YoutubeDL


class YouTubeDownloader:
    """A comprehensive YouTube downloader that extracts all available information in memory."""

    def __init__(self) -> None:
        """Initialize the YouTube downloader for in-memory processing."""
        pass

    def get_all_info(self, url: str) -> dict[str, Any]:
        """Extract all available information from a YouTube URL in memory.

        Args:
            url: YouTube URL to process

        Returns:
            Dictionary containing all extracted information
        """
        ydl_opts = {
            "skip_download": True,  # Never download files
            "extract_flat": False,
            "quiet": True,  # Suppress output
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return self._process_info(info)
            except Exception as e:
                return {"error": str(e), "url": url}

    def get_metadata_only(self, url: str) -> dict[str, Any]:
        """Extract only metadata without downloading any files.

        Args:
            url: YouTube URL to process

        Returns:
            Dictionary containing metadata information
        """
        ydl_opts = {
            "skip_download": True,
            "extract_flat": False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return self._process_info(info)
            except Exception as e:
                return {"error": str(e), "url": url}

    def get_subtitles(self, url: str) -> dict[str, Any]:
        """Extract subtitles/captions from a YouTube video in memory.

        Args:
            url: YouTube URL to process

        Returns:
            Dictionary containing subtitle information
        """
        ydl_opts = {
            "skip_download": True,
            "extract_flat": False,
            "quiet": True,
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return {
                    "subtitles": info.get("subtitles", {}),
                    "automatic_captions": info.get("automatic_captions", {}),
                    "title": info.get("title", ""),
                    "id": info.get("id", ""),
                }
            except Exception as e:
                return {"error": str(e), "url": url}

    def _process_info(self, info: dict[str, Any] | None) -> dict[str, Any]:
        """Process and organize the extracted information.

        Args:
            info: Raw information dictionary from yt-dlp

        Returns:
            Processed and organized information dictionary
        """
        if not info:
            return {"error": "No information extracted"}

        # Extract key information
        processed = {
            # Basic video information
            "id": info.get("id"),
            "title": info.get("title"),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "upload_date": info.get("upload_date"),
            "uploader": info.get("uploader"),
            "uploader_id": info.get("uploader_id"),
            "uploader_url": info.get("uploader_url"),
            "channel": info.get("channel"),
            "channel_id": info.get("channel_id"),
            "channel_url": info.get("channel_url"),
            # View and engagement metrics
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "dislike_count": info.get("dislike_count"),
            "comment_count": info.get("comment_count"),
            "subscriber_count": info.get("subscriber_count"),
            # Technical information
            "width": info.get("width"),
            "height": info.get("height"),
            "fps": info.get("fps"),
            "vcodec": info.get("vcodec"),
            "acodec": info.get("acodec"),
            "filesize": info.get("filesize"),
            "filesize_approx": info.get("filesize_approx"),
            # URLs and thumbnails
            "webpage_url": info.get("webpage_url"),
            "original_url": info.get("original_url"),
            "thumbnail": info.get("thumbnail"),
            "thumbnails": info.get("thumbnails", []),
            # Categories and tags
            "categories": info.get("categories", []),
            "tags": info.get("tags", []),
            "age_limit": info.get("age_limit"),
            # Subtitles and captions
            "subtitles": info.get("subtitles", {}),
            "automatic_captions": info.get("automatic_captions", {}),
            # Available formats
            "formats": info.get("formats", []),
            "format_id": info.get("format_id"),
            "ext": info.get("ext"),
            # Playlist information (if applicable)
            "playlist": info.get("playlist"),
            "playlist_id": info.get("playlist_id"),
            "playlist_title": info.get("playlist_title"),
            "playlist_index": info.get("playlist_index"),
            "playlist_count": info.get("playlist_count"),
            # Additional metadata
            "availability": info.get("availability"),
            "live_status": info.get("live_status"),
            "release_timestamp": info.get("release_timestamp"),
            "modified_timestamp": info.get("modified_timestamp"),
            "location": info.get("location"),
            "artist": info.get("artist"),
            "album": info.get("album"),
            "genre": info.get("genre"),
            # Subtitle content (extract actual text if available)
            "subtitle_content": self._extract_subtitle_content(info),
        }

        # Remove None values
        return {k: v for k, v in processed.items() if v is not None}

    def _extract_subtitle_content(self, info: dict[str, Any]) -> dict[str, str]:
        """Extract subtitle content from available subtitle data.
        
        Args:
            info: Raw information dictionary from yt-dlp
            
        Returns:
            Dictionary mapping language codes to subtitle content
        """
        subtitle_content = {}
        
        # Process manual subtitles
        subtitles = info.get("subtitles", {})
        for lang, sub_list in subtitles.items():
            if sub_list and isinstance(sub_list, list):
                # Get the first subtitle format (usually the best quality)
                subtitle_content[f"manual_{lang}"] = f"Available subtitle formats: {[s.get('ext', 'unknown') for s in sub_list]}"
        
        # Process automatic captions
        auto_captions = info.get("automatic_captions", {})
        for lang, cap_list in auto_captions.items():
            if cap_list and isinstance(cap_list, list):
                subtitle_content[f"auto_{lang}"] = f"Available caption formats: {[c.get('ext', 'unknown') for c in cap_list]}"
        
        return subtitle_content
    
    def to_json_string(self, info: dict[str, Any]) -> str:
        """Convert extracted information to JSON string.

        Args:
            info: Information dictionary to convert

        Returns:
            JSON string representation of the information
        """
        return json.dumps(info, indent=2, ensure_ascii=False, default=str)


def download_youtube_info(url: str) -> dict[str, Any]:
    """Convenience function to extract YouTube information in memory.

    Args:
        url: YouTube URL to process

    Returns:
        Dictionary containing all extracted information
    """
    downloader = YouTubeDownloader()
    return downloader.get_all_info(url)


if __name__ == "__main__":
    # Example usage
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing

    downloader = YouTubeDownloader()

    # Get all information in memory
    print("Extracting all information...")
    info = downloader.get_all_info(url)

    # Process results
    if "error" not in info:
        # Convert to JSON string for webhook response
        json_output = downloader.to_json_string(info)
        print(f"JSON output length: {len(json_output)} characters")

        # Print some key information
        print(f"Title: {info.get('title')}")
        print(f"Uploader: {info.get('uploader')}")
        print(f"Duration: {info.get('duration')} seconds")
        print(f"View count: {info.get('view_count')}")
        print(f"Available subtitles: {list(info.get('subtitles', {}).keys())}")
        print(
            f"Available auto captions: {list(info.get('automatic_captions', {}).keys())}"
        )
        print(f"Subtitle content keys: {list(info.get('subtitle_content', {}).keys())}")
    else:
        print(f"Error: {info['error']}")
