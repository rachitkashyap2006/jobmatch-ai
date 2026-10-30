import csv
import re
from pathlib import Path

from resume_parser import build_candidate_profile
from semantic_matcher import calculate_similarities, get_semantic_backend
from skill_extractor import normalize_skill
from skill_gap import match_required_skills


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "claude_dataset"
JOBS_PATH = DATA_DIR / "jobs.csv"
_STOP_WORDS = {
    "and", "for", "the", "with", "from", "using", "role", "job", "work",
    "experience", "skills", "skill", "engineer", "analyst", "developer",
    "senior", "junior", "associate", "lead", "intern", "internship",
}


def _load_jobs():
    if not JOBS_PATH.exists():
        raise FileNotFoundError(f"Job catalog not found: {JOBS_PATH}")
    with JOBS_PATH.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    required_columns = {
        "job_id", "job_title", "job_description", "required_skills",
        "preferred_skills", "experience_level", "min_years_experience",
    }
    if not rows:
        raise ValueError(f"No jobs were found in {JOBS_PATH}")
    missing_columns = required_columns.difference(rows[0])
    if missing_columns:
        raise ValueError(
            f"Missing columns in jobs.csv: {sorted(missing_columns)}"
        )
    return rows


JOBS = _load_jobs()


def make_pair_text(resume_text, job):
    """Keep the saved baseline model's training text format available."""
    return (
        "RESUME "
        + str(resume_text)
        + " JOB TITLE "
        + str(job["job_title"])
        + " JOB DESCRIPTION "
        + str(job["job_description"])
        + " REQUIRED SKILLS "
        + str(job["required_skills"])
    )


def _split_skills(value):
    return [
        normalize_skill(skill.strip())
        for skill in str(value or "").split(";")
        if skill.strip()
    ]


def _profile_skills(profile):
    return [
        item["skill"]
        for section in ("technical_skills", "soft_skills")
        for item in profile.get(section, [])
    ]


def _coverage_score(candidate_skills, required_skills):
    matched, partial, missing = match_required_skills(
        candidate_skills, required_skills
    )
    weights = [
        1.5 if index < 3 else 1.0
        for index in range(len(required_skills))
    ]
    denominator = sum(weights)
    partial_credit = sum(
        item["transferability"] * (
            1.5 if required_skills.index(item["required_skill"]) < 3 else 1.0
        )
        for item in partial
    )
    exact_credit = sum(
        1.5 if skill in required_skills[:3] else 1.0
        for skill in matched
    )
    score = (exact_credit + partial_credit) / denominator if denominator else 0.0
    return score, matched, partial, missing


def _experience_fit(profile, job):
    years = profile.get("experience_years")
    try:
        minimum = max(0.0, float(job.get("min_years_experience") or 0))
    except (TypeError, ValueError):
        minimum = 0.0

    level = profile.get("candidate_level", "unknown")
    if level in {"fresher", "intern"} and (
        years is None or float(years) < 1
    ):
        if minimum == 0:
            return 1.0
        if minimum <= 1:
            return 0.55
        if minimum <= 2:
            return 0.2
        return 0.05
    if years is None:
        return 0.45

    years = max(0.0, float(years))
    if minimum == 0:
        if years >= 5:
            return max(0.35, 1.0 - (years - 4) * 0.08)
        return 1.0
    if years < minimum:
        return max(0.1, 1.0 - (minimum - years) / max(minimum + 1.0, 1.0))
    return max(0.65, 1.0 - max(0.0, years - minimum - 2) * 0.04)


def _tokens(text):
    return {
        token
        for token in re.findall(r"[a-z0-9+#.]+", (text or "").casefold())
        if len(token) > 1 and token not in _STOP_WORDS
    }


def _keyword_score(resume_text, job):
    target_terms = _tokens(
        " ".join(
            str(job.get(field, ""))
            for field in ("job_title", "job_family", "domain_focus")
        )
    )
    if not target_terms:
        return 0.0
    return len(_tokens(resume_text) & target_terms) / len(target_terms)


def _confidence(profile):
    evidence_groups = (
        bool(profile.get("technical_skills") or profile.get("soft_skills")),
        bool(profile.get("education")),
        bool(profile.get("work_experience") or profile.get("internships")),
        bool(profile.get("projects")),
        bool(profile.get("certifications")),
    )
    evidence_count = sum(evidence_groups)
    if evidence_count >= 4:
        return "high"
    if evidence_count >= 2:
        return "moderate"
    return "low"


def _explanations(
    profile, job, matched, partial, missing, experience_score, semantic_score
):
    required = _split_skills(job.get("required_skills"))
    preferred = _split_skills(job.get("preferred_skills"))
    reasons = [
        f"Matched {len(matched)} of {len(required)} required skills exactly."
    ]
    if partial:
        reasons.append(
            "Related experience provides partial coverage for "
            + ", ".join(item["required_skill"] for item in partial)
            + "."
        )
    if preferred:
        reasons.append(
            f"Matched {len(set(_profile_skills(profile)) & set(preferred))} of "
            f"{len(preferred)} preferred skills."
        )
    if profile.get("projects"):
        reasons.append(
            f"Your resume includes {len(profile['projects'])} project "
            f"{'example' if len(profile['projects']) == 1 else 'examples'}."
        )
    if profile.get("work_experience"):
        reasons.append(
            f"Your resume includes {len(profile['work_experience'])} work "
            f"experience record(s)."
        )
    if profile.get("internships"):
        reasons.append(
            f"Your resume includes {len(profile['internships'])} internship "
            f"record(s)."
        )
    if profile.get("candidate_level") in {"fresher", "intern"} and (
        float(job.get("min_years_experience") or 0) == 0
    ):
        reasons.append("This role is open to entry-level or internship experience.")
    elif experience_score >= 0.75:
        reasons.append("Your stated experience is close to this role's level.")
    else:
        reasons.append(
            "The role asks for more experience than the resume explicitly shows."
        )
    reasons.append(
        f"Resume-to-role semantic cosine similarity is {semantic_score:.1f}%."
    )
    if not matched and not partial:
        reasons.append("No required skill match was found in the resume evidence.")
    if not required and not missing:
        reasons.append("This catalog entry has no structured required-skill list.")
    return reasons


def recommend_jobs(resume_text, top_n=5, candidate_profile=None):
    if not isinstance(resume_text, str) or not resume_text.strip():
        return []

    resume_text = resume_text.strip()
    profile = candidate_profile or build_candidate_profile(resume_text)
    candidate_skills = _profile_skills(profile)
    job_descriptions = [
        " ".join(
            (
                str(job.get("job_title", "")),
                str(job.get("job_description", "")),
                str(job.get("required_skills", "")),
                str(job.get("preferred_skills", "")),
            )
        )
        for job in JOBS
    ]
    semantic_scores = calculate_similarities(resume_text, job_descriptions)
    confidence = _confidence(profile)
    warnings = list(profile.get("data_quality_warnings", []))
    results = []

    for job, semantic_score in zip(JOBS, semantic_scores):
        required = _split_skills(job.get("required_skills"))
        preferred = _split_skills(job.get("preferred_skills"))
        required_score, matched, partial, missing = _coverage_score(
            candidate_skills, required
        )
        preferred_score, preferred_matched, preferred_partial, preferred_missing = (
            _coverage_score(candidate_skills, preferred)
        )
        experience_score = _experience_fit(profile, job)
        keyword_score = _keyword_score(resume_text, job)
        component_scores = {
            "required_skill_match": round(required_score * 100, 1),
            "preferred_skill_match": round(preferred_score * 100, 1),
            "semantic_similarity": round(semantic_score * 100, 1),
            "role_keyword_match": round(keyword_score * 100, 1),
            "experience_relevance": round(experience_score * 100, 1),
        }
        final_score = (
            required_score * 0.40
            + preferred_score * 0.05
            + semantic_score * 0.20
            + keyword_score * 0.10
            + experience_score * 0.25
        ) * 100

        reasons = _explanations(
            profile,
            job,
            matched,
            partial,
            missing,
            experience_score,
            semantic_score * 100,
        )
        results.append({
            "job_id": str(job["job_id"]),
            "job_title": str(job["job_title"]),
            "job_family": str(job.get("job_family", "")),
            "experience_level": str(job["experience_level"]),
            "min_years_experience": int(
                float(job.get("min_years_experience") or 0)
            ),
            "predicted_relevance": round(final_score, 1),
            "final_match_score": round(final_score, 1),
            "skill_match": round(required_score * 100, 1),
            "matched_skills": matched,
            "partially_matched_skills": partial,
            "missing_skills": missing,
            "matched_preferred_skills": preferred_matched,
            "partially_matched_preferred_skills": preferred_partial,
            "missing_preferred_skills": preferred_missing,
            "score_breakdown": component_scores,
            "score_weights": {
                "required_skill_match": 0.40,
                "preferred_skill_match": 0.05,
                "semantic_similarity": 0.20,
                "role_keyword_match": 0.10,
                "experience_relevance": 0.25,
            },
            "explanations": reasons,
            "confidence": confidence,
            "data_quality_warnings": warnings,
        })

    results.sort(
        key=lambda item: (-item["predicted_relevance"], item["job_title"].casefold())
    )
    return results[:max(1, int(top_n))]


def get_recommender_metadata():
    return {
        "algorithm": "hybrid-v1",
        "semantic_backend": get_semantic_backend(),
        "score_weights": {
            "required_skill_match": 0.40,
            "preferred_skill_match": 0.05,
            "semantic_similarity": 0.20,
            "role_keyword_match": 0.10,
            "experience_relevance": 0.25,
        },
    }
