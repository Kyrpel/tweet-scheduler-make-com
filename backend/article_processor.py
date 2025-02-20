import asyncio
from crawl4ai import AsyncWebCrawler
from typing import Optional
import nest_asyncio
import re
from openai import OpenAI
import os
import random
from hooks_config import VIRAL_HOOKS
import logging

# Enable nested event loops
nest_asyncio.apply()

logger = logging.getLogger(__name__)

class ArticleProcessor:
    def __init__(self):
        self.client = OpenAI()  # Will use OPENAI_API_KEY from environment

    async def process_url(self, url: str) -> Optional[str]:
        """Process an article URL and return a tweet-worthy summary."""
        try:
            # Configure crawler with more robust settings
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                    max_pages=1,
                    markdown=True,
                    timeout=30,
                    extract_content=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    },
                    follow_redirects=True,
                    verify_ssl=False  # Be careful with this in production
                )

            if not result or not result.markdown:
                # Try alternative extraction if primary fails
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun(
                        url=url,
                        max_pages=1,
                        extract_text=True,  # Fallback to text extraction
                        timeout=30
                    )
                    
                if not result or (not result.text and not result.markdown):
                    raise Exception("No content extracted from URL")
                
                content = result.text if result.text else result.markdown

            else:
                content = result.markdown

            # Clean up the content
            content = self._clean_content(content)
            
            return self._create_tweet(content, url)

        except Exception as e:
            logger.error(f"Error processing article: {str(e)}")
            return None

    def _clean_content(self, content: str) -> str:
        """Clean and format the extracted content."""
        # Remove URLs
        content = re.sub(r'http\S+', '', content)
        # Remove markdown formatting
        content = re.sub(r'[#*`_~\[\]\(\)\{\}]', '', content)
        # Fix multiple newlines
        content = re.sub(r'\n\s*\n', '\n\n', content)
        # Fix multiple spaces
        content = re.sub(r'\s+', ' ', content)
        # Remove common boilerplate text
        content = re.sub(r'(Cookie Policy|Privacy Policy|Terms of Service|Subscribe to our newsletter|Advertisement)', '', content, flags=re.IGNORECASE)
        # Get first few paragraphs
        paragraphs = content.split('\n\n')
        main_content = '\n\n'.join(paragraphs[:3])
        return main_content.strip()

    def process_url_sync(self, url: str) -> Optional[str]:
        """Synchronous wrapper for process_url."""
        return asyncio.run(self.process_url(url))

    def get_viral_hook(self, content: str) -> str:
        """Select appropriate viral hook based on content."""
        try:
            # Analyze content to select best hook type
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the article content and select the most appropriate viral hook type:
1. Question Hook (for how-to/educational content)
2. Challenge Hook (for myth-busting/contrarian views)
3. Story Hook (for case studies/experiences)
4. Authority Hook (for expert insights/research)
5. Stats Hook (for data-driven content)
Choose the most engaging format based on content."""
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                max_tokens=50
            )
            
            hook_type = response.choices[0].message.content.strip().lower()
            # Get appropriate hook based on content analysis
            hooks = VIRAL_HOOKS.get(hook_type, VIRAL_HOOKS["question"])["examples"]
            
            # Use GPT to select most relevant hook template
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "Select the most appropriate hook template that matches the article's content and message. Consider the key points, tone, and purpose of the article."
                    },
                    {
                        "role": "user",
                        "content": f"Article content: {content}\n\nAvailable hook templates:\n" + "\n".join(hooks)
                    }
                ],
                max_tokens=50
            )
            
            selected_hook = response.choices[0].message.content.strip()
            if selected_hook in hooks:
                return selected_hook
            return hooks[0]  # Fallback to first hook if no match found
        except Exception as e:
            print(f"Error generating hook: {str(e)}")
            return "" 

    def _create_tweet(self, content: str, url: str) -> Optional[str]:
        """Create a tweet-worthy summary from the processed content."""
        try:
            url_length = len(url) + 1
            max_tweet_length = 280 - url_length

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You're writing a tweet about an interesting article. Make it sound natural and engaging, like a real person sharing something they found fascinating.

Write the tweet following these guidelines:
1. Keep it under {max_tweet_length} characters
2. Use a conversational, friendly tone
3. Start with a hook or interesting angle
4. Use simple, clear language (7th grade level)
5. Include specific details or numbers when relevant
6. Break complex ideas into digestible bits
7. Sound genuinely excited about sharing this
8. End with a complete thought that makes people want to read more

Avoid:
- Formal or academic language
- Promotional buzzwords (revolutionary, game-changing, etc.)
- Hashtags, emojis, or excessive punctuation
- Robotic phrases like "it is worth noting" or "moreover"

Write like you're telling a friend about something cool you just read."""
                    },
                    {
                        "role": "user",
                        "content": f"""Here's an interesting article I found:
{content}

Write a natural-sounding tweet that makes people want to read this article. Keep it under {max_tweet_length} characters and make it sound like a real person sharing something fascinating."""
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )

            tweet = response.choices[0].message.content.strip()
            
            # Handle tweet length without truncation
            if len(tweet) > max_tweet_length:
                # Try to find a complete sentence that fits
                sentences = tweet.split('. ')
                final_tweet = ''
                for i, sentence in enumerate(sentences):
                    test_tweet = final_tweet + ('. ' if final_tweet else '') + sentence
                    if len(test_tweet) <= max_tweet_length:
                        final_tweet = test_tweet
                    else:
                        break
                tweet = final_tweet.strip()

            # Add the URL
            final_tweet = f"{tweet} {url}"
            return final_tweet

        except Exception as e:
            logger.error(f"Error creating tweet: {str(e)}")
            return None 