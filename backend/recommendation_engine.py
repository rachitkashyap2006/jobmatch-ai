
from skill_extractor import normalize_skill


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


def recommend_skills(
    missing_skills,
    candidate_skills,
    partially_matched=(),
    required_skills=None,
):
    recommendations = []

    candidate_skills = {normalize_skill(skill) for skill in candidate_skills}
    required_order = [
        normalize_skill(skill)
        for skill in (required_skills or [])
    ]
    partial_by_required = {
        item["required_skill"]: item
        for item in partially_matched
    }
    skills_to_learn = list(dict.fromkeys(
        [
            *(normalize_skill(skill) for skill in missing_skills),
            *partial_by_required,
        ]
    ))

    for skill in skills_to_learn:
        details = SKILL_RECOMMENDATIONS.get(
            skill.casefold(),
            {
                "priority": 3,
                "prerequisites": [],
                "learning_path": f"Learn the fundamentals of {skill}"
            }
        )

        prerequisites_missing = [
            prerequisite
            for prerequisite in details["prerequisites"]
            if normalize_skill(prerequisite) not in candidate_skills
        ]

        recommendations.append({
            "skill": skill,
            "priority": min(
                details["priority"],
                1 if skill in required_order[:3] else (
                    2 if skill in required_order else 3
                ),
            ),
            "learning_path": details["learning_path"],
            "prerequisites_missing": prerequisites_missing,
            "status": "partially_matched" if skill in partial_by_required else "missing",
            "related_skill": next(
                (
                    item["candidate_skill"]
                    for item in partially_matched
                    if item["required_skill"] == skill
                ),
                None,
            ),
        })

    recommendations.sort(
        key=lambda item: (
            item["priority"],
            required_order.index(item["skill"])
            if item["skill"] in required_order else len(required_order),
            item["skill"].casefold(),
        )
    )

    return recommendations
