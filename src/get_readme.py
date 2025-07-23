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

if __name__ == "__main__":
    markdown: str = firecrawl_markdown(
        url="https://github.com/josephmisiti/awesome-machine-learning",
    )
    urls: List[str] = extract_youtube_urls_from_markdown(markdown)
    print(urls)
