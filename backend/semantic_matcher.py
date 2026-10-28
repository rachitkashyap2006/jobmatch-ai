from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the pre-trained NLP model
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(resume_text, job_description):

    # Convert resume and job description into numerical vectors
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_description])

    # Calculate similarity between the two vectors
    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]

    # Convert 0-1 into percentage
    similarity_percentage = similarity * 100

    return float(similarity_percentage)