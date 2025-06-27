import streamlit as st
import os
import json
import time
import re
from typing import List, Optional
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    import pdfplumber
    import google.generativeai as genai
except ImportError as e:
    st.error(f"Missing required package: {e}")
    st.stop()

st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🫠",
    layout="wide",
    initial_sidebar_state="expanded"
)


if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

class AILearningAssistant:
    def __init__(self):
        self.setup_api()

    def setup_api(self):
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("⚠️ Google API Key not found.")
            st.stop()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_youtube_transcript(self, video_url: str) -> Optional[str]:
        try:
            video_id = self.extract_video_id(video_url)
            if not video_id:
                st.error("❌ Invalid YouTube URL format")
                return None
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([item['text'] for item in transcript_list])
        except Exception as e:
            st.error(f"❌ Error fetching transcript: {str(e)}")
            return None

    def chunk_text(self, text: str, max_chars: int = 30000) -> List[str]:
        if len(text) <= max_chars:
            return [text]
        chunks, words, current_chunk, current_length = [], text.split(), [], 0
        for word in words:
            if current_length + len(word) + 1 > max_chars:
                chunks.append(" ".join(current_chunk))
                current_chunk, current_length = [word], len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def generate_summary(self, text: str, content_type: str = "content") -> str:
        try:
            chunks = self.chunk_text(text)
            summaries = []
            for chunk in chunks:
                prompt = f"""
                Provide a comprehensive and structured summary of the following {content_type}:

                {chunk}
                """
                response = self.model.generate_content(prompt)
                summaries.append(response.text)
                time.sleep(1)
            return "\n\n".join(summaries)
        except Exception as e:
            st.error(f"❌ Error generating summary: {str(e)}")
            return ""

    def generate_mcqs(self, text: str, num_questions: int = 8) -> str:
        try:
            chunks = self.chunk_text(text)
            all_mcqs = []
            questions_per_chunk = max(1, num_questions // len(chunks))
            for chunk in chunks:
                prompt = f"""
                Create {questions_per_chunk} multiple-choice questions:

                {chunk}
                """
                response = self.model.generate_content(prompt)
                all_mcqs.append(response.text)
                time.sleep(1)
            return "\n\n".join(all_mcqs)
        except Exception as e:
            st.error(f"❌ Error generating MCQs: {str(e)}")
            return ""

    def generate_flashcards(self, text: str, num_cards: int = 12) -> str:
        try:
            chunks = self.chunk_text(text)
            all_cards = []
            cards_per_chunk = max(1, num_cards // len(chunks))
            for chunk in chunks:
                prompt = f"""
                Create {cards_per_chunk} flashcards with front and back:

                {chunk}
                """
                response = self.model.generate_content(prompt)
                all_cards.append(response.text)
                time.sleep(1)
            return "\n\n".join(all_cards)
        except Exception as e:
            st.error(f"❌ Error generating flashcards: {str(e)}")
            return ""

    def extract_pdf_text(self, pdf_file) -> Optional[str]:
        try:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip() if text.strip() else None
        except Exception as e:
            st.error(f"❌ Error extracting PDF text: {str(e)}")
            return None

def pdf_interface(assistant: AILearningAssistant):
    st.markdown("<div class='feature-card fade-in-up'>", unsafe_allow_html=True)
    st.header("📄 PDF Learning Assistant")
    uploaded_file = st.file_uploader("Upload your PDF", type=['pdf'])
    col1, col2 = st.columns(2)
    with col1:
        generate_btn = st.button("🚀 Generate Learning Materials")
    with col2:
        clear_btn = st.button("🗑️ Clear")
    st.markdown("</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Summary", "❓ MCQs", "🗃️ Flashcards"])

    if clear_btn:
        st.rerun()

    with tab1:
        st.markdown("<div class='feature-card fade-in-up'>", unsafe_allow_html=True)
        st.markdown("📋 Waiting to generate summary..." if not generate_btn else "")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='feature-card fade-in-up'>", unsafe_allow_html=True)
        st.markdown("❓ Waiting to generate MCQs..." if not generate_btn else "")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='feature-card fade-in-up'>", unsafe_allow_html=True)
        st.markdown("🗃️ Waiting to generate flashcards..." if not generate_btn else "")
        st.markdown("</div>", unsafe_allow_html=True)

    if generate_btn:
        if not uploaded_file:
            st.warning("⚠️ Please upload a PDF file")
            return

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("📖 Extracting text from PDF...")
        progress_bar.progress(20)

        with st.spinner("Extracting text..."):
            pdf_text = assistant.extract_pdf_text(uploaded_file)

        if pdf_text:
            st.success(f"✅ Text extracted ({len(pdf_text):,} characters)")
            progress_bar.progress(40)

            with tab1:
                status_text.text("🤖 Generating summary...")
                progress_bar.progress(60)
                summary = assistant.generate_summary(pdf_text, "PDF document")
                st.subheader("📋 Summary")
                st.markdown(summary)

            with tab2:
                with st.spinner("Generating MCQs..."):
                    mcqs = assistant.generate_mcqs(pdf_text)
                st.subheader("❓ MCQs")
                st.markdown(mcqs)
                st.download_button("📥 Download MCQs", mcqs, "mcqs.md", "text/markdown")

            with tab3:
                with st.spinner("Generating Flashcards..."):
                    flashcards = assistant.generate_flashcards(pdf_text)
                st.subheader("🗃️ Flashcards")
                st.markdown(flashcards)
                st.download_button("📥 Download Flashcards", flashcards, "flashcards.md", "text/markdown")

def youtube_interface(assistant: AILearningAssistant):
    st.markdown('<div class="feature-card fade-in-up">', unsafe_allow_html=True)
    st.header("🎥 YouTube Video Summarizer")

    col1, col2 = st.columns([3, 1])
    with col1:
        video_url = st.text_input(
            "📎 Enter YouTube Video URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube video URL here"
        )
    with col2:
        generate_btn = st.button("🚀 Generate Summary", key="yt_generate")

    st.markdown('</div>', unsafe_allow_html=True)

    if generate_btn:
        if not video_url.strip():
            st.warning("⚠️ Please enter a YouTube URL")
            return

        with st.spinner("🔄 Fetching transcript..."):
            transcript = assistant.get_youtube_transcript(video_url)

        if transcript:
            st.success(f"✅ Transcript fetched! ({len(transcript):,} characters)")

            with st.spinner("🤖 Generating summary..."):
                summary = assistant.generate_summary(transcript, "YouTube video")

            if summary:
                st.subheader("📋 Video Summary")
                st.markdown(summary)

                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name="youtube_summary.md",
                    mime="text/markdown"
                )
        else:
            st.error("❌ Could not retrieve transcript from video.")

def main():
    st.title("🧠 AI Learning Assistant")
    assistant = AILearningAssistant()

    mode = st.radio(
        "Choose your learning mode:",
        ["📄 PDF Learning Assistant", "🎥 YouTube Video Summarizer"]
    )

    if "PDF" in mode:
        pdf_interface(assistant)
    else:
        youtube_interface(assistant)

if __name__ == "__main__":
    main()
