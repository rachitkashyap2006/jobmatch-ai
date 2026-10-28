
import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "claude_dataset"
MODEL_PATH = BASE_DIR / "job_recommender_v2.pkl"
JOBS_PATH = DATA_DIR / "jobs.csv"

# Load V2 model
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"V2 model not found: {MODEL_PATH}\n"
        "Run python train_recommender_v2.py first."
    )

saved_model = joblib.load(MODEL_PATH)
model = saved_model["model"]
vectorizer = saved_model["vectorizer"]

# Load the 100-job dataset
jobs = pd.read_csv(JOBS_PATH)

REQUIRED_JOB_COLUMNS = [
    "job_title",
    "job_description",
    "required_skills",
    "experience_level",
]

missing_columns = [
    column for column in REQUIRED_JOB_COLUMNS
    if column not in jobs.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns in jobs.csv: {missing_columns}"
    )


def make_pair_text(resume_text, job):
    """Keep inference text format consistent with training."""
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


def recommend_jobs(resume_text, top_n=5):
    if not isinstance(resume_text, str) or not resume_text.strip():
        return []

    resume_text = resume_text.strip()
    results = []

    for _, job in jobs.iterrows():
        required_skills = [
            skill.strip()
            for skill in str(job["required_skills"]).split(";")
            if skill.strip()
        ]

        resume_lower = resume_text.lower()

        matched_skills = [
            skill for skill in required_skills
            if skill.lower() in resume_lower
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill.lower() not in resume_lower
        ]

        skill_overlap = (
            len(matched_skills) / len(required_skills)
            if required_skills else 0.0
        )

        pair_text = make_pair_text(resume_text, job)
        vector = vectorizer.transform([pair_text])

        probabilities = model.predict_proba(vector)[0]
        classes = list(model.classes_)

        # Expected relevance: P(0)*0 + P(1)*1 + P(2)*2
        predicted_relevance = sum(
            float(probability) * int(label)
            for probability, label in zip(probabilities, classes)
        )

        # Probability of high relevance (class 2)
        high_relevance_probability = (
            float(probabilities[classes.index(2)])
            if 2 in classes else 0.0
        )

        results.append({
            "job_title": str(job["job_title"]),
            "experience_level": str(job["experience_level"]),
            "skill_match": round(skill_overlap * 100, 1),
            "predicted_relevance": round(
                predicted_relevance / 2 * 100, 1
            ),
            "high_relevance_probability": round(
                high_relevance_probability * 100, 1
            ),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        })

    results.sort(
        key=lambda item: item["predicted_relevance"],
        reverse=True,
    )

    return results[:max(1, int(top_n))]


if __name__ == "__main__":
    sample_resume = """
    Python SQL pandas numpy matplotlib machine learning
    data analysis data visualization scikit-learn statistics
    """

    recommendations = recommend_jobs(sample_resume)

    print("\nTop Job Recommendations (V2)")
    print("=" * 50)

    for rank, job in enumerate(recommendations, start=1):
        print(f"\n{rank}. {job['job_title']}")
        print(f"   Experience: {job['experience_level']}")
        print(f"   Predicted relevance: {job['predicted_relevance']}%")
        print(
            "   High relevance probability: "
            f"{job['high_relevance_probability']}%"
        )
        print(f"   Skill overlap: {job['skill_match']}%")
        print(
            "   Matched skills: "
            f"{', '.join(job['matched_skills']) or 'None'}"
        )
        print(
            "   Missing skills: "
            f"{', '.join(job['missing_skills']) or 'None'}"
        )
