def compare_skills(candidate_skills, required_skills):

    candidate_skills = set(candidate_skills)
    required_skills = set(required_skills)

    matched_skills = candidate_skills.intersection(required_skills)

    missing_skills = required_skills - candidate_skills

    if len(required_skills) > 0:
        skill_score = (
            len(matched_skills) / len(required_skills)
        ) * 100
    else:
        skill_score = 0

    return matched_skills, missing_skills, skill_score


def calculate_final_score(skill_score, semantic_score):

    final_score = (
        skill_score * 0.60
        + semantic_score * 0.40
    )

    return final_score