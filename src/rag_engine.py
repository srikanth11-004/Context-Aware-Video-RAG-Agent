from typing import List, Dict, Optional
from openai import OpenAI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


class RAGEngine:
    """
    RAG Query Engine that retrieves relevant chunks and generates answers.
    Supports both OpenAI and Google Gemini.
    """
    
    def __init__(self, vector_store, provider: str = None, model: str = None, temperature: float = 0.7):
        self.vector_store = vector_store
        self.temperature = temperature
        
        # Determine provider
        self.provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        
        # Initialize based on provider
        if self.provider == "gemini":
            self.model = model or "models/gemini-2.5-flash"
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
            print(f"Using Gemini: {self.model}")
        
        elif self.provider == "openai":
            self.model = model or "gpt-3.5-turbo"
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            self.client = OpenAI(api_key=api_key)
            print(f"Using OpenAI: {self.model}")
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Use 'gemini' or 'openai'")
    
    def query(self, question: str, top_k: int = 4, include_timestamps: bool = True) -> Dict:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            include_timestamps: Whether to include timestamps in response
        
        Returns:
            Dict with answer, sources, and metadata
        """
        # Step 1: Retrieve relevant chunks
        print(f"Searching for relevant content...")
        retrieved_chunks = self.vector_store.search(question, top_k=top_k)
        
        if not retrieved_chunks:
            return {
                'answer': "I couldn't find any relevant information in the video transcripts.",
                'sources': [],
                'question': question
            }
        
        # Step 2: Build context from retrieved chunks
        context = self._build_context(retrieved_chunks, include_timestamps)
        
        # Step 3: Generate answer using LLM
        print(f"Generating answer...")
        answer = self._generate_answer(question, context, include_timestamps)
        
        # Step 4: Format sources
        sources = self._format_sources(retrieved_chunks)
        
        return {
            'answer': answer,
            'sources': sources,
            'question': question,
            'num_sources': len(sources)
        }
    
    def _build_context(self, chunks: List[Dict], include_timestamps: bool) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            text = chunk['text']
            
            if include_timestamps:
                timestamp = metadata['timestamp_range']
                context_parts.append(f"[Timestamp: {timestamp}]\n{text}")
            else:
                context_parts.append(text)
        
        return "\n\n---\n\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str, include_timestamps: bool) -> str:
        """Generate answer using configured LLM provider."""
        
        system_prompt = """You are a helpful AI assistant that answers questions about YouTube lecture content.

Your task:
1. Answer the user's question based ONLY on the provided transcript context
2. Be concise and accurate
3. If timestamps are provided, reference them in your answer (e.g., "At 5:30, the professor explains...")
4. If the context doesn't contain enough information, say so clearly
5. Do not make up information not present in the context

Format your response naturally and conversationally."""

        user_prompt = f"""Context from video transcript:
{context}

Question: {question}

Answer the question based on the context above."""

        try:
            if self.provider == "gemini":
                # Gemini API
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.temperature,
                        max_output_tokens=500,
                    )
                )
                return response.text.strip()
            
            else:
                # OpenAI API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format source information for display."""
        sources = []
        
        for chunk in chunks:
            metadata = chunk['metadata']
            source = {
                'video_url': metadata['video_url'],
                'timestamp_range': metadata['timestamp_range'],
                'start_time': metadata['start_time'],
                'text_preview': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            }
            sources.append(source)
        
        return sources
    
    def summarize_video(self, video_id: str, max_chunks: int = 10) -> str:
        """
        Generate a summary of the entire video.
        
        Args:
            video_id: YouTube video ID
            max_chunks: Maximum number of chunks to use for summary
        """
        # Get all chunks for this video
        all_data = self.vector_store.collection.get(
            where={"video_id": video_id}
        )
        
        if not all_data['documents']:
            return "No transcript found for this video."
        
        # Take evenly distributed chunks
        total_chunks = len(all_data['documents'])
        step = max(1, total_chunks // max_chunks)
        selected_texts = [all_data['documents'][i] for i in range(0, total_chunks, step)][:max_chunks]
        
        context = "\n\n".join(selected_texts)
        
        system_prompt = """You are a helpful AI assistant that summarizes YouTube lectures.
Create a comprehensive but concise summary of the lecture content provided."""

        user_prompt = f"""Transcript excerpts from a lecture:

{context}

Please provide a well-structured summary of this lecture, covering the main topics and key points."""

        try:
            if self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=800,
                    )
                )
                return response.text.strip()
            
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"


# Test function
if __name__ == "__main__":
    from transcript_extractor import TranscriptExtractor
    from chunker import SmartChunker
    from vector_store import VectorStore
    
    # Initialize components
    extractor = TranscriptExtractor()
    chunker = SmartChunker()
    vector_store = VectorStore()
    rag_engine = RAGEngine(vector_store)
    
    # Test video
    test_url = "https://www.youtube.com/watch?v=aircAruvnKk"
    
    try:
        # Check if video already in store
        stats = vector_store.get_collection_stats()
        
        if stats['total_chunks'] == 0:
            print("📥 Processing video (first time)...")
            transcript_data = extractor.get_transcript(test_url)
            chunks = chunker.chunk_transcript(transcript_data['segments'])
            vector_store.add_documents(
                chunks=chunks,
                video_id=transcript_data['video_id'],
                video_url=transcript_data['video_url']
            )
        
        # Test queries
        test_questions = [
            "What is a neural network?",
            "How does backpropagation work?",
            "What are the layers in a neural network?"
        ]
        
        for question in test_questions:
            print(f"\n{'='*60}")
            print(f"❓ Question: {question}")
            print(f"{'='*60}")
            
            result = rag_engine.query(question, top_k=3)
            
            print(f"\n💡 Answer:\n{result['answer']}")
            print(f"\n📚 Sources ({result['num_sources']}):")
            for i, source in enumerate(result['sources'], 1):
                print(f"  {i}. [{source['timestamp_range']}] {source['text_preview']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
