from recommendation_engine import recommend_skills


def test_learning_roadmap_prioritizes_required_gaps():
    items = recommend_skills(
        ["pandas", "SQL"],
        ["Python"],
        required_skills=["Python", "pandas", "SQL"],
    )

    assert [item["skill"] for item in items] == ["pandas", "SQL"]
    assert all(item["priority"] == 1 for item in items)
    assert items[0]["learning_path"]


def test_partially_matched_skill_gets_a_roadmap_item():
    items = recommend_skills(
        [],
        ["Power BI"],
        partially_matched=[{
            "required_skill": "Tableau",
            "candidate_skill": "Power BI",
            "transferability": 0.45,
        }],
        required_skills=["Tableau"],
    )

    assert items[0]["status"] == "partially_matched"
    assert items[0]["related_skill"] == "Power BI"
