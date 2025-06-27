import streamlit as st
import os
import json
import time
from typing import List, Dict, Optional, Tuple
import re

# Third-party imports
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    import pdfplumber
    import google.generativeai as genai
except ImportError as e:
    st.error(f"Missing required package: {e}")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Learning Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AILearningAssistant:
    """Main class for the AI Learning Assistant application."""
    
    def __init__(self):
        """Initialize the AI Learning Assistant."""
        self.setup_api()
        
    def setup_api(self):
        """Configure the Google Generative AI API."""
        try:
            # Try to get API key from Streamlit secrets first, then environment variables
            api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                st.error("⚠️ Google API Key not found. Please set GOOGLE_API_KEY in your environment variables or Streamlit secrets.")
                st.info("To get an API key, visit: https://makersuite.google.com/app/apikey")
                st.stop()
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
        except Exception as e:
            st.error(f"Failed to initialize Google Generative AI: {str(e)}")
            st.stop()
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_youtube_transcript(self, video_url: str) -> Optional[str]:
        """Fetch YouTube video transcript."""
        try:
            video_id = self.extract_video_id(video_url)
            if not video_id:
                st.error("❌ Invalid YouTube URL format")
                return None
            
            # Try to get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine all transcript segments
            full_transcript = " ".join([item['text'] for item in transcript_list])
            
            return full_transcript
            
        except Exception as e:
            st.error(f"❌ Error fetching transcript: {str(e)}")
            st.info("💡 Make sure the video has captions/subtitles available")
            return None
    
    def chunk_text(self, text: str, max_chars: int = 30000) -> List[str]:
        """Split text into chunks to handle token limits."""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_chars:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = word_length
                else:
                    # Single word is too long, split it
                    chunks.append(word[:max_chars])
                    current_chunk = [word[max_chars:]] if len(word) > max_chars else []
                    current_length = len(word[max_chars:]) if len(word) > max_chars else 0
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def generate_summary(self, text: str, content_type: str = "content") -> str:
        """Generate a comprehensive summary using Gemini."""
        try:
            chunks = self.chunk_text(text)
            summaries = []
            
            for i, chunk in enumerate(chunks):
                prompt = f"""
                Please provide a comprehensive and well-structured summary of the following {content_type}.
                
                Requirements:
                - Create a clear, concise summary that captures all key points
                - Use bullet points and headings for better organization
                - Maintain the logical flow of information
                - Include important details, concepts, and takeaways
                - Format using Markdown for better readability
                
                {content_type.capitalize()} content:
                {chunk}
                """
                
                response = self.model.generate_content(prompt)
                summaries.append(response.text)
                
                if len(chunks) > 1:
                    time.sleep(1)  # Rate limiting
            
            if len(summaries) > 1:
                # Combine multiple summaries
                combined_prompt = f"""
                Please create a unified, comprehensive summary from these individual summaries:
                
                {' '.join(summaries)}
                
                Combine them into a single, well-organized summary that eliminates redundancy and maintains all important information.
                """
                
                response = self.model.generate_content(combined_prompt)
                return response.text
            else:
                return summaries[0]
                
        except Exception as e:
            st.error(f"❌ Error generating summary: {str(e)}")
            return "Failed to generate summary."
    
    def generate_mcqs(self, text: str, num_questions: int = 8) -> str:
        """Generate multiple choice questions from the text."""
        try:
            chunks = self.chunk_text(text)
            all_mcqs = []
            
            questions_per_chunk = max(1, num_questions // len(chunks))
            
            for chunk in chunks:
                prompt = f"""
                Create {questions_per_chunk} multiple-choice questions based on the following content.
                
                Requirements:
                - Each question should test understanding of key concepts
                - Provide exactly 4 options (A, B, C, D) for each question
                - Make sure only one option is clearly correct
                - Include varied difficulty levels
                - Clearly indicate the correct answer
                
                Format each question as:
                **Question X:** [Question text]
                A) [Option A]
                B) [Option B]
                C) [Option C]
                D) [Option D]
                **Correct Answer:** [Letter]
                
                Content:
                {chunk}
                """
                
                response = self.model.generate_content(prompt)
                all_mcqs.append(response.text)
                
                if len(chunks) > 1:
                    time.sleep(1)  # Rate limiting
            
            return "\n\n".join(all_mcqs)
            
        except Exception as e:
            st.error(f"❌ Error generating MCQs: {str(e)}")
            return "Failed to generate MCQs."
    
    def generate_flashcards(self, text: str, num_cards: int = 12) -> str:
        """Generate flashcards from the text."""
        try:
            chunks = self.chunk_text(text)
            all_flashcards = []
            
            cards_per_chunk = max(1, num_cards // len(chunks))
            
            for chunk in chunks:
                prompt = f"""
                Create {cards_per_chunk} flashcards based on the following content.
                
                Requirements:
                - Cover key concepts, definitions, and important facts
                - Each flashcard should have a clear question/term and comprehensive answer/definition
                - Make them suitable for studying and memorization
                - Vary the types (definitions, concepts, facts, processes)
                
                Format each flashcard as:
                **Card X:**
                **Front:** [Question/Term]
                **Back:** [Answer/Definition]
                
                Content:
                {chunk}
                """
                
                response = self.model.generate_content(prompt)
                all_flashcards.append(response.text)
                
                if len(chunks) > 1:
                    time.sleep(1)  # Rate limiting
            
            return "\n\n".join(all_flashcards)
            
        except Exception as e:
            st.error(f"❌ Error generating flashcards: {str(e)}")
            return "Failed to generate flashcards."
    
    def extract_pdf_text(self, pdf_file) -> Optional[str]:
        """Extract text from uploaded PDF file."""
        try:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if not text.strip():
                st.error("❌ No text could be extracted from the PDF")
                return None
                
            return text.strip()
            
        except Exception as e:
            st.error(f"❌ Error extracting PDF text: {str(e)}")
            return None

def main():
    """Main application function."""
    # Initialize the assistant
    assistant = AILearningAssistant()
    
    # Header
    st.markdown('<h1 class="main-header">🧠 AI Learning Assistant</h1>', unsafe_allow_html=True)
    st.markdown("Transform YouTube videos and PDFs into structured learning materials using AI")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📚 Navigation")
        mode = st.radio(
            "Choose your learning mode:",
            ["🎥 YouTube Video Summarizer", "📄 PDF Learning Assistant"],
            index=0
        )
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        if "YouTube" in mode:
            st.markdown("• Paste any YouTube URL\n• Works with videos that have captions\n• Generates comprehensive summaries")
        else:
            st.markdown("• Upload PDF documents\n• Get summaries, MCQs, and flashcards\n• Perfect for study materials")
        
        st.markdown("---")
        st.markdown("### ⚡ Features")
        st.markdown("• AI-powered content analysis\n• Structured learning materials\n• Export and download options")
    
    # Main content area
    if "YouTube" in mode:
        youtube_interface(assistant)
    else:
        pdf_interface(assistant)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and Google Gemini AI")

def youtube_interface(assistant: AILearningAssistant):
    """YouTube video summarizer interface."""
    st.header("🎥 YouTube Video Summarizer")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        video_url = st.text_input(
            "📎 Enter YouTube Video URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube video URL here"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        generate_btn = st.button("🚀 Generate Summary", type="primary")
        clear_btn = st.button("🗑️ Clear")
    
    if clear_btn:
        st.rerun()
    
    if generate_btn and video_url:
        if not video_url.strip():
            st.warning("⚠️ Please enter a YouTube URL")
            return
        
        with st.spinner("🔄 Fetching video transcript..."):
            transcript = assistant.get_youtube_transcript(video_url)
        
        if transcript:
            st.success(f"✅ Transcript fetched! ({len(transcript)} characters)")
            
            with st.spinner("🤖 Generating AI summary..."):
                summary = assistant.generate_summary(transcript, "YouTube video")
            
            if summary:
                st.subheader("📋 Video Summary")
                st.markdown(summary)
                
                # Download option
                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name="youtube_summary.md",
                    mime="text/markdown"
                )
    
    elif generate_btn:
        st.warning("⚠️ Please enter a YouTube URL")

def pdf_interface(assistant: AILearningAssistant):
    """PDF learning assistant interface."""
    st.header("📄 PDF Learning Assistant")
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload PDF Document:",
        type=['pdf'],
        help="Upload a PDF file to generate learning materials"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        generate_btn = st.button("🚀 Generate Learning Materials", type="primary")
    with col2:
        clear_btn = st.button("🗑️ Clear All")
    
    if clear_btn:
        st.rerun()
    
    if generate_btn and uploaded_file:
        with st.spinner("📖 Extracting text from PDF..."):
            pdf_text = assistant.extract_pdf_text(uploaded_file)
        
        if pdf_text:
            st.success(f"✅ Text extracted! ({len(pdf_text)} characters)")
            
            # Create tabs for different outputs
            tab1, tab2, tab3 = st.tabs(["📋 Summary", "❓ MCQs", "🗃️ Flashcards"])
            
            with tab1:
                with st.spinner("🤖 Generating comprehensive summary..."):
                    summary = assistant.generate_summary(pdf_text, "PDF document")
                
                st.markdown("### 📄 Document Summary")
                st.markdown(summary)
                
                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name="pdf_summary.md",
                    mime="text/markdown"
                )
            
            with tab2:
                with st.spinner("🤖 Creating multiple choice questions..."):
                    mcqs = assistant.generate_mcqs(pdf_text)
                
                st.markdown("### ❓ Multiple Choice Questions")
                st.markdown(mcqs)
                
                st.download_button(
                    label="📥 Download MCQs",
                    data=mcqs,
                    file_name="pdf_mcqs.md",
                    mime="text/markdown"
                )
            
            with tab3:
                with st.spinner("🤖 Generating flashcards..."):
                    flashcards = assistant.generate_flashcards(pdf_text)
                
                st.markdown("### 🗃️ Study Flashcards")
                st.markdown(flashcards)
                
                st.download_button(
                    label="📥 Download Flashcards",
                    data=flashcards,
                    file_name="pdf_flashcards.md",
                    mime="text/markdown"
                )
    
    elif generate_btn:
        st.warning("⚠️ Please upload a PDF file")

if __name__ == "__main__":
    main()
