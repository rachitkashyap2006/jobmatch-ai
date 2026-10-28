# Synthetic Resume-Job Relevance Dataset (v1)

**All data is fictional and machine-generated.** No real people, employers, or schools are intended; any resemblance
(company names, institutions) is coincidental. Labels come from a documented rule-based scoring function, **not** from
human annotators or real hiring outcomes. The dataset is **not validated against real-world data**; use it for
prototyping, pipeline testing and sanity-checking, not for claims about real hiring decisions.

## Files
| File | Rows | Purpose |
|---|---|---|
| jobs.csv | 100 | 10 jobs per family (Data Analyst, Data Scientist, ML Engineer, NLP Engineer, CV Engineer, Python Backend, Data Engineer, Business Analyst, Data Viz Analyst, AI/ML Intern) |
| resumes.csv | 200 | 20 resumes per primary domain, mixed archetypes and strengths |
| training_pairs.csv | 2,000 | 10 pairs per resume; exactly the 9 requested columns |
| pair_label_audit.csv | 2,000 | Optional: factor scores behind each label (do NOT feed to a model as features if you want a fair evaluation) |
| validation_report.json | - | Machine-readable output of validate_dataset.py |
| generate_dataset.py, taxonomy.py, validate_dataset.py | - | Reproducible generator (seed 20261022) and validator |

## Data dictionary
**training_pairs.csv**: `resume_id` (FK to resumes.csv), `job_id` (FK to jobs.csv), `resume_text` (single-line resume; sections separated by " | ", entries by " || "), `job_title`, `job_description`, `required_skills` ("; "-separated, ordered by importance), `experience_level` (Intern (0-1 years) / Junior (1-3 years) / Mid (3-5 years) / Senior (5+ years)), `skill_overlap` (share of required skills literally listed in the resume's skills list, 0-1), `relevance_label` (0 not relevant, 1 partially relevant, 2 highly relevant).

**jobs.csv**: job_id, job_title, job_family, domain_focus, company_name (fictional), industry, location, work_mode, employment_type, experience_level, min_years_experience, required_skills, preferred_skills, job_description.

**resumes.csv**: resume_id, primary_domain (the domain the resume is built around; may leak the answer for same-domain pairs, so treat as metadata), years_experience (total, any domain), education_level, skills ("; "-separated), resume_text.

**pair_label_audit.csv**: resume_archetype (strong / moderate / adjacent / student / stuffer / switcher), pair_type (same/adjacent/distant domain), and the four factor scores below.

## How labels were assigned (not keyword overlap alone)
Four factors in [0,1], computed from structured data hidden behind the text:
1. **skill_match** (weight .35): credit per required skill (first 3 weighted 1.5x): exact = 1.0, transferable tool/concept = 0.3-0.9 (e.g. Power BI for Tableau, PyTorch for TensorFlow, Hypothesis Testing for A/B Testing).
2. **evidence_score** (.20): the same credit, counted only where the matched skill is actually demonstrated in a project or job bullet (skills only listed do not count).
3. **domain_alignment** (.25): how closely past roles and projects match the job's responsibilities (family-to-family affinity matrix).
4. **experience_fit** (.20): effective relevant years vs the job's minimum, with penalties for under- and over-qualification (e.g. a senior profile for an internship).

overall = weighted sum. Label 0 if experience_fit < .2, skill_match < .2 or domain_alignment < .2. Otherwise 2 if overall >= .70 and gates are met (skill_match >= .65, evidence >= .30, domain >= .55, experience_fit >= .60), else 1 if overall >= .46, else 0.

## Validation summary (all automated checks passed; see validation_report.json)
- Counts: 100 jobs, 200 resumes, 2,000 pairs; 10 pairs per resume; all 100 jobs used (6-32 pairs each).
- Integrity: unique IDs, valid foreign keys, no duplicate pairs, no blank fields, strict-CSV parse OK, pair text identical to source tables, `skill_overlap` recomputes exactly, every listed skill appears in its text.
- Duplicates: no identical resumes; max TF-IDF cosine 0.885 (resumes) and 0.760 (jobs).
- Label distribution: 0 = 784 (39%), 1 = 789 (39%), 2 = 427 (21%). Every resume has 2-3 distinct labels (153 have all three).
- Consistency: zero cases where a pair that is at least as strong on all four factors received a lower label within the same job.
- Not trivial: Spearman(skill_overlap, label) = 0.67; best overlap-only threshold rule reaches 65% accuracy. 161 label-0 pairs have overlap >= 0.4 (72 have >= 0.6), 23 label-2 pairs have overlap < 0.5, 165 label-1 pairs have overlap < 0.3.

## Known limitations
- Labels are deterministic functions of generator features, so a model can in principle learn the generator's rules; real data will be noisier.
- Pairs are stratified-sampled by label and difficulty (oversampling hard negatives and transferable positives), so the class mix is not the natural 20,000-pair mix (~7% / 20% / 74%).
- Resume and job language comes from templates; vocabulary is narrower than real text. Metrics and wording are invented.
- Domain tags and the audit file can leak labels; exclude them from model inputs.
