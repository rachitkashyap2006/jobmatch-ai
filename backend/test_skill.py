from skill_extractor import extract_skills


resume_text = """
I am a Python developer.
I have experience with Pandas, NumPy,
SQL, Machine Learning and FastAPI.
"""


skills = extract_skills(resume_text)

print("Skills found:")
print(skills)