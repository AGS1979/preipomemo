import streamlit as st
from pathlib import Path
import tempfile
from pipeline import run_pipeline, PDFQueryEngine

st.set_page_config(page_title="IPO Investment Memo Generator", layout="wide")

st.title("📄 Pre-IPO Investment Memo Generator")
st.markdown("Upload an IPO/DRHP PDF and get a structured investment memo.")

# Upload PDF
pdf_file = st.file_uploader("Upload DRHP or IPO PDF", type=["pdf"])

# Optional: Add custom focus
custom_focus = st.text_area(
    "Optional: Add custom notes or focus areas to guide memo generation",
    help="Example: 'Focus more on the EV strategy and Indian market exposure'"
)

# Buttons and results
if pdf_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_pdf_path = tmp_file.name

    if st.button("📘 Generate Investment Memo"):
        with st.spinner("Processing and analyzing the document..."):
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

    st.markdown("---")
    st.subheader("🔍 Ask Questions from the PDF")
    query = st.text_input("Type your question below (e.g., What are the risk factors?)")

    if query:
        try:
            engine = PDFQueryEngine()
            with st.spinner("Answering your query using DeepSeek..."):
                answer_html, cited_pages = engine.answer_query(tmp_pdf_path, query)
                st.markdown(answer_html, unsafe_allow_html=True)
                st.caption(f"📄 Cited Pages: {cited_pages}")
        except Exception as e:
            st.error(f"❌ Error: {e}")
