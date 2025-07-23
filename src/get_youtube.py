from __future__ import annotations

from typing import Any

from yt_dlp import YoutubeDL
from pydantic import BaseModel, Field


class YouTubeData(BaseModel):
    """Comprehensive model for YouTube video data."""

    # Basic video information
    id: str | None = Field(None, description="Video ID")
    title: str | None = Field(None, description="Video title")
    description: str | None = Field(None, description="Video description")
    duration: int | None = Field(None, description="Video duration in seconds")
    upload_date: str | None = Field(None, description="Upload date (YYYYMMDD format)")
    uploader: str | None = Field(None, description="Channel/uploader name")
    uploader_id: str | None = Field(None, description="Channel/uploader ID")
    uploader_url: str | None = Field(None, description="Channel/uploader URL")
    channel: str | None = Field(None, description="Channel name")
    channel_id: str | None = Field(None, description="Channel ID")
    channel_url: str | None = Field(None, description="Channel URL")

    # View and engagement metrics
    view_count: int | None = Field(None, description="Number of views")
    like_count: int | None = Field(None, description="Number of likes")
    dislike_count: int | None = Field(None, description="Number of dislikes")
    comment_count: int | None = Field(None, description="Number of comments")
    subscriber_count: int | None = Field(None, description="Channel subscriber count")

    # Technical information
    width: int | None = Field(None, description="Video width in pixels")
    height: int | None = Field(None, description="Video height in pixels")
    fps: float | None = Field(None, description="Frames per second")
    vcodec: str | None = Field(None, description="Video codec")
    acodec: str | None = Field(None, description="Audio codec")
    filesize: int | None = Field(None, description="File size in bytes")
    filesize_approx: int | None = Field(None, description="Approximate file size in bytes")

    # URLs and thumbnails
    webpage_url: str | None = Field(None, description="Original webpage URL")
    original_url: str | None = Field(None, description="Original video URL")
    thumbnail: str | None = Field(None, description="Main thumbnail URL")
    thumbnails: list[dict[str, Any]] = Field(default_factory=list, description="List of available thumbnails")

    # Categories and tags
    categories: list[str] = Field(default_factory=list, description="Video categories")
    tags: list[str] = Field(default_factory=list, description="Video tags")
    age_limit: int | None = Field(None, description="Age restriction limit")

    # Subtitles and captions
    subtitles: dict[str, Any] = Field(default_factory=dict, description="Available subtitles")
    automatic_captions: dict[str, Any] = Field(default_factory=dict, description="Available automatic captions")
    subtitle_content: dict[str, str] = Field(default_factory=dict, description="Processed subtitle content")

    # Available formats
    formats: list[dict[str, Any]] = Field(default_factory=list, description="Available video/audio formats")
    format_id: str | None = Field(None, description="Selected format ID")
    ext: str | None = Field(None, description="File extension")

    # Playlist information (if applicable)
    playlist: str | None = Field(None, description="Playlist name")
    playlist_id: str | None = Field(None, description="Playlist ID")
    playlist_title: str | None = Field(None, description="Playlist title")
    playlist_index: int | None = Field(None, description="Position in playlist")
    playlist_count: int | None = Field(None, description="Total videos in playlist")

    # Additional metadata
    availability: str | None = Field(None, description="Video availability status")
    live_status: str | None = Field(None, description="Live stream status")
    release_timestamp: int | None = Field(None, description="Release timestamp")
    modified_timestamp: int | None = Field(None, description="Last modified timestamp")
    location: str | None = Field(None, description="Geographic location")
    artist: str | None = Field(None, description="Artist name (for music videos)")
    album: str | None = Field(None, description="Album name (for music videos)")
    genre: str | None = Field(None, description="Genre")

    # Error handling
    error: str | None = Field(None, description="Error message if extraction failed")
    url: str | None = Field(None, description="Original URL that was processed")


class YouTubeDownloader:
    """A comprehensive YouTube downloader that extracts all available information in memory."""

    def __init__(self) -> None:
        """Initialize the YouTube downloader for in-memory processing."""
        pass

    def get_all_info(self, url: str) -> YouTubeData:
        """Extract all available information from a YouTube URL in memory.

        Args:
            url: YouTube URL to process

        Returns:
            YouTubeData model containing all extracted information
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
                return self._process_info(info, url)
            except Exception as e:
                return YouTubeData(error=str(e), url=url)

    def get_metadata_only(self, url: str) -> YouTubeData:
        """Extract only metadata without downloading any files.

        Args:
            url: YouTube URL to process

        Returns:
            YouTubeData model containing metadata information
        """
        ydl_opts = {
            "skip_download": True,
            "extract_flat": False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                return self._process_info(info, url)
            except Exception as e:
                return YouTubeData(error=str(e), url=url)

    def get_subtitles(self, url: str) -> YouTubeData:
        """Extract subtitles/captions from a YouTube video in memory.

        Args:
            url: YouTube URL to process

        Returns:
            YouTubeData model containing subtitle information
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
                return YouTubeData(
                    subtitles=info.get("subtitles", {}),
                    automatic_captions=info.get("automatic_captions", {}),
                    title=info.get("title"),
                    id=info.get("id"),
                    subtitle_content=self._extract_subtitle_content(info),
                    url=url
                )
            except Exception as e:
                return YouTubeData(error=str(e), url=url)

    def _process_info(self, info: dict[str, Any] | None, url: str) -> YouTubeData:
        """Process and organize the extracted information.

        Args:
            info: Raw information dictionary from yt-dlp
            url: Original URL that was processed

        Returns:
            YouTubeData model with processed information
        """
        if not info:
            return YouTubeData(error="No information extracted", url=url)

        # Create YouTubeData model with all extracted information
        return YouTubeData(
            # Basic video information
            id=info.get("id"),
            title=info.get("title"),
            description=info.get("description"),
            duration=info.get("duration"),
            upload_date=info.get("upload_date"),
            uploader=info.get("uploader"),
            uploader_id=info.get("uploader_id"),
            uploader_url=info.get("uploader_url"),
            channel=info.get("channel"),
            channel_id=info.get("channel_id"),
            channel_url=info.get("channel_url"),
            # View and engagement metrics
            view_count=info.get("view_count"),
            like_count=info.get("like_count"),
            dislike_count=info.get("dislike_count"),
            comment_count=info.get("comment_count"),
            subscriber_count=info.get("subscriber_count"),
            # Technical information
            width=info.get("width"),
            height=info.get("height"),
            fps=info.get("fps"),
            vcodec=info.get("vcodec"),
            acodec=info.get("acodec"),
            filesize=info.get("filesize"),
            filesize_approx=info.get("filesize_approx"),
            # URLs and thumbnails
            webpage_url=info.get("webpage_url"),
            original_url=info.get("original_url"),
            thumbnail=info.get("thumbnail"),
            thumbnails=info.get("thumbnails", []),
            # Categories and tags
            categories=info.get("categories", []),
            tags=info.get("tags", []),
            age_limit=info.get("age_limit"),
            # Subtitles and captions
            subtitles=info.get("subtitles", {}),
            automatic_captions=info.get("automatic_captions", {}),
            subtitle_content=self._extract_subtitle_content(info),
            # Available formats
            formats=info.get("formats", []),
            format_id=info.get("format_id"),
            ext=info.get("ext"),
            # Playlist information (if applicable)
            playlist=info.get("playlist"),
            playlist_id=info.get("playlist_id"),
            playlist_title=info.get("playlist_title"),
            playlist_index=info.get("playlist_index"),
            playlist_count=info.get("playlist_count"),
            # Additional metadata
            availability=info.get("availability"),
            live_status=info.get("live_status"),
            release_timestamp=info.get("release_timestamp"),
            modified_timestamp=info.get("modified_timestamp"),
            location=info.get("location"),
            artist=info.get("artist"),
            album=info.get("album"),
            genre=info.get("genre"),
            # Original URL
            url=url
        )

    def get_transcript(self, url: str, language: str = "en") -> dict[str, Any]:
        """Extract transcript/captions from a YouTube video.

        Args:
            url: YouTube URL to process
            language: Preferred language code (default: "en")

        Returns:
            Dictionary containing transcript text and metadata
        """
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en'],  # Fallback to English
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    return {
                        "error": "Could not extract video information",
                        "transcript": None,
                        "language": None,
                        "source": None
                    }

                transcript_text = None
                used_language = None
                source_type = None

                # Try to get manual subtitles first
                subtitles = info.get("subtitles", {})
                if language in subtitles and subtitles[language]:
                    transcript_text = self._download_subtitle_content(subtitles[language][0])
                    used_language = language
                    source_type = "manual"
                elif "en" in subtitles and subtitles["en"]:
                    transcript_text = self._download_subtitle_content(subtitles["en"][0])
                    used_language = "en"
                    source_type = "manual"

                # Fallback to automatic captions if no manual subtitles
                if not transcript_text:
                    auto_captions = info.get("automatic_captions", {})
                    if language in auto_captions and auto_captions[language]:
                        transcript_text = self._download_subtitle_content(auto_captions[language][0])
                        used_language = language
                        source_type = "automatic"
                    elif "en" in auto_captions and auto_captions["en"]:
                        transcript_text = self._download_subtitle_content(auto_captions["en"][0])
                        used_language = "en"
                        source_type = "automatic"

                if transcript_text:
                    return {
                        "transcript": transcript_text,
                        "language": used_language,
                        "source": source_type,
                        "title": info.get("title"),
                        "duration": info.get("duration"),
                        "error": None
                    }
                else:
                    available_langs = list(subtitles.keys()) + list(auto_captions.keys())
                    return {
                        "error": f"No transcript available for language '{language}' or 'en'. Available languages: {available_langs}",
                        "transcript": None,
                        "language": None,
                        "source": None,
                        "available_languages": available_langs
                    }

        except Exception as e:
            return {
                "error": f"Error extracting transcript: {str(e)}",
                "transcript": None,
                "language": None,
                "source": None
            }

    def _download_subtitle_content(self, subtitle_info: dict[str, Any]) -> str | None:
        """Download and extract text content from subtitle URL.

        Args:
            subtitle_info: Subtitle information dictionary containing URL

        Returns:
            Extracted text content or None if failed
        """
        try:
            import urllib.request
            import re

            url = subtitle_info.get("url")
            if not url:
                return None

            # Download subtitle content
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')

            # Extract text from different subtitle formats
            if subtitle_info.get("ext") == "vtt":
                # WebVTT format
                lines = content.split('\n')
                text_lines = []
                for line in lines:
                    line = line.strip()
                    # Skip WebVTT headers, timestamps, and empty lines
                    if (line and
                        not line.startswith('WEBVTT') and
                        not line.startswith('NOTE') and
                        not '-->' in line and
                        not re.match(r'^\d+$', line)):
                        # Remove HTML tags
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        if clean_line:
                            text_lines.append(clean_line)
                return ' '.join(text_lines)

            elif subtitle_info.get("ext") == "srv3" or "srv" in subtitle_info.get("ext", ""):
                # YouTube's srv3 format (XML-based)
                import xml.etree.ElementTree as ET
                try:
                    root = ET.fromstring(content)
                    text_parts = []
                    for text_elem in root.findall('.//text'):
                        if text_elem.text:
                            text_parts.append(text_elem.text.strip())
                    return ' '.join(text_parts)
                except ET.ParseError:
                    # Fallback: extract text using regex
                    text_matches = re.findall(r'<text[^>]*>([^<]+)</text>', content)
                    return ' '.join(text_matches)

            else:
                # Generic text extraction (remove common subtitle formatting)
                clean_content = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
                clean_content = re.sub(r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}', '', clean_content)  # Remove SRT timestamps
                clean_content = re.sub(r'^\d+$', '', clean_content, flags=re.MULTILINE)  # Remove SRT sequence numbers
                lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
                return ' '.join(lines)

        except Exception as e:
            print(f"Error downloading subtitle content: {e}")
            return None

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

    def to_json_string(self, youtube_data: YouTubeData) -> str:
        """Convert YouTubeData model to JSON string.

        Args:
            youtube_data: YouTubeData model to convert

        Returns:
            JSON string representation of the YouTube data
        """
        return youtube_data.model_dump_json(indent=2, exclude_none=True)


def download_youtube_info(url: str) -> YouTubeData:
    """Convenience function to extract YouTube information in memory.

    Args:
        url: YouTube URL to process

    Returns:
        YouTubeData model containing all extracted information
    """
    downloader = YouTubeDownloader()
    return downloader.get_all_info(url)


def get_youtube_transcript(url: str, language: str = "en") -> dict[str, Any]:
    """Convenience function to extract transcript from a YouTube video.

    Args:
        url: YouTube URL to process
        language: Preferred language code (default: "en")

    Returns:
        Dictionary containing transcript text and metadata:
        {
            "transcript": str | None,  # The extracted transcript text
            "language": str | None,   # Language code used
            "source": str | None,     # "manual" or "automatic"
            "title": str | None,      # Video title
            "duration": int | None,   # Video duration in seconds
            "error": str | None,      # Error message if extraction failed
            "available_languages": list[str] | None  # Available languages if extraction failed
        }
    """
    downloader = YouTubeDownloader()
    return downloader.get_transcript(url, language)



if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    downloader = YouTubeDownloader()
    print("Extracting all information...")
    info = downloader.get_all_info(url)
    print(info)
