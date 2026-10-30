"""
Tests for Molecular Property Calculations, Lipinski Rule of 5, Veber, and Fingerprints
"""

import pytest
from chem_engine.properties import (
    calculate_properties,
    check_lipinski_rule_of_five,
    check_veber_rules,
    calculate_elemental_composition,
    generate_fingerprints,
)


def test_aspirin_properties():
    """Verify calculated properties for Aspirin (CC(=O)Oc1ccccc1C(=O)O)."""
    aspirin_smiles = "CC(=O)Oc1ccccc1C(=O)O"
    props = calculate_properties(aspirin_smiles)

    assert props["formula"] == "C9H8O4"
    assert round(props["molecular_weight"], 1) == 180.2
    assert props["heavy_atom_count"] == 13
    assert props["total_atom_count"] == 21  # 9 C, 8 H, 4 O
    assert props["hbd"] == 1  # Carboxylic acid OH
    assert props["hba"] == 3  # Ester and carboxylic oxygens
    assert props["rotatable_bonds"] == 2
    assert props["ring_count"] == 1
    assert props["aromatic_rings"] == 1
    assert round(props["tpsa"], 1) == 63.6
    assert props["formal_charge"] == 0

    # Functional groups
    fg = props["functional_groups"]
    assert "Carboxylic acid" in fg
    assert "Ester" in fg


def test_lipinski_rule_of_five_compliance():
    """Verify Lipinski compliance for Aspirin and Caffeine."""
    aspirin_props = calculate_properties("CC(=O)Oc1ccccc1C(=O)O")
    lip = check_lipinski_rule_of_five(aspirin_props)

    assert lip["is_compliant"] is True
    assert lip["violation_count"] == 0
    assert "disclaimer" in lip
    assert "screening heuristic" in lip["disclaimer"].lower()


def test_veber_rules_compliance():
    """Verify Veber rules evaluation."""
    caffeine_props = calculate_properties("Cn1c(=O)c2c(ncn2C)n(C)c1=O")
    veber = check_veber_rules(caffeine_props)

    assert veber["is_compliant"] is True
    assert veber["violation_count"] == 0
    assert "Rotatable Bonds <= 10" in veber["rules"]
    assert "TPSA <= 140 Å²" in veber["rules"]


def test_elemental_composition():
    """Verify elemental composition percentages summing to ~100%."""
    comp = calculate_elemental_composition("CCO")  # Ethanol C2H6O
    assert "C" in comp and "H" in comp and "O" in comp
    total_pct = sum(comp.values())
    assert 99.5 <= total_pct <= 100.5


def test_fingerprints_generation():
    """Verify Morgan, MACCS, and Topological fingerprint generation."""
    fps = generate_fingerprints("c1ccccc1")  # Benzene
    assert fps["morgan"]["size"] == 2048
    assert fps["morgan"]["on_bits_count"] > 0
    assert fps["maccs"]["size"] == 166
    assert fps["maccs"]["on_bits_count"] > 0
    assert fps["rdkit_topological"]["size"] == 2048
