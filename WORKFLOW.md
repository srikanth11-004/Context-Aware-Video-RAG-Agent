# YouTube Lecture Synthesizer - Workflow

---

**Step 1: User Inputs a YouTube URL (app.py)**

The Streamlit UI takes a YouTube URL from the user and triggers the processing pipeline when "Process Video" is clicked.

---

**Step 2: Transcript Extraction (transcript_extractor.py)**

- `extract_video_id()` parses the URL to get the 11-character video ID (e.g., dQw4w9WgXcQ)
- `get_transcript()` calls the youtube_transcript_api library to fetch the auto-generated or manual captions
- Each segment comes back with text, start (seconds), and duration
- Timestamps are formatted into human-readable MM:SS or HH:MM:SS format

---

**Step 3: Smart Chunking (chunker.py)**

- The raw transcript segments are grouped into overlapping chunks of ~1000 characters with 200-character overlap
- Each chunk preserves its timestamp_range (e.g., "2:30 - 3:45") so answers can be traced back to the video
- Overlap ensures context isn't lost at chunk boundaries

---

**Step 4: Embedding & Storage (vector_store.py)**

- The sentence-transformers/all-MiniLM-L6-v2 model converts each chunk's text into a numerical vector (embedding)
- These embeddings + metadata (video_id, timestamps, text) are stored in ChromaDB, a local persistent vector database saved in ./data/chroma_db/
- Each chunk gets a unique ID like VIDEO_ID_chunk_0, VIDEO_ID_chunk_1, etc.

---

**Step 5: User Asks a Question (app.py → rag_engine.py)**

When the user types a question and clicks "Ask":

- **Retrieve** — the question is also embedded using the same model, then ChromaDB finds the top-3 most semantically similar chunks via cosine similarity
- **Build Context** — the retrieved chunks are assembled into a prompt with their timestamps
- **Generate Answer** — the context + question is sent to either Gemini (gemini-2.5-flash) or OpenAI (gpt-3.5-turbo) depending on your .env config
- **Return Sources** — the answer is shown along with the source timestamps so you can jump to that part of the video

---

**Step 6: Video Summary (optional)**

Clicking "Generate Video Summary" samples up to 10 evenly-distributed chunks from the video and sends them to the LLM to produce a structured summary.

---

**Data Flow Diagram**

```
YouTube URL
    ↓
TranscriptExtractor  →  raw segments [{text, start, duration}]
    ↓
SmartChunker         →  chunks [{text, timestamp_range, start_time}]
    ↓
VectorStore          →  embeddings stored in ChromaDB
    ↓
User Question
    ↓
VectorStore.search() →  top-K similar chunks
    ↓
RAGEngine            →  LLM generates answer with timestamp references
    ↓
Streamlit UI         →  displays answer + clickable sources
```
