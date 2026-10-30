"""
Tests for Multi-Molecule Comparison and Fingerprint Similarity
"""

import pytest
from chem_engine.comparison import compare_molecules, calculate_similarity_matrix


def test_compare_aspirin_and_paracetamol():
    """Verify comparison between Aspirin and Paracetamol."""
    mols = [
        {"name": "Aspirin", "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
        {"name": "Paracetamol", "smiles": "CC(=O)Nc1ccc(O)cc1"},
    ]
    comp = compare_molecules(mols)

    assert len(comp["molecules"]) == 2
    assert len(comp["pairwise"]) == 1

    p = comp["pairwise"][0]
    assert 0.0 <= p["tanimoto_morgan"] <= 1.0
    assert 0.0 <= p["dice_morgan"] <= 1.0

    # Self-similarity diagonal
    assert comp["tanimoto_matrix"][0][0] == 1.0
    assert comp["tanimoto_matrix"][1][1] == 1.0

    # Symmetric matrix
    assert comp["tanimoto_matrix"][0][1] == comp["tanimoto_matrix"][1][0]


def test_compare_three_molecules():
    """Verify 3-molecule comparison."""
    mols = [
        {"name": "Water", "smiles": "O"},
        {"name": "Methane", "smiles": "C"},
        {"name": "Ethanol", "smiles": "CCO"},
    ]
    comp = compare_molecules(mols)
    assert len(comp["molecules"]) == 3
    assert len(comp["tanimoto_matrix"]) == 3
    assert len(comp["pairwise"]) == 3  # (3 choose 2 = 3)


def test_compare_less_than_two():
    """Verify exception when fewer than 2 molecules provided."""
    with pytest.raises(ValueError):
        compare_molecules([{"name": "Water", "smiles": "O"}])
