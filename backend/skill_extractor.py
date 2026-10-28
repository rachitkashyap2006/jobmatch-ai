SKILLS = [
    "python",
    "java",
    "sql",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "nlp",
    "power bi",
    "tableau",
    "docker",
    "git",
    "aws",
    "fastapi",
    "react"
]


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return found_skills