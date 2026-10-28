def analyze_skill_gap(candidate_skills, required_skills):

    candidate_skills = set(candidate_skills)
    required_skills = set(required_skills)

    matched_skills = candidate_skills.intersection(required_skills)

    missing_skills = required_skills - candidate_skills

    return matched_skills, missing_skills