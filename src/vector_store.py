from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
import json


class VectorStore:
    """
    Manages embeddings and vector search using ChromaDB.
    Uses sentence-transformers for free, local embeddings.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db", 
                 collection_name: str = "youtube_lectures",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print("Embedding model loaded")
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "YouTube lecture transcripts with timestamps"}
        )
    
    def add_documents(self, chunks: List[Dict], video_id: str, video_url: str):
        """
        Add chunked transcript documents to the vector store.
        
        Args:
            chunks: List of chunks from SmartChunker
            video_id: YouTube video ID
            video_url: Full YouTube URL
        """
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        # Prepare metadata
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            metadata = {
                'video_id': video_id,
                'video_url': video_url,
                'chunk_index': i,
                'start_time': chunk['start_time'],
                'end_time': chunk['end_time'],
                'start_timestamp': chunk['start_timestamp'],
                'end_timestamp': chunk['end_timestamp'],
                'timestamp_range': chunk['timestamp_range']
            }
            metadatas.append(metadata)
            ids.append(f"{video_id}_chunk_{i}")
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"Added {len(chunks)} chunks to vector store")
    
    def search(self, query: str, top_k: int = 4) -> List[Dict]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: User's question
            top_k: Number of results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                result = {
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def delete_video(self, video_id: str):
        """Delete all chunks for a specific video."""
        # Get all IDs for this video
        results = self.collection.get(
            where={"video_id": video_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"Deleted {len(results['ids'])} chunks for video {video_id}")
    
    def list_videos(self) -> List[Dict]:
        """List all videos in the vector store."""
        all_data = self.collection.get()
        
        if not all_data['metadatas']:
            return []
        
        # Extract unique videos
        videos = {}
        for metadata in all_data['metadatas']:
            video_id = metadata['video_id']
            if video_id not in videos:
                videos[video_id] = {
                    'video_id': video_id,
                    'video_url': metadata['video_url'],
                    'chunk_count': 0
                }
            videos[video_id]['chunk_count'] += 1
        
        return list(videos.values())
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        count = self.collection.count()
        videos = self.list_videos()
        
        return {
            'total_chunks': count,
            'total_videos': len(videos),
            'videos': videos
        }
