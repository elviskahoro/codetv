from __future__ import annotations

import json
import os
from typing import Any

import yt_dlp
from yt_dlp import YoutubeDL


class YouTubeDownloader:
    """A comprehensive YouTube downloader that extracts all available information."""

    def __init__(self, output_path: str = "./downloads") -> None:
        """Initialize the YouTube downloader.

        Args:
            output_path: Directory to save downloaded files
        """
        self.output_path = output_path
        os.makedirs(output_path, exist_ok=True)

    def get_all_info(self, url: str, download_video: bool = False) -> dict[str, Any]:
        """Extract all available information from a YouTube URL.

        Args:
            url: YouTube URL to process
            download_video: Whether to download the actual video file

        Returns:
            Dictionary containing all extracted information
        """
        ydl_opts = {
            "writeinfojson": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "writedescription": True,
            "writethumbnail": True,
            "writeannotations": True,
            "extract_flat": False,
            "outtmpl": f"{self.output_path}/%(title)s.%(ext)s",
        }

        if not download_video:
            ydl_opts["skip_download"] = True

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=download_video)
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
        """Extract subtitles/captions from a YouTube video.

        Args:
            url: YouTube URL to process

        Returns:
            Dictionary containing subtitle information
        """
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "outtmpl": f"{self.output_path}/%(title)s.%(ext)s",
        }

        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                # Download subtitles separately
                ydl.download([url])

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
        }

        # Remove None values
        return {k: v for k, v in processed.items() if v is not None}

    def save_info_to_json(self, info: dict[str, Any], filename: str) -> str:
        """Save extracted information to a JSON file.

        Args:
            info: Information dictionary to save
            filename: Name of the output file (without extension)

        Returns:
            Path to the saved file
        """
        filepath = os.path.join(self.output_path, f"{filename}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False, default=str)
        return filepath


def download_youtube_info(
    url: str, output_path: str = "./downloads", download_video: bool = False
) -> dict[str, Any]:
    """Convenience function to download YouTube information.

    Args:
        url: YouTube URL to process
        output_path: Directory to save files
        download_video: Whether to download the actual video

    Returns:
        Dictionary containing all extracted information
    """
    downloader = YouTubeDownloader(output_path)
    return downloader.get_all_info(url, download_video)


if __name__ == "__main__":
    # Example usage
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing

    downloader = YouTubeDownloader("./youtube_downloads")

    # Get all information without downloading video
    print("Extracting all information...")
    info = downloader.get_all_info(url, download_video=False)

    # Save to JSON file
    if "error" not in info:
        json_path = downloader.save_info_to_json(info, f"info_{info['id']}")
        print(f"Information saved to: {json_path}")

        # Print some key information
        print(f"Title: {info.get('title')}")
        print(f"Uploader: {info.get('uploader')}")
        print(f"Duration: {info.get('duration')} seconds")
        print(f"View count: {info.get('view_count')}")
        print(f"Available subtitles: {list(info.get('subtitles', {}).keys())}")
        print(
            f"Available auto captions: {list(info.get('automatic_captions', {}).keys())}"
        )
    else:
        print(f"Error: {info['error']}")
