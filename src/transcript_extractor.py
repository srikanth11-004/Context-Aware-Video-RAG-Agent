from youtube_transcript_api import YouTubeTranscriptApi as YTAPI
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Optional
import re


class TranscriptExtractor:
    """Extracts transcripts from YouTube videos with timestamp metadata."""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.
        
        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Convert seconds to MM:SS or HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    def get_transcript(self, video_url: str) -> Dict:
        """
        Fetch transcript for a YouTube video.
        
        Returns:
            Dict with video_id, transcript segments, and full_text
        """
        video_id = self.extract_video_id(video_url)
        
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")
        
        try:
            # Fetch transcript - try multiple languages
            try:
                transcript_list = YTAPI().fetch(video_id, languages=['en'])
            except:
                # Try other common languages if English fails
                transcript_list = YTAPI().fetch(video_id, languages=['hi', 'es', 'fr', 'de', 'pt', 'ja', 'ko'])
            
            # Process segments
            segments = []
            full_text = []
            
            for entry in transcript_list:
                segment = {
                    'text': entry.text,
                    'start': entry.start,
                    'duration': entry.duration,
                    'timestamp': self.format_timestamp(entry.start)
                }
                segments.append(segment)
                full_text.append(entry.text)
            
            return {
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'segments': segments,
                'full_text': ' '.join(full_text),
                'total_segments': len(segments)
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch transcript: {str(e)}")
    
    def get_transcript_with_timestamps(self, video_url: str) -> List[Dict]:
        """
        Get transcript as a list of timestamped chunks.
        Useful for preserving timestamp context during chunking.
        """
        transcript_data = self.get_transcript(video_url)
        return transcript_data['segments']


# Quick test function
if __name__ == "__main__":
    extractor = TranscriptExtractor()
    
    # Test with a sample video
    test_url = "https://www.youtube.com/watch?v=aircAruvnKk"  # 3Blue1Brown neural networks
    
    try:
        result = extractor.get_transcript(test_url)
        print(f"✅ Video ID: {result['video_id']}")
        print(f"✅ Total segments: {result['total_segments']}")
        print(f"✅ First segment: {result['segments'][0]}")
        print(f"✅ Text preview: {result['full_text'][:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
