#!/usr/bin/env python3
"""
Comprehensive example demonstrating all Awesome List Agent tools working together.

This script shows how to use:
1. Awesome List Parser Tool
2. YouTube Metadata Tool  
3. Web Scraping Tool
4. Content Analysis Tool

Each tool includes Galileo logging for observability.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from awesome_list_agent.factory import AwesomeListAgentFactory
from awesome_list_agent.utils.logging import setup_logging


async def demonstrate_awesome_list_parser():
    """Demonstrate the Awesome List Parser tool."""
    print("\n" + "="*60)
    print("DEMONSTRATING AWESOME LIST PARSER TOOL")
    print("="*60)
    
    # Create agent with Galileo logging enabled
    agent = await AwesomeListAgentFactory.create_agent(
        verbosity="high",
        enable_galileo=True
    )
    
    # Test URL - a real awesome list
    test_url = "https://github.com/sindresorhus/awesome"
    
    print(f"Processing Awesome List: {test_url}")
    
    try:
        # Use the awesome list parser tool directly
        parser_tool = agent.parser
        result = await parser_tool.execute(test_url)
        
        if isinstance(result, dict) and "error" not in result:
            print("✅ Successfully parsed Awesome List!")
            print(f"📋 Topic: {result.get('topic', 'N/A')}")
            print(f"📝 Description: {result.get('description', 'N/A')[:100]}...")
            print(f"📊 Total Items: {result.get('total_items', 0)}")
            print(f"🏷️  Categories: {len(result.get('categories', []))}")
            print(f"💻 Language: {result.get('language', 'N/A')}")
            print(f"📄 Context Summary: {result.get('context_summary', 'N/A')[:200]}...")
        else:
            print(f"❌ Error parsing Awesome List: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")


async def demonstrate_youtube_metadata_tool():
    """Demonstrate the YouTube Metadata tool."""
    print("\n" + "="*60)
    print("DEMONSTRATING YOUTUBE METADATA TOOL")
    print("="*60)
    
    # Create agent with Galileo logging enabled
    agent = await AwesomeListAgentFactory.create_agent(
        verbosity="high",
        enable_galileo=True
    )
    
    # Test YouTube URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"Extracting metadata from: {test_url}")
    
    try:
        # Use the YouTube metadata tool directly
        youtube_tool = agent.youtube_tool
        result = await youtube_tool.execute(test_url, extract_comments=True)
        
        if isinstance(result, dict) and "error" not in result:
            print("✅ Successfully extracted YouTube metadata!")
            print(f"🎬 Video ID: {result.get('video_id', 'N/A')}")
            print(f"📺 Title: {result.get('title', 'N/A')}")
            print(f"📝 Description: {result.get('description', 'N/A')[:100]}...")
            print(f"⏱️  Duration: {result.get('duration', 'N/A')} ({result.get('duration_seconds', 0)} seconds)")
            print(f"👁️  Views: {result.get('view_count', 0):,}")
            print(f"👍 Likes: {result.get('like_count', 0):,}")
            print(f"💬 Comments: {result.get('comment_count', 0):,}")
            print(f"📅 Upload Date: {result.get('upload_date', 'N/A')}")
            print(f"📺 Channel: {result.get('channel_name', 'N/A')}")
            print(f"🏷️  Tags: {', '.join(result.get('tags', [])[:5])}")
            print(f"📊 Summary: {result.get('metadata_summary', 'N/A')}")
        else:
            print(f"❌ Error extracting YouTube metadata: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")


async def demonstrate_web_scraping_tool():
    """Demonstrate the Web Scraping tool."""
    print("\n" + "="*60)
    print("DEMONSTRATING WEB SCRAPING TOOL")
    print("="*60)
    
    # Create agent with Galileo logging enabled
    agent = await AwesomeListAgentFactory.create_agent(
        verbosity="high",
        enable_galileo=True
    )
    
    # Test URL - a simple webpage
    test_url = "https://httpbin.org/html"
    
    print(f"Scraping content from: {test_url}")
    
    try:
        # Use the web scraping tool directly
        scraping_tool = agent.web_scraping_tool
        result = await scraping_tool.execute(
            test_url,
            extract_text=True,
            extract_links=True,
            extract_images=True,
            extract_metadata=True,
            max_links=10,
            max_images=5
        )
        
        if isinstance(result, dict) and "error" not in result:
            print("✅ Successfully scraped web content!")
            print(f"📄 Title: {result.get('title', 'N/A')}")
            print(f"📊 Content Type: {result.get('content_type', 'N/A')}")
            print(f"📏 Content Length: {result.get('content_length', 0):,} characters")
            print(f"📝 Text Summary: {result.get('text_summary', 'N/A')}")
            print(f"🔗 Links Found: {len(result.get('links', []))}")
            print(f"🖼️  Images Found: {len(result.get('images', []))}")
            print(f"📋 Metadata Fields: {len(result.get('metadata', {}))}")
            print(f"📊 Scraping Summary: {result.get('scraping_summary', 'N/A')}")
            
            # Show first few links
            links = result.get('links', [])
            if links:
                print("\n🔗 Sample Links:")
                for i, link in enumerate(links[:3]):
                    print(f"  {i+1}. {link.get('text', 'No text')} -> {link.get('url', 'No URL')}")
                    
        else:
            print(f"❌ Error scraping web content: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")


async def demonstrate_content_analysis_tool():
    """Demonstrate the Content Analysis tool."""
    print("\n" + "="*60)
    print("DEMONSTRATING CONTENT ANALYSIS TOOL")
    print("="*60)
    
    # Create agent with Galileo logging enabled
    agent = await AwesomeListAgentFactory.create_agent(
        verbosity="high",
        enable_galileo=True
    )
    
    # Sample text for analysis
    sample_text = """
    Python is an amazing programming language that has revolutionized software development. 
    It's known for its simplicity, readability, and extensive library ecosystem. 
    Many developers love Python because it makes coding fun and efficient.
    
    The language is widely used in data science, web development, artificial intelligence, 
    and automation. Companies like Google, Netflix, and Instagram rely heavily on Python 
    for their backend services and data processing pipelines.
    
    Python's community is incredibly supportive and the documentation is excellent. 
    There are countless tutorials, courses, and resources available for learning Python. 
    Whether you're a beginner or an experienced developer, Python has something to offer.
    """
    
    print(f"Analyzing text content ({len(sample_text)} characters)")
    
    try:
        # Use the content analysis tool directly
        analysis_tool = agent.content_analysis_tool
        result = await analysis_tool.execute(
            sample_text,
            analyze_sentiment=True,
            extract_topics=True,
            extract_entities=True,
            analyze_readability=True,
            extract_keywords=True,
            max_topics=5,
            max_keywords=10
        )
        
        if isinstance(result, dict) and "error" not in result:
            print("✅ Successfully analyzed content!")
            print(f"📊 Basic Stats:")
            print(f"  - Words: {result.get('word_count', 0)}")
            print(f"  - Sentences: {result.get('sentence_count', 0)}")
            print(f"  - Paragraphs: {result.get('paragraph_count', 0)}")
            
            # Sentiment analysis
            sentiment = result.get('sentiment', {})
            if sentiment:
                print(f"😊 Sentiment: {sentiment.get('overall', 'N/A')} (score: {sentiment.get('score', 0):.3f})")
                print(f"  - Positive words: {', '.join(sentiment.get('positive_words', [])[:5])}")
                print(f"  - Negative words: {', '.join(sentiment.get('negative_words', [])[:5])}")
            
            # Topics
            topics = result.get('topics', [])
            if topics:
                print(f"📋 Top Topics:")
                for i, topic in enumerate(topics[:3]):
                    print(f"  {i+1}. {topic['topic']} (freq: {topic['frequency']}, score: {topic['relevance_score']:.3f})")
            
            # Keywords
            keywords = result.get('keywords', [])
            if keywords:
                print(f"🔑 Top Keywords:")
                for i, keyword in enumerate(keywords[:5]):
                    print(f"  {i+1}. {keyword['keyword']} (freq: {keyword['frequency']}, score: {keyword['tf_idf_score']:.3f})")
            
            # Readability
            readability = result.get('readability', {})
            if readability:
                print(f"📖 Readability Metrics:")
                print(f"  - Flesch Reading Ease: {readability.get('flesch_reading_ease', 0):.1f}")
                print(f"  - Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 0):.1f}")
                print(f"  - Gunning Fog Index: {readability.get('gunning_fog_index', 0):.1f}")
            
            # Content structure
            structure = result.get('content_structure', {})
            if structure:
                print(f"📐 Content Structure:")
                print(f"  - Has headings: {structure.get('has_headings', False)}")
                print(f"  - Has lists: {structure.get('has_lists', False)}")
                print(f"  - Has links: {structure.get('has_links', False)}")
                print(f"  - Avg sentence length: {structure.get('average_sentence_length', 0):.1f} words")
                print(f"  - Avg word length: {structure.get('average_word_length', 0):.1f} characters")
            
            print(f"📊 Analysis Summary: {result.get('analysis_summary', 'N/A')}")
            
        else:
            print(f"❌ Error analyzing content: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")


async def demonstrate_integrated_workflow():
    """Demonstrate how all tools can work together in an integrated workflow."""
    print("\n" + "="*60)
    print("DEMONSTRATING INTEGRATED WORKFLOW")
    print("="*60)
    
    # Create agent with Galileo logging enabled
    agent = await AwesomeListAgentFactory.create_agent(
        verbosity="high",
        enable_galileo=True
    )
    
    # Test with a GitHub README that might contain YouTube links
    test_url = "https://github.com/sindresorhus/awesome"
    
    print(f"Running integrated workflow on: {test_url}")
    print("This will: 1) Parse the awesome list, 2) Scrape content, 3) Analyze the content")
    
    try:
        # Step 1: Parse the awesome list
        print("\n🔍 Step 1: Parsing Awesome List...")
        parser_result = await agent.parser.execute(test_url)
        
        if isinstance(parser_result, dict) and "error" not in parser_result:
            print(f"✅ Parsed: {parser_result.get('topic', 'Unknown')} with {parser_result.get('total_items', 0)} items")
            
            # Step 2: Scrape the content for more details
            print("\n🌐 Step 2: Scraping web content...")
            scraping_result = await agent.web_scraping_tool.execute(
                test_url,
                extract_text=True,
                extract_links=True,
                extract_metadata=True,
                max_links=20
            )
            
            if isinstance(scraping_result, dict) and "error" not in scraping_result:
                print(f"✅ Scraped: {scraping_result.get('title', 'Unknown')}")
                
                # Step 3: Analyze the scraped content
                print("\n📊 Step 3: Analyzing content...")
                text_content = scraping_result.get('text_content', '')
                if text_content:
                    analysis_result = await agent.content_analysis_tool.execute(
                        text_content[:2000],  # Limit to first 2000 chars for demo
                        analyze_sentiment=True,
                        extract_topics=True,
                        extract_keywords=True,
                        max_topics=5,
                        max_keywords=10
                    )
                    
                    if isinstance(analysis_result, dict) and "error" not in analysis_result:
                        print("✅ Content analysis completed!")
                        
                        # Show integrated results
                        print(f"\n📋 Integrated Results:")
                        print(f"  - Awesome List Topic: {parser_result.get('topic', 'N/A')}")
                        print(f"  - Web Page Title: {scraping_result.get('title', 'N/A')}")
                        print(f"  - Content Sentiment: {analysis_result.get('sentiment', {}).get('overall', 'N/A')}")
                        print(f"  - Key Topics: {', '.join([t['topic'] for t in analysis_result.get('topics', [])[:3]])}")
                        print(f"  - Total Links Found: {len(scraping_result.get('links', []))}")
                        print(f"  - Content Length: {analysis_result.get('word_count', 0)} words")
                        
                        print(f"\n🎯 This demonstrates how all tools can work together to provide comprehensive analysis!")
                    else:
                        print(f"❌ Content analysis failed: {analysis_result.get('error', 'Unknown error')}")
                else:
                    print("❌ No text content available for analysis")
            else:
                print(f"❌ Web scraping failed: {scraping_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Awesome list parsing failed: {parser_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Exception in integrated workflow: {str(e)}")


async def main():
    """Main function to run all demonstrations."""
    print("🚀 Awesome List Agent - Comprehensive Tool Demonstration")
    print("This script demonstrates all available tools with Galileo logging enabled.")
    
    # Setup logging
    setup_logging(level="INFO")
    
    # Check if Galileo is enabled
    galileo_enabled = os.getenv("GALILEO_ENABLED", "false").lower() == "true"
    if galileo_enabled:
        print("📊 Galileo observability is ENABLED - all tool executions will be logged")
    else:
        print("📊 Galileo observability is DISABLED - set GALILEO_ENABLED=true to enable")
    
    try:
        # Run all demonstrations
        await demonstrate_awesome_list_parser()
        await demonstrate_youtube_metadata_tool()
        await demonstrate_web_scraping_tool()
        await demonstrate_content_analysis_tool()
        await demonstrate_integrated_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n🎉 You've successfully seen all tools in action:")
        print("  • Awesome List Parser - extracts metadata from awesome lists")
        print("  • YouTube Metadata Tool - extracts video information")
        print("  • Web Scraping Tool - scrapes and parses web content")
        print("  • Content Analysis Tool - analyzes text for insights")
        print("  • Integrated Workflow - shows how tools work together")
        
        if galileo_enabled:
            print("\n📊 Check your Galileo dashboard to see detailed execution logs and metrics!")
        
    except Exception as e:
        print(f"\n❌ Error running demonstrations: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 