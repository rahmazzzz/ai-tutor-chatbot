# app/services/summarize_video.py
import logging
from fastapi import HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from app.core.config import settings
from app.clients.gemini_client import GeminiClient

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Instantiate Gemini client
gemini_client = GeminiClient(model_name="gemini-1.5-flash")


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL (supports youtu.be and youtube.com)."""
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    if "youtube.com" in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]
    return None


def get_transcript(video_url: str) -> str:
    """Extract transcript from YouTube video if available."""
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL, could not extract video_id")

        logger.info(f"Extracting transcript for video_id={video_id}")

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        logger.info(f"Transcript extracted successfully (length={len(text)})")
        return text

    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        logger.warning(f"No transcript available for {video_url}: {e}")
        raise HTTPException(status_code=404, detail=f"No transcript available for this video: {e}")

    except Exception as e:
        logger.error(f"Transcript fetch failed for {video_url}: {e}")
        raise HTTPException(status_code=400, detail=f"Transcript not available: {e}")


async def summarize_text(text: str) -> str:
    """Summarize transcript using GeminiClient."""
    try:
        prompt = f"Summarize the following YouTube video transcript:\n\n{text}"
        response = await gemini_client.generate(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {e}")


async def summarize_video_service(url: str) -> str:
    """Main service function to get transcript and summarize."""
    try:
        transcript = get_transcript(url)
        return await summarize_text(transcript)
    except HTTPException as e:
        logger.warning(f"Falling back: {e.detail}")
        # fallback: just return a message instead of crashing
        return f"No transcript available for this video. Please try another one.\nURL: {url}"
