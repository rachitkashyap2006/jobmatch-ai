from matcher import compare_skills
from skill_extractor import extract_skills


def test_compare_skills_returns_exact_matches_and_missing_skills():
    candidate = extract_skills("Python, SQL, and pandas")
    required = extract_skills("Python, SQL, Tableau")

    matched, missing, score = compare_skills(candidate, required)

    assert matched == {"Python", "SQL"}
    assert missing == {"Tableau"}
    assert abs(score - 200 / 3) < 1e-8
