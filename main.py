import os
import streamlit as st
import subprocess
import cv2
import google.generativeai as genai
import re
import glob
import shutil
from dotenv import load_dotenv
from PIL import Image
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from scenedetect.scene_manager import save_images

# Load Generative AI model
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Utility Functions

def download_video(url, output_dir="videos", filename="video.mp4"):
    print(f"Downloading video...")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    ydl_opts = {
        'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    title = info.get('title', 'Unknown Title')
    channel = info.get('uploader', 'Unknown Channel')
    print(f"Video downloaded: {title} by {channel}")
    return output_path, title, channel

def extract_keyframes(video_path, output_dir="frames", threshold=20.0):
    print(f"Extracting keyframes...")
    os.makedirs(output_dir, exist_ok=True)

    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    video_manager.set_downscale_factor()
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scenes = scene_manager.get_scene_list()

    if scenes:
        save_images(scenes, video_manager, num_images=1, output_dir=output_dir)
    else:
        fallback_frame_extraction(video_path, output_dir)

    video_manager.release()
    print(f"Keyframes extracted to {output_dir}")

def fallback_frame_extraction(video_path, output_dir="frames", interval_sec=10):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval_sec)

    count, saved = 0, 0
    while True:
        success, frame = cap.read()
        if not success:
            break
        if count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{saved:03d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved += 1
        count += 1

    cap.release()

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
        print(transcript_data)
        return " ".join([entry.text for entry in transcript_data])

    except Exception as e:
        return f"Error: {str(e)}"

def generate_gemini_summary(title, channel, transcript, frame_dir="frames"):
    print(f"Generating summary with Gemini...")
    frame_paths = sorted(glob.glob(os.path.join(frame_dir, "*.jpg")))
    frames = [Image.open(path).convert("RGB") for path in frame_paths]

    prompt = """
You are a multimodal expert analyst with deep skills in language, vision, and storytelling and knowledge in all forms of art and media both fiction and non fiction. You've been given:

1. A transcript of a video, capturing the spoken content.
2. A sequence of key visual frames (screenshots extracted throughout the video), which may include screens, people, product shots, slides, snippets, animations, or any relevant visuals.

Your task is to produce a **rich, insightful, and structured analysis and insights** of the video, combining both visual and textual information. Do not merely summarize — instead:

ANALYZE:
- Extract the core **narrative or structure** of the video.
- Identify **main ideas, insights, arguments, and claims**.
- Understand the **purpose** of the video: is it educating, explaining, reviewing, persuading, or entertaining?

INTERPRET VISUALS:
- Use the frames to **validate, supplement, or challenge** the transcript.
- Describe what is visually shown: diagrams, interfaces, scenes, animations, gestures, text on screen, etc.
- Link the visuals to the topics discussed. For example, "While the speaker talks about X, the screen shows Y."

CONNECT & CONTEXTUALIZE:
- Infer what's **not explicitly said** — e.g., intent, bias, audience assumptions.
- Add **commentary, comparisons, or critique** where relevant.
- If it's a tutorial, suggest real-world applications or deeper insights.
- If it's a review, discuss tradeoffs or user impact.
- If it's a skit

FORMAT:
Return a structured response with:
1. **Comprehensive Summary** (paragraphs)
2. **Key Takeaways** (5-10 bullet points)
3. **Deeper Concepts or Subtle Insights** (3+ points)
4. **Critical Reflection / Expert Commentary** (Add your own view)
5. **Suggested Follow-up**: related topics, readings, or questions the viewer should explore next

Be clear, specific, and avoid vague generalities. Use both visual and textual context to form your response. You are not a summarizer — you are a **knowledge interpreter**.
    """

    content = [
        f"Video Title: {title}",
        f"Channel: {channel}",
        prompt,
        transcript,
    ] + frames

    response = model.generate_content(content)
    print(response.text)
    return response.text

def delete_folder_contents(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

# Streamlit UI
st.set_page_config(
    page_title="ClipGist: YouTube Video Insight Generator",
    layout="wide",
    page_icon="🎬"
)

# --- Header Section ---
st.markdown("""
<div style="text-align:center; padding-bottom: 1rem;">
    <h1 style='color:#FF4B4B; font-size: 3rem;'>🎬 ClipGist: YouTube Video Insight Generator</h1>
    <p style="font-size:1.1rem; color:lightgray;">
        Paste any YouTube link below, and it'll generate a smart summary and analysis using Gemini.<br>
        You can then ask questions about the video and get instant insights.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Input Section ---
with st.container():
    video_url = st.text_input("🎥 Enter YouTube video URL:", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("🚀 Summarize"):
        if not video_url.strip():
            st.warning("Please enter a valid YouTube URL.")
        else:
            with st.spinner("📥 Downloading video..."):
                video_path, title, channel = download_video(video_url)
                st.session_state["title"] = title
                st.session_state["channel"] = channel

            with st.spinner("🖼️ Extracting keyframes..."):
                extract_keyframes(video_path)

            with st.spinner("📝 Getting transcript..."):
                transcript = get_transcript(video_url)
                st.session_state["transcript"] = transcript

            if transcript.startswith("Error"):
                st.error(transcript)
            else:
                with st.spinner("Generating summary with Gemini..."):
                    summary = generate_gemini_summary(title, channel, transcript)
                    st.session_state["summary"] = summary

                    st.success("✅ Summary generated!")

                    # Save video context for Q&A
                    st.session_state["video_context"] = f"""
Video Title: {title}
Channel: {channel}

Summary:
{summary}

Transcript:
{transcript}
"""

            delete_folder_contents('frames')
            delete_folder_contents('videos')

# --- Summary Display ---
if st.session_state.get("summary"):
    with st.container():
        st.markdown("### 📄 Video Summary")
        with st.expander("See Summary", expanded=True):
            st.markdown(f"**🎬 Video Title:** {st.session_state.get('title', '')}")
            st.markdown(f"**📺 Channel:** {st.session_state.get('channel', '')}")
            st.markdown("**📝 Gemini Summary:**")
            st.markdown(st.session_state.get("summary", ""))

# --- Initialize Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Q&A Section ---
if st.session_state.get("video_context"):
    with st.container():
        st.markdown("### 💬 Ask Questions About the Video")
        user_query = st.text_input("Your question:", key="user_query_input")

        if user_query:
            with st.spinner("Gemini is thinking..."):
                prompt = f"""
You are a helpful assistant. Based on the following video content, answer the user's question. The answer should contain both info from the video and you can also add your existing knowledge of the topic especially if the topic is educational to add to the video content and make a better experience.

{st.session_state.video_context}

User Question: {user_query}
"""
                chat_response = model.generate_content(prompt)
                answer = chat_response.text
                st.session_state.chat_history.append((user_query, answer))

                st.markdown("**🧠 Gemini's Answer:**")
                st.text_area("", answer, height=200)

# --- Chat History ---
if st.session_state.chat_history:
    with st.container():
        st.markdown("### 📝 Previous Q&A")
        for i, (q, a) in enumerate(reversed(st.session_state.chat_history), 1):
            st.markdown(f"**Q{i}:** {q}")
            st.markdown(f"**A{i}:** {a}")
