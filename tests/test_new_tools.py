"""Tests for the new tools added to the Awesome List Agent."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from awesome_list_agent.tools.youtube_metadata_tool import YouTubeMetadataTool
from awesome_list_agent.tools.web_scraping_tool import WebScrapingTool
from awesome_list_agent.tools.content_analysis_tool import ContentAnalysisTool
from awesome_list_agent.tools.awesome_list_parser import AwesomeListParser
from awesome_list_agent.tools.markdown_youtube_extractor_tool import MarkdownYouTubeExtractorTool


class TestYouTubeMetadataTool:
    """Test the YouTube Metadata Tool."""
    
    @pytest.fixture
    def tool(self):
        return YouTubeMetadataTool()
    
    @pytest.mark.asyncio
    async def test_valid_youtube_url_validation(self, tool):
        """Test that valid YouTube URLs are accepted."""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://www.youtube.com/v/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            assert tool._is_valid_youtube_url(url), f"URL should be valid: {url}"
    
    @pytest.mark.asyncio
    async def test_invalid_url_validation(self, tool):
        """Test that invalid URLs are rejected."""
        invalid_urls = [
            "https://example.com",
            "not-a-url",
            "https://www.youtube.com/invalid",
            "ftp://youtube.com/watch?v=123"
        ]
        
        for url in invalid_urls:
            assert not tool._is_valid_youtube_url(url), f"URL should be invalid: {url}"
    
    @pytest.mark.asyncio
    async def test_video_id_extraction(self, tool):
        """Test video ID extraction from various URL formats."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ")
        ]
        
        for url, expected_id in test_cases:
            extracted_id = tool._extract_video_id(url)
            assert extracted_id == expected_id, f"Failed to extract video ID from {url}"
    
    @pytest.mark.asyncio
    async def test_execute_with_valid_url(self, tool):
        """Test tool execution with a valid YouTube URL."""
        with patch.object(tool, '_fetch_video_metadata', new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = {
                "video_id": "test123",
                "title": "Test Video",
                "description": "Test description",
                "duration": "PT5M30S",
                "duration_seconds": 330,
                "view_count": 1000,
                "like_count": 100,
                "comment_count": 50,
                "upload_date": "2024-01-01T00:00:00Z",
                "channel_name": "Test Channel",
                "channel_id": "UC123",
                "tags": ["test", "video"],
                "category": "Education",
                "thumbnail_url": "https://example.com/thumb.jpg",
                "metadata_summary": "Test summary"
            }
            
            result = await tool.execute("https://www.youtube.com/watch?v=test123")
            
            assert isinstance(result, dict)
            assert "error" not in result
            assert result["video_id"] == "test123"
            assert result["title"] == "Test Video"
            assert "extraction_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_url(self, tool):
        """Test tool execution with an invalid URL."""
        result = await tool.execute("https://example.com")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid YouTube URL format" in result["error"]


class TestWebScrapingTool:
    """Test the Web Scraping Tool."""
    
    @pytest.fixture
    def tool(self):
        return WebScrapingTool()
    
    @pytest.mark.asyncio
    async def test_extract_text_content(self, tool):
        """Test text content extraction from HTML."""
        html_content = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Main Title</h1>
                <p>This is a paragraph with <strong>bold text</strong>.</p>
                <script>console.log('test');</script>
                <style>body { color: red; }</style>
                <p>Another paragraph.</p>
            </body>
        </html>
        """
        
        soup = tool._create_soup(html_content)
        text_content = tool._extract_text_content(soup)
        
        assert "Main Title" in text_content
        assert "This is a paragraph with bold text" in text_content
        assert "Another paragraph" in text_content
        assert "console.log" not in text_content  # Script should be removed
        assert "color: red" not in text_content   # Style should be removed
    
    @pytest.mark.asyncio
    async def test_extract_links(self, tool):
        """Test link extraction from HTML."""
        html_content = """
        <html>
            <body>
                <a href="https://example.com">Example Link</a>
                <a href="https://test.com" title="Test Link">Test</a>
                <a href="javascript:void(0)">JavaScript Link</a>
                <a href="">Empty Link</a>
            </body>
        </html>
        """
        
        soup = tool._create_soup(html_content)
        links = tool._extract_links(soup, max_links=10)
        
        assert len(links) == 2  # Should exclude JS and empty links
        assert links[0]["url"] == "https://example.com"
        assert links[0]["text"] == "Example Link"
        assert links[1]["url"] == "https://test.com"
        assert links[1]["title"] == "Test Link"
    
    @pytest.mark.asyncio
    async def test_extract_images(self, tool):
        """Test image extraction from HTML."""
        html_content = """
        <html>
            <body>
                <img src="https://example.com/image1.jpg" alt="Image 1" title="Title 1">
                <img src="https://example.com/image2.png" alt="Image 2">
                <img src="" alt="Empty src">
            </body>
        </html>
        """
        
        soup = tool._create_soup(html_content)
        images = tool._extract_images(soup, max_images=10)
        
        assert len(images) == 2  # Should exclude empty src
        assert images[0]["src"] == "https://example.com/image1.jpg"
        assert images[0]["alt"] == "Image 1"
        assert images[0]["title"] == "Title 1"
        assert images[1]["src"] == "https://example.com/image2.png"
        assert images[1]["alt"] == "Image 2"
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self, tool):
        """Test metadata extraction from HTML."""
        html_content = """
        <html>
            <head>
                <meta name="description" content="Test description">
                <meta name="keywords" content="test, keywords">
                <meta property="og:title" content="OG Title">
                <meta name="author" content="Test Author">
            </head>
            <body>Content</body>
        </html>
        """
        
        soup = tool._create_soup(html_content)
        metadata = tool._extract_metadata(soup)
        
        assert metadata["description"] == "Test description"
        assert metadata["keywords"] == "test, keywords"
        assert metadata["og:title"] == "OG Title"
        assert metadata["author"] == "Test Author"
    
    def _create_soup(self, html_content):
        """Helper method to create BeautifulSoup object."""
        from bs4 import BeautifulSoup
        return BeautifulSoup(html_content, 'html.parser')


class TestContentAnalysisTool:
    """Test the Content Analysis Tool."""
    
    @pytest.fixture
    def tool(self):
        return ContentAnalysisTool()
    
    @pytest.mark.asyncio
    async def test_calculate_basic_stats(self, tool):
        """Test basic text statistics calculation."""
        text = "This is a test sentence. This is another sentence. And a third one."
        
        stats = tool._calculate_basic_stats(text)
        
        assert stats["text_length"] == len(text)
        assert stats["word_count"] == 12
        assert stats["sentence_count"] == 3
        assert stats["paragraph_count"] == 1
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, tool):
        """Test sentiment analysis."""
        positive_text = "This is amazing and wonderful. I love it!"
        negative_text = "This is terrible and awful. I hate it!"
        neutral_text = "This is a neutral statement."
        
        pos_result = tool._analyze_sentiment(positive_text)
        neg_result = tool._analyze_sentiment(negative_text)
        neutral_result = tool._analyze_sentiment(neutral_text)
        
        assert pos_result["overall"] == "positive"
        assert pos_result["score"] > 0
        assert neg_result["overall"] == "negative"
        assert neg_result["score"] < 0
        assert neutral_result["overall"] == "neutral"
        assert abs(neutral_result["score"]) < 0.05
    
    @pytest.mark.asyncio
    async def test_extract_topics(self, tool):
        """Test topic extraction."""
        text = "Python programming language is great for data science and web development. Python has many libraries."
        
        topics = tool._extract_topics(text, max_topics=5)
        
        assert len(topics) > 0
        assert any(topic["topic"] == "python" for topic in topics)
        assert all("frequency" in topic for topic in topics)
        assert all("relevance_score" in topic for topic in topics)
    
    @pytest.mark.asyncio
    async def test_extract_entities(self, tool):
        """Test entity extraction."""
        text = "Google is a company. John Smith works at Microsoft. Visit https://example.com"
        
        entities = tool._extract_entities(text)
        
        assert len(entities) > 0
        # Should find capitalized words as entities
        entity_texts = [e["entity"] for e in entities]
        assert "Google" in entity_texts or any("Google" in e["entity"] for e in entities)
        assert "Microsoft" in entity_texts or any("Microsoft" in e["entity"] for e in entities)
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, tool):
        """Test keyword extraction."""
        text = "Python programming language is great for data science and web development. Python has many libraries."
        
        keywords = tool._extract_keywords(text, max_keywords=5)
        
        assert len(keywords) > 0
        assert all("keyword" in kw for kw in keywords)
        assert all("frequency" in kw for kw in keywords)
        assert all("tf_idf_score" in kw for kw in keywords)
    
    @pytest.mark.asyncio
    async def test_calculate_readability(self, tool):
        """Test readability metrics calculation."""
        text = "This is a simple sentence. It has basic words. The readability should be good."
        
        readability = tool._calculate_readability(text)
        
        assert "flesch_reading_ease" in readability
        assert "flesch_kincaid_grade" in readability
        assert "gunning_fog_index" in readability
        assert "smog_index" in readability
        assert "coleman_liau_index" in readability
        assert "automated_readability_index" in readability
        
        # All scores should be non-negative
        for score in readability.values():
            assert score >= 0
    
    @pytest.mark.asyncio
    async def test_analyze_content_structure(self, tool):
        """Test content structure analysis."""
        text = "# Heading\n\nThis is a paragraph with [a link](https://example.com).\n\n- List item 1\n- List item 2"
        
        structure = tool._analyze_content_structure(text)
        
        assert "has_headings" in structure
        assert "has_lists" in structure
        assert "has_links" in structure
        assert "has_code_blocks" in structure
        assert "average_sentence_length" in structure
        assert "average_word_length" in structure
    
    @pytest.mark.asyncio
    async def test_execute_comprehensive_analysis(self, tool):
        """Test comprehensive content analysis execution."""
        text = "Python is an amazing programming language. It's great for beginners and experts alike."
        
        result = await tool.execute(
            text,
            analyze_sentiment=True,
            extract_topics=True,
            extract_entities=True,
            analyze_readability=True,
            extract_keywords=True
        )
        
        assert isinstance(result, dict)
        assert "error" not in result
        assert "text_length" in result
        assert "word_count" in result
        assert "sentiment" in result
        assert "topics" in result
        assert "entities" in result
        assert "keywords" in result
        assert "readability" in result
        assert "content_structure" in result
        assert "analysis_summary" in result
        assert "analysis_time_ms" in result


class TestAwesomeListParser:
    """Test the Awesome List Parser Tool."""
    
    @pytest.fixture
    def tool(self):
        return AwesomeListParser()
    
    @pytest.mark.asyncio
    async def test_extract_topic_from_title(self, tool):
        """Test topic extraction from HTML title."""
        content = '<title>Awesome Python - A curated list of Python resources</title>'
        
        topic = tool._extract_topic(content, "https://example.com")
        
        assert "Python" in topic
        assert "Awesome" not in topic  # Should be removed
    
    @pytest.mark.asyncio
    async def test_extract_topic_from_h1(self, tool):
        """Test topic extraction from H1 tag."""
        content = '<h1>Awesome JavaScript Libraries</h1>'
        
        topic = tool._extract_topic(content, "https://example.com")
        
        assert "JavaScript" in topic
        assert "Libraries" in topic
    
    @pytest.mark.asyncio
    async def test_extract_topic_from_markdown(self, tool):
        """Test topic extraction from Markdown heading."""
        content = '# Awesome Machine Learning\n\nThis is a list of ML resources.'
        
        topic = tool._extract_topic(content, "https://example.com")
        
        assert "Machine Learning" in topic
    
    @pytest.mark.asyncio
    async def test_extract_categories(self, tool):
        """Test category extraction."""
        content = """
        # Awesome Python
        
        ## Web Frameworks
        - Django
        - Flask
        
        ## Data Science
        - Pandas
        - NumPy
        
        ## Contributing
        Please contribute!
        """
        
        categories = tool._extract_categories(content)
        
        assert "Web Frameworks" in categories
        assert "Data Science" in categories
        assert "Contributing" not in categories  # Should be filtered out
    
    @pytest.mark.asyncio
    async def test_count_items(self, tool):
        """Test item counting."""
        content = """
        - [Item 1](https://example1.com)
        - [Item 2](https://example2.com)
        - [Item 3](https://example3.com)
        """
        
        count = tool._count_items(content)
        
        assert count >= 3  # Should find at least 3 items
    
    @pytest.mark.asyncio
    async def test_detect_language(self, tool):
        """Test language detection."""
        # Test Python detection
        python_content = "Python Django Flask pandas numpy"
        python_url = "https://github.com/awesome-python"
        
        language = tool._detect_language(python_content, python_url)
        
        assert "Python" in language
        
        # Test JavaScript detection
        js_content = "JavaScript React Vue Angular npm"
        js_url = "https://github.com/awesome-javascript"
        
        language = tool._detect_language(js_content, js_url)
        
        assert "JavaScript" in language or "Typescript" in language


class TestMarkdownYouTubeExtractorTool:
    """Test the Markdown YouTube Extractor Tool."""
    
    @pytest.fixture
    def tool(self):
        return MarkdownYouTubeExtractorTool()
    
    @pytest.mark.asyncio
    async def test_extract_youtube_urls_from_markdown(self, tool):
        """Test YouTube URL extraction from markdown content."""
        markdown_content = """
        # My Awesome List
        
        Check out this great video: [Amazing Tutorial](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
        
        Also watch: https://youtu.be/jNQXAC9IVRw
        
        Here's a playlist: https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMZOz59Oq8B7Oe8
        
        ![Video Thumbnail](https://www.youtube.com/watch?v=ScMzIvxBSi4)
        """
        
        urls = tool._extract_youtube_urls_from_markdown(markdown_content, max_urls=10)
        
        assert len(urls) >= 3  # Should find at least 3 YouTube URLs
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in urls
        assert "https://youtu.be/jNQXAC9IVRw" in urls
        assert "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMZOz59Oq8B7Oe8" in urls
    
    @pytest.mark.asyncio
    async def test_extract_video_ids_from_urls(self, tool):
        """Test video ID extraction from YouTube URLs."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/jNQXAC9IVRw",
            "https://www.youtube.com/embed/ScMzIvxBSi4",
            "https://www.youtube.com/v/anotherVideoId"
        ]
        
        video_ids = tool._extract_video_ids_from_urls(urls)
        
        assert "dQw4w9WgXcQ" in video_ids
        assert "jNQXAC9IVRw" in video_ids
        assert "ScMzIvxBSi4" in video_ids
        assert "anotherVideoId" in video_ids
        assert len(video_ids) == 4
    
    @pytest.mark.asyncio
    async def test_extract_markdown_from_html(self, tool):
        """Test HTML to markdown conversion."""
        html_content = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <h2>Subtitle</h2>
            <p>This is a paragraph with a <a href="https://www.youtube.com/watch?v=test123">YouTube link</a>.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </body>
        </html>
        """
        
        markdown = tool._extract_markdown_from_html(html_content)
        
        assert "# Main Title" in markdown
        assert "## Subtitle" in markdown
        assert "YouTube link" in markdown
        assert "- Item 1" in markdown
        assert "- Item 2" in markdown
    
    @pytest.mark.asyncio
    async def test_generate_url_metadata(self, tool):
        """Test URL metadata generation."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMZOz59Oq8B7Oe8"
        ]
        markdown_content = """
        Check out this [great video](https://www.youtube.com/watch?v=dQw4w9WgXcQ) and this playlist.
        """
        
        metadata = tool._generate_url_metadata(urls, markdown_content)
        
        assert len(metadata) == 2
        assert metadata[0]["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert metadata[0]["video_id"] == "dQw4w9WgXcQ"
        assert metadata[0]["url_type"] == "video"
        assert metadata[1]["url_type"] == "playlist"
    
    @pytest.mark.asyncio
    async def test_calculate_statistics(self, tool):
        """Test statistics calculation."""
        urls = [
            "https://www.youtube.com/watch?v=video1",
            "https://www.youtube.com/watch?v=video2",
            "https://www.youtube.com/playlist?list=playlist1"
        ]
        video_ids = ["video1", "video2"]
        markdown_content = "# Title\n\nSome content with [links](https://example.com)."
        
        stats = tool._calculate_statistics(urls, video_ids, markdown_content)
        
        assert stats["total_urls_found"] == 3
        assert stats["unique_video_ids"] == 2
        assert stats["url_types"]["video"] == 2
        assert stats["url_types"]["playlist"] == 1
        assert stats["content_analysis"]["has_headings"] == True
        assert stats["content_analysis"]["has_markdown_links"] == True
    
    @pytest.mark.asyncio
    async def test_execute_with_mock_scraping(self, tool):
        """Test tool execution with mocked web scraping."""
        with patch.object(tool, '_scrape_markdown_content', new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = """
            # Test Content
            
            Watch this video: https://www.youtube.com/watch?v=test123
            
            And this one: [Another Video](https://youtu.be/another456)
            """
            
            result = await tool.execute(
                url="https://example.com",
                extract_video_ids=True,
                include_metadata=True
            )
            
            assert isinstance(result, dict)
            assert "error" not in result
            assert result["source_url"] == "https://example.com"
            assert len(result["youtube_urls"]) >= 2
            assert len(result["video_ids"]) >= 2
            assert len(result["url_metadata"]) >= 2
            assert "statistics" in result
            assert "extraction_summary" in result
            assert "extraction_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_invalid_url(self, tool):
        """Test tool execution with an invalid URL."""
        result = await tool.execute("not-a-url")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "Invalid URL format" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 