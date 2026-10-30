"""
Tests for 3D Conformer Generation, MMFF94/UFF Optimization, and Geometric Analysis
"""

import pytest
from chem_engine.conformer import (
    generate_3d_conformer,
    extract_3d_coordinates,
    calculate_bond_distances,
)


def test_conformer_generation_ethanol():
    """Verify 3D conformer embedding and optimization for Ethanol."""
    conf = generate_3d_conformer("CCO")
    assert conf.atom_count == 9  # 2 C + 1 O + 6 H
    assert conf.heavy_atom_count == 3
    assert conf.force_field in ["MMFF94", "UFF"]
    assert conf.mol_block != ""
    assert conf.pdb_block != ""
    assert conf.xyz_block != ""
    assert "Computationally generated" in conf.disclaimer


def test_conformer_benzene_coordinates():
    """Verify coordinate extraction for Benzene."""
    conf = generate_3d_conformer("c1ccccc1")
    coords = extract_3d_coordinates(conf.rdkit_mol)
    assert len(coords) == 12  # 6 C + 6 H
    # Check that all coordinates are non-null floats
    for c in coords:
        assert isinstance(c["x"], float)
        assert isinstance(c["y"], float)
        assert isinstance(c["z"], float)
        assert c["symbol"] in ["C", "H"]


def test_bond_distances_water():
    """Verify bond distances for Water (H2O, O-H ~ 0.95 - 1.05 Å)."""
    conf = generate_3d_conformer("O")
    bonds = calculate_bond_distances(conf.rdkit_mol)
    assert len(bonds) == 2  # Two O-H bonds
    for b in bonds:
        assert 0.85 <= b["length_angstrom"] <= 1.15, f"Unexpected O-H bond length: {b['length_angstrom']}"
        assert b["bond_type"] == "SINGLE"


def test_invalid_smiles_conformer():
    """Verify error handling on invalid SMILES."""
    with pytest.raises(ValueError):
        generate_3d_conformer("INVALID_XYZ")
