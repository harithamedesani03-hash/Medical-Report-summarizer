"""
MediReport AI — Patient-Friendly Medical Report Summariser
Powered by Google Gemini 2.5 Flash
"""

import os
import streamlit as st
from dotenv import load_dotenv

from document_processor import process_uploaded_file
from gemini_client import configure_gemini, analyze_report

# ─────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MediReport AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────
load_dotenv()


# ─────────────────────────────────────────────
# Session State Initialisation
# ─────────────────────────────────────────────
if "summary" not in st.session_state:
    st.session_state.summary = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# ─────────────────────────────────────────────
# Sidebar — Configuration & Instructions
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    st.divider()

    # API Key Input
    st.subheader("🔑 Gemini API Key")
    api_key_env = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Enter your Gemini API Key",
        value=api_key_env,
        type="password",
        placeholder="AIza...",
        help="Get your free API key from https://aistudio.google.com/app/apikey",
    )

    if not api_key_input:
        st.warning("Please enter your Gemini API key to get started.")
    else:
        st.success("API key loaded ✓")

    st.divider()

    # How it Works
    st.subheader("ℹ️ How It Works")
    st.markdown(
        """
        1. **Upload** your medical report (PDF, image, DOCX, or TXT)
        2. **Click** "Analyse Report"
        3. **Receive** a plain-language summary with:
           - Key findings explained simply
           - Flagged abnormal values
           - Recommended next steps
           - Questions to ask your doctor
        """
    )

    st.divider()

    # Supported File Types
    st.subheader("📂 Supported Formats")
    st.markdown(
        """
        | Format | Description |
        |--------|-------------|
        | 📄 PDF | Lab results, discharge summaries |
        | 🖼️ PNG/JPG | Scanned reports, photos |
        | 📝 DOCX | Word documents |
        | 📃 TXT | Plain text reports |
        """
    )

    st.divider()

    # Disclaimer
    st.caption(
        "⚕️ **Disclaimer:** This tool is for informational purposes only "
        "and does not constitute medical advice. Always consult a qualified "
        "healthcare professional."
    )


# ─────────────────────────────────────────────
# Main Page — Header
# ─────────────────────────────────────────────
st.title("🏥 MediReport AI")
st.markdown(
    "#### Your personal medical report interpreter — powered by Google Gemini 2.5 Flash"
)
st.markdown(
    "Upload your medical report and receive a **clear, patient-friendly summary** "
    "that explains key findings in plain English."
)
st.divider()


# ─────────────────────────────────────────────
# File Upload Section
# ─────────────────────────────────────────────
st.subheader("📤 Upload Your Medical Report")

uploaded_file = st.file_uploader(
    "Choose a file to upload",
    type=["pdf", "png", "jpg", "jpeg", "bmp", "tiff", "webp", "docx", "txt"],
    help="Supported: PDF, PNG, JPG, JPEG, BMP, TIFF, WebP, DOCX, TXT",
    label_visibility="collapsed",
)

# Show file preview info
if uploaded_file is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📁 File Name", uploaded_file.name)
    with col2:
        size_kb = uploaded_file.size / 1024
        size_label = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        st.metric("📏 File Size", size_label)
    with col3:
        ext = uploaded_file.name.rsplit(".", 1)[-1].upper() if "." in uploaded_file.name else "Unknown"
        st.metric("🗂️ File Type", ext)

    # Image preview (for image uploads)
    if uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")):
        st.image(uploaded_file, caption="Uploaded Report Preview", use_container_width=True)


st.divider()


# ─────────────────────────────────────────────
# Analyse Button
# ─────────────────────────────────────────────
analyse_col, clear_col = st.columns([3, 1])

with analyse_col:
    analyse_clicked = st.button(
        "🔍 Analyse Report",
        type="primary",
        disabled=(uploaded_file is None or not api_key_input),
        use_container_width=True,
    )

with clear_col:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.summary = None
        st.session_state.file_name = None
        st.session_state.analysis_done = False
        st.rerun()


# ─────────────────────────────────────────────
# Analysis Logic
# ─────────────────────────────────────────────
if analyse_clicked and uploaded_file is not None and api_key_input:
    # Reset previous result
    st.session_state.summary = None
    st.session_state.analysis_done = False

    try:
        # Configure Gemini
        configure_gemini(api_key_input)

        # Read file bytes
        file_bytes = uploaded_file.read()

        # Process document
        with st.spinner("📄 Reading and processing your document…"):
            text, images, file_type = process_uploaded_file(file_bytes, uploaded_file.name)

        # Send to Gemini
        with st.spinner("🤖 Gemini is analysing your report — this usually takes 10–30 seconds…"):
            summary = analyze_report(text, images, file_type)

        # Store result
        st.session_state.summary = summary
        st.session_state.file_name = uploaded_file.name
        st.session_state.analysis_done = True
        st.success("✅ Analysis complete!")

    except ValueError as ve:
        st.error(f"⚠️ File Processing Error: {ve}")
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            st.error("❌ Invalid Gemini API Key. Please check your key and try again.")
        elif "quota" in error_msg.lower():
            st.error("⏳ API quota exceeded. Please wait a moment and try again.")
        elif "SAFETY" in error_msg:
            st.error("🚫 The content was blocked by Gemini's safety filters. Please try a different document.")
        else:
            st.error(f"❌ An error occurred: {error_msg}")


# ─────────────────────────────────────────────
# Results Section
# ─────────────────────────────────────────────
if st.session_state.analysis_done and st.session_state.summary:
    st.divider()
    st.subheader(f"📊 Summary for: `{st.session_state.file_name}`")
    st.markdown(st.session_state.summary)

    st.divider()

    # Download Button
    st.download_button(
        label="⬇️ Download Summary as Text File",
        data=st.session_state.summary,
        file_name=f"MediReport_Summary_{st.session_state.file_name.rsplit('.', 1)[0]}.txt",
        mime="text/plain",
        use_container_width=True,
    )


# ─────────────────────────────────────────────
# Empty State — When no file is uploaded yet
# ─────────────────────────────────────────────
if not uploaded_file and not st.session_state.analysis_done:
    st.info(
        "👆 Upload a medical report above to get started. "
        "Your file is processed securely and never stored permanently."
    )

    st.divider()

    # Feature highlight cards using columns
    st.subheader("✨ What MediReport AI Can Do For You")

    feat1, feat2, feat3 = st.columns(3)

    with feat1:
        st.markdown("### 🔬 Decode Lab Results")
        st.markdown(
            "Understand what your blood test numbers mean, which values "
            "are within range, and which ones need attention."
        )

    with feat2:
        st.markdown("### 🏥 Simplify Discharge Summaries")
        st.markdown(
            "Get a clear breakdown of your hospital stay, diagnoses, "
            "medications prescribed, and follow-up instructions."
        )

    with feat3:
        st.markdown("### 📋 Action-Oriented Guidance")
        st.markdown(
            "Receive specific next steps and a list of questions you "
            "can bring to your next doctor's appointment."
        )
