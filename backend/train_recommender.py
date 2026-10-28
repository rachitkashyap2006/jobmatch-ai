
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# Load datasets
data_folder = r"D:\projectCV\backend\data"

jobs = pd.read_csv(f"{data_folder}\\jobs.csv")
pairs = pd.read_csv(f"{data_folder}\\training_pairs.csv")

# Prepare simple baseline features
def calculate_features(row):
    job = jobs[jobs["job_id"] == row["job_id"]]

    if job.empty:
        raise ValueError(f"Unknown job_id: {row['job_id']}")

    required_skills = {
        skill.strip().lower()
        for skill in job.iloc[0]["required_skills"].split(";")
    }

    resume_words = set(row["resume_text"].lower().split())

    matched = sum(
        1 for skill in required_skills
        if skill in row["resume_text"].lower()
    )

    skill_overlap = matched / max(len(required_skills), 1)

    return [skill_overlap, len(resume_words)]

X = pd.DataFrame(
    pairs.apply(calculate_features, axis=1).tolist(),
    columns=["skill_overlap", "resume_word_count"]
)

y = pairs["relevant"].astype(int)

# Split before training
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# Train the classifier
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)

print("Accuracy:", round(accuracy_score(y_test, predictions), 3))
print("Precision:", round(precision_score(y_test, predictions, zero_division=0), 3))
print("Recall:", round(recall_score(y_test, predictions, zero_division=0), 3))
print("F1-score:", round(f1_score(y_test, predictions, zero_division=0), 3))

print("\nClassification report:")
print(classification_report(y_test, predictions, zero_division=0))

# Save model and feature names
joblib.dump(
    {
        "model": model,
        "feature_names": list(X.columns)
    },
    "job_recommender.pkl"
)

print("\nModel saved as job_recommender.pkl")
