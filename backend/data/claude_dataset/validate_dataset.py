import csv, json, re, sys
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

D = sys.argv[1] if len(sys.argv) > 1 else "."
jobs = pd.read_csv(f"{D}/jobs.csv", dtype={"min_years_experience": int}, keep_default_na=False)
res = pd.read_csv(f"{D}/resumes.csv", keep_default_na=False)
pairs = pd.read_csv(f"{D}/training_pairs.csv", keep_default_na=False)
aud = pd.read_csv(f"{D}/pair_label_audit.csv", keep_default_na=False)
R = {}
chk = lambda name, ok, detail="": R.__setitem__(name, {"pass": bool(ok), "detail": detail})

chk("row_counts", len(jobs) == 100 and len(res) == 200 and len(pairs) == 2000, f"jobs={len(jobs)}, resumes={len(res)}, pairs={len(pairs)}")
chk("pairs_columns_exact", list(pairs.columns) == ["resume_id", "job_id", "resume_text", "job_title", "job_description",
    "required_skills", "experience_level", "skill_overlap", "relevance_label"])
chk("no_missing_or_blank", all((df.astype(str).apply(lambda c: c.str.strip()) != "").all().all() for df in (jobs, res, pairs)))
chk("unique_ids", jobs.job_id.is_unique and res.resume_id.is_unique)
chk("foreign_keys", pairs.resume_id.isin(res.resume_id).all() and pairs.job_id.isin(jobs.job_id).all())
chk("no_duplicate_pairs", not pairs.duplicated(["resume_id", "job_id"]).any())
chk("labels_valid", set(pairs.relevance_label) <= {0, 1, 2}, str(pairs.relevance_label.value_counts().sort_index().to_dict()))
J, Rs = jobs.set_index("job_id"), res.set_index("resume_id")
chk("pair_text_matches_source_tables",
    (pairs.resume_text.values == Rs.loc[pairs.resume_id, "resume_text"].values).all() and
    (pairs.job_description.values == J.loc[pairs.job_id, "job_description"].values).all() and
    (pairs.job_title.values == J.loc[pairs.job_id, "job_title"].values).all() and
    (pairs.required_skills.values == J.loc[pairs.job_id, "required_skills"].values).all() and
    (pairs.experience_level.values == J.loc[pairs.job_id, "experience_level"].values).all())
# skill_overlap recompute
def ov(r):
    have = set(Rs.loc[r.resume_id, "skills"].split("; "))
    req = r.required_skills.split("; ")
    return round(sum(s in have for s in req) / len(req), 3)
chk("skill_overlap_recomputes", np.allclose(pairs.apply(ov, axis=1), pairs.skill_overlap, atol=1e-3))
chk("resume_skills_appear_in_text", all(all(s in t for s in sk.split("; ")) for sk, t in zip(res.skills, res.resume_text)))
chk("required_skills_appear_in_description", all(all(s in t for s in sk.split("; ")) for sk, t in zip(jobs.required_skills, jobs.job_description)))
pc = pairs.resume_id.value_counts()
chk("pairs_per_resume_is_10", (pc == 10).all() and len(pc) == 200)
jc = pairs.job_id.value_counts()
chk("every_job_used", len(jc) == 100, f"pairs per job min/median/max = {jc.min()}/{int(jc.median())}/{jc.max()}")
fam = jobs.job_family.value_counts()
chk("jobs_10_per_family", (fam == 10).all() and len(fam) == 10)
chk("resumes_20_per_domain", (res.primary_domain.value_counts() == 20).all())
lab_per_res = pairs.groupby("resume_id").relevance_label.nunique()
chk("each_resume_has_2plus_label_values", (lab_per_res >= 2).all(), str(lab_per_res.value_counts().sort_index().to_dict()))
hi = pairs.groupby("resume_id").relevance_label.max()
chk("resumes_with_a_label_ge1", (hi >= 1).all(), f"resumes with at least one label-2 pair: {(hi == 2).sum()}/200")
# privacy-ish
pat = re.compile(r"@|https?://|www\.|\b\d{10}\b|\+\d{2}")
chk("no_emails_urls_phones", not any(pat.search(t) for t in list(res.resume_text) + list(jobs.job_description)))
# csv roundtrip with strict csv module
for f in ("jobs", "resumes", "training_pairs", "pair_label_audit"):
    with open(f"{D}/{f}.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh, strict=True))
    n = len(rows[0])
    chk(f"csv_strict_parse_{f}", all(len(r) == n for r in rows), f"{len(rows)-1} rows x {n} cols")
# duplicates
def maxsim(texts):
    m = cosine_similarity(TfidfVectorizer(stop_words="english").fit_transform(texts))
    np.fill_diagonal(m, 0)
    return float(m.max()), float((m > .9).sum() / 2)
chk("no_duplicate_resume_text", res.resume_text.is_unique and not res.skills.duplicated().any())
rs, rn = maxsim(res.resume_text)
js, jn = maxsim(jobs.job_description)
chk("resume_near_duplicates_lt_0.9", rn == 0, f"max pairwise TF-IDF cosine = {rs:.3f}")
chk("job_near_duplicates_lt_0.9", jn == 0, f"max pairwise TF-IDF cosine = {js:.3f}")
# label consistency: monotonic in the four factors within each job
A = aud.copy()
viol = 0
for jid, g in A.groupby("job_id"):
    M = g[["skill_match", "evidence_score", "domain_alignment", "experience_fit"]].values
    L = g.relevance_label.values
    for i in range(len(g)):
        dom = (M >= M[i]).all(axis=1) & (L < L[i])   # someone dominates i yet has a lower label
        viol += int(dom.sum())
chk("no_dominance_label_contradictions", viol == 0, f"violations={viol}")
ident = A.groupby(["job_id", "skill_match", "evidence_score", "domain_alignment", "experience_fit"]).relevance_label.nunique()
chk("identical_factors_same_label", (ident == 1).all())
chk("audit_labels_match_pairs", (A.merge(pairs[["resume_id", "job_id", "relevance_label"]], on=["resume_id", "job_id"],
    suffixes=("_a", "_p")).eval("relevance_label_a == relevance_label_p")).all())

# difficulty / non-triviality
y = pairs.relevance_label.values
x = pairs.skill_overlap.values
tf = TfidfVectorizer(stop_words="english").fit(list(pairs.resume_text) + list(pairs.job_description))
cs = np.asarray(tf.transform(pairs.resume_text).multiply(tf.transform(pairs.job_description)).sum(axis=1)).ravel()
best = max(((np.where(x >= b, 2, np.where(x >= a_, 1, 0)) == y).mean(), a_, b) for a_ in np.arange(.1, .7, .05) for b in np.arange(.3, .95, .05) if b > a_)
stats = {
    "label_distribution": {int(k): int(v) for k, v in pd.Series(y).value_counts().sort_index().items()},
    "mean_skill_overlap_by_label": {int(k): round(float(v), 3) for k, v in pairs.groupby("relevance_label").skill_overlap.mean().items()},
    "spearman_overlap_vs_label": round(float(spearmanr(x, y)[0]), 3),
    "spearman_tfidf_cosine_vs_label": round(float(spearmanr(cs, y)[0]), 3),
    "best_overlap_only_threshold_accuracy": round(float(best[0]), 3),
    "label2_with_overlap_lt_0.5": int(((y == 2) & (x < .5)).sum()),
    "label0_with_overlap_ge_0.4": int(((y == 0) & (x >= .4)).sum()),
    "label1_with_overlap_lt_0.3": int(((y == 1) & (x < .3)).sum()),
    "label0_with_overlap_ge_0.6": int(((y == 0) & (x >= .6)).sum()),
    "pair_type_by_label": pd.crosstab(aud.pair_type, aud.relevance_label).to_dict("index"),
    "rule_applied_counts": aud.rule_applied.value_counts().to_dict(),
    "experience_level_counts_jobs": jobs.experience_level.value_counts().to_dict(),
    "resume_years_summary": res.years_experience.astype(float).describe().round(2).to_dict(),
    "max_resume_cosine": round(rs, 3), "max_job_cosine": round(js, 3),
}
json.dump({"checks": R, "stats": stats}, open(f"{D}/validation_report.json", "w"), indent=2, default=int)
for k, v in R.items():
    print(("PASS" if v["pass"] else "FAIL"), k, v["detail"])
print(json.dumps(stats, indent=1, default=int))
