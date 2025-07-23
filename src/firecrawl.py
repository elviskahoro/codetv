from msvcrt import kbhit
from firecrawl.firecrawl import FirecrawlApp

API_KEY: str = "fc-96612b847eab48adaaa9ca9d15fe9d1c"


def firecrawl_markdown(
    api_key: str,
    url: str,
) -> str:
    app: Any = FirecrawlApp(api_key=api_key)
    scrape_data: Dict[str, Any] = app.scrape_url(
        url,
        params={
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
    )
    markdown: str = scrape_data["markdown"]
    print(markdown)
    return markdown
