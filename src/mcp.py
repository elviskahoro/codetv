# trunk-ignore-all(ruff/PGH003,trunk/ignore-does-nothing)
from __future__ import annotations

import modal
from modal import Image
from pydantic import BaseModel


class Webhook(BaseModel):
    link: str
    limit: int = 10


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
    query: str = webhook.link
    limit: int = webhook.limit
    print(query)
    print(limit)
    return "github search"


@app.local_entrypoint()
def local(
    search_query: str,
) -> None:
    print("test")

