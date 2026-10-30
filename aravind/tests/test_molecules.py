"""
Tests for Predefined Chemical Library and SMILES Parsing & Validation
"""

import pytest
from chem_engine.molecules import (
    PREDEFINED_MOLECULES,
    list_predefined_molecules,
    get_predefined_molecule,
    parse_and_validate_smiles,
)


def test_predefined_molecules_count():
    """Verify all 10 predefined molecules are loaded."""
    mols = list_predefined_molecules()
    assert len(mols) == 10, f"Expected 10 predefined molecules, got {len(mols)}"


def test_predefined_molecules_names():
    """Verify exact presence of the 10 required molecules."""
    expected_names = [
        "Water", "Methane", "Ethanol", "Acetic acid", "Acetone",
        "Benzene", "Caffeine", "Aspirin", "Paracetamol", "Ibuprofen"
    ]
    for name in expected_names:
        mol = get_predefined_molecule(name)
        assert mol is not None, f"Molecule {name} not found in library"
        assert mol.smiles != "", f"Molecule {name} has empty SMILES"
        assert mol.molecular_weight > 0, f"Molecule {name} has invalid MW: {mol.molecular_weight}"
        assert mol.canonical_smiles != "", f"Molecule {name} has empty canonical SMILES"


def test_ibuprofen_stereochemistry():
    """Verify stereochemistry of Ibuprofen."""
    ibup = get_predefined_molecule("Ibuprofen")
    assert ibup is not None
    assert ibup.has_stereochemistry is True
    assert len(ibup.chiral_centers) >= 1


def test_custom_smiles_valid():
    """Test validation and property calculation for a valid custom SMILES."""
    smiles = "c1ccccc1O"  # Phenol
    mol_data, err = parse_and_validate_smiles(smiles, "Phenol")
    assert err is None
    assert mol_data is not None
    assert mol_data.name == "Phenol"
    assert mol_data.formula == "C6H6O"
    assert round(mol_data.molecular_weight, 1) == 94.1


def test_custom_smiles_invalid_syntax():
    """Verify rejection and clear diagnostic for invalid SMILES syntax."""
    invalid_smiles = "C1CC"  # Unclosed ring
    mol_data, err = parse_and_validate_smiles(invalid_smiles)
    assert mol_data is None
    assert err is not None
    assert "Invalid SMILES" in err or "ring" in err.lower()


def test_custom_smiles_invalid_valence():
    """Verify rejection of chemically invalid valence (e.g. 5-valent carbon)."""
    invalid_valence = "C(=O)(=O)(=O)O"  # Carbon with too many bonds
    mol_data, err = parse_and_validate_smiles(invalid_valence)
    assert mol_data is None
    assert err is not None
    assert "valence" in err.lower() or "error" in err.lower()


def test_empty_smiles():
    """Verify rejection of empty input."""
    mol_data, err = parse_and_validate_smiles("   ")
    assert mol_data is None
    assert "Empty" in err
