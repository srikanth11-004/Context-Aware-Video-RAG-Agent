"""
Quick test script to verify the entire RAG pipeline.
Run this to ensure everything is working before using the UI.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.transcript_extractor import TranscriptExtractor
from src.chunker import SmartChunker
from src.vector_store import VectorStore
from src.rag_engine import RAGEngine


def test_pipeline():
    """Test the complete RAG pipeline."""
    
    print("=" * 60)
    print("TESTING YOUTUBE LECTURE SYNTHESIZER PIPELINE")
    print("=" * 60)
    print()

    # Test video (3Blue1Brown - Neural Networks)
    test_url = "https://www.youtube.com/watch?v=aircAruvnKk"
    
    try:
        # Step 1: Initialize components
        print("[1/6] Initializing components...")
        extractor = TranscriptExtractor()
        chunker = SmartChunker(chunk_size=500, chunk_overlap=100)
        vector_store = VectorStore()
        rag_engine = RAGEngine(vector_store)
        print("   SUCCESS: All components initialized")
        
        # Step 2: Extract transcript
        print("\n[2/6] Extracting transcript...")
        transcript_data = extractor.get_transcript(test_url)
        print(f"   SUCCESS: Extracted {transcript_data['total_segments']} segments")
        print(f"   Video ID: {transcript_data['video_id']}")
        
        # Step 3: Chunk transcript
        print("\n[3/6] Chunking transcript...")
        chunks = chunker.chunk_transcript(transcript_data['segments'])
        stats = chunker.get_chunk_stats(chunks)
        print(f"   SUCCESS: Created {stats['total_chunks']} chunks")
        print(f"   Avg chunk length: {stats['avg_chunk_length']:.0f} chars")
        
        # Step 4: Store in vector database
        print("\n[4/6] Storing in vector database...")
        vector_store.add_documents(
            chunks=chunks,
            video_id=transcript_data['video_id'],
            video_url=transcript_data['video_url']
        )
        print("   SUCCESS: Embeddings stored successfully")
        
        # Step 5: Test queries
        print("\n[5/6] Testing RAG queries...")
        test_questions = [
            "What is a neural network?",
            "How do neurons work in neural networks?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n   Question {i}: {question}")
            result = rag_engine.query(question, top_k=2)
            print(f"   Answer: {result['answer'][:150]}...")
            print(f"   Sources: {result['num_sources']} chunks retrieved")
        
        # Step 6: Collection stats
        print("\n[6/6] Vector store statistics...")
        collection_stats = vector_store.get_collection_stats()
        print(f"   Total videos: {collection_stats['total_videos']}")
        print(f"   Total chunks: {collection_stats['total_chunks']}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYou can now run: streamlit run app.py")
        
        return True
    
    except Exception as e:
        print(f"\nTEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
