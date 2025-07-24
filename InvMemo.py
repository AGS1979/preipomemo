import streamlit as st
from pathlib import Path
import tempfile
import base64
import streamlit.components.v1 as components
from pipeline import run_pipeline, PDFQueryEngine, generate_infographic_html

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
        padding-top: 3rem; /* Changed from 1rem to 3rem */
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
# HEADER: Smaller logo + Title below
# ---------------------------
st.markdown(f"""
    <div style="display: flex; flex-direction: column; align-items: flex-start; gap: 0.5rem; margin-bottom: 1.5rem;">
        <img src="data:image/png;base64,{logo_base64}" style="height: 36px; width: auto;" />
        <div style="margin-left: 2px;">
            <h1 style="font-size: 1.6rem; font-weight: 800; color: #1F2937; margin-bottom: 0.2rem;">
                Pre-IPO Investment Memo Generator
            </h1>
            <p style="font-size: 1rem; color: #4B5563; margin-top: 0;">
                Upload an IPO/DRHP PDF to generate a structured investment memo with optional Q&A.
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------
# STATE INITIALIZATION
# ---------------------------
if "memo_generated" not in st.session_state:
    st.session_state.memo_generated = False

if "memo_path" not in st.session_state:
    st.session_state.memo_path = None

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
                st.session_state.memo_generated = True
                st.session_state.memo_path = memo_path
                st.success("✅ Memo generated successfully!")

                with open(memo_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Memo",
                        data=f,
                        file_name=Path(memo_path).name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"❌ Error generating memo: {e}")

# ---------------------------
# GENERATE INFOGRAPHIC
# ---------------------------
if st.session_state.memo_generated and st.session_state.memo_path:
    st.markdown("---")
    st.subheader("🎨 Infographic View")

    if st.button("🎨 Generate Infographic"):
        try:
            with st.spinner("🖼️ Generating infographic..."):
                company_name = Path(st.session_state.memo_path).stem.split("_")[0]
                infographic_html = generate_infographic_html(
                    docx_path=st.session_state.memo_path,
                    company_name=company_name
                )
                st.components.v1.html(infographic_html, height=1000, scrolling=True)

                st.download_button(
                    label="📥 Download Infographic HTML",
                    data=infographic_html,
                    file_name="infographic.html",
                    mime="text/html"
                )
        except Exception as e:
            st.error(f"❌ Error generating infographic: {e}")

# ---------------------------
# QUESTION & ANSWER
# ---------------------------
if pdf_file:
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
    © 2025 Aranca. All rights reserved.
</div>
""", unsafe_allow_html=True)
