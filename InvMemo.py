import streamlit as st
from pathlib import Path
import tempfile
from pipeline import run_pipeline, PDFQueryEngine

# ---------------------------
# PAGE CONFIG & BRANDING CSS
# ---------------------------
st.set_page_config(page_title="IPO Investment Memo Generator", layout="wide")

st.markdown("""
    <style>
    /* Hide only the 'Made with Streamlit' footer */
    footer:after {
        content:'' !important;
        display:none !important;
    }

    /* Preserve Streamlit menu and top-right controls */
    #MainMenu {visibility: visible;}
    header {visibility: visible;}

    /* Font & color styling */
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
    }
    </style>
""", unsafe_allow_html=True)



# ---------------------------
# LOGO + TITLE
# ---------------------------
logo_path = Path("logo.png").as_posix()
st.markdown(f"""
    <div style="text-align: center; padding-top: 2rem; padding-bottom: 1.5rem;">
        <img src="data:image/png;base64,{Path(logo_path).read_bytes().hex()}" style="height: 80px; margin-bottom: 1rem;" />
        <h1 style="font-size: 2.25rem; font-weight: 800; color: #1F2937; margin-bottom: 0.5rem;">
            Pre-IPO Investment Memo Generator
        </h1>
        <p style="font-size: 1.05rem; color: #4B5563;">
            Upload an IPO/DRHP PDF to generate a structured investment memo with optional Q&A.
        </p>
    </div>
""", unsafe_allow_html=True)
# ---------------------------
# INPUT SECTION
# ---------------------------
with st.container():
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
    <div style='text-align: center; font-size: 0.85rem; color: gray;'>
        © 2025 YourCompanyName. All rights reserved.
    </div>
""", unsafe_allow_html=True)
