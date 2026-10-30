from fastapi.testclient import TestClient

import main
from recommend_jobs import recommend_jobs
from resume_parser import build_candidate_profile
from skill_extractor import extract_skills, normalize_skill
from skill_gap import match_required_skills


FRESHER_RESUME = """
PROFILE: Recent graduate seeking an entry-level data analyst role.
EDUCATION: B.Sc. in Statistics, North College (2022-2025)
TECHNICAL SKILLS: SQL, Excel, Power BI, Data Analysis, Statistics
PROJECTS: Sales Dashboard - Analyzed sales data with SQL and Power BI.
"""

EXPERIENCED_RESUME = """
PROFILE: Backend engineer with 7 years of professional experience.
WORK EXPERIENCE: Senior Python Backend Developer, Acme (2019-Present):
Built REST APIs and distributed services for production workloads.
TECHNICAL SKILLS: Python, FastAPI, PostgreSQL, Docker, Kubernetes,
Microservices, AWS, Git
CERTIFICATIONS: AWS Certified Developer
"""

INTERN_RESUME = """
PROFILE: Computer science student looking for an internship.
EDUCATION: B.Tech in Computer Science (2023-Present)
INTERNSHIPS: Software Engineering Intern, Example Labs (2025-Present):
Built a Python API and wrote unit tests.
TECHNICAL SKILLS: Python, FastAPI, Git, pytest
PROJECTS: Course Planner - Built a small web application.
"""

NONTECHNICAL_RESUME = """
PROFILE: Business analyst with 5 years of experience supporting operations.
WORK EXPERIENCE: Business Analyst, Example Services (2020-Present):
Gathered requirements, documented processes, and coordinated user acceptance
testing with stakeholders.
SOFT SKILLS: Stakeholder Management, Communication, Presentation Skills
TECHNICAL SKILLS: Requirements Gathering, Documentation, User Stories, JIRA,
Agile/Scrum, Process Mapping, UAT, Excel
EDUCATION: B.A. in Business Administration
"""

INCOMPLETE_RESUME = "Python and Excel."


def test_skill_normalization_preserves_distinct_technologies():
    assert normalize_skill("SKLearn") == "scikit-learn"
    assert normalize_skill("PowerBI") == "Power BI"
    assert normalize_skill("TensorFlow") != normalize_skill("PyTorch")

    matched, partial, missing = match_required_skills(
        ["Power BI", "TensorFlow"],
        ["Tableau", "PyTorch", "NLP"],
    )
    assert matched == []
    assert {item["required_skill"] for item in partial} == {
        "Tableau", "PyTorch"
    }
    assert missing == ["NLP"]


def test_profile_builder_uses_evidence_and_handles_incomplete_resumes():
    fresher = build_candidate_profile(FRESHER_RESUME)
    experienced = build_candidate_profile(EXPERIENCED_RESUME)
    intern = build_candidate_profile(INTERN_RESUME)
    nontechnical = build_candidate_profile(NONTECHNICAL_RESUME)
    incomplete = build_candidate_profile(INCOMPLETE_RESUME)

    assert fresher["candidate_level"] == "fresher"
    assert fresher["education"][0]["degree"] is not None
    assert fresher["projects"][0]["evidence"]
    assert experienced["candidate_level"] == "experienced"
    assert experienced["experience_years"] >= 7
    assert experienced["work_experience"][0]["role"]
    assert experienced["certifications"][0]["evidence"]
    assert intern["candidate_level"] == "intern"
    assert intern["internships"][0]["evidence"]
    assert nontechnical["candidate_level"] == "experienced"
    assert nontechnical["soft_skills"]
    assert incomplete["candidate_level"] == "unknown"
    assert incomplete["data_quality_warnings"]
    extracted = extract_skills(FRESHER_RESUME)
    assert "SQL" in extracted
    assert "Python" not in extracted


def test_candidate_profiles_receive_distinct_recommendations():
    fresher_jobs = recommend_jobs(FRESHER_RESUME, top_n=5)
    backend_jobs = recommend_jobs(EXPERIENCED_RESUME, top_n=5)
    business_jobs = recommend_jobs(NONTECHNICAL_RESUME, top_n=5)
    intern_jobs = recommend_jobs(INTERN_RESUME, top_n=5)

    assert fresher_jobs and backend_jobs and business_jobs and intern_jobs
    assert fresher_jobs[0]["job_id"] != backend_jobs[0]["job_id"]
    assert backend_jobs[0]["job_id"] != business_jobs[0]["job_id"]
    assert fresher_jobs[0]["min_years_experience"] <= 1
    assert sum(job["min_years_experience"] <= 2 for job in fresher_jobs) >= 4
    assert backend_jobs[0]["min_years_experience"] >= 3
    assert any(job["min_years_experience"] == 0 for job in intern_jobs)
    assert all(job["explanations"] for job in fresher_jobs)
    assert all(0 <= job["final_match_score"] <= 100 for job in business_jobs)
    assert all("required_skill_match" in job["score_breakdown"] for job in backend_jobs)


def test_existing_api_routes_return_profile_and_hybrid_fields(monkeypatch):
    monkeypatch.setattr(main, "extract_pdf_text", lambda _: FRESHER_RESUME)
    client = TestClient(main.app)
    upload = ("candidate.pdf", b"not parsed by this test", "application/pdf")

    analysis = client.post(
        "/analyze",
        files={"resume": upload},
        data={
            "job_description": (
                "Required skills: SQL, Excel, Power BI. "
                "Nice to have: Tableau."
            )
        },
    )
    assert analysis.status_code == 200
    analysis_data = analysis.json()
    assert analysis_data["candidate_profile"]["candidate_level"] == "fresher"
    assert "SQL" in analysis_data["required_skills"]
    assert "Tableau" in analysis_data["preferred_skills"]
    assert "partially_matched_skills" in analysis_data
    assert "data_quality_warnings" in analysis_data

    recommendations = client.post("/recommend-jobs", files={"resume": upload})
    assert recommendations.status_code == 200
    recommendation_data = recommendations.json()
    assert recommendation_data["candidate_profile"]["candidate_level"] == "fresher"
    assert recommendation_data["recommender"]["algorithm"] == "hybrid-v1"
    assert recommendation_data["recommended_jobs"][0]["explanations"]


def test_learning_resource_endpoint_still_uses_youtube_integration(monkeypatch):
    monkeypatch.setattr(
        main,
        "search_youtube",
        lambda skill, max_results: [{"title": f"{skill} tutorial"}],
    )
    response = TestClient(main.app).post(
        "/learning-resources",
        json={"skills": ["Python", "Python"]},
    )

    assert response.status_code == 200
    assert response.json()["total_skills"] == 1
    assert "Python" in response.json()["resources"]
