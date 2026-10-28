from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from matcher import compare_skills


# Resume PDF
pdf_file = r"D:\projectCV\Rachit_cv.pdf"


# -----------------------------
# STEP 1: Extract resume text
# -----------------------------

resume_text = extract_text_from_pdf(pdf_file)


# -----------------------------
# STEP 2: Extract candidate skills
# -----------------------------

candidate_skills = extract_skills(resume_text)


print("\n========== YOUR SKILLS ==========")

for skill in candidate_skills:
    print("✓", skill)


# -----------------------------
# STEP 3: Job Description
# -----------------------------

job_description = """
We are looking for a Data Scientist with experience
in Python, SQL, Pandas, NumPy, Scikit-learn,
Machine Learning, Power BI and Docker.
"""


# -----------------------------
# STEP 4: Extract required skills
# -----------------------------

required_skills = extract_skills(job_description)


print("\n========== REQUIRED SKILLS ==========")

for skill in required_skills:
    print("•", skill)


# -----------------------------
# STEP 5: Compare skills
# -----------------------------

matched_skills, missing_skills, match_percentage = compare_skills(
    candidate_skills,
    required_skills
)


# -----------------------------
# STEP 6: Display results
# -----------------------------

print("\n========== MATCHED SKILLS ==========")

for skill in matched_skills:
    print("✓", skill)


print("\n========== MISSING SKILLS ==========")

for skill in missing_skills:
    print("✗", skill)


print("\n========== MATCH SCORE ==========")

print(f"{match_percentage:.2f}%")