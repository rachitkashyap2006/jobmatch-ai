from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from io import BytesIO
from pypdf import PdfReader

# IMPORTING ALL FUNCTION FROM OTHER FILES

from skill_extractor import extract_skills
from matcher import compare_skills, calculate_final_score
from semantic_matcher import calculate_similarity
from recommendation_engine import recommend_skills
from recommend_jobs import recommend_jobs
from learning_resources import search_youtube




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

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        raise ValueError("No readable text found in PDF.")

    return text


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
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {error}"
        )

    candidate_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    matched, missing, skill_score = compare_skills(
        candidate_skills,
        required_skills
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
        candidate_skills
    )

    return {
        "candidate_skills": sorted(candidate_skills),
        "required_skills": sorted(required_skills),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "skill_match_score": float(round(float(skill_score), 2)),
        "semantic_similarity_score": float(round(float(semantic_score), 2)),
        "final_match_score": float(round(float(final_score), 2)),
        "recommendations": recommendations
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
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {error}"
        )

    try:
        jobs = recommend_jobs(resume_text, top_n=5)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Job recommendation failed: {error}"
        )

    return {
        "message": "Job recommendations generated successfully",
        "total_recommendations": len(jobs),
        "recommended_jobs": jobs
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
