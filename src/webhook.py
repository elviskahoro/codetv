# trunk-ignore-all(ruff/PGH003,trunk/ignore-does-nothing)
from __future__ import annotations

import modal
from modal import Image
from pydantic import BaseModel
from enum import Enum


class TranscriptOrMetadata(Enum):
    transcript = "transcript"
    metadata = "metadata"


class Webhook(BaseModel):
    link: str
    transcript_or_metadata: TranscriptOrMetadata = TranscriptOrMetadata.metadata


image: Image = modal.Image.debian_slim().pip_install(
    "fastapi[standard]",
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
    return link


@app.local_entrypoint()
def local(
    search_query: str,
) -> None:
    print("test")
