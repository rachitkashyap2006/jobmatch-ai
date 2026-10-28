from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills


pdf_file = "Rachit_cv.pdf"


# Stage 1: Extract text
resume_text = extract_text_from_pdf(pdf_file)

print("========== RESUME TEXT ==========")
print(resume_text)


# Stage 2: Extract skills
skills = extract_skills(resume_text)

print("\n========== SKILLS FOUND ==========")

for skill in skills:
    print("✓", skill)