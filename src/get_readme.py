from firecrawl.firecrawl import FirecrawlApp


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
    print(markdown)
    return markdown

if __name__ == "__main__":
    firecrawl_markdown(
        url="https://github.com/josephmisiti/awesome-machine-learning",
    )
