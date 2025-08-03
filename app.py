import streamlit as st
from utils import (
    get_transcript, generate_gemini_summary, scrape_article_text, extract_text_from_pdf, model
)
from pathlib import Path

# Initialize page
st.set_page_config(
    page_title="ClipGist: Research Insight Generator",
    layout="wide",
    page_icon="🎬"
)

# Header
st.markdown("""
<div style="text-align:center; padding-bottom: 1rem;">
    <h1 style='color:#FF4B4B; font-size: 3rem;'>🎬 ClipGist: Research Insight Generator</h1>
    <p style="font-size:1.1rem; color:lightgray;">
        Paste a YouTube link, an article URL, or upload a document (PDF/TXT) to get a smart summary using Gemini.<br>
        You can then ask questions based on the content.
    </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# Input Type Selection
input_mode = st.radio("Select Input Type:", ["YouTube Video", "Article Link", "Upload Document"], horizontal=True)

# Input Fields
uploaded_file = None
transcript = ""
title = ""
source_type = ""
source_content = ""

if input_mode == "YouTube Video":
    video_url = st.text_input("🎥 Enter YouTube video URL:", placeholder="https://www.youtube.com/watch?v=...")
    if st.button("🚀 Summarize"):
        if not video_url.strip():
            st.warning("Please enter a valid YouTube URL.")
        else:
            source_type = "video"
            with st.spinner("📝 Getting transcript..."):
                transcript, title, channel = get_transcript(video_url)

            if transcript.startswith("Error"):
                st.error(transcript)
            else:
                with st.spinner("Generating summary with Gemini..."):
                    summary = generate_gemini_summary(title, channel, transcript)
                    st.session_state["summary"] = summary
                    st.success("✅ Summary generated!")

                    st.session_state["context"] = f"""
Video Title: {title}
Channel: {channel}

Summary:
{summary}

Transcript:
{transcript}
"""

elif input_mode == "Article Link":
    article_url = st.text_input("📰 Enter Article URL:", placeholder="https://example.com/article")
    if st.button("🚀 Summarize", key="article_button"):
        if not article_url.strip():
            st.warning("Please enter a valid article URL.")
        else:
            source_type = "article"
            with st.spinner("Scraping article..."):
                article_text, title = scrape_article_text(article_url)

            if not article_text:
                st.error("❌ Failed to extract article content.")
            else:
                with st.spinner("Generating summary with Gemini..."):
                    summary = generate_gemini_summary(title, "Unknown", article_text)
                    st.session_state["summary"] = summary
                    st.success("✅ Summary generated!")

                    st.session_state["context"] = f"""
Article Title: {title}

Summary:
{summary}

Full Text:
{article_text}
"""

elif input_mode == "Upload Document":
    uploaded_file = st.file_uploader("📄 Upload a document (PDF or TXT)", type=["pdf", "txt"])
    if uploaded_file and st.button("🚀 Summarize"):
        source_type = "document"
        with st.spinner("📄 Extracting text..."):
            if uploaded_file.type == "text/plain":
                text = uploaded_file.read().decode("utf-8")
                title = uploaded_file.name
            elif uploaded_file.type == "application/pdf":
                text = extract_text_from_pdf(uploaded_file)
                title = uploaded_file.name
            else:
                st.error("Unsupported file type.")
                st.stop()

        if text.startswith("Error"):
            st.error(text)
        else:
            with st.spinner("Generating summary with Gemini..."):
                summary = generate_gemini_summary(title, "Uploaded Document", text)
                st.session_state["summary"] = summary
                st.success("✅ Summary generated!")

                st.session_state["context"] = f"""
Document Title: {title}
Source: Uploaded File

Summary:
{summary}

Extracted Content:
{text}
"""

# Summary Display
if st.session_state.get("summary"):
    with st.container():
        st.markdown("### 📄 Summary")
        with st.expander("See Summary", expanded=True):
            st.markdown(f"**📌 Title:** {st.session_state.get('title', '')}")
            st.markdown("**📝 Gemini Summary:**")
            st.markdown(st.session_state.get("summary", ""))

# Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Q&A Section
if st.session_state.get("context"):
    with st.container():
        st.markdown("### 💬 Ask Questions Based on the Content")
        user_query = st.text_input("Your question:", key="user_query_input")

        if user_query:
            with st.spinner("Gemini is thinking..."):
                prompt = f"""
You are a helpful assistant. Based on the following content, answer the user's question. If it's educational, feel free to enrich the answer with relevant knowledge.

{st.session_state['context']}

User Question: {user_query}
"""
                chat_response = model.generate_content(prompt)
                answer = chat_response.text
                st.session_state.chat_history.append((user_query, answer))

                st.markdown("**Gemini's Answer:**")
                st.text_area("", answer, height=200)

# Display Previous Q&A
if st.session_state.chat_history:
    with st.container():
        st.markdown("### 📝 Previous Q&A")
        for i, (q, a) in enumerate(reversed(st.session_state.chat_history), 1):
            st.markdown(f"**Q{i}:** {q}")
            st.markdown(f"**A{i}:** {a}")
