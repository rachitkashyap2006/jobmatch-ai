from resume_parser import extract_text_from_pdf
from semantic_matcher import calculate_similarity


# Resume PDF
pdf_file = r"D:\projectCV\Rachit_cv.pdf"


# Extract resume text
resume_text = extract_text_from_pdf(pdf_file)


# Job Description
job_description = """
We are looking for a Data Scientist with experience
in Python, SQL, Pandas, NumPy, Scikit-learn,
Machine Learning, Power BI and Docker.
"""


# Calculate semantic similarity
score = calculate_similarity(
    resume_text,
    job_description
)


print("\n========== SEMANTIC MATCH SCORE ==========")

print(f"{score:.2f}%")