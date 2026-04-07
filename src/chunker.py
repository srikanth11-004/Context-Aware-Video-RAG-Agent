from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken


class SmartChunker:
    """
    Intelligent chunking that preserves timestamp information.
    Creates overlapping chunks while maintaining timestamp ranges.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_transcript(self, segments: List[Dict]) -> List[Dict]:
        """
        Chunk transcript segments while preserving timestamp metadata.
        
        Args:
            segments: List of transcript segments with 'text', 'start', 'timestamp'
        
        Returns:
            List of chunks with text, start_time, end_time, and timestamp_range
        """
        chunks = []
        current_chunk = []
        current_length = 0
        
        for segment in segments:
            segment_text = segment['text']
            segment_length = len(segment_text)
            
            # If adding this segment exceeds chunk size, save current chunk
            if current_length + segment_length > self.chunk_size and current_chunk:
                chunks.append(self._create_chunk(current_chunk))
                
                # Keep overlap: retain last few segments
                overlap_length = 0
                overlap_segments = []
                for seg in reversed(current_chunk):
                    overlap_length += len(seg['text'])
                    overlap_segments.insert(0, seg)
                    if overlap_length >= self.chunk_overlap:
                        break
                
                current_chunk = overlap_segments
                current_length = overlap_length
            
            current_chunk.append(segment)
            current_length += segment_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk))
        
        return chunks
    
    def _create_chunk(self, segments: List[Dict]) -> Dict:
        """Create a chunk from segments with metadata."""
        text = ' '.join([seg['text'] for seg in segments])
        start_time = segments[0]['start']
        end_time = segments[-1]['start'] + segments[-1].get('duration', 0)
        start_timestamp = segments[0]['timestamp']
        end_timestamp = self._format_timestamp(end_time)
        
        return {
            'text': text,
            'start_time': start_time,
            'end_time': end_time,
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp,
            'timestamp_range': f"{start_timestamp} - {end_timestamp}",
            'num_segments': len(segments)
        }
    
    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Convert seconds to MM:SS or HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    def get_chunk_stats(self, chunks: List[Dict]) -> Dict:
        """Get statistics about the chunks."""
        if not chunks:
            return {}
        
        chunk_lengths = [len(chunk['text']) for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'avg_chunk_length': sum(chunk_lengths) / len(chunk_lengths),
            'min_chunk_length': min(chunk_lengths),
            'max_chunk_length': max(chunk_lengths),
            'total_duration': chunks[-1]['end_time'] if chunks else 0
        }


# Test function
if __name__ == "__main__":
    from transcript_extractor import TranscriptExtractor
    
    extractor = TranscriptExtractor()
    chunker = SmartChunker(chunk_size=500, chunk_overlap=100)
    
    # Test with a video
    test_url = "https://www.youtube.com/watch?v=aircAruvnKk"
    
    try:
        print("📥 Extracting transcript...")
        transcript_data = extractor.get_transcript(test_url)
        
        print("✂️ Chunking transcript...")
        chunks = chunker.chunk_transcript(transcript_data['segments'])
        
        print(f"\n✅ Created {len(chunks)} chunks")
        
        # Show stats
        stats = chunker.get_chunk_stats(chunks)
        print(f"\n📊 Chunk Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Show first chunk
        print(f"\n📄 First Chunk:")
        print(f"  Timestamp: {chunks[0]['timestamp_range']}")
        print(f"  Text: {chunks[0]['text'][:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
