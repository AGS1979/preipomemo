import streamlit as st
from pathlib import Path
import tempfile
import base64
from pipeline import run_pipeline, PDFQueryEngine

# ---------------------------
# PAGE CONFIG & BRANDING CSS
# ---------------------------
st.set_page_config(page_title="IPO Investment Memo Generator", layout="wide")

st.markdown("""
    <style>
    footer:after {
        content:'' !important;
        display:none !important;
    }
    #MainMenu {visibility: visible;}
    header {visibility: visible;}
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: #222;
        background-color: #f9f9f9;
    }
    h1, h2, h3 {
        color: #00416A;
    }
    .stButton>button {
        background-color: #00416A;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.6em 1.5em;
    }
    .stTextInput>div>div>input,
    .stTextArea textarea {
        border-radius: 6px;
    }
    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# BASE64 LOGO HELPER
# ---------------------------
def get_base64_logo(path="logo.png"):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_logo()

# ---------------------------
# HEADER: LOGO + TITLE (Left-Aligned)
# ---------------------------
st.markdown(f"""
<div style="display: flex; align-items: center; gap: 1.25rem; margin-bottom: 2rem;">
    <img src="data:image/png;base64,{logo_base64}" style="height: 60px; max-width: 160px;" />
    <div>
        <h1 style="margin-bottom: 0.3rem; font-size: 2rem; font-weight: 800; color: #1F2937;">Pre-IPO Investment Memo Generator</h1>
        <p style="font-size: 1rem; color: #4B5563; margin-top: 0;">Upload an IPO/DRHP PDF to generate a structured investment memo with optional Q&amp;A.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# INPUT SECTION
# ---------------------------
st.subheader("📤 Upload PDF and Focus")
pdf_file = st.file_uploader("Upload DRHP or IPO PDF", type=["pdf"])

custom_focus = st.text_area(
    "Optional: Add custom notes to guide memo generation",
    help="Example: 'Focus more on the EV strategy and Indian market exposure'"
)

# ---------------------------
# PROCESS + OUTPUT
# ---------------------------
if pdf_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_pdf_path = tmp_file.name

    if st.button("📘 Generate Investment Memo"):
        with st.spinner("⏳ Processing and analyzing the document..."):
            try:
                memo_path = run_pipeline(tmp_pdf_path, custom_focus)
                st.success("✅ Memo generated successfully!")

                with open(memo_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Memo",
                        data=f,
                        file_name=Path(memo_path).name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")

    # ---------------------------
    # Q&A SECTION
    # ---------------------------
    st.markdown("---")
    st.subheader("🔍 Ask Questions from the PDF")
    query = st.text_input("Type your question (e.g., What are the key risk factors?)")

    if query:
        try:
            engine = PDFQueryEngine()
            with st.spinner("💬 Querying document..."):
                answer_html, cited_pages = engine.answer_query(tmp_pdf_path, query)
                st.markdown(answer_html, unsafe_allow_html=True)
                st.caption(f"📄 Cited Pages: {cited_pages}")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("""
    <hr>
    <div style='text-align: left; font-size: 0.85rem; color: gray;'>
        © 2025 YourCompanyName. All rights reserved.
    </div>
""", unsafe_allow_html=True)
