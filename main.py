import streamlit as st
from pypdf import PdfReader
import io
import os
import cohere
from dotenv import load_dotenv

load_dotenv()

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="🚀 AI Resume ATS Analyzer", page_icon="🤖", layout="centered")

# ----------------- CUSTOM CSS (Futuristic UI) -----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0d0f14, #111827);
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

.main {
    background: transparent;
}

.block-container {
    border-radius: 12px;
    padding: 30px;
}

h1, h2, h3, h4, h5, p, label {
    color: #f1f5f9 !important;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.05);
    padding: 28px;
    border-radius: 14px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 15px;
}

/* Upload Area */
.css-1n76uvr {
    background: rgba(255,255,255,0.1) !important;
    border: 1px dashed #4f46e5 !important;
}

/* Button */
.stButton>button {
    background: linear-gradient(90deg,#4f46e5,#9333ea);
    color: white;
    padding: 12px 22px;
    font-size: 17px;
    border-radius: 10px;
    transition: 0.3s;
    border: none;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px #7c3aed;
}

/* TextBox */
.stTextInput>div>div>input {
    background: rgba(255,255,255,0.08);
    color: white;
    border-radius: 8px;
}

/* Title Glow */
.title-glow {
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(to right, #60a5fa, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    color: transparent;
}
</style>
""", unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown("<h1 class='title-glow'>🤖 AI Resume ATS Analyzer</h1>", unsafe_allow_html=True)
st.write("Upload your resume and get **real ATS score + AI feedback instantly**")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

uploaded_file = st.file_uploader("📎 Upload Resume (PDF/TXT)", type=["pdf", "txt"])
# Upload Job Description
jd_text_input = st.text_area("📄 Paste Job Description (optional)", height=180, placeholder="Paste the Job Description here...")
job_role = st.text_input("🎯 Target Job Role (optional)", placeholder="Ex: Data Scientist / Software Engineer")

analyze = st.button("🚀 Run ATS Analysis")

# ----------------- PDF Extract Functions -----------------
def extract_text_from_pdf(uploaded_file):
    Pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in Pdf_reader.pages:
        text += page.extract_text() + '\n'
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8", errors="ignore")

# ----------------- ANALYSIS LOGIC -----------------
if analyze and uploaded_file:
    with st.spinner("⚙️ Processing Resume, please wait..."):
        try:
            # Extract Resume Text
            resume_text = extract_text_from_file(uploaded_file)
            if not resume_text.strip():
                st.error("⚠️ Resume file contains no readable text")
                st.stop()

            # Extract JD Text (optional)
            # JD Text from textarea
            jd_text = jd_text_input.strip() if jd_text_input.strip() else (job_role if job_role else "")


            prompt = f"""
            You are an ATS and resume evaluation system.

            Tasks:
            1️⃣ Score resume vs ATS systems (0-100)
            2️⃣ Provide Keyword Match Score (0-100)
            3️⃣ Score Resume vs Job Description (0-100)
            4️⃣ List Matched Keywords
            5️⃣ List Missing & Recommended Keywords
            6️⃣ Give Strengths (bullet points)
            7️⃣ Give Weaknesses (bullet points)
            8️⃣ Suggestions to improve ATS score
            9️⃣ Provide one-line summary

            Resume:
            {resume_text}

            Job Description:
            {jd_text}
            """

            response = co.chat(
                model="command-r-08-2024",
                message=prompt,
                temperature=0.3,
                max_tokens=1200
            )

            st.markdown("<div class='card'><h3>📊 ATS + JD Match Analysis</h3></div>", unsafe_allow_html=True)
            st.write(response.text)

        except Exception as e:
            st.error(f"❌ Error: {e}")


#uv run streamlit run main.py  