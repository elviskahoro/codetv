# trunk-ignore-all(ruff/PGH003,trunk/ignore-does-nothing)
from __future__ import annotations

import modal
from modal import Image
from pydantic import BaseModel
from enum import Enum
import yt_dlp
from yt_dlp import YoutubeDL

from get_youtube import YouTubeDownloader, YouTubeData

DEFAULT_YOUTUBE_VIDEO: str = (
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
)



class TranscriptOrMetadata(Enum):
    transcript = "transcript"
    metadata = "metadata"


class Webhook(BaseModel):
    link: str
    transcript_or_metadata: TranscriptOrMetadata = TranscriptOrMetadata.metadata


image: Image = modal.Image.debian_slim().pip_install(
    "fastapi[standard]",
    "yt-dlp",
    "firecrawl-py",
)
image.add_local_python_source(
    *[
        "src",
    ],
)
app = modal.App(
    name="postman-mcp",
    image=image,
)


def get_youtube_info(
    url: str,
) -> YouTubeData:
    downloader = YouTubeDownloader()
    youtube_data = downloader.get_all_info(url)
    
    if youtube_data.error is None:
        # Convert to JSON string for webhook response
        json_output = downloader.to_json_string(youtube_data)
        print(f"JSON output length: {len(json_output)} characters")
        print(json_output)

        # Print some key information
        print(f"Title: {youtube_data.title}")
        print(f"Uploader: {youtube_data.uploader}")
        print(f"Duration: {youtube_data.duration} seconds")
        print(f"View count: {youtube_data.view_count}")
        print(f"Available subtitles: {list(youtube_data.subtitles.keys()) if youtube_data.subtitles else []}")
        print(f"Available auto captions: {list(youtube_data.automatic_captions.keys()) if youtube_data.automatic_captions else []}")
        print(f"Subtitle content keys: {list(youtube_data.subtitle_content.keys()) if youtube_data.subtitle_content else []}")
    else:
        print(f"Error: {youtube_data.error}")

    return youtube_data


@app.function(
    region="us-east4",
    allow_concurrent_inputs=1000,
    enable_memory_snapshot=False,
)
@modal.fastapi_endpoint(
    method="POST",
    docs=True,
)
def web(
    webhook: Webhook,
) -> YouTubeData:
    link: str = webhook.link
    transcript_or_metadata: TranscriptOrMetadata = webhook.transcript_or_metadata
    print(link)
    print(transcript_or_metadata)
    return get_youtube_info(
        url=link,
    )


@app.local_entrypoint()
def local() -> None:
    print("test")
    youtube_data = get_youtube_info(
        url=DEFAULT_YOUTUBE_VIDEO,
    )
    print(f"Successfully extracted data for: {youtube_data.title}")
