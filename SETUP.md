# 🚀 Quick Setup Guide

## Step 1: Install Python

Check if Python is installed:
```bash
py --version
```

If not installed, download from: https://www.python.org/downloads/

## Step 2: Create Virtual Environment

```bash
py -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal.

## Step 3: Install Dependencies

```bash
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

This will take a few minutes. It will download:
- LangChain (RAG framework)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- Streamlit (UI)
- Google Generative AI (Gemini)

## Step 4: Get Gemini API Key (FREE!)

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

## Step 5: Configure Environment

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Open `.env` in notepad and add your key:
```
GEMINI_API_KEY=your_actual_key_here
LLM_PROVIDER=gemini
```

## Step 6: Test the Pipeline

```bash
py test_pipeline.py
```

This will:
- Extract a sample video transcript
- Create embeddings
- Test the RAG system
- Verify everything works

## Step 7: Run the App!

```bash
streamlit run app.py
```

The app will open at: http://localhost:8501

---

## 🎯 Quick Start Usage

1. **Paste a YouTube URL** (e.g., educational video)
2. **Click "Process Video"** (takes 30-60 seconds)
3. **Ask questions** about the video content
4. **Click timestamps** to jump to relevant parts

---

## 🐛 Troubleshooting

### "py is not recognized"
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation

### "GEMINI_API_KEY not found"
- Make sure you created `.env` file (not `.env.example`)
- Check that the key is on the line: `GEMINI_API_KEY=your_key`
- No spaces around the `=` sign

### "No transcript available"
- Some videos don't have transcripts
- Try a different video (educational channels usually have them)

### "Module not found"
- Make sure virtual environment is activated: `venv\Scripts\activate`
- Reinstall dependencies: `py -m pip install -r requirements.txt`

---

## 📚 Recommended Test Videos

Try these educational videos:
- 3Blue1Brown Neural Networks: `https://www.youtube.com/watch?v=aircAruvnKk`
- Khan Academy: Any math/science video
- MIT OpenCourseWare: Lecture videos
- Crash Course: Any subject

---

## 💡 Tips

- First video processing takes longer (downloads embedding model)
- Processed videos are cached - instant on second use
- Use specific questions for best results
- Check the "Sources" to verify answers

---

## 🎓 Next Steps

After basic setup works:
1. Try the Jupyter notebook: `notebooks/experiment.ipynb`
2. Process multiple videos
3. Experiment with different chunk sizes in `src/config.py`
4. Customize the UI in `app.py`

---

Need help? Check the main README.md or create an issue!
