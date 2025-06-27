```python
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

# Initialize theme in session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def apply_custom_styling():
    """Apply comprehensive custom styling with theme support and cursor effects."""
    
    # Determine theme colors
    if st.session_state.dark_mode:
        bg_primary = "#0e1117"
        bg_secondary = "#1a1d26"
        bg_tertiary = "#262730"
        text_primary = "#ffffff"
        text_secondary = "#c5c5c5"
        accent_color = "#00d4ff"
        accent_secondary = "#ff6b6b"
        border_color = "#404040"
        shadow_color = "rgba(0, 212, 255, 0.3)"
        glow_color = "rgba(0, 212, 255, 0.15)"
    else:
        bg_primary = "#fafafa"
        bg_secondary = "#ffffff"
        bg_tertiary = "#f8f9fa"
        text_primary = "#1a1a1a"
        text_secondary = "#666666"
        accent_color = "#4a90ff"
        accent_secondary = "#ff4757"
        border_color = "#e1e5e9"
        shadow_color = "rgba(74, 144, 255, 0.3)"
        glow_color = "rgba(74, 144, 255, 0.08)"
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Global Variables */
        :root {{
            --bg-primary: {bg_primary};
            --bg-secondary: {bg_secondary};
            --bg-tertiary: {bg_tertiary};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --accent-color: {accent_color};
            --accent-secondary: {accent_secondary};
            --border-color: {border_color};
            --shadow-color: {shadow_color};
            --glow-color: {glow_color};
        }}
        
        /* Cursor Tracking Glow Effect */
        body {{
            position: relative;
            overflow-x: hidden;
        }}
        
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(600px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), 
                                var(--glow-color) 0%, 
                                transparent 40%);
            pointer-events: none;
            z-index: -1;
            transition: opacity 0.3s ease;
        }}
        
        /* Base Styling */
        .stApp {{
            background: var(--bg-primary);
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
        }}
        
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}
        
        /* Header Styling */
        .main-header {{
            font-family: 'Inter', sans-serif;
            font-size: 3.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--accent-color), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 4px 8px var(--shadow-color);
            letter-spacing: -0.02em;
        }}
        
        .subtitle {{
            text-align: center;
            font-size: 1.2rem;
            color: var(--text-secondary);
            margin-bottom: 3rem;
            font-weight: 400;
        }}
        
        /* Sidebar Styling */
        .css-1d391kg {{
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
        }}
        
        .css-1d391kg .css-1v0mbdj {{
            color: var(--text-primary);
        }}
        
        /* Custom Button Styling */
        .stButton > button {{
            background: linear-gradient(135deg, var(--accent-color), var(--accent-secondary));
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px var(--shadow-color);
            position: relative;
            overflow: hidden;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px var(--shadow-color);
        }}
        
        .stButton > button:active {{
            transform: translateY(0);
        }}
        
        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        
        .stButton > button:hover::before {{
            left: 100%;
        }}
        
        /* Theme Toggle Button */
        .theme-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 1000;
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: 50px;
            padding: 0.5rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px var(--shadow-color);
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 20px var(--shadow-color);
        }}
        
        /* Input Field Styling */
        .stTextInput > div > div > input {{
            background: var(--bg-secondary);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            color: var(--text-primary);
            padding: 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px var(--glow-color);
            outline: none;
        }}
        
        /* File Uploader Styling */
        .stFileUploader > div {{
            background: var(--bg-secondary);
            border: 2px dashed var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            transition: all 0.3s ease;
        }}
        
        .stFileUploader > div:hover {{
            border-color: var(--accent-color);
            background: var(--bg-tertiary);
        }}
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 0.5rem;
            margin-bottom: 2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: transparent;
            border-radius: 8px;
            color: var(--text-secondary);
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: var(--accent-color) !important;
            color: white !important;
        }}
        
        /* Card Styling */
        .feature-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px var(--shadow-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .feature-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(135deg, var(--accent-color), var(--accent-secondary));
        }}
        
        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px var(--shadow-color);
        }}
        
        /* Success/Error Messages */
        .stSuccess > div {{
            background: linear-gradient(135deg, #00c851, #007e33);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 500;
        }}
        
        .stError > div {{
            background: linear-gradient(135deg, #ff4444, #cc0000);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 500;
        }}
        
        .stWarning > div {{
            background: linear-gradient(135deg, #ffbb33, #ff8800);
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 500;
        }}
        
        /* Spinner Styling */
        .stSpinner > div {{
            border-top-color: var(--accent-color) !important;
        }}
        
        /* Download Button */
        .stDownloadButton > button {{
            background: var(--bg-secondary);
            border: 2px solid var(--accent-color);
            color: var(--accent-color);
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stDownloadButton > button:hover {{
            background: var(--accent-color);
            color: white;
            transform: translateY(-2px);
        }}
        
        /* Radio Button Styling */
        .stRadio > div {{
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 1rem;
        }}
        
        /* Markdown Content */
        .stMarkdown {{
            color: var(--text-primary);
        }}
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            color: var(--text-primary);
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: var(--accent-color);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-secondary);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .main-header {{
                font-size: 2.5rem;
            }}
            
            .theme-toggle {{
                top: 0.5rem;
                right: 0.5rem;
            }}
            
            .feature-card {{
                padding: 1.5rem;
            }}
        }}
        
        /* Animation Keyframes */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .fade-in-up {{
            animation: fadeInUp 0.6s ease-out;
        }}
    </style>
    
    <script>
        // Cursor tracking for glow effect
        document.addEventListener('mousemove', (e) => {{
            const x = (e.clientX / window.innerWidth) * 100;
            const y = (e.clientY / window.innerHeight) * 100;
            document.documentElement.style.setProperty('--mouse-x', x + '%');
            document.documentElement.style.setProperty('--mouse-y', y + '%');
        }});
    </script>
    """, unsafe_allow_html=True)

# Apply the styling
apply_custom_styling()

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

def create_theme_toggle():
    """Create a theme toggle button."""
    theme_icon = "🌙" if not st.session_state.dark_mode else "☀️"
    theme_text = "Dark Mode" if not st.session_state.dark_mode else "Light Mode"
    
    st.markdown(f"""
    <div class="theme-toggle" onclick="toggleTheme()">
        <span style="font-size: 1.5rem;">{theme_icon}</span>
    </div>
    
    <script>
        function toggleTheme() {{
            // This will trigger a rerun with the theme toggle
            const event = new CustomEvent('streamlit:theme-toggle');
            window.parent.document.dispatchEvent(event);
        }}
    </script>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Initialize the assistant
    assistant = AILearningAssistant()
    
    # Theme toggle button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        if st.button("🌙 Toggle Theme" if not st.session_state.dark_mode else "☀️ Toggle Theme", key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    # Header with enhanced styling
    st.markdown('<div class="fade-in-up">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🧠 AI Learning Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Transform YouTube videos and PDFs into structured learning materials using AI</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar navigation with enhanced styling
    with st.sidebar:
        st.markdown('<div class="fade-in-up">', unsafe_allow_html=True)
        st.title("📚 Navigation")
        
        # Enhanced radio button styling
        mode = st.radio(
            "Choose your learning mode:",
            ["🎥 YouTube Video Summarizer", "📄 PDF Learning Assistant"],
            index=0
        )
        
        st.markdown("---")
        
        # Feature cards in sidebar
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Tips")
        if "YouTube" in mode:
            st.markdown("• Paste any YouTube URL  \n• Works with videos that have captions  \n• Generates comprehensive summaries")
        else:
            st.markdown("• Upload PDF documents  \n• Get summaries, MCQs, and flashcards  \n• Perfect for study materials")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Features")
        st.markdown("• AI-powered content analysis  \n• Structured learning materials  \n• Export and download options  \n• Dynamic themes & modern UI")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    if "YouTube" in mode:
        youtube_interface(assistant)
    else:
        pdf_interface(assistant)
    
    # Footer with enhanced styling
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: var(--text-secondary);">
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Built with ❤️ using Streamlit and Google Gemini AI</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">Featuring dynamic themes, cursor effects, and modern UI design</p>
    </div>
    """, unsafe_allow_html=True)

def youtube_interface(assistant: AILearningAssistant):
    """YouTube video summarizer interface with enhanced styling."""
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
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        generate_btn = st.button("🚀 Generate Summary", type="primary", key="yt_generate")
        clear_btn = st.button("🗑️ Clear", key="yt_clear")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if clear_btn:
        st.rerun()
    
    if generate_btn and video_url:
        if not video_url.strip():
            st.warning("⚠️ Please enter a YouTube URL")
            return
        
        # Progress container with enhanced styling
        progress_container = st.empty()
        
        with st.spinner("🔄 Fetching video transcript..."):
            transcript = assistant.get_youtube_transcript(video_url)
        
        if transcript:
            st.success(f"✅ Transcript fetched! ({len(transcript):,} characters)")
            
            with st.spinner("🤖 Generating AI summary..."):
                summary = assistant.generate_summary(transcript, "YouTube video")
            
            if summary:
                st.markdown('<div class="feature-card fade-in-up">', unsafe_allow_html=True)
                st.subheader("📋 Video Summary")
                st.markdown(summary)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Enhanced download section
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    st.download_button(
                        label="📥 Download Summary",
                        data=summary,
                        file_name="youtube_summary.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
    
    elif generate_btn:
        st.warning("⚠️ Please enter a YouTube URL")

def pdf_interface(assistant: AILearningAssistant):
    """PDF learning assistant interface with enhanced styling."""
    st.markdown('<div class="feature-card fade-in-up">', unsafe_allow_html=True)
    st.header("📄 PDF Learning Assistant")
    
    # Enhanced file upload
    uploaded_file = st.file_uploader(
        "📁 Upload Your PDF Document:",
        type=['pdf'],
        help="Upload a PDF file to generate comprehensive learning materials"
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        generate_btn = st.button("🚀 Generate Learning Materials", type="primary", key="pdf_generate")
    with col2:
        clear_btn = st.button("🗑️ Clear All", key="pdf_clear")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if clear_btn:
        st.rerun()
    
    # Corrected indentation for the main logic when generate_btn is clicked
    if generate_btn and uploaded_file:
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("📖 Extracting text from PDF...")
        progress_bar.progress(20)
        
        with st.spinner("📖 Extracting text from PDF..."):
            pdf_text = assistant.extract_pdf_text(uploaded_file)
        
        if pdf_text:
            st.success(f"✅ Text extracted successfully! ({len(pdf_text):,} characters)")
            progress_bar.progress(40)
            
            # Enhanced tabs with better styling
            tab1, tab2, tab3 = st.tabs(["📋 Summary", "❓ MCQs", "🗃️ Flashcards"])
            
            with tab1:
                st.markdown('<div class="feature-card fade-in-up">', unsafe_allow_html=True)
                status_text.text("🤖 Generating comprehensive summary...")
                progress_bar.progress(60)
                # Ensure summary generation is within the tab block
                summary = assistant.generate_summary(pdf_text, "PDF document") 
                if summary:
                    st.subheader("📋 Document Summary")
                    st.markdown(summary)
                st.markdown('</div>', unsafe_allow_html=True) # Closing div for tab1
            
            with tab2:
                st.markdown('<div class="feature-card fade-in-up">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True) # Closing div for tab2

            with tab3:
                st.markdown('<div class="feature-card fade-in-up">', unsafe_allow_html=True)
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
                st.markdown('</div>', unsafe_allow_html=True) # Closing div for tab3
    elif generate_btn: # This 'elif' needs to align with the 'if generate_btn and uploaded_file:'
        st.warning("⚠️ Please upload a PDF file")
        
if __name__ == "__main__":
    main()
```
