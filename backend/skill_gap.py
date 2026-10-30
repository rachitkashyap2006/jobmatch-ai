from skill_extractor import normalize_skill


# These are transferable, not equivalent: they can earn partial credit but stay
# visible as distinct skills in the profile and in the remaining gap.
TRANSFERABLE_SKILLS = {
    "Tableau": {"Power BI": 0.45, "Looker Studio": 0.4},
    "Power BI": {"Tableau": 0.45, "Looker Studio": 0.4},
    "Looker Studio": {"Tableau": 0.4, "Power BI": 0.4},
    "PyTorch": {"TensorFlow": 0.35},
    "TensorFlow": {"PyTorch": 0.35},
    "Excel": {"Google Sheets": 0.6},
    "Google Sheets": {"Excel": 0.6},
    "A/B Testing": {"Experiment Design": 0.55, "Hypothesis Testing": 0.35},
    "Experiment Design": {"A/B Testing": 0.55},
    "Hypothesis Testing": {"A/B Testing": 0.35},
}


def _normalized_set(skills):
    return {normalize_skill(skill) for skill in skills}


def match_required_skills(candidate_skills, required_skills):
    candidates = _normalized_set(candidate_skills)
    matched = []
    partially_matched = []
    missing = []

    for required in dict.fromkeys(normalize_skill(skill) for skill in required_skills):
        if required in candidates:
            matched.append(required)
            continue

        alternatives = TRANSFERABLE_SKILLS.get(required, {})
        possible = [
            (candidate, confidence)
            for candidate, confidence in alternatives.items()
            if candidate in candidates
        ]
        if possible:
            candidate, confidence = max(possible, key=lambda item: item[1])
            partially_matched.append({
                "required_skill": required,
                "candidate_skill": candidate,
                "transferability": confidence,
            })
        else:
            missing.append(required)

    return matched, partially_matched, missing


def analyze_skill_gap(candidate_skills, required_skills):
    matched, _, missing = match_required_skills(candidate_skills, required_skills)
    return set(matched), set(missing)
