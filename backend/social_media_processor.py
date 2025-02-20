import yt_dlp
import pyktok
from openai import OpenAI
from typing import Optional
import re
import logging
import asyncio
from instaloader import Instaloader, Post
from urllib.parse import urlparse, parse_qs
import os
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class SocialMediaProcessor:
    def __init__(self):
        self.client = OpenAI()
        self.insta = Instaloader()
        # Create transcripts directory if it doesn't exist
        self.transcripts_dir = Path(__file__).parent / 'transcripts'
        self.transcripts_dir.mkdir(exist_ok=True)
        
    def process_url_sync(self, url: str) -> Optional[str]:
        """Synchronous wrapper for process_url."""
        return asyncio.run(self.process_url(url))

    async def process_url(self, url: str) -> Optional[str]:
        """Process social media URL and return a tweet-worthy summary."""
        try:
            platform = self._detect_platform(url)
            content = None

            if platform == 'tiktok':
                content = await self._process_tiktok(url)
            elif platform == 'instagram':
                content = await self._process_instagram(url)
            elif platform == 'youtube':
                content = await self._process_youtube(url)
            
            if not content:
                raise Exception(f"No content extracted from {platform} URL")

            # Save the full transcript
            transcript_path = await self._save_transcript(content, url, platform)
            if transcript_path:
                logger.info(f"Transcript saved to: {transcript_path}")

            return self._create_tweet(content, url, platform)

        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            return None

    def _detect_platform(self, url: str) -> str:
        """Detect social media platform from URL."""
        domain = urlparse(url).netloc.lower()
        if 'tiktok' in domain:
            return 'tiktok'
        elif 'instagram' in domain:
            return 'instagram'
        elif 'youtube' in domain or 'youtu.be' in domain:
            return 'youtube'
        else:
            raise ValueError("Unsupported platform")

    async def _process_tiktok(self, url: str) -> Optional[str]:
        """Process TikTok video and extract content including audio transcription."""
        try:
            # First, download the video with audio
            ydl_opts = {
                'format': 'best',  # Get best quality
                'quiet': True,
                'outtmpl': '%(title)s.%(ext)s',
                'extract_audio': True,  # We need audio for transcription
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get video information
                title = info.get('title', '')
                description = info.get('description', '')
                uploader = info.get('uploader', '')
                
                # Get the downloaded file path
                video_path = ydl.prepare_filename(info)
                
                # Convert video to audio and transcribe
                transcript = await self._transcribe_video(video_path)
                
                # Combine all information
                content = f"""
                Title: {title}
                Creator: {uploader}
                Description: {description}
                
                Transcript:
                {transcript}
                """
                
                # Clean up downloaded file
                try:
                    os.remove(video_path)
                except:
                    pass
                
                return content.strip()

        except Exception as e:
            logger.error(f"TikTok processing error: {str(e)}")
            return None

    async def _transcribe_video(self, video_path: str) -> str:
        """Transcribe video audio using OpenAI's Whisper model."""
        try:
            with open(video_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return "Transcription failed"

    async def _process_instagram(self, url: str) -> Optional[str]:
        """Process Instagram post and extract content including video transcription."""
        try:
            # Extract post ID from URL
            post_id = url.split('/')[-2]
            post = Post.from_shortcode(self.insta.context, post_id)
            
            # Gather post information
            caption = post.caption if post.caption else ''
            location = f"📍 {post.location}" if post.location else ''
            
            # Check if it's a video post
            if post.is_video:
                # Download video
                ydl_opts = {
                    'format': 'best',
                    'quiet': True,
                    'outtmpl': '%(title)s.%(ext)s',
                    'extract_audio': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(post.video_url, download=True)
                    video_path = ydl.prepare_filename(info)
                    
                    # Transcribe video
                    transcript = await self._transcribe_video(video_path)
                    
                    # Clean up video file
                    try:
                        os.remove(video_path)
                    except:
                        pass
                    
                    content = f"""
                    Caption: {caption}
                    Location: {location}
                    
                    Transcript:
                    {transcript}
                    """
            else:
                content = f"""
                Caption: {caption}
                Location: {location}
                """
            
            return content.strip()
        except Exception as e:
            logger.error(f"Instagram processing error: {str(e)}")
            return None

    async def _process_youtube(self, url: str) -> Optional[str]:
        """Process YouTube video and extract content with transcription."""
        try:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'outtmpl': '%(title)s.%(ext)s',
                'extract_audio': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get('title', '')
                description = info.get('description', '')
                uploader = info.get('uploader', '')
                
                # Get the downloaded file path
                video_path = ydl.prepare_filename(info)
                
                # Transcribe video
                transcript = await self._transcribe_video(video_path)
                
                # Clean up video file
                try:
                    os.remove(video_path)
                except:
                    pass
                
                content = f"""
                Title: {title}
                Creator: {uploader}
                Description: {description}
                
                Transcript:
                {transcript}
                """
                
                return content.strip()
        except Exception as e:
            logger.error(f"YouTube processing error: {str(e)}")
            return None

    async def _save_transcript(self, content: str, url: str, platform: str) -> str:
        """Save transcript to a file and return the file path."""
        try:
            # Create a safe filename from the URL
            safe_name = re.sub(r'[^\w\-_]', '_', url)
            filename = f"{platform}_{safe_name[:50]}.txt"
            filepath = self.transcripts_dir / filename

            # Save full content to file with clear sections
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write("=" * 50 + "\n\n")
                f.write(content)
                f.write("\n" + "=" * 50 + "\n")

            return str(filepath)
        except Exception as e:
            logger.error(f"Error saving transcript: {str(e)}")
            return None

    def _create_tweet(self, content: str, url: str, platform: str) -> str:
        """Create an engaging tweet from the social media content."""
        try:
            max_tweet_length = 280

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Create a concise, complete tweet from this content. The tweet should:
1. Be under 280 characters (no truncation)
2. Focus on the key benefit or main feature
3. Use active, engaging language
4. Include a clear value proposition
5. End with a complete thought
6. Use natural language that flows well
7. Avoid technical jargon unless necessary
8. Include a clear action or takeaway

Format: Start with the benefit/outcome, explain how, end with impact.
Do not include hashtags, emojis, URLs, or ellipsis."""
                    },
                    {
                        "role": "user",
                        "content": f"""Content from {platform}:
{content}

Create a complete tweet that captures the value proposition and key feature. Make sure it ends with a complete thought and fits in one tweet."""
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )

            tweet = response.choices[0].message.content.strip()
            
            # Ensure tweet is within length limit without truncating mid-sentence
            if len(tweet) > max_tweet_length:
                # Find the last complete sentence that fits
                sentences = tweet.split('. ')
                final_tweet = ''
                for sentence in sentences:
                    if len(final_tweet + sentence + '.') <= max_tweet_length:
                        final_tweet += sentence + '. '
                    else:
                        break
                tweet = final_tweet.strip()
            
            return tweet

        except Exception as e:
            logger.error(f"Error creating tweet: {str(e)}")
            return None 