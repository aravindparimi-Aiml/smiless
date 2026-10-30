"""
Tests for 2D Molecular Depiction (SVG and PNG)
"""

import pytest
from chem_engine.depict import generate_2d_svg, generate_2d_png


def test_generate_2d_svg():
    """Verify SVG generation for Caffeine."""
    svg = generate_2d_svg("Cn1c(=O)c2c(ncn2C)n(C)c1=O", width=400, height=300)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "rect" in svg or "path" in svg


def test_generate_2d_svg_highlighting():
    """Verify SVG generation with atom and bond highlighting."""
    svg = generate_2d_svg("CC(=O)O", highlight_atoms=[0, 1], highlight_bonds=[0])
    assert "<svg" in svg
    assert "</svg>" in svg


def test_generate_2d_png():
    """Verify PNG binary byte generation."""
    png_bytes = generate_2d_png("CC(=O)Oc1ccccc1C(=O)O")
    assert len(png_bytes) > 500
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic header


def test_depict_invalid_smiles():
    """Verify error on invalid SMILES."""
    with pytest.raises(ValueError):
        generate_2d_svg("INVALID_NOT_A_SMILES")
