from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from skill_gap import analyze_skill_gap


# Resume
pdf_file = r"D:\projectCV\Rachit_cv.pdf"


# Extract resume text
resume_text = extract_text_from_pdf(pdf_file)


# Candidate skills
candidate_skills = extract_skills(resume_text)


# Job description
job_description = """
We are looking for a Data Scientist with experience
in Python, SQL, Pandas, NumPy, Scikit-learn,
Machine Learning, Power BI, Docker and NLP.
"""


# Required skills
required_skills = extract_skills(job_description)


# Analyze skill gap
matched_skills, missing_skills = analyze_skill_gap(
    candidate_skills,
    required_skills
)


print("\n========== SKILL GAP ANALYSIS ==========")

print("\n✅ YOUR MATCHED SKILLS")

for skill in matched_skills:
    print("✓", skill)


print("\n⚠️ SKILLS YOU ARE MISSING")

for skill in missing_skills:
    print("✗", skill)


print("\n========== RECOMMENDATION ==========")

for skill in missing_skills:
    print(f"Learn {skill}")