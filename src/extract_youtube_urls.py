"""Extract YouTube URLs from markdown text."""

import re
from typing import List, Set


def extract_youtube_urls_from_markdown(markdown_text: str) -> List[str]:
    """
    Extract YouTube URLs from markdown text.

    This function finds YouTube URLs in various formats:
    - Direct links: https://www.youtube.com/watch?v=VIDEO_ID
    - Short links: https://youtu.be/VIDEO_ID
    - Embedded in markdown links: [text](youtube_url)
    - Embedded in markdown images: ![alt](youtube_url)

    Args:
        markdown_text: The markdown text to search for YouTube URLs

    Returns:
        List of unique YouTube URLs found in the markdown
    """
    if not markdown_text:
        return []

    # YouTube URL patterns
    youtube_patterns = [
        # Standard YouTube URLs
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&[\w=&-]*)?',
        r'https?://(?:www\.)?youtube\.com/embed/[\w-]+(?:\?[\w=&-]*)?',
        r'https?://(?:www\.)?youtube\.com/v/[\w-]+(?:\?[\w=&-]*)?',

        # YouTube short URLs
        r'https?://youtu\.be/[\w-]+(?:\?[\w=&-]*)?',

        # YouTube playlist URLs
        r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+(?:&[\w=&-]*)?',

        # YouTube channel URLs
        r'https?://(?:www\.)?youtube\.com/channel/[\w-]+(?:\?[\w=&-]*)?',
        r'https?://(?:www\.)?youtube\.com/c/[\w-]+(?:\?[\w=&-]*)?',
        r'https?://(?:www\.)?youtube\.com/@[\w-]+(?:\?[\w=&-]*)?',
    ]

    urls: Set[str] = set()

    # Search for URLs in the text
    for pattern in youtube_patterns:
        matches = re.findall(pattern, markdown_text, re.IGNORECASE)
        urls.update(matches)

    # Also search within markdown link syntax [text](url)
    markdown_link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    markdown_links = re.findall(markdown_link_pattern, markdown_text)

    for _, url in markdown_links:
        for pattern in youtube_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                urls.add(url)

    # Search within markdown image syntax ![alt](url)
    markdown_image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    markdown_images = re.findall(markdown_image_pattern, markdown_text)

    for _, url in markdown_images:
        for pattern in youtube_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                urls.add(url)

    return sorted(list(urls))


def extract_video_ids_from_urls(urls: List[str]) -> List[str]:
    """
    Extract YouTube video IDs from a list of YouTube URLs.

    Args:
        urls: List of YouTube URLs

    Returns:
        List of YouTube video IDs
    """
    video_ids = []

    for url in urls:
        # Extract video ID from various YouTube URL formats
        video_id = None

        # Standard watch URLs
        match = re.search(r'[?&]v=([^&]+)', url)
        if match:
            video_id = match.group(1)

        # Short URLs
        elif 'youtu.be/' in url:
            match = re.search(r'youtu\.be/([^?&]+)', url)
            if match:
                video_id = match.group(1)

        # Embed URLs
        elif '/embed/' in url:
            match = re.search(r'/embed/([^?&]+)', url)
            if match:
                video_id = match.group(1)

        # v/ URLs
        elif '/v/' in url:
            match = re.search(r'/v/([^?&]+)', url)
            if match:
                video_id = match.group(1)

        if video_id:
            video_ids.append(video_id)

    return video_ids


if __name__ == "__main__":
    # Example usage
    sample_markdown = """
    # My YouTube Playlist

    Check out this great video: [Amazing Tutorial](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

    Also watch: https://youtu.be/jNQXAC9IVRw

    Here's a playlist: https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMZOz59Oq8B7Oe8

    ![Video Thumbnail](https://www.youtube.com/watch?v=ScMzIvxBSi4)
    """

    print("Extracted URLs:")
    urls = extract_youtube_urls_from_markdown(sample_markdown)
    for url in urls:
        print(f"  {url}")

    print("\nVideo IDs:")
    video_ids = extract_video_ids_from_urls(urls)
    for vid_id in video_ids:
        print(f"  {vid_id}")

    print("\nURLs with metadata:")
    metadata = get_youtube_urls_with_metadata(sample_markdown)
    for item in metadata:
        print(f"  URL: {item['url']}")
        print(f"  Video ID: {item['video_id']}")
        print(f"  Link Text: {item['link_text']}")
        print(f"  Context: {item['context'][:100]}...")
        print()
