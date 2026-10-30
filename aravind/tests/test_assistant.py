"""
Tests for AI Chemistry Assistant and Expert Knowledge Fallback
"""

import pytest
from chem_engine.assistant import ask_chemistry_assistant
from chem_engine.properties import calculate_properties


def test_assistant_functional_groups():
    """Verify functional groups explanation."""
    smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    ctx = {
        "name": "Aspirin",
        "smiles": smiles,
        "properties": calculate_properties(smiles),
    }
    response = ask_chemistry_assistant("What functional groups are present?", ctx)
    assert "Functional Group" in response
    assert "Carboxylic acid" in response or "Ester" in response
    assert "Scientific Disclaimer" in response


def test_assistant_logp():
    """Verify LogP interpretation."""
    smiles = "CCO"  # Ethanol
    ctx = {
        "name": "Ethanol",
        "smiles": smiles,
        "properties": calculate_properties(smiles),
    }
    response = ask_chemistry_assistant("What does the LogP value mean?", ctx)
    assert "LogP" in response
    assert "partition coefficient" in response.lower()
    assert "Scientific Disclaimer" in response


def test_assistant_compare_aspirin_paracetamol():
    """Verify comparative response for aspirin and paracetamol."""
    response = ask_chemistry_assistant("Compare aspirin and paracetamol.")
    assert "Aspirin" in response
    assert "Paracetamol" in response
    assert "COX" in response or "cyclooxygenase" in response.lower()
    assert "Scientific Disclaimer" in response


def test_assistant_empty_query():
    """Verify handling of empty query."""
    response = ask_chemistry_assistant("   ")
    assert "Please ask a specific chemistry question" in response
