import io
import tempfile
from typing import Dict, Any, List, Union
from yt_dlp import YoutubeDL


def download_youtube_audio_to_memory(
    urls: Union[str, List[str]],
    audio_format: str = "mp3",
    quality: str = "192",
) -> Dict[str, Any]:
    """Download YouTube audio and keep it in memory.

    Args:
        urls: Single URL string or list of YouTube URLs
        audio_format: Audio format to convert to (default: 'mp3')
        quality: Audio quality (default: '192')

    Returns:
        Dictionary containing audio data for each video:
        {
            'video_title': {
                'data': bytes,  # Raw audio data
                'size': int,    # Size in bytes
                'title': str,   # Video title
                'url': str,     # Original URL
                'format': str   # Audio format
            },
            'error': str | None  # Error message if any
        }
    """
    # Ensure urls is a list
    if isinstance(urls, str):
        urls = [urls]

    # Store downloaded audio data
    audio_data = {}
    error_message = None

    def progress_hook(d):
        """Hook to capture download progress and data."""
        nonlocal audio_data

        if d["status"] == "finished":
            filename = d["filename"]
            info_dict = d.get("info_dict", {})
            title = info_dict.get("title", "Unknown")
            original_url = info_dict.get("original_url", "")

            # Read the file into memory
            try:
                with open(filename, "rb") as f:
                    file_data = f.read()
                    audio_data[title] = {
                        "data": file_data,
                        "size": len(file_data),
                        "title": title,
                        "url": original_url,
                        "format": audio_format,
                    }
                print(f"Loaded '{title}' into memory ({len(file_data)} bytes)")

            except Exception as e:
                print(f"Error loading file to memory: {e}")

    # Use a temporary directory for intermediate files
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": audio_format,
                        "preferredquality": quality,
                    }
                ],
                # Use temporary directory
                "outtmpl": f"{temp_dir}/%(title)s.%(ext)s",
                "ignoreerrors": True,
                "progress_hooks": [progress_hook],
                "quiet": True,  # Reduce output noise
                "no_warnings": True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                print(f"Processing {len(urls)} video(s) in memory...")
                ydl.download(urls)

                if audio_data:
                    print(f"\nProcessing completed! Audio data stored in memory:")
                    for title, data in audio_data.items():
                        print(f"- {title}: {data['size']} bytes")
                else:
                    error_message = "No audio data was successfully downloaded"

    except Exception as e:
        error_message = f"Error during processing: {e}"
        print(error_message)

    # Add error to result if present
    result = dict(audio_data)
    if error_message:
        result["error"] = error_message

    return result


def get_youtube_audio_bytes(
    url: str, audio_format: str = "mp3", quality: str = "192"
) -> Dict[str, Any]:
    """Convenience function to get audio bytes for a single YouTube video.

    Args:
        url: YouTube URL
        audio_format: Audio format (default: 'mp3')
        quality: Audio quality (default: '192')

    Returns:
        Dictionary with audio data or error:
        {
            'data': bytes | None,
            'title': str | None,
            'size': int | None,
            'error': str | None
        }
    """
    result = download_youtube_audio_to_memory(url, audio_format, quality)

    # Extract the first (and only) audio data entry
    for title, data in result.items():
        if title != "error" and isinstance(data, dict):
            return {
                "data": data.get("data"),
                "title": data.get("title"),
                "size": data.get("size"),
                "error": None,
            }

    # Return error if no data found
    return {
        "data": None,
        "title": None,
        "size": None,
        "error": result.get("error", "Unknown error occurred"),
    }


if __name__ == "__main__":
    # Example usage
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_youtube_audio_bytes(test_url)

    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(f"Successfully downloaded: {result['title']} ({result['size']} bytes)")
