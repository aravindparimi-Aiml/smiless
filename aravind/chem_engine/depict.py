"""
Cheminformatics Virtual Laboratory - 2D Molecular Depiction Engine
Generates publication-quality 2D vector SVGs and PNG bitmaps with atom/bond highlighting.
Resilient to headless Linux environments (Streamlit Cloud) without libXrender.
"""

import io
from typing import Optional, List, Tuple
from rdkit import Chem
from PIL import Image, ImageDraw

# Safe import for headless Linux environments (Streamlit Cloud Debian container)
try:
    from rdkit.Chem import Draw
    from rdkit.Chem.Draw import rdMolDraw2D
    RDKIT_DRAW_AVAILABLE = True
    RDKIT_DRAW_ERROR = None
except Exception as _draw_import_err:
    RDKIT_DRAW_AVAILABLE = False
    RDKIT_DRAW_ERROR = str(_draw_import_err)


def generate_2d_svg(
    smiles: str,
    width: int = 480,
    height: int = 360,
    highlight_atoms: Optional[List[int]] = None,
    highlight_bonds: Optional[List[int]] = None,
    dark_theme: bool = False,
) -> str:
    """
    Generate clean, scalable SVG depiction with RDKit rdMolDraw2D.
    Supports stereochemical wedges/dashes, aromatic bonds, and optional highlighting.
    Falls back gracefully if libXrender is missing in cloud environments.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Cannot depict 2D structure: invalid SMILES '{smiles}'")

    if not RDKIT_DRAW_AVAILABLE:
        # Fallback SVG when headless Linux is missing libXrender
        return (
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="100%" height="100%" fill="#161b22" rx="8"/>'
            f'<text x="50%" y="45%" text-anchor="middle" fill="#00d2ff" font-family="sans-serif" font-size="14" font-weight="bold">'
            f'2D Depiction Engine Standby'
            f'</text>'
            f'<text x="50%" y="58%" text-anchor="middle" fill="#8b949e" font-family="sans-serif" font-size="11">'
            f'System package libxrender1 required (see packages.txt)'
            f'</text>'
            f'<text x="50%" y="72%" text-anchor="middle" fill="#58a6ff" font-family="monospace" font-size="12">'
            f'SMILES: {smiles}'
            f'</text>'
            f'</svg>'
        )

    # Generate 2D coordinates if not present
    if not mol.GetNumConformers():
        from rdkit.Chem import rdDepictor
        rdDepictor.Compute2DCoords(mol)

    drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
    opts = drawer.drawOptions()
    opts.bondLineWidth = 2.2
    opts.addStereoAnnotation = True
    opts.clearBackground = False  # Transparent background

    if dark_theme:
        # High-contrast colors on dark background
        opts.setSymbolColour((0.92, 0.94, 0.96))

    h_atoms = highlight_atoms if highlight_atoms is not None else []
    h_bonds = highlight_bonds if highlight_bonds is not None else []

    drawer.DrawMolecule(mol, highlightAtoms=h_atoms, highlightBonds=h_bonds)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    # Clean up SVG XML header for inline embedding
    if "<?xml" in svg:
        svg = svg.split("?>", 1)[-1].strip()

    return svg


def generate_2d_png(
    smiles: str,
    width: int = 500,
    height: int = 400,
    dark_background: bool = False,
) -> bytes:
    """
    Generate PNG byte data for PDF embedding and user downloads.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Cannot depict 2D PNG: invalid SMILES '{smiles}'")

    if not RDKIT_DRAW_AVAILABLE:
        # Generate placeholder image with Pillow
        img = Image.new("RGB", (width, height), color=(22, 27, 34))
        draw = ImageDraw.Draw(img)
        draw.text((width // 4, height // 2 - 20), "2D Rendering - libxrender1 pending", fill=(0, 210, 255))
        draw.text((width // 4, height // 2 + 10), f"SMILES: {smiles}", fill=(139, 148, 158))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    from rdkit.Chem import rdDepictor
    rdDepictor.Compute2DCoords(mol)

    img = Draw.MolToImage(mol, size=(width, height))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
