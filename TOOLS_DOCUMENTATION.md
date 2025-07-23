# Awesome List Agent Tools Documentation

This document provides comprehensive documentation for all tools available in the Awesome List Agent, including the newly added tools with Galileo observability integration.

## Table of Contents

1. [Overview](#overview)
2. [Tool Architecture](#tool-architecture)
3. [Awesome List Parser Tool](#awesome-list-parser-tool)
4. [YouTube Metadata Tool](#youtube-metadata-tool)
5. [Web Scraping Tool](#web-scraping-tool)
6. [Content Analysis Tool](#content-analysis-tool)
7. [Galileo Observability](#galileo-observability)
8. [Usage Examples](#usage-examples)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Overview

The Awesome List Agent now includes four powerful tools that work together to provide comprehensive content analysis and metadata extraction capabilities:

- **Awesome List Parser**: Extracts metadata from awesome list repositories
- **YouTube Metadata Tool**: Extracts comprehensive metadata from YouTube videos
- **Web Scraping Tool**: Scrapes and parses web content with structured extraction
- **Content Analysis Tool**: Analyzes text content for insights, sentiment, and readability

All tools include:
- ✅ Galileo observability integration
- ✅ Comprehensive error handling
- ✅ Performance timing metrics
- ✅ Detailed logging
- ✅ Type-safe interfaces
- ✅ Extensive test coverage

## Tool Architecture

### Base Tool Structure

All tools inherit from `BaseTool` and follow a consistent pattern:

```python
class ToolName(BaseTool):
    """Tool description."""
    
    metadata = ToolNameMetadata
    
    def __init__(self):
        self.logger = logging.getLogger("awesome_list_agent.ToolName")
    
    async def execute(self, **inputs) -> Dict[str, Any]:
        """Execute the tool with given inputs."""
        # Implementation
        pass
```

### Tool Registration

Tools are automatically registered in the `AwesomeListAgent` constructor:

```python
# Register YouTube metadata tool
self.youtube_tool = YouTubeMetadataTool()
self.tool_registry.register(
    metadata=YouTubeMetadataTool.get_metadata(),
    implementation=YouTubeMetadataTool
)
```

## Awesome List Parser Tool

### Purpose
Extracts comprehensive metadata from awesome list repositories hosted on GitHub or other platforms.

### Features
- **Topic Detection**: Identifies the main subject of the awesome list
- **Category Extraction**: Finds all major categories/sections
- **Item Counting**: Estimates the number of curated resources
- **Language Detection**: Identifies the primary programming language
- **Context Summary**: Generates a natural language summary

### Input Schema
```json
{
  "url": "string (required) - The URL of the awesome list to parse"
}
```

### Output Schema
```json
{
  "topic": "string - The main topic/subject of the list",
  "description": "string - Description of what the list is about",
  "categories": ["string"] - Main categories found in the list",
  "total_items": "integer - Approximate number of items",
  "language": "string - Primary programming language if applicable",
  "context_summary": "string - Brief summary of the list's purpose"
}
```

### Example Usage
```python
# Create agent
agent = await AwesomeListAgentFactory.create_agent()

# Parse an awesome list
result = await agent.parser.execute("https://github.com/sindresorhus/awesome")

if "error" not in result:
    print(f"Topic: {result['topic']}")
    print(f"Items: {result['total_items']}")
    print(f"Categories: {len(result['categories'])}")
```

## YouTube Metadata Tool

### Purpose
Extracts comprehensive metadata from YouTube video URLs including engagement metrics, content information, and channel details.

### Features
- **Video ID Extraction**: Supports multiple YouTube URL formats
- **Engagement Metrics**: Views, likes, comments, upload date
- **Content Analysis**: Title, description, duration, tags
- **Channel Information**: Channel name, ID, category
- **Comment Extraction**: Optional comment analysis
- **Thumbnail URLs**: High-quality thumbnail links

### Input Schema
```json
{
  "url": "string (required) - YouTube video URL",
  "extract_comments": "boolean (optional) - Whether to extract comments"
}
```

### Output Schema
```json
{
  "video_id": "string - YouTube video ID",
  "title": "string - Video title",
  "description": "string - Video description",
  "duration": "string - Duration in ISO 8601 format",
  "duration_seconds": "integer - Duration in seconds",
  "view_count": "integer - Number of views",
  "like_count": "integer - Number of likes",
  "comment_count": "integer - Number of comments",
  "upload_date": "string - Upload date in ISO format",
  "channel_name": "string - Channel name",
  "channel_id": "string - Channel ID",
  "tags": ["string"] - Video tags",
  "category": "string - Video category",
  "thumbnail_url": "string - High quality thumbnail URL",
  "comments": ["object"] - Top comments (if requested)",
  "metadata_summary": "string - Brief summary of the video"
}
```

### Supported URL Formats
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

### Example Usage
```python
# Extract metadata from YouTube video
result = await agent.youtube_tool.execute(
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    extract_comments=True
)

if "error" not in result:
    print(f"Title: {result['title']}")
    print(f"Duration: {result['duration']}")
    print(f"Views: {result['view_count']:,}")
    print(f"Channel: {result['channel_name']}")
```

## Web Scraping Tool

### Purpose
Scrapes web content from URLs and extracts structured information including text, links, images, and metadata.

### Features
- **Content Extraction**: Clean text extraction with HTML parsing
- **Link Discovery**: Extracts all links with text and titles
- **Image Analysis**: Finds images with alt text and titles
- **Metadata Extraction**: Extracts meta tags and page information
- **Configurable Limits**: Control the number of links/images extracted
- **Timeout Handling**: Configurable request timeouts

### Input Schema
```json
{
  "url": "string (required) - The URL to scrape",
  "extract_text": "boolean (optional) - Extract text content",
  "extract_links": "boolean (optional) - Extract links",
  "extract_images": "boolean (optional) - Extract images",
  "extract_metadata": "boolean (optional) - Extract meta tags",
  "max_links": "integer (optional) - Maximum links to extract",
  "max_images": "integer (optional) - Maximum images to extract",
  "timeout": "integer (optional) - Request timeout in seconds"
}
```

### Output Schema
```json
{
  "url": "string - The URL that was scraped",
  "title": "string - Page title",
  "text_content": "string - Extracted text content",
  "text_summary": "string - Brief summary of text content",
  "links": [
    {
      "url": "string - Link URL",
      "text": "string - Link text",
      "title": "string - Link title"
    }
  ],
  "images": [
    {
      "src": "string - Image source URL",
      "alt": "string - Alt text",
      "title": "string - Image title"
    }
  ],
  "metadata": "object - Page metadata (meta tags)",
  "content_type": "string - Content type of the page",
  "content_length": "integer - Length of content in characters",
  "scraping_summary": "string - Summary of what was extracted"
}
```

### Example Usage
```python
# Scrape a webpage
result = await agent.web_scraping_tool.execute(
    "https://example.com",
    extract_text=True,
    extract_links=True,
    extract_images=True,
    max_links=20,
    max_images=10
)

if "error" not in result:
    print(f"Title: {result['title']}")
    print(f"Text length: {result['content_length']:,} characters")
    print(f"Links found: {len(result['links'])}")
    print(f"Images found: {len(result['images'])}")
```

## Content Analysis Tool

### Purpose
Analyzes text content to extract insights including sentiment, key topics, entities, readability metrics, and content structure.

### Features
- **Sentiment Analysis**: Positive/negative/neutral sentiment with scoring
- **Topic Extraction**: Identifies key topics with frequency analysis
- **Entity Recognition**: Extracts named entities (organizations, URLs, etc.)
- **Keyword Analysis**: TF-IDF based keyword extraction
- **Readability Metrics**: Multiple readability scores (Flesch, Gunning Fog, etc.)
- **Content Structure**: Analyzes document structure and formatting

### Input Schema
```json
{
  "text": "string (required) - The text content to analyze",
  "analyze_sentiment": "boolean (optional) - Perform sentiment analysis",
  "extract_topics": "boolean (optional) - Extract key topics",
  "extract_entities": "boolean (optional) - Extract named entities",
  "analyze_readability": "boolean (optional) - Calculate readability metrics",
  "extract_keywords": "boolean (optional) - Extract keywords",
  "max_topics": "integer (optional) - Maximum topics to extract",
  "max_keywords": "integer (optional) - Maximum keywords to extract"
}
```

### Output Schema
```json
{
  "text_length": "integer - Length of analyzed text",
  "word_count": "integer - Number of words",
  "sentence_count": "integer - Number of sentences",
  "paragraph_count": "integer - Number of paragraphs",
  "sentiment": {
    "overall": "string - Overall sentiment (positive/negative/neutral)",
    "score": "number - Sentiment score (-1 to 1)",
    "positive_words": ["string"] - Positive words found",
    "negative_words": ["string"] - Negative words found"
  },
  "topics": [
    {
      "topic": "string - Topic name",
      "frequency": "integer - Frequency count",
      "relevance_score": "number - Relevance score"
    }
  ],
  "entities": [
    {
      "entity": "string - Entity name",
      "type": "string - Entity type",
      "frequency": "integer - Frequency count"
    }
  ],
  "keywords": [
    {
      "keyword": "string - Keyword",
      "frequency": "integer - Frequency count",
      "tf_idf_score": "number - TF-IDF score"
    }
  ],
  "readability": {
    "flesch_reading_ease": "number - Flesch Reading Ease score",
    "flesch_kincaid_grade": "number - Flesch-Kincaid Grade Level",
    "gunning_fog_index": "number - Gunning Fog Index",
    "smog_index": "number - SMOG Index",
    "coleman_liau_index": "number - Coleman-Liau Index",
    "automated_readability_index": "number - ARI score"
  },
  "content_structure": {
    "has_headings": "boolean - Contains headings",
    "has_lists": "boolean - Contains lists",
    "has_links": "boolean - Contains links",
    "has_code_blocks": "boolean - Contains code blocks",
    "average_sentence_length": "number - Average words per sentence",
    "average_word_length": "number - Average characters per word"
  },
  "analysis_summary": "string - Brief summary of analysis"
}
```

### Readability Metrics Explained

- **Flesch Reading Ease**: 0-100 scale (higher = easier to read)
- **Flesch-Kincaid Grade**: US grade level (e.g., 8.0 = 8th grade)
- **Gunning Fog Index**: Years of education needed (lower = easier)
- **SMOG Index**: Years of education needed for 100% comprehension
- **Coleman-Liau Index**: US grade level based on characters and sentences
- **Automated Readability Index**: US grade level based on characters and words

### Example Usage
```python
# Analyze text content
text = "Python is an amazing programming language. It's great for beginners and experts alike."

result = await agent.content_analysis_tool.execute(
    text,
    analyze_sentiment=True,
    extract_topics=True,
    extract_entities=True,
    analyze_readability=True,
    extract_keywords=True
)

if "error" not in result:
    print(f"Sentiment: {result['sentiment']['overall']}")
    print(f"Top topics: {[t['topic'] for t in result['topics'][:3]]}")
    print(f"Readability grade: {result['readability']['flesch_kincaid_grade']:.1f}")
```

## Galileo Observability

All tools include comprehensive Galileo observability integration for monitoring and debugging.

### Features
- **Execution Logging**: All tool executions are logged with timing
- **Error Tracking**: Errors are captured with full context
- **Performance Metrics**: Execution time and resource usage
- **Input/Output Logging**: Tool inputs and outputs are recorded
- **Span Tracking**: Each tool execution creates a span for tracing

### Configuration

Enable Galileo by setting environment variables:

```bash
export GALILEO_ENABLED=true
export GALILEO_API_KEY=your_api_key_here
export GALILEO_PROJECT=your_project_name
```

### Logging Levels

Tools use different logging levels:
- **INFO**: Major operations and results
- **DEBUG**: Detailed execution steps and timing
- **ERROR**: Errors and exceptions with full context

### Example Galileo Integration

```python
# Galileo logging is automatically included in all tools
async def execute(self, url: str) -> Dict[str, Any]:
    start_time = time.perf_counter_ns()
    
    try:
        self.logger.info(f"Starting tool execution for: {url}")
        # ... tool logic ...
        
        duration_ns = time.perf_counter_ns() - start_time
        self.logger.info(f"Tool execution completed in {duration_ns / 1_000_000:.2f}ms")
        
        result['execution_time_ms'] = duration_ns / 1_000_000
        return result
        
    except Exception as e:
        self.logger.error(f"Tool execution failed: {str(e)}", exc_info=True)
        return ToolError(error=str(e))
```

## Usage Examples

### Basic Tool Usage

```python
from awesome_list_agent.factory import AwesomeListAgentFactory

async def main():
    # Create agent with Galileo enabled
    agent = await AwesomeListAgentFactory.create_agent(
        verbosity="high",
        enable_galileo=True
    )
    
    # Use individual tools
    parser_result = await agent.parser.execute("https://github.com/sindresorhus/awesome")
    youtube_result = await agent.youtube_tool.execute("https://www.youtube.com/watch?v=example")
    scraping_result = await agent.web_scraping_tool.execute("https://example.com")
    analysis_result = await agent.content_analysis_tool.execute("Sample text content")
    
    # Process results
    for result in [parser_result, youtube_result, scraping_result, analysis_result]:
        if "error" not in result:
            print("✅ Success")
        else:
            print(f"❌ Error: {result['error']}")

asyncio.run(main())
```

### Integrated Workflow

```python
async def integrated_analysis(url: str):
    """Perform comprehensive analysis using all tools."""
    agent = await AwesomeListAgentFactory.create_agent()
    
    # Step 1: Parse if it's an awesome list
    if "awesome" in url.lower():
        parser_result = await agent.parser.execute(url)
        print(f"Awesome List Topic: {parser_result.get('topic', 'Unknown')}")
    
    # Step 2: Scrape the content
    scraping_result = await agent.web_scraping_tool.execute(url)
    text_content = scraping_result.get('text_content', '')
    
    # Step 3: Analyze the content
    if text_content:
        analysis_result = await agent.content_analysis_tool.execute(text_content)
        print(f"Content Sentiment: {analysis_result.get('sentiment', {}).get('overall', 'Unknown')}")
    
    # Step 4: Extract YouTube metadata if YouTube links found
    links = scraping_result.get('links', [])
    youtube_links = [link for link in links if 'youtube.com' in link.get('url', '')]
    
    for link in youtube_links[:3]:  # Process first 3 YouTube links
        youtube_result = await agent.youtube_tool.execute(link['url'])
        if "error" not in youtube_result:
            print(f"YouTube Video: {youtube_result.get('title', 'Unknown')}")
```

### Running the Comprehensive Example

```bash
# Run the comprehensive demonstration
python awesome_list_examples_with_tools.py

# With Galileo enabled
GALILEO_ENABLED=true python awesome_list_examples_with_tools.py
```

## Testing

### Running Tests

```bash
# Run all tool tests
pytest tests/test_new_tools.py -v

# Run specific tool tests
pytest tests/test_new_tools.py::TestYouTubeMetadataTool -v
pytest tests/test_new_tools.py::TestWebScrapingTool -v
pytest tests/test_new_tools.py::TestContentAnalysisTool -v
pytest tests/test_new_tools.py::TestAwesomeListParser -v
```

### Test Coverage

The test suite covers:
- ✅ Input validation
- ✅ URL parsing and extraction
- ✅ Content processing
- ✅ Error handling
- ✅ Edge cases
- ✅ Performance metrics
- ✅ Galileo integration

### Example Test

```python
@pytest.mark.asyncio
async def test_youtube_metadata_extraction():
    """Test YouTube metadata extraction."""
    tool = YouTubeMetadataTool()
    
    # Test valid URL
    result = await tool.execute("https://www.youtube.com/watch?v=test123")
    assert "error" not in result
    assert result["video_id"] == "test123"
    
    # Test invalid URL
    result = await tool.execute("https://example.com")
    assert "error" in result
```

## Troubleshooting

### Common Issues

#### 1. Network Errors
**Problem**: Tools fail with network errors
**Solution**: Check internet connection and URL accessibility

```python
# Add timeout handling
result = await agent.web_scraping_tool.execute(
    url,
    timeout=60  # Increase timeout
)
```

#### 2. Galileo Configuration
**Problem**: Galileo logging not working
**Solution**: Verify environment variables

```bash
# Check Galileo configuration
echo $GALILEO_ENABLED
echo $GALILEO_API_KEY
echo $GALILEO_PROJECT
```

#### 3. BeautifulSoup Import Error
**Problem**: `ModuleNotFoundError: No module named 'bs4'`
**Solution**: Install BeautifulSoup

```bash
pip install beautifulsoup4==4.12.3
```

#### 4. Tool Registration Errors
**Problem**: Tools not found in registry
**Solution**: Check tool registration in agent initialization

```python
# Verify tools are registered
print(agent.tool_registry.list_tools())
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use the setup function
from awesome_list_agent.utils.logging import setup_logging
setup_logging(level="DEBUG")
```

### Performance Optimization

For large-scale usage:

```python
# Reuse agent instances
agent = await AwesomeListAgentFactory.create_agent()

# Process multiple URLs efficiently
async def process_urls(urls):
    tasks = []
    for url in urls:
        task = agent.web_scraping_tool.execute(url)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Conclusion

The Awesome List Agent now provides a comprehensive suite of tools for content analysis and metadata extraction. Each tool is designed with:

- **Reliability**: Comprehensive error handling and validation
- **Observability**: Full Galileo integration for monitoring
- **Performance**: Optimized execution with timing metrics
- **Extensibility**: Easy to extend and customize
- **Testing**: Comprehensive test coverage

These tools can be used individually or combined in powerful workflows to analyze web content, extract metadata, and gain insights from various data sources. 