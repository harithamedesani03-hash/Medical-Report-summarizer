# 🏥 MediReport AI

**AI-Powered Medical Report Summariser** — Powered by Google Gemini 2.5 Flash

Upload any medical report (lab results, discharge summaries, scanned images) and receive a clear, patient-friendly explanation with key findings, flagged abnormal values, and recommended next steps.

---

## ✨ Features

- 📄 **Multi-format support** — PDF, PNG, JPG, DOCX, TXT
- 🔬 **Smart extraction** — text-based analysis for digital PDFs; vision-based for scanned images
- 🤖 **Gemini 2.5 Flash** — state-of-the-art LLM for accurate, empathetic summaries
- 🔍 **Structured output** — Key findings, abnormal values, next steps, doctor Q&A
- ⬇️ **Download** — Save the summary as a plain-text file
- 🔐 **Privacy-first** — Files are never stored; processed in-memory only

---

## 🚀 Getting Started

### 1. Clone / Download the project

```bash
git clone <your-repo-url>
cd medical-report-project
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your Gemini API Key

Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

**Option A — `.env` file (recommended for local dev):**
```bash
cp .env.example .env
# Edit .env and paste your key
```

**Option B — Enter directly in the app sidebar** (no file needed).

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Cloud

1. Push the project to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Set **Main file path** to `app.py`.
4. In **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click **Deploy**.

---

## 📁 Project Structure

```
medical-report-project/
├── app.py                  # Main Streamlit application
├── gemini_client.py        # Gemini API integration
├── document_processor.py   # PDF / image / DOCX / TXT parsing
├── prompts.py              # Prompt templates
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .streamlit/
│   └── config.toml         # Streamlit theme & server config
└── README.md
```

---

## ⚕️ Disclaimer

This application is for **informational purposes only** and does not constitute medical advice. Always consult a qualified healthcare professional regarding your health and medical reports.
