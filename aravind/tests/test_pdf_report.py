"""
Tests for PDF Lab Report Generation
"""

import pytest
from chem_engine.pdf_report import generate_molecule_pdf_report, generate_comparison_pdf_report


def test_single_molecule_pdf():
    """Verify PDF report generation for Aspirin."""
    pdf_bytes = generate_molecule_pdf_report(
        name="Aspirin",
        smiles="CC(=O)Oc1ccccc1C(=O)O",
        category="Salicylate / NSAID",
        canonical_smiles="CC(=O)Oc1ccccc1C(=O)O",
    )
    assert len(pdf_bytes) > 2000
    assert pdf_bytes[:5] == b"%PDF-"  # Standard PDF magic header


def test_comparative_pdf():
    """Verify comparative PDF report generation."""
    mols = [
        {"name": "Aspirin", "smiles": "CC(=O)Oc1ccccc1C(=O)O"},
        {"name": "Paracetamol", "smiles": "CC(=O)Nc1ccc(O)cc1"},
    ]
    pdf_bytes = generate_comparison_pdf_report(mols)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes[:5] == b"%PDF-"
