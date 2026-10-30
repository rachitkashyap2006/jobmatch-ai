import logging
import re
from functools import lru_cache

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


LOGGER = logging.getLogger(__name__)
MODEL_NAME = "all-MiniLM-L6-v2"
_SEMANTIC_BACKEND = None


@lru_cache(maxsize=1)
def _load_local_sentence_transformer():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, local_files_only=True)


@lru_cache(maxsize=4)
def _encode_job_documents(documents):
    model = _load_local_sentence_transformer()
    return model.encode(
        list(documents),
        normalize_embeddings=True,
        convert_to_numpy=True,
    )


def _tfidf_similarities(query, documents):
    corpus = [query, *documents]
    if not any(re.search(r"[A-Za-z0-9]", text or "") for text in corpus):
        return [0.0] * len(documents)

    try:
        vectors = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            sublinear_tf=True,
        ).fit_transform(corpus)
    except ValueError as error:
        if "empty vocabulary" not in str(error).casefold():
            raise
        return [0.0] * len(documents)

    scores = cosine_similarity(vectors[0:1], vectors[1:]).ravel()
    return [float(score) for score in scores]


def calculate_similarities(query, documents):
    """Return cosine similarities in [0, 1], using local embeddings when present."""
    global _SEMANTIC_BACKEND

    query = query if isinstance(query, str) else ""
    documents = [document if isinstance(document, str) else "" for document in documents]
    if not documents:
        return []
    if _SEMANTIC_BACKEND == "tfidf":
        return _tfidf_similarities(query, documents)

    try:
        model = _load_local_sentence_transformer()
    except (ImportError, OSError, ValueError) as error:
        _SEMANTIC_BACKEND = "tfidf"
        LOGGER.warning(
            "Local Sentence Transformers model unavailable; using TF-IDF cosine similarity: %s",
            error,
        )
        return _tfidf_similarities(query, documents)

    document_embeddings = _encode_job_documents(tuple(documents))
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    similarities = cosine_similarity(
        query_embedding, np.asarray(document_embeddings)
    ).ravel()
    _SEMANTIC_BACKEND = "sentence-transformers"
    return [float(max(0.0, min(1.0, score))) for score in similarities]


def get_semantic_backend():
    return _SEMANTIC_BACKEND or "not_initialized"


def calculate_similarity(resume_text, job_description):
    """Legacy single-job API; scores are returned as percentages."""
    similarities = calculate_similarities(resume_text, [job_description])
    return similarities[0] * 100
