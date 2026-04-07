from typing import List, Dict
import re
from urllib.parse import urlparse, parse_qs


class PlaylistProcessor:
    """Process YouTube playlists and batch operations."""
    
    def __init__(self, extractor, chunker, vector_store):
        self.extractor = extractor
        self.chunker = chunker
        self.vector_store = vector_store
    
    @staticmethod
    def extract_playlist_id(url: str) -> str:
        """Extract playlist ID from YouTube URL."""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        if 'list' in query_params:
            return query_params['list'][0]
        
        raise ValueError("Invalid playlist URL")
    
    def process_video(self, video_url: str) -> Dict:
        """
        Process a single video: extract, chunk, and store.
        
        Returns:
            Dict with status and metadata
        """
        try:
            # Extract video ID
            video_id = self.extractor.extract_video_id(video_url)
            
            # Check if already exists
            existing_videos = self.vector_store.list_videos()
            if any(v['video_id'] == video_id for v in existing_videos):
                return {
                    'status': 'skipped',
                    'video_id': video_id,
                    'message': 'Video already processed'
                }
            
            # Extract transcript
            transcript_data = self.extractor.get_transcript(video_url)
            
            # Chunk
            chunks = self.chunker.chunk_transcript(transcript_data['segments'])
            
            # Store
            self.vector_store.add_documents(
                chunks=chunks,
                video_id=transcript_data['video_id'],
                video_url=transcript_data['video_url']
            )
            
            return {
                'status': 'success',
                'video_id': video_id,
                'chunks': len(chunks),
                'message': f'Processed {len(chunks)} chunks'
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'video_id': video_url,
                'message': str(e)
            }
    
    def process_multiple_videos(self, video_urls: List[str]) -> List[Dict]:
        """
        Process multiple videos in batch.
        
        Returns:
            List of results for each video
        """
        results = []
        
        for i, url in enumerate(video_urls, 1):
            print(f"\n📹 Processing video {i}/{len(video_urls)}: {url}")
            result = self.process_video(url)
            results.append(result)
            
            print(f"   Status: {result['status']} - {result['message']}")
        
        return results


class TranscriptExporter:
    """Export transcripts in various formats."""
    
    @staticmethod
    def to_text(segments: List[Dict], include_timestamps: bool = True) -> str:
        """Export transcript as plain text."""
        lines = []
        
        for segment in segments:
            if include_timestamps:
                lines.append(f"[{segment['timestamp']}] {segment['text']}")
            else:
                lines.append(segment['text'])
        
        return '\n'.join(lines)
    
    @staticmethod
    def to_srt(segments: List[Dict]) -> str:
        """Export transcript as SRT subtitle format."""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start_time = TranscriptExporter._format_srt_time(segment['start'])
            end_time = TranscriptExporter._format_srt_time(
                segment['start'] + segment.get('duration', 0)
            )
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(segment['text'])
            srt_lines.append("")
        
        return '\n'.join(srt_lines)
    
    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


# Test script
if __name__ == "__main__":
    from transcript_extractor import TranscriptExtractor
    from chunker import SmartChunker
    from vector_store import VectorStore
    
    # Initialize
    extractor = TranscriptExtractor()
    chunker = SmartChunker()
    vector_store = VectorStore()
    
    processor = PlaylistProcessor(extractor, chunker, vector_store)
    exporter = TranscriptExporter()
    
    # Test with multiple videos
    test_videos = [
        "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown NN
    ]
    
    print("🎬 Processing videos...")
    results = processor.process_multiple_videos(test_videos)
    
    print("\n📊 Summary:")
    for result in results:
        print(f"  {result['video_id']}: {result['status']}")
    
    # Test export
    print("\n📄 Testing export...")
    transcript_data = extractor.get_transcript(test_videos[0])
    
    # Export as text
    text_export = exporter.to_text(transcript_data['segments'][:5])
    print("\nText format (first 5 segments):")
    print(text_export)
