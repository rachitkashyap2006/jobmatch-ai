
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from skill_gap import analyze_skill_gap
from recommendation_engine import recommend_skills

pdf_file = r"D:\projectCV\Rachit_cv.pdf"

# 1. Read resume
resume_text = extract_text_from_pdf(pdf_file)

# 2. Extract candidate skills
candidate_skills = extract_skills(resume_text)

# 3. Example job description
job_description = """
We need a Data Scientist with Python, SQL, Pandas,
NumPy, Scikit-learn, Machine Learning, Power BI,
Docker and NLP.
"""

# 4. Extract job requirements
required_skills = extract_skills(job_description)

# 5. Find missing skills
matched_skills, missing_skills = analyze_skill_gap(
    candidate_skills,
    required_skills
)

# 6. Generate recommendations
recommendations = recommend_skills(
    missing_skills,
    candidate_skills
)

# 7. Display results
print("\n===== SKILL RECOMMENDATIONS =====")

for item in recommendations:
    print(f"\nSkill: {item['skill']}")
    print(f"Priority: {item['priority']}")
    print(f"Learning path: {item['learning_path']}")

    if item["prerequisites_missing"]:
        print(
            "Learn prerequisites first:",
            ", ".join(item["prerequisites_missing"])
        )
