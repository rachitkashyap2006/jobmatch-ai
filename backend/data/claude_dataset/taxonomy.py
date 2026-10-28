"""Static knowledge used by the synthetic dataset generator (all fictional / synthetic)."""

FAMILIES = {
    "DA": "Data Analyst",
    "DS": "Data Scientist",
    "MLE": "Machine Learning Engineer",
    "NLP": "NLP Engineer",
    "CV": "Computer Vision Engineer",
    "BE": "Python Backend Developer",
    "DE": "Data Engineer",
    "BA": "Business Analyst",
    "DV": "Data Visualization Analyst",
    "INT": "AI/ML Intern",
}
KEYS = list(FAMILIES)

# must = always-central skills, core = common main skills, common = optional/specialised
POOLS = {
    "DA": dict(must=["SQL", "Excel", "Data Analysis"],
               core=["Data Cleaning", "Statistics", "Python", "pandas", "KPI Reporting", "Data Visualization"],
               common=["Tableau", "Power BI", "Looker Studio", "A/B Testing", "Google Analytics", "Hypothesis Testing",
                       "Dashboard Design", "Stakeholder Management", "PostgreSQL", "MySQL"]),
    "DS": dict(must=["Python", "Statistics", "Machine Learning"],
               core=["pandas", "NumPy", "scikit-learn", "SQL", "Feature Engineering", "Model Evaluation", "Jupyter",
                     "Hypothesis Testing"],
               common=["XGBoost", "LightGBM", "Time Series Forecasting", "Clustering", "A/B Testing", "Experiment Design",
                       "Causal Inference", "Bayesian Methods", "Deep Learning", "PyTorch", "TensorFlow", "Matplotlib",
                       "Seaborn", "Data Visualization", "Git"]),
    "MLE": dict(must=["Python", "Machine Learning", "Docker"],
                core=["scikit-learn", "PyTorch", "MLOps", "Model Deployment", "Git", "CI/CD", "REST APIs"],
                common=["TensorFlow", "MLflow", "Kubernetes", "FastAPI", "Flask", "AWS", "GCP", "Azure",
                        "Model Monitoring", "ONNX", "Feature Stores", "GitHub Actions", "Linux", "SQL", "System Design",
                        "Airflow"]),
    "NLP": dict(must=["Python", "NLP", "Deep Learning"],
                core=["spaCy", "NLTK", "Hugging Face Transformers", "PyTorch", "Text Classification",
                      "Named Entity Recognition", "Embeddings"],
                common=["LLM Fine-tuning", "RAG", "Vector Databases", "Prompt Engineering", "Elasticsearch",
                        "Information Retrieval", "Sentiment Analysis", "TensorFlow", "scikit-learn", "FastAPI", "Docker",
                        "Git"]),
    "CV": dict(must=["Python", "Computer Vision", "Deep Learning"],
               core=["OpenCV", "PyTorch", "Convolutional Neural Networks", "Object Detection", "Image Classification",
                     "Image Segmentation", "Data Augmentation"],
               common=["TensorFlow", "Keras", "YOLO", "Albumentations", "TensorRT", "ONNX", "Video Analytics", "Docker",
                       "Git", "NumPy", "Linux"]),
    "BE": dict(must=["Python", "REST APIs", "SQL"],
               core=["FastAPI", "PostgreSQL", "Docker", "Git", "Unit Testing", "pytest", "SQLAlchemy", "API Design"],
               common=["Django", "Flask", "Redis", "Celery", "RabbitMQ", "JWT Authentication", "Microservices", "CI/CD",
                       "GitHub Actions", "AWS", "Kubernetes", "MongoDB", "Linux", "System Design"]),
    "DE": dict(must=["SQL", "Python", "ETL Pipelines"],
               core=["Apache Spark", "Airflow", "Data Warehousing", "Data Modeling", "PostgreSQL", "Docker", "Git"],
               common=["Kafka", "Snowflake", "BigQuery", "Redshift", "dbt", "Databricks", "Parquet", "Terraform", "AWS",
                       "GCP", "Azure", "Data Quality", "Hadoop", "Linux"]),
    "BA": dict(must=["Requirements Gathering", "Stakeholder Management", "Documentation"],
               core=["Process Mapping", "User Stories", "JIRA", "Agile/Scrum", "Excel", "SQL", "Data Analysis",
                     "Business Process Modeling"],
               common=["Power BI", "UAT", "Gap Analysis", "Cost-Benefit Analysis", "Business Case Development",
                       "Confluence", "Presentation Skills", "Wireframing", "Figma", "Tableau"]),
    "DV": dict(must=["Data Visualization", "Dashboard Design", "SQL"],
               core=["Tableau", "Power BI", "Excel", "Data Storytelling", "Data Cleaning", "Python"],
               common=["Looker Studio", "DAX", "D3.js", "Plotly", "Matplotlib", "Seaborn", "pandas", "Figma",
                       "Google Analytics", "Data Analysis", "Stakeholder Management"]),
    "INT": dict(must=["Python", "Machine Learning", "scikit-learn"],
                core=["pandas", "NumPy", "Deep Learning", "Git", "Jupyter", "Statistics"],
                common=["PyTorch", "TensorFlow", "Keras", "NLP", "Computer Vision", "SQL", "Matplotlib",
                        "Data Visualization", "Linux", "OpenCV", "spaCy"]),
}

# job foci: (label, skills that must appear among the required skills, domain family used for responsibility alignment)
FOCI = {
    "DA": [("Marketing Analytics", ["Google Analytics", "A/B Testing"], "DA"),
           ("Operations Analytics", ["KPI Reporting", "Excel"], "DA"),
           ("Product Analytics", ["A/B Testing", "Python"], "DA"),
           ("Finance Analytics", ["Excel", "Power BI"], "DA"),
           ("Supply Chain Analytics", ["SQL", "Tableau"], "DA")],
    "DS": [("Forecasting", ["Time Series Forecasting", "Statistics"], "DS"),
           ("Experimentation", ["Experiment Design", "A/B Testing", "Causal Inference"], "DS"),
           ("Risk Modeling", ["XGBoost", "Feature Engineering"], "DS"),
           ("Customer Analytics", ["Clustering", "scikit-learn"], "DS"),
           ("Applied ML", ["Deep Learning", "PyTorch"], "DS")],
    "MLE": [("Model Serving", ["Model Deployment", "FastAPI", "Docker"], "MLE"),
            ("ML Platform", ["MLOps", "Kubernetes", "MLflow"], "MLE"),
            ("Real-time Inference", ["ONNX", "Docker", "Model Monitoring"], "MLE"),
            ("Recommendation Systems", ["Feature Stores", "PyTorch"], "MLE")],
    "NLP": [("Conversational AI", ["Hugging Face Transformers", "Prompt Engineering"], "NLP"),
            ("Document Intelligence", ["Named Entity Recognition", "spaCy"], "NLP"),
            ("Search and Retrieval", ["Embeddings", "Elasticsearch", "Information Retrieval"], "NLP"),
            ("LLM Applications", ["RAG", "Vector Databases", "LLM Fine-tuning"], "NLP")],
    "CV": [("Industrial Inspection", ["Object Detection", "OpenCV"], "CV"),
           ("Medical Imaging", ["Image Segmentation", "PyTorch"], "CV"),
           ("Video Analytics", ["Video Analytics", "YOLO"], "CV"),
           ("Edge Vision", ["TensorRT", "ONNX"], "CV")],
    "BE": [("Platform APIs", ["FastAPI", "PostgreSQL"], "BE"),
           ("Payments Services", ["Django", "JWT Authentication"], "BE"),
           ("Event-driven Services", ["Celery", "RabbitMQ", "Redis"], "BE"),
           ("Microservices", ["Microservices", "Docker", "Kubernetes"], "BE")],
    "DE": [("Batch Pipelines", ["Airflow", "Apache Spark"], "DE"),
           ("Streaming Platforms", ["Kafka", "Apache Spark"], "DE"),
           ("Cloud Data Warehouse", ["Snowflake", "dbt", "Data Warehousing"], "DE"),
           ("Lakehouse", ["Databricks", "Parquet"], "DE")],
    "BA": [("Digital Transformation", ["Process Mapping", "Gap Analysis"], "BA"),
           ("Product Delivery", ["User Stories", "JIRA", "Agile/Scrum"], "BA"),
           ("Data-driven Analysis", ["SQL", "Power BI", "Data Analysis"], "BA"),
           ("Finance Systems", ["Requirements Gathering", "UAT"], "BA")],
    "DV": [("Executive Reporting", ["Power BI", "DAX"], "DV"),
           ("Public Data Stories", ["Data Storytelling", "D3.js"], "DV"),
           ("Self-service BI", ["Tableau", "SQL"], "DV"),
           ("Product Analytics Visuals", ["Plotly", "Python"], "DV")],
    "INT": [("General AI/ML", ["Python", "Machine Learning", "pandas"], "DS"),
            ("NLP", ["NLP", "spaCy", "Python"], "NLP"),
            ("Computer Vision", ["Computer Vision", "OpenCV", "PyTorch"], "CV"),
            ("Data Science", ["Statistics", "scikit-learn", "pandas"], "DS"),
            ("Applied ML", ["Git", "Python", "Machine Learning"], "MLE")],
}

SENIOR_EXTRA = {
    "DA": ["Mentoring", "Stakeholder Management"], "DS": ["Mentoring", "Experiment Design"],
    "MLE": ["System Design", "Mentoring"], "NLP": ["Mentoring", "System Design"], "CV": ["Mentoring", "System Design"],
    "BE": ["System Design", "Mentoring", "Microservices"], "DE": ["System Design", "Mentoring", "Data Modeling"],
    "BA": ["Mentoring", "Business Case Development", "Presentation Skills"],
    "DV": ["Mentoring", "Stakeholder Management"], "INT": [],
}

# Having X on a resume implies the prerequisite skills (realistic skill combinations)
IMPLIES = {
    "pandas": ["Python"], "NumPy": ["Python"], "Jupyter": ["Python"],
    "scikit-learn": ["Python", "Machine Learning"], "XGBoost": ["Machine Learning"], "LightGBM": ["Machine Learning"],
    "PyTorch": ["Python", "Deep Learning"], "TensorFlow": ["Python", "Deep Learning"], "Keras": ["Deep Learning"],
    "Deep Learning": ["Machine Learning"], "Feature Engineering": ["Machine Learning"], "Clustering": ["Machine Learning"],
    "Model Evaluation": ["Machine Learning"],
    "Time Series Forecasting": ["Statistics"], "Hypothesis Testing": ["Statistics"], "Causal Inference": ["Statistics"],
    "Bayesian Methods": ["Statistics"], "A/B Testing": ["Statistics"], "Experiment Design": ["Statistics"],
    "Matplotlib": ["Python", "Data Visualization"], "Seaborn": ["Python", "Data Visualization"],
    "Plotly": ["Python", "Data Visualization"], "Tableau": ["Data Visualization"], "Power BI": ["Data Visualization"],
    "Looker Studio": ["Data Visualization"], "D3.js": ["Data Visualization"], "DAX": ["Power BI"],
    "Dashboard Design": ["Data Visualization"], "Data Storytelling": ["Data Visualization"],
    "PostgreSQL": ["SQL"], "MySQL": ["SQL"], "BigQuery": ["SQL", "GCP", "Data Warehousing"],
    "Snowflake": ["SQL", "Data Warehousing"], "Redshift": ["SQL", "AWS", "Data Warehousing"], "dbt": ["SQL"],
    "Airflow": ["Python"], "Databricks": ["Apache Spark"], "SQLAlchemy": ["Python", "SQL"],
    "FastAPI": ["Python", "REST APIs"], "Flask": ["Python", "REST APIs"], "Django": ["Python", "REST APIs"],
    "Celery": ["Python"], "pytest": ["Python", "Unit Testing"], "Kubernetes": ["Docker"], "MLflow": ["MLOps"],
    "GitHub Actions": ["CI/CD", "Git"], "spaCy": ["Python", "NLP"], "NLTK": ["Python", "NLP"],
    "Hugging Face Transformers": ["Python", "NLP", "Deep Learning"], "Text Classification": ["NLP", "Machine Learning"],
    "Named Entity Recognition": ["NLP"], "Sentiment Analysis": ["NLP"], "Embeddings": ["Machine Learning"],
    "RAG": ["NLP", "Embeddings"], "LLM Fine-tuning": ["NLP", "Deep Learning"],
    "OpenCV": ["Python", "Computer Vision"], "Object Detection": ["Computer Vision", "Deep Learning"],
    "YOLO": ["Object Detection"], "Image Segmentation": ["Computer Vision", "Deep Learning"],
    "Image Classification": ["Computer Vision", "Machine Learning"], "Convolutional Neural Networks": ["Deep Learning"],
    "Albumentations": ["Python", "Data Augmentation"], "TensorRT": ["Deep Learning"], "Video Analytics": ["Computer Vision"],
    "Data Cleaning": ["Data Analysis"], "KPI Reporting": ["Data Analysis"], "Google Analytics": ["Data Analysis"],
}

# substitutable tools / sibling concepts: (members, credit when one stands in for another)
CLUSTERS = [
    ({"Tableau", "Power BI", "Looker Studio"}, 0.72),
    ({"PyTorch", "TensorFlow", "Keras"}, 0.78),
    ({"FastAPI", "Flask", "Django"}, 0.72),
    ({"AWS", "Azure", "GCP"}, 0.65),
    ({"Snowflake", "BigQuery", "Redshift"}, 0.72),
    ({"PostgreSQL", "MySQL"}, 0.85),
    ({"Apache Spark", "Databricks"}, 0.75),
    ({"Kafka", "RabbitMQ"}, 0.45),
    ({"spaCy", "NLTK"}, 0.70),
    ({"XGBoost", "LightGBM"}, 0.88),
    ({"Matplotlib", "Seaborn", "Plotly"}, 0.82),
    ({"CI/CD", "GitHub Actions"}, 0.80),
    ({"Process Mapping", "Business Process Modeling"}, 0.90),
    ({"Image Classification", "Object Detection", "Image Segmentation"}, 0.55),
    ({"Text Classification", "Named Entity Recognition", "Sentiment Analysis"}, 0.55),
    ({"Hypothesis Testing", "A/B Testing", "Experiment Design"}, 0.70),
    ({"Vector Databases", "Elasticsearch"}, 0.55),
    ({"ONNX", "TensorRT"}, 0.60),
    ({"Requirements Gathering", "User Stories"}, 0.55),
    ({"Unit Testing", "pytest"}, 0.85),
    ({"REST APIs", "API Design"}, 0.70),
    ({"MLOps", "Model Deployment"}, 0.70),
]

# directed links: requirement <- (have, credit)
LINKS = {
    "Data Analysis": [("pandas", .75), ("SQL", .55), ("Excel", .55), ("Statistics", .4)],
    "KPI Reporting": [("Excel", .5), ("Power BI", .5), ("Tableau", .5), ("Dashboard Design", .5), ("Data Analysis", .45)],
    "Dashboard Design": [("Tableau", .7), ("Power BI", .7), ("Looker Studio", .7), ("Data Visualization", .6), ("Figma", .4)],
    "Data Storytelling": [("Data Visualization", .55), ("Presentation Skills", .5), ("Tableau", .4), ("Power BI", .4)],
    "Presentation Skills": [("Data Storytelling", .55), ("Stakeholder Management", .35)],
    "Stakeholder Management": [("Requirements Gathering", .45), ("Presentation Skills", .4), ("Mentoring", .3)],
    "Requirements Gathering": [("Gap Analysis", .5), ("Stakeholder Management", .4), ("Business Process Modeling", .35)],
    "Documentation": [("Requirements Gathering", .5), ("Confluence", .6)],
    "Gap Analysis": [("Requirements Gathering", .5), ("Business Process Modeling", .5), ("Process Mapping", .45)],
    "Business Case Development": [("Cost-Benefit Analysis", .75)],
    "Cost-Benefit Analysis": [("Business Case Development", .75), ("Excel", .3)],
    "Agile/Scrum": [("JIRA", .5), ("User Stories", .45)],
    "JIRA": [("Confluence", .4), ("Agile/Scrum", .4)],
    "UAT": [("Requirements Gathering", .35)],
    "Wireframing": [("Figma", .6)], "Figma": [("Wireframing", .6)],
    "Hypothesis Testing": [("Statistics", .55)],
    "Feature Engineering": [("Machine Learning", .55), ("scikit-learn", .55), ("pandas", .45)],
    "Model Evaluation": [("scikit-learn", .6), ("Machine Learning", .5)],
    "Clustering": [("scikit-learn", .55), ("Machine Learning", .4)],
    "Time Series Forecasting": [("Statistics", .45), ("Machine Learning", .3)],
    "Causal Inference": [("Statistics", .4), ("Experiment Design", .55), ("Bayesian Methods", .45)],
    "Bayesian Methods": [("Statistics", .45)],
    "scikit-learn": [("Machine Learning", .5), ("XGBoost", .6), ("LightGBM", .6)],
    "NumPy": [("pandas", .6)], "pandas": [("NumPy", .6)],
    "Jupyter": [("Python", .5)],
    "Deep Learning": [("Machine Learning", .3)],
    "Convolutional Neural Networks": [("Deep Learning", .55), ("Image Classification", .7)],
    "Data Augmentation": [("Deep Learning", .25), ("OpenCV", .4)],
    "Hugging Face Transformers": [("PyTorch", .3), ("NLP", .35), ("LLM Fine-tuning", .6)],
    "LLM Fine-tuning": [("Hugging Face Transformers", .6), ("Deep Learning", .3)],
    "RAG": [("Embeddings", .5), ("Vector Databases", .5), ("Prompt Engineering", .45)],
    "Prompt Engineering": [("RAG", .6), ("LLM Fine-tuning", .5)],
    "Embeddings": [("Vector Databases", .5), ("Hugging Face Transformers", .4), ("NLP", .3)],
    "Information Retrieval": [("Elasticsearch", .6), ("Vector Databases", .5), ("Embeddings", .4)],
    "Video Analytics": [("Object Detection", .5), ("OpenCV", .45)],
    "Albumentations": [("Data Augmentation", .6)],
    "Model Deployment": [("FastAPI", .5), ("Docker", .5), ("Flask", .45), ("Kubernetes", .5)],
    "MLOps": [("Docker", .3), ("CI/CD", .35), ("Kubernetes", .4)],
    "Model Monitoring": [("MLOps", .5), ("Model Deployment", .4)],
    "Feature Stores": [("MLOps", .35), ("Data Warehousing", .3)],
    "System Design": [("Microservices", .55), ("API Design", .45)],
    "Microservices": [("Docker", .35), ("Kubernetes", .45), ("System Design", .45), ("API Design", .4)],
    "API Design": [("FastAPI", .5), ("Django", .5), ("Flask", .45)],
    "SQLAlchemy": [("Django", .35), ("SQL", .3)],
    "Celery": [("RabbitMQ", .45), ("Redis", .4)],
    "RabbitMQ": [("Celery", .35)],
    "MongoDB": [("PostgreSQL", .3)],
    "Kubernetes": [("Docker", .4)],
    "Linux": [("Docker", .3), ("Kubernetes", .3)],
    "ETL Pipelines": [("Airflow", .7), ("Apache Spark", .5), ("dbt", .6), ("Data Warehousing", .45), ("Kafka", .35)],
    "Data Warehousing": [("Data Modeling", .5), ("dbt", .45)],
    "Data Modeling": [("Data Warehousing", .55), ("dbt", .45), ("SQL", .3), ("Snowflake", .4)],
    "Airflow": [("ETL Pipelines", .45)],
    "Apache Spark": [("Hadoop", .55)], "Hadoop": [("Apache Spark", .55)],
    "Parquet": [("Apache Spark", .35), ("Databricks", .35)],
    "dbt": [("SQL", .35), ("Data Modeling", .4)],
    "Data Quality": [("ETL Pipelines", .4), ("dbt", .35), ("Data Cleaning", .4)],
    "Data Cleaning": [("pandas", .55), ("Data Analysis", .5), ("Excel", .35), ("SQL", .3)],
    "DAX": [("Power BI", .5)],
    "D3.js": [("Plotly", .4), ("Data Visualization", .25)],
    "Business Process Modeling": [("Process Mapping", .9)],
}

# responsibility-domain affinity (how much experience in family A evidences duties of family B)
_AFF = {
    ("DA", "DS"): .60, ("DA", "DV"): .75, ("DA", "BA"): .65, ("DA", "DE"): .35, ("DA", "MLE"): .20, ("DA", "NLP"): .15,
    ("DA", "CV"): .10, ("DA", "BE"): .10, ("DA", "INT"): .30,
    ("DS", "MLE"): .65, ("DS", "NLP"): .60, ("DS", "CV"): .55, ("DS", "DE"): .35, ("DS", "BE"): .15, ("DS", "BA"): .25,
    ("DS", "DV"): .35, ("DS", "INT"): .60,
    ("MLE", "NLP"): .65, ("MLE", "CV"): .65, ("MLE", "BE"): .55, ("MLE", "DE"): .50, ("MLE", "BA"): .05,
    ("MLE", "DV"): .05, ("MLE", "INT"): .50,
    ("NLP", "CV"): .45, ("NLP", "BE"): .25, ("NLP", "DE"): .20, ("NLP", "BA"): .05, ("NLP", "DV"): .05, ("NLP", "INT"): .60,
    ("CV", "BE"): .20, ("CV", "DE"): .15, ("CV", "BA"): .03, ("CV", "DV"): .05, ("CV", "INT"): .60,
    ("BE", "DE"): .55, ("BE", "BA"): .10, ("BE", "DV"): .05, ("BE", "INT"): .20,
    ("DE", "BA"): .15, ("DE", "DV"): .25, ("DE", "INT"): .15,
    ("BA", "DV"): .55, ("BA", "INT"): .05, ("DV", "INT"): .10,
}
AFF = {}
for (a, b), v in _AFF.items():
    AFF[(a, b)] = v
    AFF[(b, a)] = v
OTHER_AFF = {"DA": .12, "BA": .20, "BE": .05, "DS": .03, "MLE": .02, "NLP": .02, "CV": .02, "DE": .04, "DV": .08, "INT": .03}


def aff(a, b):
    if a == b:
        return 1.0
    if a == "OTHER":
        return OTHER_AFF.get(b, 0.03)
    if a is None:
        return 0.0
    return AFF.get((a, b), 0.0)


def closure(skills):
    out = set(skills)
    stack = list(out)
    while stack:
        s = stack.pop()
        for t in IMPLIES.get(s, []):
            if t not in out:
                out.add(t)
                stack.append(t)
    return out


PAIR_CREDIT = {}
for members, c in CLUSTERS:
    for a in members:
        for b in members:
            if a != b:
                PAIR_CREDIT[(a, b)] = max(PAIR_CREDIT.get((a, b), 0), c)
for req, lst in LINKS.items():
    for have, c in lst:
        PAIR_CREDIT[(req, have)] = max(PAIR_CREDIT.get((req, have), 0), c)


def credit(req, have):
    """Return (credit, matched_skill) for a required skill given a resume's skill closure."""
    if req in have:
        return 1.0, req
    best = (0.0, None)
    for h in have:
        c = PAIR_CREDIT.get((req, h), 0.0)
        if c > best[0]:
            best = (c, h)
    return best


# skill groups where a person typically lists one (occasionally two) tools
EXCLUSIVE = [
    ({"Tableau", "Power BI", "Looker Studio"}, .25), ({"PyTorch", "TensorFlow", "Keras"}, .30),
    ({"FastAPI", "Django", "Flask"}, .25), ({"AWS", "Azure", "GCP"}, .20),
    ({"Snowflake", "BigQuery", "Redshift"}, .15), ({"PostgreSQL", "MySQL"}, .25),
]

# ---------------------------------------------------------------- experience / project templates
# (family, name, text, slots)  -- {0},{1},{2} are filled with skills the resume actually has
TEMPLATES = [
    # Data Analyst
    ("DA", "Order Cancellation Analysis", "Analyzed {k}K order records with {0} and {1} to isolate the main drivers of cancellations; recommendations reduced returns by {p}%", [["SQL", "PostgreSQL", "MySQL"], ["Excel", "pandas", "Power BI", "Tableau"]]),
    ("DA", "Regional Sales Dashboard", "Built an interactive sales dashboard in {0} fed by {1} queries, giving managers weekly visibility into {n} KPIs", [["Tableau", "Power BI", "Looker Studio"], ["SQL", "Excel", "Google Analytics"]]),
    ("DA", "Checkout A/B Test", "Designed and analyzed an {0} on a checkout redesign using {1}; the winning variant lifted conversion by {p}%", [["A/B Testing"], ["Python", "SQL", "Excel", "Hypothesis Testing"]]),
    ("DA", "Automated KPI Reporting", "Automated a monthly {0} pack with {1}, saving roughly {h} analyst hours each month", [["KPI Reporting"], ["Python", "Excel", "SQL", "pandas"]]),
    ("DA", "Data Quality Cleanup", "Cleaned and standardized {k}K records from {n} sources using {0} and {1}, raising completeness from {q}% to {r}%", [["pandas", "Excel", "SQL"], ["Data Cleaning"]]),
    ("DA", "Web Funnel Analysis", "Mapped the user funnel in {0} and segmented drop-off with {1}, uncovering {n} friction points that shaped the product backlog", [["Google Analytics"], ["SQL", "Excel", "Python"]]),
    ("DA", "Customer Segmentation Study", "Segmented customers by purchase behavior using {0} and {1}, helping marketing target {n} cohorts", [["Excel", "SQL", "pandas"], ["Data Analysis", "Statistics"]]),
    # Data Scientist
    ("DS", "Customer Churn Model", "Built a churn prediction model with {0} and {1} on {k}K customer records, reaching an AUC of 0.{a} and guiding retention offers", [["scikit-learn", "XGBoost", "LightGBM"], ["Feature Engineering", "Model Evaluation"]]),
    ("DS", "Demand Forecasting", "Forecast weekly demand for {n} product lines using {0} and {1}, cutting forecast error by {p}%", [["Time Series Forecasting"], ["Python", "Statistics", "pandas"]]),
    ("DS", "Pricing Experiment", "Planned and analyzed a pricing experiment using {0} and {1}, estimating a {p}% revenue uplift with confidence intervals", [["Experiment Design", "A/B Testing", "Hypothesis Testing"], ["Statistics", "Python", "SQL"]]),
    ("DS", "Customer Clustering", "Clustered {k}K customers with {0} and {1} to define {n} behavioral segments adopted by the marketing team", [["Clustering"], ["scikit-learn", "pandas"]]),
    ("DS", "Credit Risk Scorecard", "Developed a default-risk model using {0} with {1}, improving gini by {p} points over the rule-based baseline", [["XGBoost", "LightGBM", "scikit-learn"], ["Feature Engineering", "Model Evaluation"]]),
    ("DS", "Loyalty Uplift Analysis", "Applied {0} methods and {1} to estimate the incremental effect of a loyalty program", [["Causal Inference", "Bayesian Methods"], ["Statistics", "Python"]]),
    # Machine Learning Engineer
    ("MLE", "Model Serving API", "Deployed a {0} model as a {1} service using {2}, handling {k}K predictions per day with p95 latency under {n}0 ms", [["scikit-learn", "PyTorch", "TensorFlow", "XGBoost"], ["FastAPI", "Flask"], ["Docker", "Model Deployment"]]),
    ("MLE", "Training Pipeline Automation", "Set up {0} to automate training, testing and release of models with {1}, cutting release time by {p}%", [["CI/CD", "GitHub Actions"], ["MLflow", "Docker", "MLOps"]]),
    ("MLE", "Experiment Tracking Rollout", "Introduced {0} to track experiments and register models for {n} data scientists, supported by {1}", [["MLflow"], ["MLOps", "Model Deployment"]]),
    ("MLE", "Production Model Monitoring", "Implemented {0} for drift and latency alerts on {n} production models using {1}", [["Model Monitoring"], ["Python", "Docker", "Kubernetes"]]),
    ("MLE", "Containerized Inference", "Containerized inference workloads with {0} and orchestrated them on {1}, enabling autoscaling during peak load", [["Docker"], ["Kubernetes"]]),
    ("MLE", "Inference Optimization", "Reduced inference latency by {p}% by exporting a {0} model to {1}", [["PyTorch", "TensorFlow"], ["ONNX"]]),
    ("MLE", "Shared Feature Layer", "Designed a {0} layer with {1} shared across {n} models to remove training-serving skew", [["Feature Stores"], ["Python", "SQL"]]),
    # NLP Engineer
    ("NLP", "Support Ticket Classifier", "Trained a {0} model with {1} to route support tickets, reaching {p}% macro-F1 across {n} categories", [["Text Classification"], ["scikit-learn", "Hugging Face Transformers", "spaCy"]]),
    ("NLP", "Entity Extraction Pipeline", "Built a {0} pipeline with {1} to extract names, skills and organizations from {k}K documents", [["Named Entity Recognition"], ["spaCy", "Hugging Face Transformers", "NLTK"]]),
    ("NLP", "Document Q&A Assistant", "Created a {0} assistant backed by {1} and {2} for answering questions over internal documents", [["RAG"], ["Vector Databases", "Embeddings"], ["Hugging Face Transformers", "Prompt Engineering"]]),
    ("NLP", "Domain Model Adaptation", "Applied {0} with {1} to adapt a language model, improving domain accuracy by {p}% over the base model", [["LLM Fine-tuning"], ["Hugging Face Transformers", "PyTorch"]]),
    ("NLP", "Review Sentiment Tracker", "Analyzed {k}K product reviews with {0} and {1} to track sentiment trends by feature", [["Sentiment Analysis"], ["NLTK", "spaCy", "scikit-learn"]]),
    ("NLP", "Semantic Search Prototype", "Prototyped semantic search using {0} and {1}, improving top-5 hit rate by {p}% over keyword search", [["Embeddings"], ["Elasticsearch", "Vector Databases", "Information Retrieval"]]),
    ("NLP", "Prompt Evaluation Harness", "Built a {0} test harness in {1} to compare prompt variants and cut hallucination reports by {p}%", [["Prompt Engineering"], ["Python"]]),
    # Computer Vision Engineer
    ("CV", "Defect Detection System", "Trained a {0} detector with {1} to spot surface defects on a production line, reaching {p}% recall", [["Object Detection", "YOLO"], ["PyTorch", "TensorFlow", "OpenCV"]]),
    ("CV", "Scan Image Segmentation", "Built an {0} model using {1} to outline regions of interest in scan images, with a Dice score of 0.{a}", [["Image Segmentation"], ["PyTorch", "TensorFlow"]]),
    ("CV", "Product Image Classifier", "Developed an {0} model with {1} and {2}, lifting top-1 accuracy by {n} points", [["Image Classification"], ["Convolutional Neural Networks"], ["Data Augmentation", "Albumentations"]]),
    ("CV", "Footfall Counter", "Used {0} and {1} to count and track visitors in video streams across {n} camera feeds", [["Video Analytics"], ["OpenCV", "Object Detection"]]),
    ("CV", "Edge Deployment", "Optimized a vision model with {0} for edge devices, cutting latency by {p}%", [["TensorRT", "ONNX"]]),
    ("CV", "Document Image Preprocessing", "Built {0} preprocessing for scanned documents with {1}, improving downstream text recognition accuracy by {n} points", [["OpenCV"], ["Python"]]),
    # Python Backend Developer
    ("BE", "Order Management API", "Designed a {0} service with {1} and {2} exposing {n} endpoints for order and inventory workflows", [["FastAPI", "Django", "Flask"], ["PostgreSQL", "MySQL"], ["REST APIs", "SQLAlchemy"]]),
    ("BE", "Async Job Processing", "Moved slow tasks to {0} workers with {1}, reducing request latency by {p}%", [["Celery"], ["Redis", "RabbitMQ"]]),
    ("BE", "Token Auth Module", "Implemented {0} for a multi-tenant API and covered it with {1}", [["JWT Authentication"], ["pytest", "Unit Testing"]]),
    ("BE", "Caching Layer", "Added {0} caching to hot endpoints, lowering database load by {p}%", [["Redis"]]),
    ("BE", "Release Pipeline", "Containerized services with {0} and automated releases using {1}", [["Docker"], ["CI/CD", "GitHub Actions"]]),
    ("BE", "Service Decomposition", "Split a monolith into {n} {0} with clear {1} contracts", [["Microservices"], ["API Design", "REST APIs"]]),
    ("BE", "Test Coverage Drive", "Raised unit test coverage from {q}% to {r}% with {0} and {1}", [["pytest", "Unit Testing"], ["Git", "CI/CD"]]),
    # Data Engineer
    ("DE", "Batch ETL Pipeline", "Built {0} orchestrated by {1} to load {k}K daily records from {n} sources into {2}", [["ETL Pipelines"], ["Airflow"], ["Snowflake", "BigQuery", "Redshift", "PostgreSQL"]]),
    ("DE", "Spark Transformation Jobs", "Rewrote slow transformations in {0} and stored output as {1}, cutting runtime by {p}%", [["Apache Spark", "Databricks"], ["Parquet"]]),
    ("DE", "Streaming Ingestion", "Set up {0} streaming ingestion for {n} event types and processed it with {1}", [["Kafka"], ["Apache Spark", "Python", "SQL"]]),
    ("DE", "Warehouse Modeling", "Modeled star-schema marts using {0} and {1}, giving analysts consistent metrics", [["Data Modeling", "Data Warehousing"], ["dbt", "SQL"]]),
    ("DE", "Data Quality Checks", "Added automated {0} checks to {n} pipelines using {1}, catching issues before dashboards refreshed", [["Data Quality"], ["Python", "dbt", "SQL", "Airflow"]]),
    ("DE", "Infrastructure as Code", "Provisioned data infrastructure with {0} on {1}", [["Terraform"], ["AWS", "GCP", "Azure"]]),
    # Business Analyst
    ("BA", "Requirements Workshop Series", "Led {n} workshops to capture {0} from {1}, turning them into {2} for the delivery team", [["Requirements Gathering"], ["Stakeholder Management"], ["User Stories", "Documentation"]]),
    ("BA", "Process Redesign", "Mapped the as-is workflow using {0} and {1}, then proposed a streamlined flow that removed {n} manual handoffs", [["Process Mapping", "Business Process Modeling"], ["Gap Analysis", "Documentation"]]),
    ("BA", "Business Case Preparation", "Prepared a {0} for a workflow automation initiative, backed by {1}; projected {p}% lower processing cost", [["Cost-Benefit Analysis", "Business Case Development"], ["Excel", "SQL", "Power BI"]]),
    ("BA", "Backlog Management", "Managed the backlog in {0} using {1} ceremonies for a team of {n}", [["JIRA", "Confluence"], ["Agile/Scrum"]]),
    ("BA", "UAT Coordination", "Coordinated {0} cycles with {1}, reducing post-release defects by {p}%", [["UAT"], ["Stakeholder Management", "Documentation"]]),
    ("BA", "Operational Reporting", "Pulled data with {0} and presented findings through {1} to leadership every month", [["SQL", "Excel", "Data Analysis"], ["Presentation Skills", "Power BI"]]),
    ("BA", "Wireframe Prototyping", "Created {0} in {1} to align stakeholders on screens before development", [["Wireframing"], ["Figma"]]),
    # Data Visualization Analyst
    ("DV", "Executive KPI Dashboard", "Designed a {0} dashboard applying {1} that consolidated {n} metrics for leadership", [["Tableau", "Power BI", "Looker Studio"], ["Dashboard Design", "Data Storytelling"]]),
    ("DV", "Interactive Data Story", "Built a {0} piece using {1} to explain trends to non-technical readers", [["Data Storytelling"], ["D3.js", "Plotly", "Tableau"]]),
    ("DV", "Self-service Report Model", "Modeled measures with {0} in {1} so teams could slice data without analyst help", [["DAX"], ["Power BI"]]),
    ("DV", "Weekly Chart Library", "Produced reusable {0} charts with {1} for weekly publications", [["Matplotlib", "Seaborn", "Plotly"], ["Python", "pandas"]]),
    ("DV", "Dashboard Redesign", "Redesigned legacy dashboards after user testing in {0}, reducing time-to-insight by {p}% using {1}", [["Tableau", "Power BI", "Looker Studio"], ["Dashboard Design", "Figma"]]),
    ("DV", "Data Prep for Visuals", "Prepared data with {0} and {1} to feed {n} published dashboards", [["SQL"], ["Excel", "pandas", "Python"]]),
    # Student / intern style projects (family tag = domain of the work)
    ("DS", "House Price Prediction", "Trained and compared {n} regression models in {0} on a public housing dataset using {1}", [["scikit-learn"], ["pandas", "NumPy"]], ),
    ("DS", "Exploratory Data Analysis Notebook", "Explored a public dataset in {0} with {1} and {2}, documenting {n} insights", [["Jupyter"], ["pandas", "Matplotlib"], ["Data Visualization"]]),
    ("DS", "Deep Learning Digit Classifier", "Built a small {0} classifier in {1} reaching {p}% test accuracy", [["Deep Learning"], ["PyTorch", "TensorFlow", "Keras"]]),
    ("NLP", "Tweet Sentiment Baseline", "Built a baseline {0} sentiment classifier using {1}", [["NLP"], ["scikit-learn", "spaCy", "NLTK"]]),
    ("CV", "Image Classifier Mini-project", "Built a {0} image classifier on a small public dataset using {1}", [["Computer Vision"], ["OpenCV", "PyTorch", "TensorFlow"]]),
]

# seniority-flavoured bullets
SENIOR_TEMPLATES = [
    ("Mentoring", "Mentored {n} junior teammates and ran weekly review sessions"),
    ("System Design", "Led the system design for {n} new services, documenting trade-offs and rollout plans"),
]

GENERIC_BULLETS = [
    "Assisted the team with routine data tasks, documentation and ad-hoc requests",
    "Supported senior colleagues on analysis and reporting work",
    "Attended sprint meetings and helped with testing and bug fixes",
    "Helped prepare datasets and documentation for ongoing projects",
    "Shadowed senior team members and completed small assigned tickets",
]
OTHER_BULLETS = [
    "Coordinated daily operations for a team of {n} and tracked weekly targets",
    "Prepared weekly status reports and handled escalations from {n} clients",
    "Tracked inventory and reconciled monthly figures in spreadsheets",
    "Trained {n} new joiners on standard operating procedures",
    "Tested release builds against written test cases and logged defects",
    "Handled customer queries and documented recurring issues for the product team",
    "Prepared quotations and followed up with {n} accounts each month",
]
OTHER_TITLES = ["Operations Executive", "Marketing Executive", "QA Tester", "Customer Support Lead",
                "Accounts Associate", "Sales Coordinator", "Logistics Coordinator", "Content Analyst"]
OTHER_INDUSTRY = ["a logistics firm", "a retail chain", "a manufacturing unit", "a marketing agency", "a services company"]

ROLE_TITLES = {
    "DA": [["Junior Data Analyst", "Data Analyst Trainee", "Reporting Analyst"], ["Data Analyst", "Business Intelligence Analyst"], ["Senior Data Analyst", "Lead Analyst"]],
    "DS": [["Junior Data Scientist", "Associate Data Scientist"], ["Data Scientist", "Applied Data Scientist"], ["Senior Data Scientist", "Lead Data Scientist"]],
    "MLE": [["Junior ML Engineer", "Associate Machine Learning Engineer"], ["Machine Learning Engineer", "ML Engineer"], ["Senior Machine Learning Engineer", "Lead ML Engineer"]],
    "NLP": [["Junior NLP Engineer", "Associate NLP Engineer"], ["NLP Engineer", "Language Technology Engineer"], ["Senior NLP Engineer", "Lead NLP Engineer"]],
    "CV": [["Junior Computer Vision Engineer", "Associate Vision Engineer"], ["Computer Vision Engineer", "Vision ML Engineer"], ["Senior Computer Vision Engineer", "Lead Vision Engineer"]],
    "BE": [["Junior Python Developer", "Associate Backend Developer"], ["Python Backend Developer", "Backend Engineer"], ["Senior Backend Engineer", "Lead Python Developer"]],
    "DE": [["Junior Data Engineer", "Associate Data Engineer"], ["Data Engineer", "ETL Developer"], ["Senior Data Engineer", "Lead Data Engineer"]],
    "BA": [["Junior Business Analyst", "Associate Business Analyst"], ["Business Analyst", "Systems Analyst"], ["Senior Business Analyst", "Lead Business Analyst"]],
    "DV": [["Junior BI Developer", "Reporting Associate"], ["Data Visualization Analyst", "BI Analyst"], ["Senior Visualization Specialist", "Lead BI Analyst"]],
    "INT": [["Intern"], ["Intern"], ["Intern"]],
}
INTERN_TITLES = {
    "DA": "Data Analytics Intern", "DS": "Data Science Intern", "MLE": "Machine Learning Intern", "NLP": "NLP Intern",
    "CV": "Computer Vision Intern", "BE": "Backend Development Intern", "DE": "Data Engineering Intern",
    "BA": "Business Analysis Intern", "DV": "Visualization Intern", "INT": "AI/ML Intern",
}
# typical earlier-career families
PATHS = {"DA": ["OTHER", "BA"], "DS": ["DA"], "MLE": ["BE", "DS"], "NLP": ["DS", "BE"], "CV": ["DS", "MLE"],
         "BE": ["BE"], "DE": ["BE", "DA"], "BA": ["DA", "OTHER"], "DV": ["DA"], "INT": ["DA"]}

INDUSTRIES = ["retail", "fintech", "healthcare", "logistics", "e-commerce", "telecom", "manufacturing", "insurance",
              "edtech", "energy", "media", "travel", "agritech", "real estate"]

RESP = {
    "DA": ["Query transactional and event data to answer business questions for {ind} stakeholders",
           "Build and maintain recurring reports and dashboards that track core business KPIs",
           "Clean, validate and reconcile data from multiple internal sources before analysis",
           "Translate ambiguous questions from product, marketing and operations teams into clear analyses",
           "Present findings and recommendations to non-technical teams through concise write-ups",
           "Support experiments by defining success metrics and analyzing results",
           "Document metric definitions so teams interpret numbers the same way"],
    "DS": ["Develop, validate and iterate on predictive models that support {ind} decisions",
           "Frame business problems as modeling tasks and choose appropriate evaluation metrics",
           "Engineer features from transactional, behavioral and time-series data",
           "Design and analyze experiments to measure the impact of product and pricing changes",
           "Communicate model assumptions, limitations and results to business leaders",
           "Partner with engineers to hand models over for production use",
           "Monitor model performance and retrain when the data drifts"],
    "MLE": ["Productionize machine learning models and expose them through reliable, low-latency services",
            "Build training and deployment pipelines that are reproducible and automated",
            "Containerize and scale inference workloads for {ind} use cases",
            "Monitor models in production for drift, latency and failures",
            "Collaborate with data scientists to turn research notebooks into maintainable code",
            "Improve the performance and cost of model training and serving",
            "Maintain experiment tracking, versioning and release processes for models"],
    "NLP": ["Build language pipelines for classification, extraction and search over {ind} text",
            "Fine-tune and evaluate transformer-based models on domain-specific data",
            "Design retrieval and embedding-based features to improve result relevance",
            "Create annotation guidelines and evaluation sets for text tasks",
            "Prototype LLM-powered features and measure quality, cost and latency",
            "Reduce hallucination and error rates through prompt design and systematic evaluation",
            "Work with engineers to ship NLP components as services"],
    "CV": ["Develop computer vision models for detection, segmentation and classification in {ind} settings",
           "Curate, label and augment image and video datasets",
           "Train and benchmark deep learning models and analyze failure cases",
           "Optimize models for real-time inference on edge and cloud hardware",
           "Build image preprocessing pipelines and integrate results into applications",
           "Evaluate models with task-specific metrics and field data",
           "Document experiments and share findings with product and hardware teams"],
    "BE": ["Design, build and maintain REST APIs and backend services in Python for {ind} products",
           "Model relational data and write efficient queries",
           "Write automated tests and take part in code reviews",
           "Improve the reliability, security and performance of production services",
           "Integrate with third-party services and internal systems",
           "Build background workers and queues for long-running tasks",
           "Containerize services and contribute to CI/CD pipelines"],
    "DE": ["Design and operate batch and streaming pipelines that feed analytics and ML in {ind}",
           "Model data for the warehouse and maintain curated marts",
           "Ensure data quality through validation, monitoring and alerting",
           "Optimize pipeline performance and storage cost",
           "Work with analysts and scientists to understand their data needs",
           "Automate infrastructure and deployments for the data platform",
           "Document lineage and ownership of key datasets"],
    "BA": ["Elicit and document business requirements through interviews and workshops with {ind} stakeholders",
           "Analyze current processes, identify gaps and recommend improvements",
           "Write user stories and acceptance criteria and groom the backlog with delivery teams",
           "Coordinate user acceptance testing and track defects to closure",
           "Use data to size opportunities and measure results after release",
           "Prepare business cases and status updates for leadership",
           "Act as the bridge between business teams and engineers"],
    "DV": ["Design clear, accessible dashboards that help {ind} teams monitor performance",
           "Turn raw data into visual stories for executives and operational teams",
           "Gather requirements from stakeholders and iterate on prototypes",
           "Build reusable data models and measures behind self-service reports",
           "Apply visual design principles when choosing chart types, color and layout",
           "Set standards for dashboard governance and documentation",
           "Train colleagues to explore data on their own"],
    "INT": ["Assist the team with data preparation, model training and evaluation for {ind} projects",
            "Run experiments, track results and summarize learnings",
            "Read papers and prototype ideas in notebooks",
            "Contribute clean, documented code to the team repository",
            "Present weekly progress to mentors and peers",
            "Help build baseline models and evaluation scripts"],
}
