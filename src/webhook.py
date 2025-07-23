# trunk-ignore-all(ruff/PGH003,trunk/ignore-does-nothing)
from __future__ import annotations

import modal
from modal import Image
from pydantic import BaseModel
from enum import Enum
import yt_dlp
from yt_dlp import YoutubeDL

from get_youtube import YouTubeDownloader

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
) -> dict[str, Any]:
    downloader = YouTubeDownloader()
    info = downloader.get_all_info(url)
    if "error" not in info:
        # Convert to JSON string for webhook response
        json_output = downloader.to_json_string(info)
        print(f"JSON output length: {len(json_output)} characters")
        print(json_output)

        # Print some key information
        # print(f"Title: {info.get('title')}")
        # print(f"Uploader: {info.get('uploader')}")
        # print(f"Duration: {info.get('duration')} seconds")
        # print(f"View count: {info.get('view_count')}")
        # print(f"Available subtitles: {list(info.get('subtitles', {}).keys())}")
        # print(
        #     f"Available auto captions: {list(info.get('automatic_captions', {}).keys())}"
        # )
        # print(f"Subtitle content keys: {list(info.get('subtitle_content', {}).keys())}")
    else:
        print(f"Error: {info['error']}")

    return {}


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
) -> str:
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
    return get_youtube_info(
        url=DEFAULT_YOUTUBE_VIDEO,
    )
