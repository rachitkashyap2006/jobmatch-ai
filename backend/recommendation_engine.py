
# Skill priority and learning recommendations

SKILL_RECOMMENDATIONS = {
    "python": {
        "priority": 1,
        "prerequisites": [],
        "learning_path": "Python fundamentals and functions"
    },
    "sql": {
        "priority": 1,
        "prerequisites": [],
        "learning_path": "SQL queries, joins and aggregations"
    },
    "pandas": {
        "priority": 2,
        "prerequisites": ["python"],
        "learning_path": "Data cleaning and data manipulation"
    },
    "numpy": {
        "priority": 2,
        "prerequisites": ["python"],
        "learning_path": "Arrays and numerical computing"
    },
    "scikit-learn": {
        "priority": 2,
        "prerequisites": ["python", "numpy"],
        "learning_path": "Model training and evaluation"
    },
    "machine learning": {
        "priority": 2,
        "prerequisites": ["python", "pandas"],
        "learning_path": "Regression, classification and model evaluation"
    },
    "power bi": {
        "priority": 2,
        "prerequisites": ["sql"],
        "learning_path": "Data modeling and interactive dashboards"
    },
    "docker": {
        "priority": 3,
        "prerequisites": [],
        "learning_path": "Containers and deployment of ML APIs"
    },
    "nlp": {
        "priority": 3,
        "prerequisites": ["python", "machine learning"],
        "learning_path": "Text preprocessing, embeddings and NLP models"
    },
    "fastapi": {
        "priority": 2,
        "prerequisites": ["python"],
        "learning_path": "Build and serve ML models through REST APIs"
    }
}


def recommend_skills(missing_skills, candidate_skills):
    recommendations = []

    candidate_skills = set(candidate_skills)

    for skill in missing_skills:
        details = SKILL_RECOMMENDATIONS.get(
            skill,
            {
                "priority": 3,
                "prerequisites": [],
                "learning_path": f"Learn the fundamentals of {skill}"
            }
        )

        prerequisites_missing = [
            prerequisite
            for prerequisite in details["prerequisites"]
            if prerequisite not in candidate_skills
        ]

        recommendations.append({
            "skill": skill,
            "priority": details["priority"],
            "learning_path": details["learning_path"],
            "prerequisites_missing": prerequisites_missing
        })

    recommendations.sort(key=lambda item: item["priority"])

    return recommendations
