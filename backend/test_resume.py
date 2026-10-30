from resume_parser import build_candidate_profile


def test_resume_profile_extracts_education_projects_and_evidence():
    resume = """
    PROFILE: Recent graduate seeking an internship.
    EDUCATION: B.Sc. in Computer Science, North College
    TECHNICAL SKILLS: Python, SQL
    PROJECTS: Job Tracker - Built a small Python and SQL application.
    """

    profile = build_candidate_profile(resume)

    assert profile["candidate_level"] == "fresher"
    assert profile["education"][0]["degree"].startswith("B.Sc")
    assert profile["projects"][0]["name"] == "Job Tracker"
    assert profile["technical_skills"]
    assert profile["technical_skills"][0]["evidence"][0]["text"]


def test_resume_parser_accepts_headings_without_punctuation():
    resume = """
    PROFILE
    Experienced application developer.
    EDUCATION
    B.Tech in Computer Science, North College
    EXPERIENCE
    Backend Developer at Example Labs
    Built APIs with Python and FastAPI.
    SKILLS
    Python, FastAPI, SQL
    """

    profile = build_candidate_profile(resume)

    assert profile["education"][0]["degree"].startswith("B.Tech")
    assert profile["work_experience"][0]["role"] == "Backend Developer"
    assert profile["experience_years"] is None
    assert profile["candidate_level"] == "experienced"
    assert profile["experience_years"] is None
