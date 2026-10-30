# Resume intelligence backend

## Run and validate

Run the API from this directory with `uvicorn main:app --reload`.
The existing PDF upload routes remain available:

- `POST /analyze` returns the parsed candidate profile, required/preferred skill
  coverage, skill gaps, score components, learning roadmap, and data-quality
  warnings.
- `POST /recommend-jobs` returns the candidate profile and ranked job records
  with explanations, matched/partial/missing skills, component scores, and
  confidence.
- `POST /learning-resources` continues to use the YouTube integration.

Run the tests and the labeled-corpus comparison from the repository root:

```powershell
python -m pytest -q backend
python backend\evaluate_recommendations.py
```

The evaluator groups its 80/20 split by resume ID, so a candidate's pairs do
not occur in both splits. Its labels are generated from synthetic rules, not
human judgments; the metrics are a reproducible prototype check, not evidence
of real-world hiring performance. The run below used the locally cached
Sentence Transformers model; the binary hybrid threshold was 50/100.

## Matching approach

Job recommendation scores are normalized to 0-100 and combine:

| Component | Weight |
|---|---:|
| Required-skill match (exact plus explicit transferable credit) | 40% |
| Preferred-skill match | 5% |
| Resume/job semantic cosine similarity | 20% |
| Role and domain keyword match | 10% |
| Experience relevance | 25% |

The first three required skills receive extra weight. Skill aliases such as
`sklearn`/`scikit-learn` normalize to one canonical skill; related technologies
such as TensorFlow and PyTorch remain distinct and can only receive partial
credit. Preferred skills are scored separately from required skills.

The analyzer endpoint retains its existing overall-score contract: 60% required
and transferable skill coverage and 40% semantic cosine similarity. Its
response includes each component and the weights.

Sentence Transformers (`all-MiniLM-L6-v2`) is used only when it is already
available in the local model cache. The application does not download the
model during a request. If it is unavailable, the response identifies the
TF-IDF cosine fallback as the semantic backend and the backend logs the
fallback reason.

## Evaluation snapshot

Last run on the bundled 200-resume/2,000-pair synthetic dataset, with 40
held-out resumes and 400 held-out pairs:

| Metric | Existing TF-IDF classifier | Hybrid |
|---|---:|---:|
| Binary relevance accuracy (label >= 1) | 0.7200 | 0.8375 |
| Binary relevance precision | 0.7708 | 0.8899 |
| Binary relevance recall | 0.7645 | 0.8347 |
| Precision@5 for label 2 | 0.3700 | 0.4850 |
| Recall@5 for labels >= 1 | 0.6724 | 0.7697 |
| NDCG@5 | 0.7397 | 0.9506 |

Skill extraction against the dataset's listed skills measured micro precision
0.9413, micro recall 0.9498, F1 0.9455, and exact-set accuracy 0.1750. These
results are specific to generated templates and labels. The lower exact-set
accuracy shows that extraction still adds or misses skills on some resumes;
human-labeled, real resume/job data is needed before making production accuracy
claims.

## Limitations

- PDF extraction requires selectable text; scanned/image-only resumes need OCR,
  which is not included.
- Skill extraction is evidence-based against a maintained vocabulary and the
  bundled job catalog. Unrecognized or novel skills are not inferred.
- Candidate levels use explicit resume cues and experience evidence; numeric
  years are reported only when supported by a duration or date range.
  Incomplete profiles are marked unknown or receive warnings rather than
  having missing details filled in.
- The job catalog and evaluation labels are synthetic. Scores are ranking
  signals, not calibrated hiring probabilities.
