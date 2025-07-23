from __future__ import annotations

import reflex as rx

from app.pages.index import page

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        scaling="100%",
    )
)

app.add_page(
    component=page,
    route="/",
    title="CodeTV - AI Learning Path Generator",
    description="Transform Awesome Lists into personalized learning paths with AI",
    image="favicon",
    on_load=None,
    meta=[
        {
            "author": "CodeTV Team",
            "viewport": "width=device-width, initial-scale=1",
        },
    ],
)
