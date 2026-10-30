import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from io import BytesIO
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# IMPORTING ALL FUNCTION FROM OTHER FILES

from resume_parser import build_candidate_profile
from skill_extractor import extract_job_requirements, extract_skills
from skill_gap import match_required_skills
from matcher import calculate_final_score
from semantic_matcher import calculate_similarity, get_semantic_backend
from recommendation_engine import recommend_skills
from recommend_jobs import recommend_jobs, get_recommender_metadata
from learning_resources import search_youtube


LOGGER = logging.getLogger(__name__)

app = FastAPI(title="AI Job Match & Skill Gap Analyzer")


from pydantic import BaseModel, Field


class LearningResourcesRequest(BaseModel):
    skills: list[str] = Field(min_length=1, max_length=5)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



def extract_pdf_text(pdf_bytes):
    reader = PdfReader(BytesIO(pdf_bytes))

    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    if not text.strip():
        raise ValueError("No readable text found in PDF.")

    return text.strip()


@app.get("/")
def home():
    return {"message": "AI Job Match API is running!"}


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if resume.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume."
        )

    pdf_bytes = await resume.read()

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The file is empty.")

    try:
        resume_text = extract_pdf_text(pdf_bytes)
    except (PdfReadError, ValueError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {error}"
        )

    candidate_profile = build_candidate_profile(resume_text)
    candidate_skills = extract_skills(resume_text)
    requirements = extract_job_requirements(job_description)
    required_skills = requirements["required_skills"]
    preferred_skills = requirements["preferred_skills"]
    matched, partially_matched, missing = match_required_skills(
        candidate_skills, required_skills
    )
    skill_score = (
        (len(matched) + sum(
            item["transferability"] for item in partially_matched
        )) / len(required_skills) * 100
        if required_skills else 0.0
    )
    preferred_matched, preferred_partial, preferred_missing = (
        match_required_skills(candidate_skills, preferred_skills)
    )

    semantic_score = calculate_similarity(
        resume_text,
        job_description
    )

    final_score = calculate_final_score(
        skill_score,
        semantic_score
    )

    recommendations = recommend_skills(
        missing,
        candidate_skills,
        partially_matched,
        required_skills,
    )

    return {
        "candidate_profile": candidate_profile,
        "candidate_skills": sorted(candidate_skills),
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
        "matched_skills": sorted(matched),
        "partially_matched_skills": partially_matched,
        "missing_skills": sorted(missing),
        "matched_preferred_skills": sorted(preferred_matched),
        "partially_matched_preferred_skills": preferred_partial,
        "missing_preferred_skills": sorted(preferred_missing),
        "skill_match_score": float(round(float(skill_score), 2)),
        "semantic_similarity_score": float(round(float(semantic_score), 2)),
        "final_match_score": float(round(float(final_score), 2)),
        "score_weights": {
            "required_and_transferable_skills": 0.60,
            "semantic_similarity": 0.40,
        },
        "recommendations": recommendations,
        "confidence": (
            "high" if len(candidate_skills) >= 5 and not candidate_profile[
                "data_quality_warnings"
            ] else "moderate" if len(candidate_skills) >= 2 else "low"
        ),
        "data_quality_warnings": candidate_profile["data_quality_warnings"],
        "semantic_backend": get_semantic_backend(),
    }

@app.post("/recommend-jobs")
async def get_job_recommendations(
    resume: UploadFile = File(...)
):
    if resume.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF resume."
        )

    pdf_bytes = await resume.read()

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The file is empty."
        )

    try:
        resume_text = extract_pdf_text(pdf_bytes)
    except (PdfReadError, ValueError, OSError) as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {error}"
        )

    try:
        candidate_profile = build_candidate_profile(resume_text)
        jobs = recommend_jobs(
            resume_text, top_n=5, candidate_profile=candidate_profile
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        LOGGER.exception("Job recommendation could not use the job catalog.")
        raise HTTPException(
            status_code=500,
            detail=f"Job recommendation failed: {error}"
        )

    return {
        "message": "Job recommendations generated successfully",
        "candidate_profile": candidate_profile,
        "total_recommendations": len(jobs),
        "recommended_jobs": jobs,
        "recommender": get_recommender_metadata(),
        "confidence": jobs[0]["confidence"] if jobs else "low",
        "data_quality_warnings": (
            candidate_profile.get("data_quality_warnings", [])
        ),
    }

@app.post("/learning-resources")
def get_learning_resources(request: LearningResourcesRequest):
    resources = {}

    # Remove empty and duplicate skills.
    skills = list(dict.fromkeys(
        skill.strip()
        for skill in request.skills
        if skill.strip()
    ))

    if not skills:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one valid skill."
        )

    for skill in skills:
        try:
            videos = search_youtube(skill, max_results=5)
            resources[skill] = videos

        except (RuntimeError, ValueError) as error:
            raise HTTPException(
                status_code=502,
                detail=f"Could not fetch YouTube resources for '{skill}'."
            ) from error

    return {
        "message": "Learning resources fetched successfully",
        "total_skills": len(resources),
        "resources": resources
    }
