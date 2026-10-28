
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# 1. File paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "claude_dataset"

PAIRS_FILE = DATA_DIR / "training_pairs.csv"
MODEL_FILE = BASE_DIR / "job_recommender_v2.pkl"


# -----------------------------
# 2. Load dataset
# -----------------------------
df = pd.read_csv(PAIRS_FILE)

required_columns = [
    "resume_id",
    "resume_text",
    "job_title",
    "job_description",
    "required_skills",
    "relevance_label",
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise ValueError(f"Missing columns in dataset: {missing_columns}")

df = df.dropna(subset=required_columns).copy()

df["relevance_label"] = df["relevance_label"].astype(int)

# Labels: 0 = low, 1 = medium, 2 = high relevance
if not set(df["relevance_label"].unique()).issubset({0, 1, 2}):
    raise ValueError("relevance_label must contain only 0, 1, and 2.")


# -----------------------------
# 3. Prepare resume-job text
# -----------------------------
def make_pair_text(row):
    return (
        "RESUME "
        + str(row["resume_text"])
        + " JOB TITLE "
        + str(row["job_title"])
        + " JOB DESCRIPTION "
        + str(row["job_description"])
        + " REQUIRED SKILLS "
        + str(row["required_skills"])
    )


X_text = df.apply(make_pair_text, axis=1)
y = df["relevance_label"].to_numpy()
groups = df["resume_id"].to_numpy()


# -----------------------------
# 4. Split by resume ID
# -----------------------------
# All pairs belonging to a resume stay in one split.
# This reduces data leakage during evaluation.
splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42,
)

train_idx, test_idx = next(
    splitter.split(X_text, y, groups=groups)
)

X_train_text = X_text.iloc[train_idx]
X_test_text = X_text.iloc[test_idx]
y_train = y[train_idx]
y_test = y[test_idx]

print("Total pairs:", len(df))
print("Training pairs:", len(train_idx))
print("Testing pairs:", len(test_idx))
print("Training resumes:", len(set(groups[train_idx])))
print("Testing resumes:", len(set(groups[test_idx])))


# -----------------------------
# 5. Train multiclass model
# -----------------------------
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    max_features=20000,
    sublinear_tf=True,
)

X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42,
)

model.fit(X_train, y_train)

# -----------------------------
# 6. Evaluate held-out resumes
# -----------------------------
predictions = model.predict(X_test)

print("\n--- Classification Results ---")
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))

print(
    classification_report(
        y_test,
        predictions,
        labels=[0, 1, 2],
        target_names=[
            "Low relevance (0)",
            "Medium relevance (1)",
            "High relevance (2)",
        ],
        zero_division=0,
    )
)


# -----------------------------
# 7. Ranking evaluation
# -----------------------------
def dcg_at_k(relevances, k=5):
    relevances = np.asarray(relevances, dtype=float)[:k]
    if len(relevances) == 0:
        return 0.0

    gains = (2 ** relevances) - 1
    discounts = np.log2(np.arange(2, len(relevances) + 2))

    return float(np.sum(gains / discounts))


def ndcg_at_k(actual, predicted, k=5):
    order = np.argsort(-np.asarray(predicted))
    ranked_actual = np.asarray(actual)[order][:k]

    actual_dcg = dcg_at_k(ranked_actual, k)
    ideal_dcg = dcg_at_k(
        sorted(actual, reverse=True),
        k,
    )

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


probabilities = model.predict_proba(X_test)

# Convert predicted class probabilities into an expected relevance score.
# Example: P(0)*0 + P(1)*1 + P(2)*2
expected_scores = probabilities @ model.classes_

test_df = df.iloc[test_idx].copy()
test_df["predicted_score"] = expected_scores

ndcg_scores = []
precision_scores = []

for resume_id, group in test_df.groupby("resume_id"):
    actual = group["relevance_label"].to_numpy()
    predicted = group["predicted_score"].to_numpy()

    ndcg_scores.append(ndcg_at_k(actual, predicted, k=5))

    top_indices = np.argsort(-predicted)[:5]
    top_actual = actual[top_indices]

    # High relevance means label 2.
    precision_scores.append(
        float(np.mean(top_actual == 2))
    )

print("\n--- Ranking Results (held-out resumes) ---")
print("Evaluated resumes:", len(ndcg_scores))
print("Mean NDCG@5:", round(float(np.mean(ndcg_scores)), 4))
print("Mean Precision@5 (label 2):", round(float(np.mean(precision_scores)), 4))


# -----------------------------
# 8. Train final model on all pairs
# -----------------------------
# Evaluation is complete. Refit on the full synthetic dataset
# before saving the model for inference.
final_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    max_features=20000,
    sublinear_tf=True,
)

X_all = final_vectorizer.fit_transform(X_text)

final_model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42,
)

final_model.fit(X_all, y)

artifact = {
    "model": final_model,
    "vectorizer": final_vectorizer,
    "model_version": 2,
    "classes": final_model.classes_.tolist(),
    "training_pairs": int(len(df)),
    "training_resumes": int(df["resume_id"].nunique()),
    "training_data": "synthetic_claude_dataset",
}

joblib.dump(artifact, MODEL_FILE)

print("\nModel saved successfully:")
print(MODEL_FILE)
print("Existing job_recommender.pkl was not changed.")
