import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.transcript_extractor import TranscriptExtractor
from src.chunker import SmartChunker
from src.vector_store import VectorStore
from src.rag_engine import RAGEngine

# Page config
st.set_page_config(
    page_title="YouTube Lecture Synthesizer",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF0000;
        text-align: center;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .timestamp-link {
        color: #FF0000;
        font-weight: bold;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore()
    st.session_state.rag_engine = RAGEngine(st.session_state.vector_store)
    st.session_state.extractor = TranscriptExtractor()
    st.session_state.chunker = SmartChunker()
    st.session_state.current_video_id = None
    st.session_state.chat_history = []

# Header
st.markdown('<div class="main-header">🎓 YouTube Lecture Synthesizer</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Video Management")
    
    # Video input
    video_url = st.text_input("YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button(" Process Video", type="primary"):
        if video_url:
            with st.spinner("Processing video..."):
                try:
                    # Extract video ID
                    video_id = st.session_state.extractor.extract_video_id(video_url)
                    
                    # Check if already processed
                    existing_videos = st.session_state.vector_store.list_videos()
                    video_exists = any(v['video_id'] == video_id for v in existing_videos)
                    
                    if video_exists:
                        st.warning("⚠️ Video already processed!")
                        st.session_state.current_video_id = video_id
                    else:
                        # Process video
                        st.info("📥 Extracting transcript...")
                        transcript_data = st.session_state.extractor.get_transcript(video_url)
                        
                        st.info("✂️ Chunking transcript...")
                        chunks = st.session_state.chunker.chunk_transcript(transcript_data['segments'])
                        
                        st.info("💾 Storing embeddings...")
                        st.session_state.vector_store.add_documents(
                            chunks=chunks,
                            video_id=transcript_data['video_id'],
                            video_url=transcript_data['video_url']
                        )
                        
                        st.session_state.current_video_id = video_id
                        st.success(f"✅ Processed {len(chunks)} chunks!")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("Please enter a YouTube URL")
    
    st.markdown("---")
    
    # Show processed videos
    st.subheader("Processed Videos")
    stats = st.session_state.vector_store.get_collection_stats()
    
    if stats['total_videos'] > 0:
        st.metric("Total Videos", stats['total_videos'])
        st.metric("Total Chunks", stats['total_chunks'])
        
        for video in stats['videos']:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📹 {video['video_id'][:15]}...")
            with col2:
                if st.button("🗑️", key=f"delete_{video['video_id']}"):
                    st.session_state.vector_store.delete_video(video['video_id'])
                    st.rerun()
    else:
        st.info("No videos processed yet")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Video Player")
    
    if st.session_state.current_video_id:
        # Embed YouTube video
        video_url_embed = f"https://www.youtube.com/embed/{st.session_state.current_video_id}"
        st.markdown(f"""
        <iframe width="100%" height="400" 
        src="{video_url_embed}" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
        </iframe>
        """, unsafe_allow_html=True)
        
        # Summary button
        if st.button("📝 Generate Video Summary"):
            with st.spinner("Generating summary..."):
                try:
                    summary = st.session_state.rag_engine.summarize_video(
                        st.session_state.current_video_id
                    )
                    st.info(summary)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("👈 Process a video to start")

with col2:
    st.header("💬 Ask Questions")
    
    # Chat interface
    question = st.text_input("Your question:", placeholder="What is explained in this video?")
    
    col_a, col_b = st.columns([1, 1])
    with col_a:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    with col_b:
        clear_button = st.button("🗑️ Clear Chat", use_container_width=True)
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask_button and question:
        if st.session_state.current_video_id:
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.rag_engine.query(question, top_k=3)
                    st.session_state.chat_history.append({
                        'question': question,
                        'answer': result['answer'],
                        'sources': result['sources']
                    })
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please process a video first!")
    
    # Display chat history
    st.markdown("---")
    
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container():
                st.markdown(f"**❓ Q:** {chat['question']}")
                st.markdown(f"**💡 A:** {chat['answer']}")
                
                # Show sources
                with st.expander("📚 View Sources"):
                    for j, source in enumerate(chat['sources'], 1):
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>Source {j}</strong><br>
                            <span class="timestamp-link">⏱️ {source['timestamp_range']}</span><br>
                            <small>{source['text_preview']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
    else:
        st.info("💭 Ask a question to get started!")


