import asyncio
from crawl4ai import AsyncWebCrawler
from typing import Optional
import nest_asyncio
import re
from openai import OpenAI
import os
import random
from hooks_config import VIRAL_HOOKS

# Enable nested event loops
nest_asyncio.apply()

class ArticleProcessor:
    def __init__(self):
        self.client = OpenAI()  # Will use OPENAI_API_KEY from environment

    async def process_url(self, url: str) -> Optional[str]:
        """Process an article URL and return a tweet-worthy summary."""
        try:
            # Crawl the article with basic configuration
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                    max_pages=1,
                    markdown=True,
                    timeout=30,
                    extract_content=True
                )

            if not result or not result.markdown:
                raise Exception("No content extracted from URL")

            # Clean up the content
            content = result.markdown
            content = re.sub(r'http\S+', '', content)
            content = re.sub(r'[#*`_~\[\]\(\)\{\}]', '', content)
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = re.sub(r'\s+', ' ', content)
            
            # Get first few paragraphs
            paragraphs = content.split('\n\n')
            main_content = '\n\n'.join(paragraphs[:3])

            # Create tweet using GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Create a single engaging tweet from the article content. The tweet should:
1. Be under 280 characters
2. Be written in a natural, human voice
3. Include the most interesting point
4. Be engaging but professional
5. End with the article URL
6. Use some engaging hook/words at the begining
Do not use hashtags or emojis."""
                    },
                    {
                        "role": "user",
                        "content": f"Article content:\n{main_content}\n\nURL: {url}\n\nCreate a single tweet that would make people want to read this article."
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )

            tweet = response.choices[0].message.content.strip()
            
            # Ensure URL is at the end and tweet is within limits
            if url not in tweet:
                tweet = f"{tweet[:200]}... {url}"
            if len(tweet) > 280:
                tweet = f"{tweet[:277]}..."

            return tweet

        except Exception as e:
            print(f"Error processing article: {str(e)}")
            return None

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