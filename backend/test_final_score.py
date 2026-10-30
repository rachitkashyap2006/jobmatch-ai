from matcher import calculate_final_score


def test_final_score_uses_skill_and_semantic_weights():
    assert calculate_final_score(80, 60) == 72


def test_final_score_handles_zero_scores():
    assert calculate_final_score(0, 0) == 0
