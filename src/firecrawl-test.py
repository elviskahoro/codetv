a  #!/usr/bin/env python3
import os
from lxml import html
import re
from pathlib import Path
from typing import Iterator, List, Set, Optional, Dict, Any
import hashlib
import time
import urllib.parse

API_KEY: str = "fc-96612b847eab48adaaa9ca9d15fe9d1c"


def extract_urls_from_html_file(
    html_file_path: str,
) -> Iterator[str]:
    if not os.path.exists(html_file_path):
        print(f"Error: File '{html_file_path}' not found.")
        return

    try:
        with open(
            html_file_path,
            "r",
            encoding="utf-8",
        ) as file:
            html_content: str = file.read()

    except Exception as e:
        print(f"Error reading file: {e}")
        return

    try:
        tree: html.HtmlElement = html.fromstring(html_content)

    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return

    href_elements: List[str] = tree.xpath("//@href")
    src_elements: List[str] = tree.xpath("//@src")
    seen_urls: Set[str] = set()
    for url in href_elements + src_elements:
        url = url.strip()
        if not url or url.startswith("#") or url.startswith("javascript:"):
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        yield url


def extract_all_urls_from_folder(
    html_file_folder: Path,
) -> List[str]:
    html_files: List[Path] = list(html_file_folder.glob("*.html"))
    if not html_files:
        print(f"No HTML files found in {html_file_folder}")
        return []

    print(f"Found {len(html_files)} HTML files to process.")
    all_urls: Set[str] = set()
    for html_file in html_files:
        url_count: int = 0
        print(f"Processing {html_file.name}...")
        for url in extract_urls_from_html_file(str(html_file)):
            all_urls.add(url)
            url_count += 1

        print(f"  - Extracted {url_count} URLs")

    return sorted(all_urls)


def create_safe_filename(url: str) -> str:
    parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(url)
    domain: str = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]

    path: str = parsed_url.path
    path = path.rstrip("/")
    path: str = re.sub(r"\.(html|htm|php|asp|aspx)$", "", path)
    path_segments: List[str] = [seg for seg in path.split("/") if seg]
    path_text: str = "-".join(path_segments)
    if path_text:
        path_text = path_text[:50]  # Limit to 50 chars
        filename: str = f"{domain}-{path_text}"

    else:
        filename: str = domain

    filename: str = re.sub(r"[^\w\-]", "_", filename)
    filename = filename.strip("_")
    url_hash: str = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{filename}-{url_hash}.md"


def download_urls_with_firecrawl(
    urls: List[str],
    output_dir: Path,
    api_key: str,
    delay: int = 1,
    max_downloads: Optional[int] = None,
) -> None:
    from firecrawl.firecrawl import FirecrawlApp
    import json

    output_dir.mkdir(parents=True, exist_ok=True)
    json_output_dir = output_dir / "json"
    json_output_dir.mkdir(parents=True, exist_ok=True)
    app: Any = FirecrawlApp(api_key=api_key)

    failed: int = 0
    successful: int = 0
    url_count: int = len(urls)
    if max_downloads and max_downloads < url_count:
        urls = urls[:max_downloads]
        print(f"Limiting to {max_downloads} URLs out of {url_count} total URLs")

    print(f"\nStarting downloads to {output_dir}...")
    for i, url in enumerate(urls, 1):
        safe_filename: str = create_safe_filename(url)
        output_file: Path = output_dir / safe_filename
        json_output_file: Path = json_output_dir / f"{safe_filename}.json"
        if output_file.exists() and json_output_file.exists():
            print(f"[{i}/{len(urls)}] Skipping existing files for: {url}")
            successful += 1
            continue

        print(f"[{i}/{len(urls)}] Downloading: {url}")
        try:
            scrape_data: Dict[str, Any] = app.scrape_url(
                url,
                params={
                    "formats": ["markdown"],
                    "onlyMainContent": True,
                },
            )
            if not output_file.exists() and "markdown" in scrape_data:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(scrape_data["markdown"])

            if not json_output_file.exists():
                with open(json_output_file, "w", encoding="utf-8") as f:
                    json.dump(
                        scrape_data,
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )

            successful += 1
            print(f"  ✓ Saved markdown and JSON for: {url}")
            if i < len(urls) and delay > 0:
                time.sleep(delay)

        except Exception as e:
            failed += 1
            print(f"  ✗ Failed to process {url}: {str(e)}")

    print("\nDownload summary:")
    print(f"  - Successfully processed: {successful}")
    print(f"  - Failed: {failed}")
    print(f"  - Total: {len(urls)}")


def main() -> None:
    cwd: Path = Path.cwd()
    output_dir: Path = cwd / "output"
    html_file_folder: Path = cwd / "data" / "bookmarks"
    unique_urls: List[str] = extract_all_urls_from_folder(html_file_folder)
    if unique_urls:
        print(f"\nFound {len(unique_urls)} unique URLs across all files:")
        for i, url in enumerate(unique_urls, 1):
            print(f"{i:06d}. {url}")

        print("\nDownloading URLs with firecrawl...")
        download_urls_with_firecrawl(
            urls=list(unique_urls[450:]),
            output_dir=output_dir,
            delay=2,
            max_downloads=None,
            api_key=API_KEY,
        )

    else:
        print("\nNo URLs found in any of the HTML files.")


if __name__ == "__main__":
    main()
