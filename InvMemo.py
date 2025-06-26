import streamlit as st
from pathlib import Path
import tempfile
import base64
from pipeline import run_pipeline, PDFQueryEngine

# ---------------------------
# PAGE CONFIG & GLOBAL STYLE
# ---------------------------
st.set_page_config(page_title="IPO Investment Memo Generator", layout="wide")

st.markdown("""
    <style>
    footer:after {content:'' !important; display:none !important;}
    #MainMenu {visibility: visible;}
    header {visibility: visible;}

    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: #222;
        background-color: #f9f9f9;
    }

    .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    h1, h2, h3 {
        color: #00416A;
        margin-bottom: 0.25rem;
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

    .header-container {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        margin-bottom: 1.25rem;
    }

    .header-text h1 {
        font-size: 1.75rem;
        font-weight: 800;
        margin: 0;
        color: #1F2937;
    }

    .header-text p {
        margin: 0.2rem 0 0;
        font-size: 1rem;
        color: #4B5563;
    }

    .footer-note {
        text-align: left;
        font-size: 0.85rem;
        color: gray;
        margin-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# LOGO BASE64
# ---------------------------
def get_base64_logo(path="logo.png"):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_logo()

# ---------------------------
# HEADER: LEFT-ALIGNED LOGO + TITLE
# ---------------------------
st.markdown(f"""
<div class="header-container">
    <img src="data:image/png;base64,{logo_base64}" style="height: 60px; width: auto;" />
    <div class="header-text">
        <h1>Pre-IPO Investment Memo Generator</h1>
        <p>Upload an IPO/DRHP PDF to generate a structured investment memo with optional Q&amp;A.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# UPLOAD SECTION
# ---------------------------
st.subheader("📤 Upload PDF and Focus")
pdf_file = st.file_uploader("Upload DRHP or IPO PDF", type=["pdf"])

custom_focus = st.text_area(
    "Optional: Add custom notes to guide memo generation",
    help="Example: 'Focus more on the EV strategy and Indian market exposure'"
)

# ---------------------------
# GENERATE MEMO
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
    # QUESTION & ANSWER
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
<div class="footer-note">
    © 2025 YourCompanyName. All rights reserved.
</div>
""", unsafe_allow_html=True)
