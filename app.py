import streamlit as st
from utils import extract_text_from_pdf
from parser import extract_skills, extract_sentences
import nltk
import os
import pandas as pd
import streamlit as st
import plotly.express as px
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
nltk.data.path.append(nltk_data_path)
if not os.path.exists(os.path.join(nltk_data_path, "tokenizers", "punkt")):
    nltk.download("punkt", download_dir=nltk_data_path)
# nltk.data.path.clear()
# nltk_data_path= os.path.abspath('K:\NLPScanner\venv311\nltk_data\tokenizers\tokenizers')
# nltk.download('punkt_tab', download_dir=nltk_data_path)
import streamlit as st
from utils import extract_text_from_pdf
from parser import extract_skills, extract_sentences, match_skills_with_scores, calculate_resume_score


st.set_page_config(page_title="Resume Scanner", layout="wide")

st.title("📝 Resume Scanner + Job Match Scorer")

# --- Upload Resume ---
uploaded_file = st.file_uploader("📤 Upload a Resume (PDF)", type=["pdf"])

# --- Job Description Input ---
job_description = st.text_area("📋 Paste Job Description Here", height=200, placeholder="e.g., We are looking for a data analyst with Python, SQL, Tableau...")

# --- Main Logic ---
if uploaded_file is not None and job_description.strip():
    with st.spinner("🔍 Processing Resume..."):
        # Step 1: Extract skills
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_description)

        # Step 2: Match skills with scores
        results = match_skills_with_scores(resume_skills, job_skills)

        # Step 3: Calculate score
        match_count = sum(1 for r in results if r["score"] >= 80)
        score = round((match_count / len(job_skills)) * 100, 2) if job_skills else 0

        # --- Critical Skill Selection ---
        st.subheader("⭐ Mark Critical Skills (Must-Have)")
        critical_skills = st.multiselect("Select critical job skills", job_skills)

        # --- Prepare DataFrame for display ---
        df = pd.DataFrame(results)
        df["status"] = df.apply(lambda row: "Matched" if row["score"] >= 80 else (
            "Missing 🔴" if row["job_skill"] in critical_skills else "Missing"), axis=1)

        # --- Skill Match Bar Chart ---
        st.subheader("📊 Skill Match Chart")
        fig = px.bar(
            df,
            x="job_skill",
            y="score",
            color="status",
            color_discrete_map={"Matched": "green", "Missing": "gray", "Missing 🔴": "red"},
            title="Skill Match Score (%) per Job Skill"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Resume Score ---
        st.subheader("📈 Resume Score")
        st.metric(label="Match Score", value=f"{score}/100")

        # --- Missing Critical Skills ---
        st.subheader("🚨 Missing Critical Skills")
        missing_critical = df[df["status"] == "Missing 🔴"]
        if not missing_critical.empty:
            for s in missing_critical["job_skill"]:
                st.markdown(f"- ❌ **{s}**")
        else:
            st.success("✅ All critical skills are covered!")

        # --- Resume & Job Skills ---
        with st.expander("📄 Extracted Resume Skills"):
            st.write(resume_skills)

        with st.expander("🧾 Extracted Job Description Skills"):
            st.write(job_skills)