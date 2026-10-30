from skill_extractor import (
    extract_job_requirements,
    extract_skills,
    extract_skills_with_evidence,
)


def test_skill_extraction_normalizes_aliases_and_keeps_context():
    text = "Built a service with SKLearn, Python, and PowerBI."

    skills = extract_skills(text)
    evidence = extract_skills_with_evidence(text)

    assert "scikit-learn" in skills
    assert "Power BI" in skills
    assert next(item for item in evidence if item["skill"] == "Python")[
        "evidence"
    ] == "Built a service with SKLearn, Python, and PowerBI"


def test_job_requirements_keep_required_and_preferred_skills_separate():
    requirements = extract_job_requirements(
        "Required skills: Python, SQL. Nice to have: Python, Tableau."
    )

    assert set(requirements["required_skills"]) == {"Python", "SQL"}
    assert set(requirements["preferred_skills"]) == {"Python", "Tableau"}
