Here’s a professional and structured **README.md** file for your **AI Learning Assistant** project:

---

````markdown
# 🧠 AI Learning Assistant

An intelligent educational web application built with **Streamlit** that helps you learn efficiently from **YouTube videos** and **PDF documents**. Powered by **Google's Gemini AI**, this app generates:
- 📋 Detailed summaries
- ❓ Multiple-choice questions (MCQs)
- 🗃️ Flashcards

---

## 🚀 Features

### 🎥 YouTube Video Summarizer
- Paste any YouTube video URL.
- Automatically fetches the transcript.
- Generates a comprehensive summary using AI.

### 📄 PDF Learning Assistant
- Upload any PDF document.
- Extracts and processes the text.
- Creates:
  - Summaries
  - MCQs
  - Flashcards

### ✅ Additional Highlights
- User-friendly UI with tab-based interface
- Light/Dark mode toggle support
- Download generated content as markdown
- Chunked processing for large files to stay within LLM limits

---

## 🧰 Tech Stack

| Component        | Tech Used |
|------------------|-----------|
| Frontend/UI      | Streamlit |
| LLM Integration  | Google Generative AI (Gemini 2.0 Flash) |
| PDF Processing   | pdfplumber |
| YouTube Transcripts | youtube-transcript-api |
| Language         | Python 3.x |

---

## 🛠️ Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ai-learning-assistant.git
   cd ai-learning-assistant
````

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google API Key**:

   * Add your Gemini API key in `.streamlit/secrets.toml`:

     ```toml
     GOOGLE_API_KEY = "your_google_api_key_here"
     ```

4. **Run the app**:

   ```bash
   streamlit run your_script_name.py
   ```

---

## 📸 Screenshots

| Mode                            | Screenshot                                          |
| ------------------------------- | --------------------------------------------------- |
| YouTube Summary                 | ![YouTube Summary](screenshots/youtube_summary.png) |
| PDF Summary + MCQs + Flashcards | ![PDF Interface](screenshots/pdf_interface.png)     |

---

## 🧪 Future Improvements

* Support for DOCX and PPTX uploads
* Interactive quizzes from MCQs
* Save learning sessions and progress
* Multi-language support
