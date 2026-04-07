# YouTube Lecture Synthesizer

A RAG-powered application that extracts YouTube lecture transcripts and enables intelligent Q&A with timestamp navigation.

## Features
- Extract transcripts from YouTube videos/playlists
- Semantic search through lecture content
- Timestamp-aware responses
- Interactive UI with embedded video player

## Setup

1. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
- Copy `.env.example` to `.env`
- Add your OpenAI API key

4. **Run the application:**
```bash
streamlit run app.py
```

## Project Structure
```
RAG/
├── src/              # Core modules
├── data/             # Cached transcripts & embeddings
├── notebooks/        # Jupyter notebooks for testing
├── tests/            # Unit tests
├── app.py            # Streamlit UI
└── requirements.txt
```
