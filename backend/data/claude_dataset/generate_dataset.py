"""Synthetic resume-job relevance dataset generator. All content is fictional."""
import csv, math, random, sys
from collections import Counter, defaultdict
from taxonomy import *

SEED = 20261022
rng = random.Random(SEED)
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
T1, T2 = 0.46, 0.70          # overall-score thresholds for labels 1 and 2
N_RESUME_PER_FAMILY = 20
PAIRS_PER_RESUME = 10
JOB_CAP = 32

LEVELS = {0: "Intern (0-1 years)", 1: "Junior (1-3 years)", 2: "Mid (3-5 years)", 3: "Senior (5+ years)"}
PRE = ["Alder", "Brindle", "Cobalt", "Dunmore", "Elmora", "Fenwick", "Garnet", "Halcyon", "Ironleaf", "Juniper",
       "Kestrel", "Larkspur", "Marlow", "Nimbus", "Oakhaven", "Pinegrove", "Quillon", "Riverton", "Saffron", "Tamarack",
       "Umbra", "Verdane", "Willowmere", "Yarrow", "Zephyra", "Ashby", "Bexley", "Corvane", "Drayton", "Eastmere"]
SUF = ["Analytics", "Systems", "Labs", "Digital", "Logic", "Works", "Technologies", "Solutions", "Dynamics", "Networks",
       "Insights", "Software", "Cloudware", "Data Co", "Ventures"]
CITIES = ["Bengaluru", "Hyderabad", "Pune", "Gurugram", "Chennai", "Mumbai", "Noida", "Remote (India)", "London",
          "Singapore", "Berlin", "Toronto", "Remote", "Dubai", "Lisbon"]
SIZES = ["early-stage", "fast-growing", "mid-sized", "established", "global"]
PRODUCTS = ["tools that help customers decide faster", "platforms used by thousands of people every day",
            "services that keep operations running smoothly", "data-driven products for everyday customers"]

_used_names = set()


def company():
    while True:
        n = f"{rng.choice(PRE)} {rng.choice(SUF)}"
        if n not in _used_names:
            _used_names.add(n)
            return n


EMPLOYERS = [f"{rng.choice(PRE)} {rng.choice(['Consulting', 'Services', 'Technologies', 'Group', 'Systems', 'Software'])}"
             for _ in range(70)]
EMPLOYERS = sorted(set(EMPLOYERS))


def listing(items):
    items = list(items)
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


# ------------------------------------------------------------------ jobs
def make_job(jid, fam, level, focus):
    P = POOLS[fam]
    flabel, boost, dom = focus
    target = rng.randint(5, 7) if level == 0 else (rng.randint(7, 9) if level == 3 else rng.randint(6, 8))
    keep = sorted(rng.sample(P["must"], rng.choice([2, 3, 3])), key=P["must"].index)
    req = []
    for s in keep + boost[:3]:
        if s not in req:
            req.append(s)
    for pool, stop in ((rng.sample(P["core"], len(P["core"])), target - 1), (rng.sample(P["common"], len(P["common"])), target)):
        for s in pool:
            if len(req) >= stop:
                break
            if s not in req:
                req.append(s)
    if level == 3 and SENIOR_EXTRA[fam]:
        for s in rng.sample(SENIOR_EXTRA[fam], rng.choice([1, 2]) if len(SENIOR_EXTRA[fam]) > 1 else 1):
            if s not in req:
                req.append(s)
    for base in ("Python", "SQL"):
        if base not in req and any(base in closure([s]) for s in req):
            req.insert(min(len(req), 2), base)
    allpool = [s for s in P["core"] + P["common"] if s not in req]
    pref = rng.sample(allpool, min(len(allpool), rng.randint(2, 4)))
    if level == 3:
        pref += [s for s in SENIOR_EXTRA[fam] if s not in req and s not in pref][:1]
    min_years = {0: 0, 1: rng.choice([0, 1, 1, 2]), 2: rng.choice([3, 3, 4]), 3: rng.choice([5, 5, 6, 7, 8])}[level]

    # title
    base = FAMILIES[fam]
    if fam == "INT":
        title = {"General AI/ML": "AI/ML Intern", "NLP": "NLP Research Intern", "Computer Vision": "Computer Vision Intern",
                 "Data Science": "Data Science Intern", "Applied ML": "Machine Learning Intern"}[flabel]
        if rng.random() < .4:
            title += rng.choice([" - 6 Months", " (Summer)", " (Winter)"])
    else:
        prefix = {1: rng.choice(["Junior ", "Associate ", "Junior "]), 2: "", 3: rng.choice(["Senior ", "Senior ", "Lead "])}[level]
        title = prefix + base
        if rng.random() < .55:
            title += f" - {flabel}"

    comp = company()
    ind = rng.choice(INDUSTRIES)
    size = rng.choice(SIZES)
    intro = rng.choice([
        f"{comp} is a {size} {ind} company that builds {rng.choice(PRODUCTS)}.",
        f"At {comp}, a {size} {ind} business, data and technology sit at the center of how we work.",
        f"{comp} is growing its {base.lower()} function. We are a {size} {ind} company with a collaborative, low-ego culture."])
    hire = f"We are hiring a {title} to join the team."
    resp_pool = RESP[fam]
    nresp = 3 if level == 0 else rng.choice([4, 4, 5])
    resp = [r.format(ind=ind) for r in rng.sample(resp_pool, min(nresp, len(resp_pool)))]
    resp_txt = rng.choice(["In this role you will: ", "Your responsibilities include: ", "Day to day you will: "]) + "; ".join(r[0].lower() + r[1:] for r in resp) + "."
    focus_txt = rng.choice([f"The team's current focus area is {flabel.lower()}.", f"You will work mainly on {flabel.lower()} initiatives.", ""])
    r3, rest = req[:3], req[3:]
    style = rng.randint(0, 3)
    if style == 0:
        req_txt = f"Required skills: {', '.join(req)}."
    elif style == 1:
        req_txt = f"You bring hands-on experience with {listing(r3)}" + (f", plus working knowledge of {listing(rest)}." if rest else ".")
    elif style == 2:
        req_txt = f"Must-have qualifications include {listing(req)}."
    else:
        req_txt = f"The ideal candidate is comfortable with {listing(req)}."
    if level == 0:
        exp_txt = rng.choice(["This role is open to current students and recent graduates; prior internships are a plus.",
                              "Ideal for final-year students or fresh graduates with academic or personal projects."])
    elif min_years == 0:
        exp_txt = "Fresh graduates with strong project work are welcome to apply."
    else:
        exp_txt = f"We expect {min_years}+ years of relevant professional experience."
    if level == 3:
        exp_txt += " You will mentor teammates and own projects end to end."
    pref_txt = f"Nice to have: {', '.join(pref)}." if pref else ""
    close = rng.choice(["We offer flexible working hours, learning support and a transparent growth path.",
                        "You will work closely with a small, supportive team and see your work reach users quickly.",
                        "We value clear communication, curiosity and ownership."])
    desc = " ".join(x for x in [intro, hire, resp_txt, focus_txt, req_txt, exp_txt, pref_txt, close] if x)
    return dict(job_id=jid, job_title=title, job_family=base, fam=fam, domain_focus=flabel, dom=dom, company_name=comp,
                industry=ind, location=rng.choice(CITIES), work_mode=rng.choice(["Onsite", "Hybrid", "Remote"]),
                employment_type="Internship" if level == 0 else rng.choice(["Full-time"] * 9 + ["Contract"]),
                level=level, experience_level=LEVELS[level], min_years_experience=min_years, req=req,
                required_skills="; ".join(req), preferred_skills="; ".join(pref), job_description=desc)


def build_jobs():
    jobs = []
    n = 0
    for fam in KEYS:
        levels = [0] * 10 if fam == "INT" else [1, 1, 1, 2, 2, 2, 2, 3, 3, 3]
        rng.shuffle(levels)
        foci = FOCI[fam]
        order = [foci[i % len(foci)] for i in range(10)]
        rng.shuffle(order)
        for lv, fo in zip(levels, order):
            n += 1
            jobs.append(make_job(f"J{n:03d}", fam, lv, fo))
    return jobs


# ------------------------------------------------------------------ resumes
TPL_BY_FAM = defaultdict(list)
for t in TEMPLATES:
    TPL_BY_FAM[t[0]].append(t)
TPL_BY_FAM["INT"] = TPL_BY_FAM["DS"] + TPL_BY_FAM["NLP"] + TPL_BY_FAM["CV"]
STUDENT_TPL = [t for t in TEMPLATES if t[1] in ("House Price Prediction", "Exploratory Data Analysis Notebook",
                                                "Deep Learning Digit Classifier", "Tweet Sentiment Baseline",
                                                "Image Classifier Mini-project")]
NOUN = {"DA": "data analyst", "DS": "data scientist", "MLE": "machine learning engineer", "NLP": "NLP engineer",
        "CV": "computer vision engineer", "BE": "Python backend developer", "DE": "data engineer",
        "BA": "business analyst", "DV": "data visualization specialist", "INT": "AI/ML practitioner"}
FOCUS_PHRASE = {"DA": "turning business data into actionable reporting", "DS": "building and validating predictive models",
                "MLE": "deploying and operating machine learning systems", "NLP": "building language-understanding systems",
                "CV": "building image and video understanding models", "BE": "building reliable Python services and APIs",
                "DE": "building dependable data pipelines", "BA": "bridging business needs and delivery teams",
                "DV": "designing clear dashboards and data stories", "INT": "machine learning and AI"}
INST_A = ["Ashgrove", "Bellmont", "Cedarfield", "Dunross", "Eastvale", "Fairhaven", "Glenmoor", "Highcrest", "Ivydale",
          "Kingsmere", "Lakeshore", "Meridian Hills", "Northgate", "Oakridge", "Pinecrest", "Quarry Hill", "Ridgeway",
          "Stonebridge", "Thornfield", "Westbrook"]
INST_B = ["Institute of Technology", "University", "College of Engineering", "School of Computing", "Institute of Management"]
BACH = {"tech": ["B.Tech in Computer Science and Engineering", "B.E. in Information Technology", "B.Sc in Computer Science",
                 "BCA", "B.Tech in Electronics and Communication", "B.Sc in Mathematics", "B.Sc in Statistics"],
        "BA": ["BBA", "B.Com", "B.Tech in Information Technology", "B.A. in Economics", "B.Sc in Statistics"],
        "DV": ["B.Sc in Statistics", "BCA", "B.Sc in Computer Science", "B.A. in Economics", "B.Des in Communication Design"],
        "other": ["B.Com", "BBA", "B.A. in Economics", "B.Sc in Physics", "B.Tech in Mechanical Engineering", "B.Sc in Chemistry"]}
MAST = {"tech": ["M.Sc in Data Science", "M.Tech in Artificial Intelligence", "MCA", "M.Sc in Statistics",
                 "MS in Computer Science", "M.Tech in Computer Science", "M.Sc in Applied Mathematics"],
        "BA": ["MBA in Business Analytics", "MBA in Operations", "MBA in Finance"],
        "DV": ["M.Sc in Statistics", "MS in Information Design"]}
MAST_P = {"DS": .35, "NLP": .35, "CV": .35, "MLE": .3, "DA": .2, "DE": .2, "BE": .15, "BA": .3, "DV": .15, "INT": .15}
CERTS = {"DA": ["Online certificate in data analytics", "Certificate in advanced spreadsheet reporting"],
         "DS": ["Online specialization in machine learning", "Certificate in statistical inference"],
         "MLE": ["Cloud practitioner certificate", "Certificate in MLOps fundamentals"],
         "NLP": ["Online specialization in natural language processing", "Certificate in applied deep learning"],
         "CV": ["Online specialization in computer vision", "Certificate in applied deep learning"],
         "BE": ["Cloud practitioner certificate", "Certificate in backend web development"],
         "DE": ["Cloud data engineering certificate", "Certificate in data warehousing"],
         "BA": ["Agile practitioner certificate", "Business analysis foundation certificate"],
         "DV": ["Online certificate in data visualization", "Certificate in business intelligence reporting"],
         "INT": ["Online specialization in machine learning", "Certificate in Python programming"]}


def fill(tpl, skillset):
    _, name, text, slots = tpl[:4]
    picks = []
    for opts in slots:
        avail = [s for s in opts if s in skillset and s not in picks]
        if not avail:
            return None
        picks.append(rng.choice(avail))
    nums = dict(k=rng.choice([8, 12, 20, 35, 50, 80, 120]), p=rng.randint(8, 38), n=rng.randint(3, 12),
                h=rng.choice([6, 8, 10, 12, 15, 20]), q=rng.randint(52, 74), r=rng.randint(82, 96), a=rng.randint(78, 93))
    return name, text.format(*picks, **nums), picks


def draw(items, weights):
    return rng.choices(items, weights=weights)[0]


def draw_years(arch, fam):
    if arch == "student":
        return rng.choice([0, 0, 0.5])
    if fam == "INT" or arch == "stuffer":
        return rng.choice([0, 0, 0.5, 0.5, 1, 1.5]) if fam == "INT" else rng.choice([0, 0.5, 1, 1.5])
    if arch == "strong":
        return draw([1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10], [5, 5, 12, 8, 12, 14, 14, 10, 8, 7, 5])
    if arch == "moderate":
        return draw([0.5, 1, 1.5, 2, 3, 4, 5, 7], [8, 12, 10, 17, 20, 13, 12, 8])
    if arch == "adjacent":
        return draw([1.5, 2, 3, 4, 5, 6, 8], [10, 15, 20, 20, 15, 10, 10])
    return 0


def pick_skills(fam, arch, sec):
    P = POOLS[fam]
    pr = {"strong": (.97, .8, .55), "moderate": (.85, .55, .3), "adjacent": (.92, .68, .4), "student": (.9, .5, .25),
          "stuffer": (.92, .88, .8), "switcher": (.55, .3, .1)}[arch]
    chosen = []
    for lst, p in ((P["must"], pr[0]), (P["core"], pr[1]), (P["common"], pr[2])):
        chosen += [s for s in lst if rng.random() < p]
    if arch == "adjacent" and sec:
        S = POOLS[sec]
        for lst, p in ((S["must"], .8), (S["core"], .5), (S["common"], .25)):
            chosen += [s for s in lst if rng.random() < p and s not in chosen]
    if arch == "stuffer":
        for f2 in rng.sample([k for k in KEYS if AFF.get((fam, k), 0) >= .45 and k != "INT"] or ["DS"], 2):
            S = POOLS[f2]
            chosen += [s for s in rng.sample(S["core"] + S["common"], 5) if s not in chosen]
    if arch == "switcher":
        chosen += rng.sample(["Excel", "SQL", "Data Analysis", "Data Cleaning"], rng.randint(1, 3))
        if fam in ("DS", "MLE", "NLP", "CV", "INT", "DE", "BE"):
            chosen.append("Python")
    if not chosen:
        chosen = [P["must"][0]]
    for members, p in EXCLUSIVE:
        present = [s for s in chosen if s in members]
        if len(present) > 1:
            keep = rng.sample(present, 2 if (rng.random() < p and len(present) > 1) else 1)
            chosen = [s for s in chosen if s not in members or s in keep]
    return list(dict.fromkeys(chosen))


def split_years(y, n):
    units = int(round(y * 2))
    n = max(1, min(n, units))
    if n == 1:
        return [y]
    cuts = sorted(rng.sample(range(1, units), n - 1))
    pts = [0] + cuts + [units]
    return [(pts[i + 1] - pts[i]) / 2 for i in range(n)]


def make_role(fam, years, cum_end, skillset, used, arch, is_current, generic=False):
    emp = rng.choice(EMPLOYERS)
    if fam == "OTHER":
        title = rng.choice(OTHER_TITLES)
        bullets = [b.format(n=rng.randint(3, 15)) for b in rng.sample(OTHER_BULLETS, rng.randint(2, 3))]
        return dict(fam=fam, years=years, title=title, employer=emp, bullets=bullets, used_skills=[])
    tier = 0 if cum_end <= 2.5 else (1 if cum_end <= 5.5 else 2)
    if years <= 0.5:
        title = INTERN_TITLES[fam]
    else:
        title = rng.choice(ROLE_TITLES[fam][tier])
    nb = 2 if years < 1.5 else (3 if years < 5 else 4)
    bullets, used_sk = [], []
    if generic:
        bullets = rng.sample(GENERIC_BULLETS, 2)
    else:
        pool = TPL_BY_FAM[fam][:]
        rng.shuffle(pool)
        if tier == 2 and is_current:
            for sk, txt in SENIOR_TEMPLATES:
                if sk in skillset and rng.random() < .65:
                    bullets.append(txt.format(n=rng.randint(2, 6)))
                    used_sk.append(sk)
        for t in pool:
            if len(bullets) >= nb:
                break
            if t[1] in used:
                continue
            r = fill(t, skillset)
            if r:
                used.add(t[1])
                bullets.append(r[1])
                used_sk += r[2]
        while len(bullets) < 2:
            bullets.append(rng.choice([b for b in GENERIC_BULLETS if b not in bullets]))
    return dict(fam=fam, years=years, title=title, employer=emp, bullets=bullets, used_skills=used_sk)


def build_resume(rid, fam, arch):
    sec = None
    if arch == "adjacent":
        cands = [k for k in KEYS if k not in (fam, "INT") and AFF.get((fam, k), 0) >= .5]
        sec = rng.choice(cands or ["DS"])
    chosen = pick_skills(fam, arch, sec)
    # senior flavour
    other_years = 0
    if arch == "switcher":
        other_years = rng.choice([2, 3, 4, 5, 6, 8])
        years = rng.choice([0, 0, 0.5, 1])
    else:
        years = draw_years(arch, fam)
    if years >= 4.5 and arch not in ("stuffer",) and rng.random() < .5:
        chosen.append("Mentoring")
    if years >= 4 and fam in ("MLE", "BE", "DE", "NLP", "CV") and rng.random() < .5 and arch != "stuffer":
        chosen.append("System Design")
    chosen = list(dict.fromkeys(chosen))
    have = closure(chosen)
    skills_all = chosen + [s for s in sorted(have) if s not in chosen]
    used = set()
    roles = []
    # role sequence
    seq = []
    if arch == "switcher":
        for y in split_years(other_years, 2 if other_years >= 4 else 1):
            seq.append(("OTHER", y))
        if years > 0:
            seq.append((fam, years))
    elif years > 0:
        n = 1 if years < 2.5 else (2 if years < 6 else rng.choice([2, 3]))
        parts = split_years(years, n)
        fams = [fam] * len(parts)
        if len(parts) > 1:
            if arch == "adjacent":
                fams[0] = sec
            elif rng.random() < .55:
                fams[0] = rng.choice(PATHS[fam])
        seq = list(zip(fams, parts))
    cum = 0
    tech_cum = 0
    for i, (f, y) in enumerate(seq):
        cum += y
        if f != "OTHER":
            tech_cum += y
        roles.append(make_role(f, y, tech_cum if f != "OTHER" else cum, have, used, arch, i == len(seq) - 1,
                               generic=(arch == "stuffer")))
    # projects
    projects = []
    pf = []
    if arch == "strong":
        pf = [fam] * 3
    elif arch == "moderate":
        pf = [fam] * 2
    elif arch == "adjacent":
        pf = [fam, fam, sec]
    elif arch == "student":
        pf = [fam, fam, "STU"] if fam != "INT" else ["INT", "INT", "STU"]
    elif arch == "switcher":
        pf = [fam] * rng.choice([1, 2])
    ev_skills = []
    for f in pf:
        pool = (STUDENT_TPL if f == "STU" else TPL_BY_FAM[f])[:]
        rng.shuffle(pool)
        done = False
        for t in pool + ([] if f == "STU" else STUDENT_TPL):
            if t[1] in used:
                continue
            r = fill(t, have)
            if r:
                used.add(t[1])
                projects.append(dict(fam=t[0], name=r[0], text=r[1]))
                ev_skills += r[2]
                done = True
                break
        if not done and (arch == "switcher" or rng.random() < .7):
            projects.append(dict(fam=fam if arch == "switcher" else None, name="Self-study Project", text="Completed guided coursework and a small capstone exercise to practise fundamentals"))
    if arch == "stuffer":
        projects = [dict(fam=fam, name="Online Coursework",
                         text=rng.choice(["Completed online courses and guided tutorials covering several tools listed below",
                                          "Followed tutorials and a capstone walkthrough to get familiar with the tools listed below"]))]
    for r in roles:
        ev_skills += r["used_skills"]
    evidence = closure(ev_skills)
    total_years = years + other_years
    return dict(rid=rid, fam=fam, arch=arch, sec=sec, chosen=chosen, skills=skills_all, have=have, roles=roles,
                projects=projects, evidence=evidence, years=total_years, tech_years=years, other_years=other_years)


def years_str(y):
    if y < 1:
        return "under a year"
    return f"{int(y)}+ years" if (y >= 5 and y == int(y)) else f"{y:g} years"


def education(res):
    fam, arch = res["fam"], res["arch"]
    career = res["years"]
    student_like = arch == "student" or (fam == "INT" and arch != "switcher")
    kind = "tech" if arch != "switcher" else "other"
    if fam == "BA" and arch != "switcher":
        kind = "BA"
    if fam == "DV" and arch != "switcher":
        kind = "DV"
    inst = lambda: f"{rng.choice(INST_A)} {rng.choice(INST_B)}"
    cg = lambda: f", CGPA {rng.uniform(6.6, 9.4):.1f}/10" if rng.random() < .5 else ""
    master = arch != "switcher" and rng.random() < MAST_P[fam] and kind in MAST
    if student_like and rng.random() < .65:
        exp = rng.choice([2027, 2027, 2028])
        if master:
            deg = rng.choice(MAST[kind])
            bach = rng.choice(BACH[kind])
            return [f"{deg}, {inst()} (expected {exp}){cg()}", f"{bach}, {inst()} ({exp-5}-{exp-2})"], "Pursuing Master's"
        return [f"{rng.choice(BACH[kind])}, {inst()} (expected {exp}){cg()}"], "Pursuing Bachelor's"
    end = int(2026 - math.floor(career) - rng.choice([0, 0, 1])) if not student_like else rng.choice([2025, 2026])
    end = min(end, 2026)
    if master:
        return [f"{rng.choice(MAST[kind])}, {inst()} ({end-2}-{end}){cg()}",
                f"{rng.choice(BACH[kind])}, {inst()} ({end-6}-{end-2})"], "Master's"
    return [f"{rng.choice(BACH[kind])}, {inst()} ({end-4}-{end}){cg()}"], "Bachelor's"


def summary(res):
    fam, arch, y = res["fam"], res["arch"], res["years"]
    noun = NOUN[fam]
    prim = [s for s in res["chosen"] if s in POOLS[fam]["must"] + POOLS[fam]["core"] + POOLS[fam]["common"]]
    top = prim[:] if len(prim) >= 3 else res["chosen"][:]
    rng.shuffle(top)
    s1, s2, s3 = (top + top + top)[:3]
    fp = FOCUS_PHRASE[fam]
    ys = years_str(res["tech_years"] if arch == "switcher" else y)
    if arch == "student":
        return rng.choice([
            f"Computer science student interested in {fp}. Completed {len(res['projects'])} hands-on projects using {s1}, {s2} and {s3}; looking for an opportunity to apply them in a real team.",
            f"Final-year undergraduate focused on {fp}, with project work in {s1} and {s2}. Quick learner who enjoys documenting experiments.",
            f"Early-career candidate seeking hands-on exposure to {fp}. Comfortable with {s1} and {s3} from academic and personal projects."])
    if arch == "stuffer":
        return rng.choice([
            "Passionate and results-driven professional with broad exposure to analytics, machine learning, cloud and modern data tools. Fast learner and team player.",
            "Dynamic, detail-oriented technologist eager to leverage a wide toolkit across data, AI and engineering roles. Strong communicator with a growth mindset."])
    if arch == "switcher":
        oth = next((r["title"] for r in res["roles"] if r["fam"] == "OTHER"), "operations professional")
        return rng.choice([
            f"Former {oth.lower()} with {res['other_years']} years of business experience, now moving into {noun} work. Completed self-driven projects using {s1} and {s2}.",
            f"Career changer from operations into {fp}. Brings {res['other_years']} years of domain experience and growing skills in {s1} and {s2}."])
    base = rng.choice([
        f"{noun.capitalize()} with {ys} of experience in {fp}. Works regularly with {s1}, {s2} and {s3}.",
        f"Results-oriented {noun} ({ys}) focused on {fp}; hands-on with {s1} and {s2}.",
        f"{ys.capitalize()} as a {noun}, {fp}. Toolbox includes {s1}, {s2} and {s3}.",
        f"Pragmatic {noun} who enjoys {fp}. {ys.capitalize()} of professional experience; strongest with {s1} and {s2}."])
    if arch == "adjacent":
        base += f" Transitioned from {NOUN[res['sec']]} responsibilities into broader {noun} work."
    return base


def role_dates(res):
    roles = res["roles"]
    total = sum(r["years"] for r in roles)
    t = 2026 - total
    out = []
    for i, r in enumerate(roles):
        s = int(round(t))
        t += r["years"]
        e = int(round(t))
        if r["years"] <= 0.5:
            out.append(f"{max(s, e)} ({int(r['years']*12)}-month stint)")
        else:
            out.append(f"{s}-{'Present' if i == len(roles) - 1 else e}")
    return out


def compose(res):
    summ = summary(res)
    edu, edu_level = education(res)
    dates = role_dates(res)
    exp_items = [f"{r['title']}, {r['employer']} ({d}): " + "; ".join(r["bullets"]) for r, d in zip(res["roles"], dates)]
    proj_items = [f"{p['name']} - {p['text']}" for p in res["projects"]]
    sk = res["skills"][:]
    if rng.random() < .6:
        rng.shuffle(sk)
    cert = [rng.choice(CERTS[res["fam"]])] if rng.random() < .35 else []
    student_like = res["arch"] == "student" or (res["fam"] == "INT" and res["arch"] != "switcher")
    layout = rng.choice([2, 2, 1, 4]) if student_like else rng.choice([1, 1, 3, 4, 4])
    E = " || ".join(exp_items) if exp_items else "No full-time experience yet; seeking first role"
    P = " || ".join(proj_items) if proj_items else "Coursework-based assignments"
    cert_txt = f" | CERTIFICATIONS: {'; '.join(cert)}" if cert else ""
    if layout == 1:
        text = f"SUMMARY: {summ} | TECHNICAL SKILLS: {', '.join(sk)} | EXPERIENCE: {E} | PROJECTS: {P} | EDUCATION: {'; '.join(edu)}{cert_txt}"
    elif layout == 2:
        text = f"OBJECTIVE: {summ} | EDUCATION: {'; '.join(edu)} | PROJECTS: {P} | SKILLS: {', '.join(sk)} | EXPERIENCE: {E}{cert_txt}"
    elif layout == 3:
        text = (f"Profile - {summ} Career history - {E}. Selected work - {P}. Day to day I work with {listing(sk)}. "
                f"Education - {'; '.join(edu)}.{(' Certifications - ' + '; '.join(cert) + '.') if cert else ''}")
    else:
        text = f"CORE COMPETENCIES: {' * '.join(sk)} | PROFILE: {summ} | CAREER HISTORY: {E} | KEY PROJECTS: {P} | ACADEMIC BACKGROUND: {'; '.join(edu)}{cert_txt}"
    res["text"] = text
    res["edu_level"] = edu_level
    return res


def build_resumes():
    res = []
    n = 0
    for fam in KEYS:
        mix = (["strong"] * 6 + ["moderate"] * 6 + ["adjacent"] * 2 + ["stuffer"] * 3 + ["switcher"] * 3) if fam == "INT" else \
              (["strong"] * 7 + ["moderate"] * 5 + ["adjacent"] * 3 + ["student"] * 2 + ["stuffer"] * 1 + ["switcher"] * 2)
        rng.shuffle(mix)
        for arch in mix:
            n += 1
            res.append(compose(build_resume(f"R{n:03d}", fam, arch)))
    return res


# ------------------------------------------------------------------ scoring
def skill_overlap(res, job):
    have = set(res["skills"])
    return round(sum(1 for s in job["req"] if s in have) / len(job["req"]), 3)


def score_pair(res, job):
    have, ev = res["have"], res["evidence"]
    W = c_sum = e_sum = 0.0
    for i, s in enumerate(job["req"]):
        w = 1.5 if i < 3 else 1.0
        c, m = credit(s, have)
        W += w
        c_sum += w * c
        if m is not None and m in ev:
            e_sum += w * c
    sm, es = c_sum / W, e_sum / W
    jd = job["dom"]
    roles = res["roles"]
    e_vals = [aff(r["fam"], jd) * min(1.0, (r["years"] / 1.0) ** 0.5) for r in roles]
    e = max(e_vals) if e_vals else None
    p_vals = sorted((aff(p["fam"], jd) for p in res["projects"]), reverse=True)
    p = (0.65 * p_vals[0] + 0.35 * (p_vals[1] if len(p_vals) > 1 else 0)) if p_vals else 0.0
    if e is None:
        dom = 0.85 * p
    else:
        dom = 0.6 * max(e, p) + 0.4 * min(e, p)
    eff = sum(r["years"] * min(1.0, aff(r["fam"], jd) / 0.6) for r in roles)
    m_y, lv = job["min_years_experience"], job["level"]
    gap = m_y - eff
    if lv == 0:
        ef = 1.0 if eff <= 1 else .75 if eff <= 2 else .45 if eff <= 3.5 else .15
    elif gap > 0:
        ef = max(0.0, 1 - 0.28 * gap)
    else:
        over = eff - m_y
        ef = (0.55 if over >= 6 else 0.75 if over >= 4 else 1.0) if lv == 1 else (0.7 if over >= 8 and lv == 2 else 1.0)
    overall = 0.35 * sm + 0.20 * es + 0.25 * dom + 0.20 * ef
    rule = "score_threshold"
    if ef < .2 or sm < .2 or dom < .2:
        label, rule = 0, "hard_floor(experience/skill/domain)"
    else:
        label = 2 if overall >= T2 else 1 if overall >= T1 else 0
        if label == 2 and not (sm >= .65 and dom >= .55 and ef >= .6 and es >= .3):
            label, rule = 1, "cap_at_1(gate for label 2 not met)"
    return dict(skill_match=round(sm, 3), evidence_score=round(es, 3), domain_alignment=round(dom, 3),
                experience_fit=round(ef, 3), overall_score=round(overall, 3), label=label, rule=rule)


def sample_pairs(resumes, jobs, matrix):
    cnt = Counter()
    pairs = []
    order = resumes[:]
    rng.shuffle(order)
    for r in order:
        by = {0: [], 1: [], 2: []}
        for j in jobs:
            by[matrix[(r["rid"], j["job_id"])]["label"]].append(j)
        n2 = rng.choice([2, 3, 3, 3, 4]); n1 = rng.choice([3, 3, 4]); n0 = PAIRS_PER_RESUME - n2 - n1
        want = {2: n2, 1: n1, 0: n0}
        chosen = []
        deficit = 0

        def take(label, k):
            cands = [j for j in by[label] if cnt[j["job_id"]] < JOB_CAP and j not in chosen]
            got = []
            for _ in range(min(k, len(cands))):
                ov = [skill_overlap(r, j) for j in cands]
                if label == 2:
                    w = [1.0 + 2 * (1 - o) for o in ov]
                elif label == 0:
                    w = [0.4 + 3 * o for o in ov]
                else:
                    w = [1.0] * len(cands)
                i = rng.choices(range(len(cands)), weights=w)[0]
                got.append(cands[i]); cands.pop(i)
            for j in got:
                chosen.append(j); cnt[j["job_id"]] += 1
            return k - len(got)
        d2 = take(2, want[2]); d1 = take(1, want[1] + d2); d0 = take(0, want[0] + d1)
        if d0:
            for lab in (1, 2):
                d0 = take(lab, d0)
                if not d0:
                    break
        for j in chosen:
            pairs.append((r, j))
    rng.shuffle(pairs)
    return pairs


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main():
    jobs = build_jobs()
    resumes = build_resumes()
    matrix = {(r["rid"], j["job_id"]): score_pair(r, j) for r in resumes for j in jobs}
    lc = Counter(v["label"] for v in matrix.values())
    print("full-matrix label counts:", dict(lc))
    pairs = sample_pairs(resumes, jobs, matrix)
    jh = ["job_id", "job_title", "job_family", "domain_focus", "company_name", "industry", "location", "work_mode",
          "employment_type", "experience_level", "min_years_experience", "required_skills", "preferred_skills", "job_description"]
    write_csv(f"{OUT}/jobs.csv", jh, [[j[c] for c in jh] for j in jobs])
    rh = ["resume_id", "primary_domain", "years_experience", "education_level", "skills", "resume_text"]
    write_csv(f"{OUT}/resumes.csv", rh, [[r["rid"], FAMILIES[r["fam"]], r["years"], r["edu_level"], "; ".join(r["skills"]), r["text"]] for r in resumes])
    ph = ["resume_id", "job_id", "resume_text", "job_title", "job_description", "required_skills", "experience_level",
          "skill_overlap", "relevance_label"]
    prow, arow = [], []
    for r, j in pairs:
        s = matrix[(r["rid"], j["job_id"])]
        ov = skill_overlap(r, j)
        prow.append([r["rid"], j["job_id"], r["text"], j["job_title"], j["job_description"], j["required_skills"],
                     j["experience_level"], ov, s["label"]])
        a = aff(r["fam"], j["dom"])
        ptype = "same_domain" if r["fam"] == j["fam"] or r["fam"] == j["dom"] else ("adjacent_domain" if a >= .45 else "distant_domain")
        arow.append([r["rid"], j["job_id"], r["arch"], FAMILIES[r["fam"]], j["job_family"], ptype, ov, s["skill_match"],
                     s["evidence_score"], s["domain_alignment"], s["experience_fit"], s["overall_score"], s["label"], s["rule"]])
    write_csv(f"{OUT}/training_pairs.csv", ph, prow)
    ah = ["resume_id", "job_id", "resume_archetype", "resume_primary_domain", "job_family", "pair_type", "skill_overlap",
          "skill_match", "evidence_score", "domain_alignment", "experience_fit", "overall_score", "relevance_label", "rule_applied"]
    write_csv(f"{OUT}/pair_label_audit.csv", ah, arow)
    print("pair label counts:", dict(Counter(p[8] for p in prow)))


if __name__ == "__main__":
    main()
