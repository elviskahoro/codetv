from firecrawl.firecrawl import FirecrawlApp


def firecrawl(api_key: str) -> FirecrawlApp:
    app: Any = FirecrawlApp(api_key=api_key)
    scrape_data: Dict[str, Any] = app.scrape_url(
        url,
        params={
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
    )
    markdown: str = scrape_data["markdown"]
