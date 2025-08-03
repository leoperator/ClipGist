import os
import streamlit as st
import subprocess
import google.generativeai as genai
import re
import shutil
import fitz
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from newspaper import Article

# Load Generative AI model
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Utility Functions

def scrape_article_text(article_url):
    try:
        article = Article(article_url)
        article.download()
        article.parse()
        return article.text, article.title
    except Exception as e:
        return f"Error scraping article: {str(e)}", "Unknown Title"

def extract_text_from_pdf(pdf_file) -> str:
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def extract_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:v\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_url: str) -> str:
    print(f"Fetching transcript")
    try:
        video_id = extract_video_id(video_url)
        ydl_opts = {'quiet': True, 'skip_download': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'Unknown Title')
            channel = info.get('uploader', 'Unknown Channel')
        if not video_id:
            return "Error: Invalid YouTube URL format."

        transcript_list = YouTubeTranscriptApi().list(video_id)

        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_transcript(['a.en'])
            except:
                if transcript_list:
                    transcript = transcript_list[0]

        if not transcript:
            return "Error: No suitable transcript found."

        transcript_data = transcript.fetch()
        print(" ".join([entry.text for entry in transcript_data]))
        return " ".join([entry.text for entry in transcript_data]), title, channel

    except Exception as e:
        return f"Error: {str(e)}"

def generate_gemini_summary(title, channel, transcript, frames=None):
    print(f"Generating summary with Gemini...")
    
    prompt = """
You are a multimodal expert analyst with deep skills in language, vision, and storytelling, with knowledge spanning academic, technical, creative, and media domains — both fiction and non-fiction. You've been given content in the form of:

- A transcript or full text (from a video, article, or document),
- (Optionally) key visuals or context where relevant.

Your task is to produce a **rich, insightful, and structured analysis and insights** of the content. Do **not merely summarize** — instead:

ANALYZE:
- Extract the core **narrative or structure** of the piece.
- Identify the **main ideas, arguments, claims, and supporting evidence**.
- Understand the **purpose**: Is it informing, explaining, reviewing, persuading, reflecting, or entertaining?

CONNECT & CONTEXTUALIZE:
- Infer **hidden implications** — such as intent, bias, assumptions, or subtext.
- Provide **commentary, critique, or comparisons** to related ideas.
- If it's technical or academic, suggest **applications or limitations**.
- If it's creative, analyze **themes, tone, or storytelling technique**.

FORMAT:
Return a structured response with:
1. **Comprehensive Summary** (paragraphs)
2. **Key Takeaways** (5-10 bullet points)
3. **Deeper Concepts or Subtle Insights** (3+ points)
4. **Critical Reflection / Expert Commentary** (your own interpretation)
5. **Suggested Follow-Up**: related questions, deeper readings, or tangents to explore

Avoid vague generalities. Be specific and precise. You are not just a summarizer — you are a **knowledge interpreter** distilling depth, nuance, and insight from complex content.
    """
    content = [
        f"Video Title: {title}",
        f"Channel: {channel}",
        prompt,
        transcript,
    ]

    response = model.generate_content(content)
    print(response.text)
    return response.text
