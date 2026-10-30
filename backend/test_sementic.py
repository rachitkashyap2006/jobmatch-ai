import semantic_matcher


def test_semantic_similarity_uses_cosine_tfidf_fallback(monkeypatch):
    def unavailable_model():
        raise OSError("no local model")

    monkeypatch.setattr(
        semantic_matcher, "_load_local_sentence_transformer", unavailable_model
    )
    scores = semantic_matcher.calculate_similarities(
        "Python backend APIs", ["Python backend APIs", "Tableau dashboards"]
    )

    assert scores[0] > scores[1]
    assert semantic_matcher.get_semantic_backend() == "tfidf"
