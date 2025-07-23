"""Tool for parsing Awesome List URLs to extract metadata and context."""

import re
import asyncio
import aiohttp
import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..tools.base import BaseTool
from ..models import ToolMetadata, ToolError


class AwesomeListParserMetadata(BaseModel):
    """Metadata for the Awesome List Parser tool."""
    
    name: str = "awesome_list_parser"
    description: str = "Parses an Awesome List URL to extract general topic, categories, and contextual information"
    tags: List[str] = ["parsing", "awesome-list", "web-scraping", "metadata"]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL of the Awesome List to parse",
                "pattern": r"^https?://.*"
            }
        },
        "required": ["url"]
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The main topic/subject of the Awesome List"
            },
            "description": {
                "type": "string", 
                "description": "Description of what the list is about"
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Main categories found in the list"
            },
            "total_items": {
                "type": "integer",
                "description": "Approximate number of items in the list"
            },
            "language": {
                "type": "string",
                "description": "Primary programming language if applicable"
            },
            "context_summary": {
                "type": "string",
                "description": "Brief summary of the list's purpose and content"
            }
        }
    }


class AwesomeListParser(BaseTool):
    """Tool for parsing Awesome List URLs and extracting contextual information."""
    
    metadata = AwesomeListParserMetadata
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("awesome_list_agent.AwesomeListParser")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; AwesomeListAgent/1.0)'
                }
            )
        return self.session
    
    async def execute(self, url: str) -> Dict[str, Any]:
        """Parse an Awesome List URL to extract metadata and context.
        
        Args:
            url: The URL of the Awesome List to parse
            
        Returns:
            Dictionary containing parsed information about the list
        """
        self.logger.info(f"Starting to parse Awesome List URL: {url}")
        
        try:
            # Validate URL format
            if not url.startswith(('http://', 'https://')):
                error_msg = "Invalid URL format. Must start with http:// or https://"
                self.logger.error(f"URL validation failed: {error_msg}")
                return ToolError(error=error_msg)
            
            self.logger.debug("URL validation passed")
            
            # Fetch the content
            self.logger.info("Fetching content from URL")
            session = await self._get_session()
            async with session.get(url) as response:
                self.logger.debug(f"HTTP response status: {response.status}")
                if response.status != 200:
                    error_msg = f"Failed to fetch URL: HTTP {response.status}"
                    self.logger.error(error_msg)
                    return ToolError(error=error_msg)
                
                content = await response.text()
                content_length = len(content)
                self.logger.info(f"Successfully fetched content ({content_length} characters)")
            
            # Parse the content
            self.logger.info("Starting content parsing")
            parsed_data = await self._parse_content(content, url)
            
            # Log parsing results
            if isinstance(parsed_data, dict):
                self.logger.info(f"Parsing completed successfully")
                self.logger.debug(f"Extracted topic: {parsed_data.get('topic', 'N/A')}")
                self.logger.debug(f"Found {parsed_data.get('total_items', 0)} items")
                self.logger.debug(f"Detected {len(parsed_data.get('categories', []))} categories")
                self.logger.debug(f"Language: {parsed_data.get('language', 'N/A')}")
            
            return parsed_data
            
        except aiohttp.ClientError as e:
            error_msg = f"Network error while fetching URL: {str(e)}"
            self.logger.error(error_msg)
            return ToolError(error=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error parsing Awesome List: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolError(error=error_msg)
    
    async def _parse_content(self, content: str, url: str) -> Dict[str, Any]:
        """Parse the HTML/Markdown content to extract list information.
        
        Args:
            content: The raw content of the page
            url: The original URL for context
            
        Returns:
            Parsed information about the Awesome List
        """
        # Extract title/topic
        topic = self._extract_topic(content, url)
        
        # Extract description
        description = self._extract_description(content)
        
        # Extract categories (headers)
        categories = self._extract_categories(content)
        
        # Count items (links)
        total_items = self._count_items(content)
        
        # Detect programming language
        language = self._detect_language(content, url)
        
        # Generate context summary
        context_summary = self._generate_context_summary(
            topic, description, categories, total_items, language
        )
        
        return {
            "topic": topic,
            "description": description,
            "categories": categories,
            "total_items": total_items,
            "language": language,
            "context_summary": context_summary
        }
    
    def _extract_topic(self, content: str, url: str) -> str:
        """Extract the main topic from title or URL."""
        # Try to extract from HTML title tag
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up common title patterns
            title = re.sub(r'^(awesome-?|Awesome\s+)', '', title, flags=re.IGNORECASE)
            if title:
                return title
        
        # Try to extract from first H1
        h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
        if h1_match:
            h1_text = h1_match.group(1).strip()
            h1_text = re.sub(r'^(awesome-?|Awesome\s+)', '', h1_text, flags=re.IGNORECASE)
            if h1_text:
                return h1_text
        
        # Try to extract from Markdown heading
        md_h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if md_h1_match:
            md_title = md_h1_match.group(1).strip()
            md_title = re.sub(r'^(awesome-?|Awesome\s+)', '', md_title, flags=re.IGNORECASE)
            if md_title:
                return md_title
        
        # Fall back to URL parsing
        url_parts = url.split('/')
        if 'awesome-' in url:
            for part in url_parts:
                if part.startswith('awesome-'):
                    return part.replace('awesome-', '').replace('-', ' ').title()
        
        return "Unknown Topic"
    
    def _extract_description(self, content: str) -> str:
        """Extract description from meta tags or content."""
        # Try meta description
        meta_desc = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', 
            content, re.IGNORECASE
        )
        if meta_desc:
            return meta_desc.group(1).strip()
        
        # Try first paragraph after title
        para_match = re.search(
            r'<h1[^>]*>[^<]+</h1>\s*<p[^>]*>([^<]+)</p>', 
            content, re.IGNORECASE | re.DOTALL
        )
        if para_match:
            return para_match.group(1).strip()
        
        # Try Markdown description (after first heading)
        md_desc = re.search(r'^#[^#\n]+\n\n([^\n]+)', content, re.MULTILINE)
        if md_desc:
            return md_desc.group(1).strip()
        
        return "No description available"
    
    def _extract_categories(self, content: str) -> List[str]:
        """Extract category headings from the content."""
        categories = []
        
        # HTML headings (h2, h3)
        html_headings = re.findall(
            r'<h[23][^>]*>([^<]+)</h[23]>', 
            content, re.IGNORECASE
        )
        categories.extend([h.strip() for h in html_headings if h.strip()])
        
        # Markdown headings (##, ###)
        md_headings = re.findall(r'^##[#]?\s+(.+)$', content, re.MULTILINE)
        categories.extend([h.strip() for h in md_headings if h.strip()])
        
        # Remove duplicates and common non-category headings
        categories = list(set(categories))
        skip_terms = {
            'contents', 'table of contents', 'contributing', 'license', 
            'awesome', 'related', 'similar', 'credits', 'acknowledgments'
        }
        categories = [c for c in categories if c.lower() not in skip_terms]
        
        return categories[:10]  # Limit to top 10 categories
    
    def _count_items(self, content: str) -> int:
        """Count approximate number of items/links in the list."""
        # Count markdown links
        md_links = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
        
        # Count HTML links (excluding navigation)
        html_links = len(re.findall(r'<a[^>]+href=[^>]*>([^<]+)</a>', content, re.IGNORECASE))
        
        # Use the higher count
        return max(md_links, html_links)
    
    def _detect_language(self, content: str, url: str) -> str:
        """Detect the primary programming language if applicable."""
        # Common programming languages to look for
        languages = {
            'javascript': ['javascript', 'js', 'node', 'npm', 'react', 'vue', 'angular'],
            'python': ['python', 'py', 'django', 'flask', 'pandas', 'numpy'],
            'java': ['java', 'spring', 'maven', 'gradle'],
            'go': ['golang', 'go', 'gin', 'beego'],
            'rust': ['rust', 'cargo', 'crates'],
            'php': ['php', 'laravel', 'symfony', 'composer'],
            'ruby': ['ruby', 'rails', 'gem'],
            'csharp': ['c#', 'csharp', '.net', 'dotnet'],
            'cpp': ['c++', 'cpp'],
            'swift': ['swift', 'ios', 'macos'],
            'kotlin': ['kotlin', 'android'],
            'typescript': ['typescript', 'ts']
        }
        
        content_lower = content.lower()
        url_lower = url.lower()
        
        # Check URL first
        for lang, keywords in languages.items():
            if any(keyword in url_lower for keyword in keywords):
                return lang.title()
        
        # Check content
        lang_scores = {}
        for lang, keywords in languages.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                lang_scores[lang] = score
        
        if lang_scores:
            best_lang = max(lang_scores, key=lang_scores.get)
            return best_lang.title()
        
        return "General"
    
    def _generate_context_summary(
        self, topic: str, description: str, categories: List[str], 
        total_items: int, language: str
    ) -> str:
        """Generate a contextual summary of the Awesome List."""
        summary_parts = [f"This is an Awesome List focused on {topic}."]
        
        if description != "No description available":
            summary_parts.append(description)
        
        if language != "General":
            summary_parts.append(f"It primarily covers {language} related resources.")
        
        if categories:
            if len(categories) <= 3:
                cat_text = ", ".join(categories)
            else:
                cat_text = f"{', '.join(categories[:3])}, and {len(categories) - 3} other categories"
            summary_parts.append(f"Main categories include: {cat_text}.")
        
        if total_items > 0:
            summary_parts.append(f"The list contains approximately {total_items} curated resources.")
        
        return " ".join(summary_parts)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
