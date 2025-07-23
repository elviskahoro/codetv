# trunk-ignore-all(ruff/PGH003,trunk/ignore-does-nothing)
from __future__ import annotations

import modal
from modal import Image
from pydantic import BaseModel, RootModel
from enum import Enum

from get_youtube import YouTubeDownloader, YouTubeData
from get_readme import firecrawl_markdown

DEFAULT_MARKDOWN_URL: str = (
    "https://github.com/josephmisiti/awesome-machine-learning"
)

from firecrawl.firecrawl import FirecrawlApp
from src.extract_youtube_urls import extract_youtube_urls_from_markdown


def firecrawl_markdown(
    url: str,
) -> str:
    api_key: str = "fc-95ddf7f5c64f4e1e814f03567183dc16"
    app: Any = FirecrawlApp(api_key=api_key)
    scrape_data = app.scrape_url(
        url,
        formats=["markdown"],
    )
    markdown: str = scrape_data.markdown
    return markdown


class WebhookInput(BaseModel):
    link: str

class WebhookOutput(RootModel):
    root: list[str]


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
    name="postman-mcp-get_readme",
    image=image,
)


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
    webhook: WebhookInput,
) -> YouTubeData:
    print("Starting pipeline")
    markdown: str = firecrawl_markdown(
        url=webhook.link,
    )
    urls: list[str] = extract_youtube_urls_from_markdown(markdown)
    print(urls)
    return WebhookOutput(root=urls)


@app.local_entrypoint()
def local() -> None:
    print("Starting pipeline")
    markdown: str = firecrawl_markdown(
        url=DEFAULT_MARKDOWN_URL,
    )
    urls: list[str] = extract_youtube_urls_from_markdown(markdown)
    print(urls)
    return WebhookOutput(root=urls)