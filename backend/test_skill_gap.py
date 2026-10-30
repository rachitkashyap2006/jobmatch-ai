from skill_gap import analyze_skill_gap, match_required_skills


def test_skill_gap_distinguishes_exact_partial_and_missing():
    matched, missing = analyze_skill_gap(
        ["Python", "Power BI"],
        ["Python", "Tableau", "NLP"],
    )
    detailed = match_required_skills(
        ["Python", "Power BI"],
        ["Python", "Tableau", "NLP"],
    )

    assert matched == {"Python"}
    assert missing == {"NLP"}
    assert detailed[1][0]["required_skill"] == "Tableau"
    assert detailed[1][0]["candidate_skill"] == "Power BI"


def test_distinct_frameworks_are_not_exact_matches():
    matched, partial, missing = match_required_skills(
        ["TensorFlow"], ["PyTorch"]
    )

    assert matched == []
    assert partial[0]["required_skill"] == "PyTorch"
    assert missing == []
