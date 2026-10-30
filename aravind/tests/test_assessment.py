"""
Tests for Assessment and Examination Module
"""

import pytest
from chem_engine.assessment import get_assessment_questions, evaluate_assessment


def test_assessment_tiers():
    """Verify questions for Beginner, Intermediate, and Advanced tiers."""
    for tier in ["Beginner", "Intermediate", "Advanced"]:
        qs = get_assessment_questions(tier)
        assert len(qs) == 5, f"Tier {tier} should have 5 questions"
        for q in qs:
            assert len(q["options"]) == 4
            assert 0 <= q["correct_index"] < 4
            assert q["explanation"] != ""


def test_assessment_scoring_perfect():
    """Verify 100% score evaluation."""
    qs = get_assessment_questions("Beginner")
    answers = {q["id"]: q["correct_index"] for q in qs}
    result = evaluate_assessment("Beginner", answers)
    assert result["score_percentage"] == 100.0
    assert result["correct_count"] == 5
    assert result["grade"] == "Distinction (Mastery)"


def test_assessment_scoring_zero():
    """Verify 0% score evaluation with wrong answers."""
    qs = get_assessment_questions("Beginner")
    answers = {q["id"]: (q["correct_index"] + 1) % 4 for q in qs}
    result = evaluate_assessment("Beginner", answers)
    assert result["score_percentage"] == 0.0
    assert result["correct_count"] == 0
    assert result["grade"] == "Needs Review"
