import asyncio
from crawl4ai import AsyncWebCrawler
from typing import Optional
from openai import OpenAI
import nest_asyncio
from bs4 import BeautifulSoup
import re

# Enable nested event loops
nest_asyncio.apply()

class ArticleProcessor:
    def __init__(self):
        self.client = OpenAI()

    def process_url_sync(self, url: str) -> Optional[str]:
        """Synchronous wrapper for process_url."""
        return asyncio.run(self.process_url(url))

    def extract_summary(self, markdown_text: str, max_length: int = 200) -> str:
        """Extract a summary from markdown text."""
        # Remove markdown formatting
        clean_text = re.sub(r'[#*`_~\[\]\(\)]', '', markdown_text)
        # Remove multiple spaces and newlines
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Get first paragraph or sentence that makes sense
        sentences = clean_text.split('.')
        summary = ''
        
        for sentence in sentences:
            if len(sentence.strip()) > 50:  # Only use substantial sentences
                summary = sentence.strip()
                break
        
        if not summary and sentences:
            summary = sentences[0].strip()
            
        return f"{summary[:max_length]}..." if len(summary) > max_length else summary

    async def process_url(self, url: str) -> Optional[str]:
        """Process an article URL and return a tweet-worthy summary."""
        try:
            # Crawl the article
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                    max_pages=1,
                    markdown=True,
                    timeout=30
                )

            if not result or not result.markdown:
                raise Exception("No content extracted from URL")

            # Extract summary from the markdown content
            summary = self.extract_summary(result.markdown)

            # Create tweet from the extracted summary
            tweet = f"{summary[:200]}... {url}"
            
            # Ensure tweet is within limits
            if len(tweet) > 280:
                tweet = f"{tweet[:277]}..."

            return tweet

        except Exception as e:
            print(f"Error processing article: {str(e)}")
            return None

    def create_tweet_from_summary(self, summary: str, url: str) -> str:
        """Create a tweet from the summary only if needed."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Create a concise, engaging tweet from the summary. The tweet should:
1. Be under 280 characters
2. Include key information
3. Be engaging and shareable
4. Not use hashtags or emojis
5. Maintain a professional tone
6. Include the article URL at the end"""
                    },
                    {
                        "role": "user",
                        "content": f"Summary:\n{summary}\n\nURL: {url}"
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback to simple summary if OpenAI fails
            tweet = f"{summary[:200]}... {url}"
            if len(tweet) > 280:
                tweet = f"{tweet[:277]}..."
            return tweet 