import logging
from typing import Optional
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

def extract_youtube_transcript(video_url: str) -> Optional[str]:
    """
    Extracts the transcript from a YouTube video URL.
    
    Args:
        video_url (str): The full URL of the YouTube video.
        
    Returns:
        Optional[str]: The full text transcript, or None if it fails.
    """
    logger.info(f"Attempting to extract transcript for: {video_url}")
    
    try:
        # Extract the video ID from the URL
        parsed_url = urlparse(video_url)
        video_id = parse_qs(parsed_url.query).get("v")
        
        if not video_id:
            # Handle shortened youtu.be URLs
            if parsed_url.netloc == "youtu.be":
                video_id = [parsed_url.path.lstrip("/")]
            else:
                logger.warning("Could not extract video ID from URL.")
                return None
                
        video_id = video_id[0]
        
        # Initialize the API client and fetch the transcript
        yt_client = YouTubeTranscriptApi()
        transcript_list = yt_client.fetch(video_id)
        
        # Combine all the text chunks into one clean string using the .text attribute
        full_text = " ".join([entry.text for entry in transcript_list])
        
        logger.info(f"Successfully extracted {len(full_text)} characters from video.")
        return full_text

    except Exception as e:
        logger.error(f"Failed to get transcript for {video_url}: {str(e)}")
        return None

# --- Quick Test Block ---
if __name__ == "__main__":
    # A short video about LangGraph
    test_vid = "https://www.youtube.com/watch?v=R8KB-Zcynxc"
    print(f"Testing YouTube extraction on: {test_vid}\n")
    
    transcript = extract_youtube_transcript(test_vid)
    if transcript:
        print("Success! Preview:\n")
        print(transcript[:500] + "...\n")
    else:
        print("Failed to get transcript. Does the video have closed captions?")