# 🎬 ClipGist: YouTube Video Insight Generator

**ClipGist** is a Streamlit-powered app that summarizes YouTube videos using AI. Just paste a YouTube link, and get a structured summary of the video, key insights, and even a chat interface to dive deeper into the content.

---

## 🚀 Features

- 📌 **YouTube Summarization**: Just paste a URL — we’ll extract the transcript and generate a clean, structured summary.
- 🧠 **Gemini AI-Powered**: Uses Gemini models to analyze and understand video content.
- 🖼️ **Scene Frame Extraction**: Automatically detects key scenes using PySceneDetect for better visual context.
- 💬 **Interactive Chat**: Ask questions about the video and get accurate answers from the model.

---

## 📦 Requirements

Install dependencies using:

```
pip install -r requirements.txt
```

You'll also need a valid Gemini API key. Copy ```.env.example``` to ```.env``` and add your key:

```
GOOGLE_API_KEY = YOUR_GOOGLE_API_KEY_HERE
```

## 🖥️ Running Locally

```
streamlit run main.py
```

---

## 🧠 How it Works
- Transcript Extraction – We grab the full transcript using YouTube's transcript API.
- Scene Detection – PySceneDetect slices the video into key scenes and extracts thumbnails.
- Gemini Inference – A structured prompt is created with title, transcript, and visual context.
- LLM Response – Gemini returns a high-quality summary with subpoints, insights, and follow-ups.
