# trunk-ignore-all(ruff/PGH003,trunk/ignore-does-nothing)
from __future__ import annotations

import modal
from modal import Image
from pydantic import BaseModel
from enum import Enum

from get_youtube import YouTubeDownloader, YouTubeData

class YoutubeDataType(Enum):
    default = "default"
    transcript = "transcript"
    metadata = "metadata"

DEFAULT_YOUTUBE_VIDEO: str = (
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)
DEFAULT_TRANSCRIPT_OR_METADATA: YoutubeDataType = YoutubeDataType.transcript


class Webhook(BaseModel):
    link: str
    transcript_or_metadata: YoutubeDataType = YoutubeDataType.metadata


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
    name="postman-mcp-youtube",
    image=image,
)


def get_youtube_info(
    url: str,
    transcript_or_metadata: YoutubeDataType,
) -> YouTubeData | dict[str, Any]:
    downloader = YouTubeDownloader()
    match transcript_or_metadata:
        case YoutubeDataType.default:
            youtube_data = downloader.get_all_info(url)
        case YoutubeDataType.transcript:
            youtube_data = downloader.get_transcript(url)
        case YoutubeDataType.metadata:
            youtube_data = downloader.get_metadata_only(url)

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
) -> YouTubeData | dict[str, Any]:
    link: str = webhook.link
    transcript_or_metadata: YoutubeDataType = webhook.transcript_or_metadata
    print(link)
    print(transcript_or_metadata)
    return get_youtube_info(
        url=link,
        transcript_or_metadata=transcript_or_metadata,
    )


@app.local_entrypoint()
def local() -> None:
    print("Starting pipeline")
    youtube_data: YouTubeData | dict[str, Any] = get_youtube_info(
        url=DEFAULT_YOUTUBE_VIDEO,
        transcript_or_metadata=DEFAULT_TRANSCRIPT_OR_METADATA,
    )
    print(youtube_data)

