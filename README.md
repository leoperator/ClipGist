# 🎬 ClipGist — Research Insight Generator

Deployed Link: https://clipgist-vuk3.onrender.com

ClipGist is a **Streamlit-powered** AI app that transforms YouTube videos, article links, and documents into rich, structured insights using **Google Gemini**.  
Paste links or upload documents, then ask questions to uncover deeper understanding.


<img width="1600" height="610" alt="image" src="https://github.com/user-attachments/assets/f7ea70b4-9654-44a8-9aa5-fac1a4a1b185" />
<img width="1600" height="633" alt="image" src="https://github.com/user-attachments/assets/4d514568-1f80-4be4-862d-f3aef1957676" />
<img width="1213" height="569" alt="image" src="https://github.com/user-attachments/assets/d9ea21d9-eb64-4470-960c-da4a238f4806" />
<img width="1433" height="698" alt="image" src="https://github.com/user-attachments/assets/2be71ca8-46cc-410f-8013-663c0c225c8f" />
<img width="1443" height="711" alt="image" src="https://github.com/user-attachments/assets/6f0b257a-a844-40b0-93c0-bc463d5b0d21" />
<img width="1448" height="689" alt="image" src="https://github.com/user-attachments/assets/42bee22a-82a4-47d2-a702-7aeac13c5a43" />

---


## ✨ Core Features

- **Paste a YouTube URL** → get transcript + structured Gemini analysis + key takeaways.
- **Enter an article URL** → ClipGist scrapes the content and generates insightful summaries.
- **Upload PDF or TXT** → extracts full text and analyzes it intelligently.
- **Structured Summary Output**: 
  - Summary overview
  - Key takeaways
  - Deeper insights
  - Expert commentary
  - Suggested follow-up questions
- **Interactive Q&A Chat**: Chat with the model using conversation context for accurate responses.

---

## 🛠️ Tech Stack

**Framework & UI**
- [Streamlit](https://streamlit.io/) — Web app frontend & backend

**AI Model**
- [Google Gemini API](https://ai.google.dev/) — Generates structured, insightful summaries

**Content Extraction**
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Retrieves YouTube video info (title, channel)  
- [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) — Fetches YouTube captions/transcripts  
- [newspaper3k](https://newspaper.readthedocs.io/) — Extracts and parses article text  
- [PyMuPDF](https://pymupdf.readthedocs.io/) — Extracts text and images from PDFs

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
