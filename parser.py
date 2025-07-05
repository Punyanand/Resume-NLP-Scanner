import spacy
import nltk
import os
nltk.data.path.clear()
nltk_data_path= os.path.abspath('nltk_data')
nltk.download('punkt_tab', download_dir=nltk_data_path)
from nltk.tokenize import sent_tokenize
from thefuzz import fuzz
from skill_set import curated_skills

nlp = spacy.load("en_core_web_sm")

import re

def extract_skills(text):
    text_lower = text.lower()
    doc = nlp(text_lower)
    tokens = {token.text for token in doc if token.pos_ in ["NOUN", "PROPN"]}

    matched_skills = set()
    for skill in curated_skills:
        if " " in skill:
            if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                matched_skills.add(skill)
        else:
            if any(fuzz.ratio(skill, token) >= 95 for token in tokens):
                matched_skills.add(skill)
    return list(matched_skills)


def extract_sentences(text):
    return sent_tokenize(text)

def match_skills_with_scores(resume_skills, job_skills, threshold=80):
    results = []
    for job_skill in job_skills:
        best_score = 0
        best_match = None
        for resume_skill in resume_skills:
            score = fuzz.token_set_ratio(job_skill.lower(), resume_skill.lower())
            if score > best_score:
                best_score = score
                best_match = resume_skill
        results.append({
            "job_skill": job_skill,
            "resume_match": best_match if best_score >= threshold else None,
            "score": best_score
        })
    return results



def calculate_resume_score(matched_skills, total_job_skills):
    if total_job_skills == 0:
        return 0
    return round((len(matched_skills) / total_job_skills) * 100, 2)