import csv
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit

from recommend_jobs import (
    JOBS,
    get_recommender_metadata,
    make_pair_text,
    recommend_jobs,
)
from skill_extractor import extract_skills, normalize_skill
from resume_parser import build_candidate_profile


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "claude_dataset"


def _read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _skill_metrics(resumes):
    true_positive = false_positive = false_negative = 0
    exact_matches = 0
    catalog = {
        normalize_skill(skill)
        for job in JOBS
        for skill in (
            job.get("required_skills", "") + ";"
            + job.get("preferred_skills", "")
        ).split(";")
        if skill.strip()
    }

    for resume in resumes:
        expected = {
            normalize_skill(skill)
            for skill in resume["skills"].split(";")
            if skill.strip()
        }
        predicted = set(extract_skills(resume["resume_text"]))
        true_positive += len(expected & predicted)
        false_positive += len(predicted - expected)
        false_negative += len(expected - predicted)
        exact_matches += expected == predicted

    precision = true_positive / (true_positive + false_positive) if (
        true_positive + false_positive
    ) else 0.0
    recall = true_positive / (true_positive + false_negative) if (
        true_positive + false_negative
    ) else 0.0
    union = true_positive + false_positive + false_negative
    # Exact set agreement is more informative than catalog-wide true negatives.
    return {
        "profiles_evaluated": len(resumes),
        "micro_precision": round(precision, 4),
        "micro_recall": round(recall, 4),
        "f1": round(
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0,
            4,
        ),
        "exact_set_accuracy": round(exact_matches / max(len(resumes), 1), 4),
        "catalog_skill_count": len(catalog),
        "micro_true_positive": true_positive,
        "micro_false_positive": false_positive,
        "micro_false_negative": false_negative,
        "micro_jaccard_accuracy": round(
            true_positive / union if union else 1.0, 4
        ),
    }


def _dcg(relevances, cutoff):
    values = np.asarray(relevances, dtype=float)[:cutoff]
    if not len(values):
        return 0.0
    gains = (2 ** values) - 1
    discounts = np.log2(np.arange(2, len(values) + 2))
    return float(np.sum(gains / discounts))


def _ranking_metrics(groups, score_key, cutoff=5):
    precisions = []
    recalls = []
    ndcgs = []
    top_relevance = []
    for rows in groups.values():
        ordered = sorted(rows, key=lambda row: row[score_key], reverse=True)
        top = ordered[:cutoff]
        labels = [int(row["relevance_label"]) for row in rows]
        top_labels = [int(row["relevance_label"]) for row in top]
        relevant_total = sum(label >= 1 for label in labels)
        precisions.append(
            sum(label == 2 for label in top_labels) / max(len(top), 1)
        )
        recalls.append(
            sum(label >= 1 for label in top_labels) / relevant_total
            if relevant_total else 0.0
        )
        ideal = sorted(labels, reverse=True)
        ideal_dcg = _dcg(ideal, cutoff)
        ndcgs.append(
            _dcg(top_labels, cutoff) / ideal_dcg if ideal_dcg else 0.0
        )
        top_relevance.append(
            sum(top_labels) / max(len(top_labels), 1)
        )

    return {
        "precision_at_5_high_relevance": round(float(np.mean(precisions)), 4),
        "recall_at_5_relevance_ge_1": round(float(np.mean(recalls)), 4),
        "ndcg_at_5": round(float(np.mean(ndcgs)), 4),
        "mean_top_5_relevance_label": round(float(np.mean(top_relevance)), 4),
        "profiles_evaluated": len(groups),
    }


def evaluate_dataset(random_state=42):
    """Compare the deployed TF-IDF classifier baseline and hybrid ranking."""
    resumes = _read_csv(DATA_DIR / "resumes.csv")
    pairs = _read_csv(DATA_DIR / "training_pairs.csv")
    resume_by_id = {row["resume_id"]: row for row in resumes}

    pair_text = [
        make_pair_text(row["resume_text"], {
            "job_title": row["job_title"],
            "job_description": row["job_description"],
            "required_skills": row["required_skills"],
        })
        for row in pairs
    ]
    labels = np.asarray([int(row["relevance_label"]) for row in pairs])
    groups = np.asarray([row["resume_id"] for row in pairs])
    splitter = GroupShuffleSplit(
        n_splits=1, test_size=0.2, random_state=random_state
    )
    train_indices, test_indices = next(
        splitter.split(pair_text, labels, groups=groups)
    )

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=20000,
        sublinear_tf=True,
    )
    train_vectors = vectorizer.fit_transform(
        [pair_text[index] for index in train_indices]
    )
    test_vectors = vectorizer.transform(
        [pair_text[index] for index in test_indices]
    )
    baseline = LogisticRegression(
        max_iter=2000, class_weight="balanced", random_state=random_state
    )
    baseline.fit(train_vectors, labels[train_indices])

    baseline_probabilities = baseline.predict_proba(test_vectors)
    baseline_labels = baseline.classes_[
        np.argmax(baseline_probabilities, axis=1)
    ]
    baseline_scores = baseline_probabilities @ baseline.classes_
    test_rows = []
    hybrid_scores_by_resume = {}
    for position, index in enumerate(test_indices):
        row = dict(pairs[index])
        row["relevance_label"] = int(row["relevance_label"])
        row["baseline_score"] = float(baseline_scores[position])
        test_rows.append(row)

        resume_id = row["resume_id"]
        if resume_id not in hybrid_scores_by_resume:
            resume_text = resume_by_id[resume_id]["resume_text"]
            profile = build_candidate_profile(resume_text)
            recommendations = recommend_jobs(
                resume_text,
                top_n=len(JOBS),
                candidate_profile=profile,
            )
            hybrid_scores_by_resume[resume_id] = {
                item["job_id"]: item["predicted_relevance"]
                for item in recommendations
            }
        row["hybrid_score"] = float(
            hybrid_scores_by_resume[resume_id].get(row["job_id"], 0.0)
        )

    baseline_groups = {}
    hybrid_groups = {}
    for row in test_rows:
        baseline_groups.setdefault(row["resume_id"], []).append(row)
        hybrid_groups.setdefault(row["resume_id"], []).append(row)

    true_relevant = np.asarray([
        int(row["relevance_label"] >= 1) for row in test_rows
    ])
    baseline_relevant = np.asarray([
        int(label >= 1) for label in baseline_labels
    ])
    hybrid_relevant = np.asarray([
        int(row["hybrid_score"] >= 50.0) for row in test_rows
    ])

    return {
        "evaluation": {
            "dataset": "synthetic_claude_dataset",
            "split": "80/20 GroupShuffleSplit by resume_id",
            "random_state": random_state,
            "training_pairs": len(train_indices),
            "held_out_pairs": len(test_indices),
            "held_out_resumes": len(set(groups[test_indices])),
            "label_definition": "0=low, 1=partial, 2=high relevance",
            "recommender": get_recommender_metadata(),
            "warning": (
                "Synthetic generator labels are not human judgments and do "
                "not establish real-world hiring or recommendation accuracy."
            ),
        },
        "resume_extraction": _skill_metrics(resumes),
        "relevance_classification": {
            "positive_label": "relevance_label >= 1",
            "hybrid_threshold": 50.0,
            "baseline_accuracy": round(
                float(accuracy_score(true_relevant, baseline_relevant)), 4
            ),
            "baseline_precision": round(
                float(precision_score(
                    true_relevant, baseline_relevant, zero_division=0
                )),
                4,
            ),
            "baseline_recall": round(
                float(recall_score(
                    true_relevant, baseline_relevant, zero_division=0
                )),
                4,
            ),
            "hybrid_accuracy": round(
                float(accuracy_score(true_relevant, hybrid_relevant)), 4
            ),
            "hybrid_precision": round(
                float(precision_score(
                    true_relevant, hybrid_relevant, zero_division=0
                )),
                4,
            ),
            "hybrid_recall": round(
                float(recall_score(
                    true_relevant, hybrid_relevant, zero_division=0
                )),
                4,
            ),
        },
        "ranking": {
            "baseline": _ranking_metrics(baseline_groups, "baseline_score"),
            "hybrid": _ranking_metrics(hybrid_groups, "hybrid_score"),
        },
    }


if __name__ == "__main__":
    print(json.dumps(evaluate_dataset(), indent=2))
