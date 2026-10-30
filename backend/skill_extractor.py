import csv
import re
from pathlib import Path


_BASE_SKILLS = {
    "Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go",
    "Rust", "R", "SQL", "NoSQL", "HTML", "CSS", "React", "Node.js",
    "pandas", "NumPy", "SciPy", "scikit-learn", "TensorFlow", "PyTorch",
    "Keras", "XGBoost", "LightGBM", "Matplotlib", "Seaborn", "Plotly",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Statistics", "Data Analysis", "Data Science", "Data Visualization",
    "Data Engineering", "Data Cleaning", "Feature Engineering",
    "Model Evaluation", "Model Deployment", "MLOps", "Model Monitoring",
    "Natural Language Processing", "OpenCV", "spaCy", "NLTK",
    "Hugging Face Transformers", "Embeddings", "Sentence Transformers",
    "Information Retrieval", "Text Classification", "Named Entity Recognition",
    "Prompt Engineering", "LLM Fine-tuning", "RAG", "Vector Databases",
    "FastAPI", "Flask", "Django", "REST APIs", "API Design", "Microservices",
    "SQLAlchemy", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis",
    "Apache Spark", "Airflow", "Kafka", "ETL Pipelines", "dbt", "Snowflake",
    "BigQuery", "Redshift", "Databricks", "Data Warehousing", "Data Modeling",
    "Docker", "Kubernetes", "Git", "GitHub Actions", "CI/CD", "Linux",
    "AWS", "Azure", "GCP", "Terraform", "Jupyter", "pytest", "Unit Testing",
    "Power BI", "Tableau", "Looker Studio", "Excel", "Google Analytics",
    "A/B Testing", "Hypothesis Testing", "KPI Reporting", "Dashboard Design",
    "Data Storytelling", "Business Analysis", "Business Process Modeling",
    "Requirements Gathering", "Stakeholder Management", "Documentation",
    "User Stories", "JIRA", "Agile/Scrum", "Process Mapping", "UAT",
    "Gap Analysis", "Cost-Benefit Analysis", "Business Case Development",
    "Presentation Skills", "Communication", "Written Communication",
    "Verbal Communication", "Teamwork", "Leadership", "Mentoring",
    "Problem Solving", "Critical Thinking", "Time Management", "Adaptability",
    "Collaboration", "Attention to Detail", "Creativity", "Ownership",
    "Customer Service", "Project Management", "Figma", "DAX", "D3.js",
    "YOLO", "ONNX", "MLflow", "Feature Stores", "Convolutional Neural Networks",
    "Object Detection", "Image Classification", "Image Segmentation",
    "Data Augmentation", "Video Analytics", "TensorRT", "Albumentations",
    "Celery", "RabbitMQ", "JWT Authentication", "Apache Hadoop", "Parquet",
    "DAX", "Clustering", "Time Series Forecasting", "Experiment Design",
    "Causal Inference", "Bayesian Methods", "Sentiment Analysis", "Elasticsearch",
    "Google Sheets", "Looker", "SAS", "SPSS", "MATLAB", "PowerPoint",
    "Microsoft Office", "Salesforce", "SAP", "QuickBooks", "Canva",
}

_ALIASES = {
    "py": "Python",
    "js": "JavaScript",
    "nodejs": "Node.js",
    "node js": "Node.js",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "scikit_learn": "scikit-learn",
    "powerbi": "Power BI",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "amazon web services": "AWS",
    "google cloud platform": "GCP",
    "google cloud": "GCP",
    "ms excel": "Excel",
    "microsoft excel": "Excel",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "communication skills": "Communication",
    "problem-solving": "Problem Solving",
    "problem solving skills": "Problem Solving",
    "team work": "Teamwork",
    "scikit learn": "scikit-learn",
}

_SOFT_SKILLS = {
    "Adaptability", "Attention to Detail", "Collaboration", "Communication",
    "Critical Thinking", "Creativity", "Customer Service", "Leadership",
    "Mentoring", "Ownership", "Presentation Skills", "Problem Solving",
    "Project Management", "Stakeholder Management", "Teamwork",
    "Time Management", "Verbal Communication", "Written Communication",
}


def _skill_key(value):
    return re.sub(r"[^a-z0-9+#.]+", " ", value.casefold()).strip()


def _load_catalog():
    skills = set(_BASE_SKILLS)
    jobs_path = Path(__file__).resolve().parent / "data" / "claude_dataset" / "jobs.csv"
    if jobs_path.exists():
        with jobs_path.open(encoding="utf-8-sig", newline="") as file:
            for job in csv.DictReader(file):
                for column in ("required_skills", "preferred_skills"):
                    skills.update(
                        skill.strip()
                        for skill in job.get(column, "").split(";")
                        if skill.strip()
                    )

    canonical_by_key = {_skill_key(skill): skill for skill in skills}
    for alias, canonical in _ALIASES.items():
        canonical_by_key[_skill_key(alias)] = canonical
        canonical_by_key.setdefault(_skill_key(canonical), canonical)
    return canonical_by_key


_CANONICAL_BY_KEY = _load_catalog()
_SKILL_PATTERNS = sorted(
    (
        (re.compile(rf"(?<![A-Za-z0-9]){re.escape(key)}(?![A-Za-z0-9])", re.I), name)
        for key, name in _CANONICAL_BY_KEY.items()
        if key
    ),
    key=lambda item: len(item[0].pattern),
    reverse=True,
)


def normalize_skill(skill):
    """Return a canonical skill name without merging merely related skills."""
    normalized_key = _skill_key(skill)
    return _CANONICAL_BY_KEY.get(normalized_key, skill.strip())


def extract_skills_with_evidence(text):
    """Extract known skills and retain the original text that supports each one."""
    if not isinstance(text, str) or not text.strip():
        return []

    def evidence_for(match):
        boundaries = list(re.finditer(r"[\n|;.!?]+", text))
        start = max(
            (boundary.end() for boundary in boundaries if boundary.end() <= match.start()),
            default=0,
        )
        end = min(
            (boundary.start() for boundary in boundaries if boundary.start() >= match.end()),
            default=len(text),
        )
        evidence = text[start:end].strip()
        if len(evidence) > 240:
            left = max(start, match.start() - 100)
            right = min(end, match.end() + 140)
            evidence = text[left:right].strip()
        return evidence or match.group(0)

    found = {}
    for pattern, canonical_name in _SKILL_PATTERNS:
        for match in pattern.finditer(text):
            found.setdefault(
                canonical_name,
                {"skill": canonical_name, "evidence": evidence_for(match)},
            )
    return sorted(found.values(), key=lambda item: item["skill"].casefold())


def extract_skills(text):
    """Extract canonical skill names; kept as the simple legacy interface."""
    return [item["skill"] for item in extract_skills_with_evidence(text)]


def extract_job_requirements(text):
    """Split recognized job skills into required and preferred groups."""
    if not isinstance(text, str) or not text.strip():
        return {"required_skills": [], "preferred_skills": []}

    marker = re.search(
        r"\b(?:preferred(?:\s+skills)?|nice\s+to\s+have|bonus\s+skills)\s*[:\-]",
        text,
        re.I,
    )
    required_text = text[:marker.start()] if marker else text
    preferred_text = text[marker.start():] if marker else ""
    preferred = extract_skills(preferred_text)
    required = extract_skills(required_text)
    return {
        "required_skills": required,
        "preferred_skills": preferred,
    }


def skill_category(skill):
    return "soft" if normalize_skill(skill) in _SOFT_SKILLS else "technical"
