"""Tool for analyzing content and extracting insights from text data."""

import re
import logging
import time
from typing import Any, Dict, List, Optional, Counter
from collections import defaultdict
import json

from .base import BaseTool
from ..models import ToolMetadata, ToolError


class ContentAnalysisToolMetadata(ToolMetadata):
    """Metadata for the Content Analysis Tool."""

    name: str = "content_analysis_tool"
    description: str = (
        "Analyzes text content to extract insights including sentiment, key topics, entities, readability metrics, and content structure"
    )
    tags: List[str] = [
        "content-analysis",
        "text-processing",
        "nlp",
        "insights",
        "sentiment-analysis",
    ]
    input_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "The text content to analyze"},
            "analyze_sentiment": {
                "type": "boolean",
                "description": "Whether to perform sentiment analysis (default: true)",
                "default": True,
            },
            "extract_topics": {
                "type": "boolean",
                "description": "Whether to extract key topics (default: true)",
                "default": True,
            },
            "extract_entities": {
                "type": "boolean",
                "description": "Whether to extract named entities (default: true)",
                "default": True,
            },
            "analyze_readability": {
                "type": "boolean",
                "description": "Whether to calculate readability metrics (default: true)",
                "default": True,
            },
            "extract_keywords": {
                "type": "boolean",
                "description": "Whether to extract keywords (default: true)",
                "default": True,
            },
            "max_topics": {
                "type": "integer",
                "description": "Maximum number of topics to extract (default: 10)",
                "default": 10,
            },
            "max_keywords": {
                "type": "integer",
                "description": "Maximum number of keywords to extract (default: 20)",
                "default": 20,
            },
        },
        "required": ["text"],
    }
    output_schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "text_length": {
                "type": "integer",
                "description": "Length of the analyzed text in characters",
            },
            "word_count": {
                "type": "integer",
                "description": "Number of words in the text",
            },
            "sentence_count": {
                "type": "integer",
                "description": "Number of sentences in the text",
            },
            "paragraph_count": {
                "type": "integer",
                "description": "Number of paragraphs in the text",
            },
            "sentiment": {
                "type": "object",
                "properties": {
                    "overall": {"type": "string"},
                    "score": {"type": "number"},
                    "positive_words": {"type": "array", "items": {"type": "string"}},
                    "negative_words": {"type": "array", "items": {"type": "string"}},
                },
                "description": "Sentiment analysis results",
            },
            "topics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "frequency": {"type": "integer"},
                        "relevance_score": {"type": "number"},
                    },
                },
                "description": "Extracted key topics",
            },
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "entity": {"type": "string"},
                        "type": {"type": "string"},
                        "frequency": {"type": "integer"},
                    },
                },
                "description": "Extracted named entities",
            },
            "keywords": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "frequency": {"type": "integer"},
                        "tf_idf_score": {"type": "number"},
                    },
                },
                "description": "Extracted keywords with scores",
            },
            "readability": {
                "type": "object",
                "properties": {
                    "flesch_reading_ease": {"type": "number"},
                    "flesch_kincaid_grade": {"type": "number"},
                    "gunning_fog_index": {"type": "number"},
                    "smog_index": {"type": "number"},
                    "coleman_liau_index": {"type": "number"},
                    "automated_readability_index": {"type": "number"},
                },
                "description": "Readability metrics",
            },
            "content_structure": {
                "type": "object",
                "properties": {
                    "has_headings": {"type": "boolean"},
                    "has_lists": {"type": "boolean"},
                    "has_links": {"type": "boolean"},
                    "has_code_blocks": {"type": "boolean"},
                    "average_sentence_length": {"type": "number"},
                    "average_word_length": {"type": "number"},
                },
                "description": "Content structure analysis",
            },
            "analysis_summary": {
                "type": "string",
                "description": "Brief summary of the content analysis",
            },
        },
    }


class ContentAnalysisTool(BaseTool):
    """Tool for analyzing text content and extracting insights."""

    metadata = ContentAnalysisToolMetadata

    def __init__(self):
        self.logger = logging.getLogger("awesome_list_agent.ContentAnalysisTool")

        # Common positive and negative words for sentiment analysis
        self.positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "awesome",
            "best",
            "perfect",
            "outstanding",
            "brilliant",
            "superb",
            "terrific",
            "incredible",
            "love",
            "like",
            "enjoy",
            "happy",
            "pleased",
            "satisfied",
            "impressed",
            "useful",
            "helpful",
            "effective",
            "efficient",
            "powerful",
            "fast",
            "easy",
            "simple",
            "clear",
            "comprehensive",
            "detailed",
            "thorough",
            "complete",
            "reliable",
        }

        self.negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "poor",
            "disappointing",
            "frustrating",
            "annoying",
            "difficult",
            "complicated",
            "confusing",
            "unclear",
            "slow",
            "broken",
            "error",
            "fail",
            "problem",
            "issue",
            "bug",
            "crash",
            "hate",
            "dislike",
            "unhappy",
            "angry",
            "upset",
            "disappointed",
            "useless",
            "ineffective",
            "inefficient",
            "weak",
            "limited",
            "incomplete",
            "unreliable",
        }

    async def execute(
        self,
        text: str,
        analyze_sentiment: bool = True,
        extract_topics: bool = True,
        extract_entities: bool = True,
        analyze_readability: bool = True,
        extract_keywords: bool = True,
        max_topics: int = 10,
        max_keywords: int = 20,
    ) -> Dict[str, Any]:
        """Analyze text content and extract various insights.

        Args:
            text: The text content to analyze
            analyze_sentiment: Whether to perform sentiment analysis
            extract_topics: Whether to extract key topics
            extract_entities: Whether to extract named entities
            analyze_readability: Whether to calculate readability metrics
            extract_keywords: Whether to extract keywords
            max_topics: Maximum number of topics to extract
            max_keywords: Maximum number of keywords to extract

        Returns:
            Dictionary containing comprehensive content analysis results
        """
        start_time = time.perf_counter_ns()

        try:
            # Log tool execution start
            self.logger.info("Starting content analysis")
            self.logger.debug(f"Text length: {len(text)} characters")
            self.logger.debug(
                f"Analysis options: sentiment={analyze_sentiment}, topics={extract_topics}, entities={extract_entities}, readability={analyze_readability}, keywords={extract_keywords}"
            )

            # Basic text statistics
            result = self._calculate_basic_stats(text)

            # Perform requested analyses
            if analyze_sentiment:
                self.logger.debug("Performing sentiment analysis")
                result["sentiment"] = self._analyze_sentiment(text)

            if extract_topics:
                self.logger.debug("Extracting topics")
                result["topics"] = self._extract_topics(text, max_topics)

            if extract_entities:
                self.logger.debug("Extracting entities")
                result["entities"] = self._extract_entities(text)

            if extract_keywords:
                self.logger.debug("Extracting keywords")
                result["keywords"] = self._extract_keywords(text, max_keywords)

            if analyze_readability:
                self.logger.debug("Calculating readability metrics")
                result["readability"] = self._calculate_readability(text)

            # Content structure analysis
            self.logger.debug("Analyzing content structure")
            result["content_structure"] = self._analyze_content_structure(text)

            # Generate analysis summary
            result["analysis_summary"] = self._generate_analysis_summary(result)

            # Calculate duration
            duration_ns = time.perf_counter_ns() - start_time

            # Log successful analysis
            self.logger.info("Successfully completed content analysis")
            self.logger.debug(f"Analysis completed in {duration_ns / 1_000_000:.2f}ms")

            # Add timing information
            result["analysis_time_ms"] = duration_ns / 1_000_000

            return result

        except Exception as e:
            error_msg = f"Unexpected error during content analysis: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return ToolError(error=error_msg)

    def _calculate_basic_stats(self, text: str) -> Dict[str, int]:
        """Calculate basic text statistics."""
        # Remove extra whitespace
        cleaned_text = re.sub(r"\s+", " ", text.strip())

        # Count words
        words = cleaned_text.split()
        word_count = len(words)

        # Count sentences (simple approach)
        sentences = re.split(r"[.!?]+", cleaned_text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Count paragraphs
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        paragraph_count = len(paragraphs)

        return {
            "text_length": len(text),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
        }

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Perform basic sentiment analysis."""
        words = re.findall(r"\b\w+\b", text.lower())

        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)

        total_words = len(words)
        if total_words == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_words

        # Determine overall sentiment
        if sentiment_score > 0.05:
            overall_sentiment = "positive"
        elif sentiment_score < -0.05:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        # Find positive and negative words
        positive_words_found = [word for word in words if word in self.positive_words]
        negative_words_found = [word for word in words if word in self.negative_words]

        return {
            "overall": overall_sentiment,
            "score": sentiment_score,
            "positive_words": list(set(positive_words_found)),
            "negative_words": list(set(negative_words_found)),
        }

    def _extract_topics(self, text: str, max_topics: int) -> List[Dict[str, Any]]:
        """Extract key topics from the text."""
        # Simple topic extraction based on word frequency
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Remove common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "mine",
            "yours",
            "his",
            "hers",
            "ours",
            "theirs",
            "what",
            "when",
            "where",
            "why",
            "how",
            "who",
            "which",
        }

        filtered_words = [word for word in words if word not in stop_words]

        # Count word frequencies
        word_freq = Counter(filtered_words)

        # Get top topics
        topics = []
        for word, freq in word_freq.most_common(max_topics):
            relevance_score = freq / len(filtered_words) if filtered_words else 0
            topics.append(
                {"topic": word, "frequency": freq, "relevance_score": relevance_score}
            )

        return topics

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from the text."""
        # Simple entity extraction based on capitalization patterns
        entities = []

        # Find capitalized words (potential proper nouns)
        capitalized_words = re.findall(r"\b[A-Z][a-z]+\b", text)
        word_freq = Counter(capitalized_words)

        # Find potential organizations (words with common org suffixes)
        org_pattern = r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Organization|Foundation|Institute|University|College)\b"
        orgs = re.findall(org_pattern, text)

        # Find potential URLs
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, text)

        # Add entities
        for word, freq in word_freq.most_common(10):
            entities.append({"entity": word, "type": "proper_noun", "frequency": freq})

        for org in orgs[:5]:
            entities.append({"entity": org, "type": "organization", "frequency": 1})

        for url in urls[:5]:
            entities.append({"entity": url, "type": "url", "frequency": 1})

        return entities

    def _extract_keywords(self, text: str, max_keywords: int) -> List[Dict[str, Any]]:
        """Extract keywords with TF-IDF-like scoring."""
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Remove stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
        }

        filtered_words = [word for word in words if word not in stop_words]
        word_freq = Counter(filtered_words)

        # Calculate simple TF-IDF-like scores
        total_words = len(filtered_words)
        keywords = []

        for word, freq in word_freq.most_common(max_keywords):
            tf = freq / total_words if total_words > 0 else 0
            # Simple IDF approximation (inverse of frequency)
            idf = 1 / (freq + 1)  # Add 1 to avoid division by zero
            tf_idf_score = tf * idf

            keywords.append(
                {"keyword": word, "frequency": freq, "tf_idf_score": tf_idf_score}
            )

        return keywords

    def _calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate various readability metrics."""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = re.findall(r"\b\w+\b", text.lower())
        syllables = self._count_syllables(text)

        sentence_count = len(sentences)
        word_count = len(words)
        syllable_count = syllables

        if sentence_count == 0 or word_count == 0:
            return {
                "flesch_reading_ease": 0,
                "flesch_kincaid_grade": 0,
                "gunning_fog_index": 0,
                "smog_index": 0,
                "coleman_liau_index": 0,
                "automated_readability_index": 0,
            }

        # Flesch Reading Ease
        flesch_ease = (
            206.835
            - (1.015 * (word_count / sentence_count))
            - (84.6 * (syllable_count / word_count))
        )

        # Flesch-Kincaid Grade Level
        flesch_grade = (
            (0.39 * (word_count / sentence_count))
            + (11.8 * (syllable_count / word_count))
            - 15.59
        )

        # Gunning Fog Index
        complex_words = len([word for word in words if self._count_syllables(word) > 2])
        fog_index = 0.4 * (
            (word_count / sentence_count) + (100 * (complex_words / word_count))
        )

        # SMOG Index
        smog_index = 1.043 * ((complex_words * (30 / sentence_count)) ** 0.5) + 3.1291

        # Coleman-Liau Index
        letters = len(re.findall(r"[a-zA-Z]", text))
        coleman_liau = (
            (0.0588 * (letters / word_count * 100))
            - (0.296 * (sentence_count / word_count * 100))
            - 15.8
        )

        # Automated Readability Index
        ari = (
            (4.71 * (letters / word_count))
            + (0.5 * (word_count / sentence_count))
            - 21.43
        )

        return {
            "flesch_reading_ease": max(0, min(100, flesch_ease)),
            "flesch_kincaid_grade": max(0, flesch_grade),
            "gunning_fog_index": max(0, fog_index),
            "smog_index": max(0, smog_index),
            "coleman_liau_index": max(0, coleman_liau),
            "automated_readability_index": max(0, ari),
        }

    def _count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified approach)."""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False

        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel

        # Adjust for common patterns
        if text.endswith("e"):
            count -= 1
        if count == 0:
            count = 1

        return count

    def _analyze_content_structure(self, text: str) -> Dict[str, Any]:
        """Analyze the structure of the content."""
        # Check for headings
        has_headings = bool(re.search(r"^#{1,6}\s+", text, re.MULTILINE))

        # Check for lists
        has_lists = bool(
            re.search(r"^[\s]*[-*+]\s+", text, re.MULTILINE)
            or re.search(r"^[\s]*\d+\.\s+", text, re.MULTILINE)
        )

        # Check for links
        has_links = bool(
            re.search(r"\[([^\]]+)\]\([^)]+\)", text)
            or re.search(r"https?://[^\s]+", text)
        )

        # Check for code blocks
        has_code_blocks = bool(
            re.search(r"```[\s\S]*?```", text) or re.search(r"`[^`]+`", text)
        )

        # Calculate average sentence length
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        )

        # Calculate average word length
        words = re.findall(r"\b\w+\b", text)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

        return {
            "has_headings": has_headings,
            "has_lists": has_lists,
            "has_links": has_links,
            "has_code_blocks": has_code_blocks,
            "average_sentence_length": avg_sentence_length,
            "average_word_length": avg_word_length,
        }

    def _generate_analysis_summary(self, result: Dict[str, Any]) -> str:
        """Generate a summary of the content analysis."""
        summary_parts = []

        # Basic stats
        summary_parts.append(
            f"Analyzed {result.get('word_count', 0)} words in {result.get('sentence_count', 0)} sentences"
        )

        # Sentiment
        if "sentiment" in result:
            sentiment = result["sentiment"]
            summary_parts.append(
                f"Overall sentiment is {sentiment['overall']} (score: {sentiment['score']:.3f})"
            )

        # Topics
        if "topics" in result and result["topics"]:
            top_topic = result["topics"][0]["topic"]
            summary_parts.append(f"Main topic: {top_topic}")

        # Readability
        if "readability" in result:
            readability = result["readability"]
            grade_level = readability.get("flesch_kincaid_grade", 0)
            summary_parts.append(
                f"Readability level: approximately {grade_level:.1f} grade level"
            )

        # Structure
        if "content_structure" in result:
            structure = result["content_structure"]
            features = []
            if structure["has_headings"]:
                features.append("headings")
            if structure["has_lists"]:
                features.append("lists")
            if structure["has_links"]:
                features.append("links")
            if structure["has_code_blocks"]:
                features.append("code blocks")

            if features:
                summary_parts.append(f"Content includes: {', '.join(features)}")

        return ". ".join(summary_parts) + "."
