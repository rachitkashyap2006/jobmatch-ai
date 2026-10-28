from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from matcher import compare_skills, calculate_final_score
from semantic_matcher import calculate_similarity


# Resume
pdf_file = r"D:\projectCV\Rachit_cv.pdf"


# Extract resume text
resume_text = extract_text_from_pdf(pdf_file)


# Extract candidate skills
candidate_skills = extract_skills(resume_text)


# Job description
job_description = """
We are looking for a Data Scientist with experience
in Python, SQL, Pandas, NumPy, Scikit-learn,
Machine Learning, Power BI and Docker.
"""


# Extract required skills
required_skills = extract_skills(job_description)


# Skill matching
matched_skills, missing_skills, skill_score = compare_skills(
    candidate_skills,
    required_skills
)


# Semantic matching
semantic_score = calculate_similarity(
    resume_text,
    job_description
)


# Final score
final_score = calculate_final_score(
    skill_score,
    semantic_score
)


# Display results
print("\n========== JOB MATCH ANALYSIS ==========")

print("\nMatched Skills:")

for skill in matched_skills:
    print("✓", skill)


print("\nMissing Skills:")

for skill in missing_skills:
    print("✗", skill)


print("\n========== SCORES ==========")

print(f"Skill Match:     {skill_score:.2f}%")
print(f"Semantic Match:  {semantic_score:.2f}%")
print(f"Final Match:     {final_score:.2f}%")