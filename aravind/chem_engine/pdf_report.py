"""
Cheminformatics Virtual Laboratory - PDF Lab Report Generator
Generates publication-quality PDF reports for single and comparative molecular analyses using ReportLab.
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .properties import calculate_properties, check_lipinski_rule_of_five, check_veber_rules
from .conformer import generate_3d_conformer
from .depict import generate_2d_png
from .molecules import get_predefined_molecule, parse_and_validate_smiles


def generate_molecule_pdf_report(
    name: str,
    smiles: str,
    category: str = "General Molecule",
    description: str = "",
    canonical_smiles: Optional[str] = None,
    inchi_str: Optional[str] = None,
    inchikey_str: Optional[str] = None,
) -> bytes:
    """
    Generate a comprehensive scientific PDF lab report for a single molecule.
    Returns raw PDF bytes suitable for streaming or file download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
    section_h2 = ParagraphStyle(
        "ReportH2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )
    cell_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
        fontName="Helvetica-Oblique",
    )

    story = []

    # 1. Header
    story.append(Paragraph("Cheminformatics Virtual Laboratory", title_style))
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    story.append(
        Paragraph(
            f"<b>Comprehensive Molecular Analysis Report</b> | Generated: {now_str} | Target: <b>{name}</b>",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#00d2ff"), spaceAfter=10))

    # Calculate properties and conformer
    props = calculate_properties(smiles)
    lip = check_lipinski_rule_of_five(props)
    veber = check_veber_rules(props)

    try:
        conf_res = generate_3d_conformer(smiles)
        ff_name = conf_res.force_field
        ff_energy = f"{conf_res.energy_kcal_mol:.2f} kcal/mol"
        ff_converged = "Converged" if conf_res.optimization_converged else "Iteration Limit Reached"
    except Exception as e:
        ff_name = "N/A"
        ff_energy = "Calculation Failed"
        ff_converged = str(e)

    # 2. Molecule Overview & 2D Depiction Table
    story.append(Paragraph("1. Molecule Identification & 2D Depiction", section_h2))

    # Generate 2D image
    png_bytes = generate_2d_png(smiles, width=450, height=350)
    img_flowable = RLImage(io.BytesIO(png_bytes), width=200, height=155)

    ident_data = [
        [Paragraph("<b>Molecule Name:</b>", cell_style), Paragraph(name, cell_style)],
        [Paragraph("<b>Chemical Class:</b>", cell_style), Paragraph(category, cell_style)],
        [Paragraph("<b>Input SMILES:</b>", cell_style), Paragraph(f"<code>{smiles}</code>", cell_style)],
        [Paragraph("<b>Canonical SMILES:</b>", cell_style), Paragraph(f"<code>{canonical_smiles or props.get('formula', '')}</code>", cell_style)],
        [Paragraph("<b>Molecular Formula:</b>", cell_style), Paragraph(props.get("formula", "N/A"), cell_style)],
        [Paragraph("<b>Molecular Weight:</b>", cell_style), Paragraph(f"{props.get('molecular_weight', 'N/A')} g/mol", cell_style)],
        [Paragraph("<b>InChIKey:</b>", cell_style), Paragraph(inchikey_str or "N/A", cell_style)],
    ]
    ident_table = Table(ident_data, colWidths=[110, 200])
    ident_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
    ]))

    two_col = Table([[img_flowable, ident_table]], colWidths=[210, 330])
    two_col.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (0, 0), 0.5, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#f8fafc")),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 10))

    # 3. Physicochemical Descriptors Table
    story.append(Paragraph("2. Computed Physicochemical Descriptors", section_h2))
    prop_rows = [
        [Paragraph("Descriptor", cell_header), Paragraph("Value", cell_header), Paragraph("Unit / Standard", cell_header), Paragraph("Significance", cell_header)],
        [Paragraph("Molecular Weight (MW)", cell_style), Paragraph(f"{props['molecular_weight']:.3f}", cell_style), Paragraph("g/mol", cell_style), Paragraph("Size / Transport parameter", cell_style)],
        [Paragraph("Monoisotopic MW", cell_style), Paragraph(f"{props['exact_molecular_weight']:.4f}", cell_style), Paragraph("g/mol", cell_style), Paragraph("High-resolution MS calibration", cell_style)],
        [Paragraph("LogP (Crippen)", cell_style), Paragraph(f"{props['logp']:.3f}", cell_style), Paragraph("Dimensionless", cell_style), Paragraph("Lipophilicity / Membrane flux", cell_style)],
        [Paragraph("Polar Surface Area (TPSA)", cell_style), Paragraph(f"{props['tpsa']:.2f}", cell_style), Paragraph("Å²", cell_style), Paragraph("Polar atom exposure; <= 140 Å²", cell_style)],
        [Paragraph("H-Bond Donors (HBD)", cell_style), Paragraph(str(props["hbd"]), cell_style), Paragraph("Count", cell_style), Paragraph("Desolvation energy factor; <= 5", cell_style)],
        [Paragraph("H-Bond Acceptors (HBA)", cell_style), Paragraph(str(props["hba"]), cell_style), Paragraph("Count", cell_style), Paragraph("Polar binding capacity; <= 10", cell_style)],
        [Paragraph("Rotatable Bonds", cell_style), Paragraph(str(props["rotatable_bonds"]), cell_style), Paragraph("Count", cell_style), Paragraph("Conformational flexibility; <= 10", cell_style)],
        [Paragraph("Total Rings", cell_style), Paragraph(str(props["ring_count"]), cell_style), Paragraph("Count", cell_style), Paragraph(f"Aromatic: {props['aromatic_rings']}, Aliphatic: {props['aliphatic_rings']}", cell_style)],
        [Paragraph("Formal Charge", cell_style), Paragraph(str(props["formal_charge"]), cell_style), Paragraph("e", cell_style), Paragraph("Net ionic state at neutral pH", cell_style)],
        [Paragraph("Fraction Csp3", cell_style), Paragraph(f"{props['fraction_csp3']:.3f}", cell_style), Paragraph("Ratio", cell_style), Paragraph("Saturation & 3D complexity", cell_style)],
    ]
    prop_table = Table(prop_rows, colWidths=[150, 70, 100, 220])
    prop_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(prop_table)
    story.append(Spacer(1, 10))

    # 4. Drug-Likeness Screening (Lipinski & Veber)
    story.append(Paragraph("3. Oral Drug-Likeness Evaluation", section_h2))
    lip_rows = [
        [Paragraph("Filter / Rule", cell_header), Paragraph("Cutoff", cell_header), Paragraph("Measured Value", cell_header), Paragraph("Evaluation", cell_header)],
        [Paragraph("Lipinski MW", cell_style), Paragraph("<= 500 g/mol", cell_style), Paragraph(f"{props['molecular_weight']:.2f}", cell_style), Paragraph("PASSED" if props["molecular_weight"] <= 500 else "FAIL", cell_style)],
        [Paragraph("Lipinski LogP", cell_style), Paragraph("<= 5.0", cell_style), Paragraph(f"{props['logp']:.2f}", cell_style), Paragraph("PASSED" if props["logp"] <= 5.0 else "FAIL", cell_style)],
        [Paragraph("Lipinski HBD", cell_style), Paragraph("<= 5", cell_style), Paragraph(str(props["hbd"]), cell_style), Paragraph("PASSED" if props["hbd"] <= 5 else "FAIL", cell_style)],
        [Paragraph("Lipinski HBA", cell_style), Paragraph("<= 10", cell_style), Paragraph(str(props["hba"]), cell_style), Paragraph("PASSED" if props["hba"] <= 10 else "FAIL", cell_style)],
        [Paragraph("Veber Rotatable Bonds", cell_style), Paragraph("<= 10", cell_style), Paragraph(str(props["rotatable_bonds"]), cell_style), Paragraph("PASSED" if props["rotatable_bonds"] <= 10 else "FAIL", cell_style)],
        [Paragraph("Veber TPSA", cell_style), Paragraph("<= 140 Å²", cell_style), Paragraph(f"{props['tpsa']:.1f}", cell_style), Paragraph("PASSED" if props["tpsa"] <= 140 else "FAIL", cell_style)],
    ]
    lip_table = Table(lip_rows, colWidths=[150, 100, 120, 170])
    lip_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdfa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(lip_table)
    story.append(Spacer(1, 10))

    # 5. 3D Conformer & Force Field Summary
    story.append(Paragraph("4. 3D Conformer Generation & Energy Minimization", section_h2))
    conf_rows = [
        [Paragraph("Parameter", cell_header), Paragraph("Specification", cell_header)],
        [Paragraph("Distance Geometry Algorithm", cell_style), Paragraph("ETKDGv3 (Experimental-Torsion Knowledge Distance Geometry)", cell_style)],
        [Paragraph("Force Field Employed", cell_style), Paragraph(ff_name, cell_style)],
        [Paragraph("Minimized Energy", cell_style), Paragraph(ff_energy, cell_style)],
        [Paragraph("Optimization Status", cell_style), Paragraph(ff_converged, cell_style)],
        [Paragraph("Total 3D Coordinates Generated", cell_style), Paragraph(f"{props['total_atom_count']} atoms (including explicit hydrogens)", cell_style)],
    ]
    conf_table = Table(conf_rows, colWidths=[180, 360])
    conf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(conf_table)
    story.append(Spacer(1, 12))

    # 6. Scientific Limitations & Legal Disclaimer
    story.append(
        Paragraph(
            "<b>Scientific Methodology & Limitations Disclaimer:</b><br/>"
            "This report was programmatically compiled by the Cheminformatics Virtual Laboratory utilizing RDKit cheminformatics algorithms. "
            "All physical property metrics (LogP, TPSA, HBD, HBA) are in silico predictions. 3D conformers represent single computed energy minima "
            "and do not encompass full thermodynamic conformational ensembles or dynamic solvent interactions. "
            "Drug-likeness guidelines (Lipinski Rule of 5 and Veber rules) are screening heuristics for absorption and permeability; "
            "they do not establish pharmacological activity, safety, metabolic clearance, or clinical suitability.",
            disclaimer_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()


def generate_comparison_pdf_report(molecule_list: List[Dict[str, str]]) -> bytes:
    """
    Generate a comparative scientific PDF report for multiple molecules.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CompTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0f172a"))
    subtitle_style = ParagraphStyle("CompSub", parent=styles["Normal"], fontSize=9, leading=12, textColor=colors.HexColor("#475569"))
    section_h2 = ParagraphStyle("CompH2", parent=styles["Heading2"], fontSize=12, leading=15, textColor=colors.HexColor("#1e293b"), spaceBefore=10, spaceAfter=6)
    cell_style = ParagraphStyle("CompCell", parent=styles["Normal"], fontSize=8, leading=10)
    cell_header = ParagraphStyle("CompHead", parent=styles["Normal"], fontSize=8, leading=10, fontName="Helvetica-Bold", textColor=colors.white)

    story = []
    story.append(Paragraph("Cheminformatics Virtual Laboratory", title_style))
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    mol_names = ", ".join([m.get("name", "Unnamed") for m in molecule_list])
    story.append(Paragraph(f"<b>Comparative Multi-Molecule Analysis</b> | Generated: {now_str} | Molecules: <b>{mol_names}</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#00d2ff"), spaceAfter=10))

    # Comparison Table
    story.append(Paragraph("1. Side-by-Side Property Comparison", section_h2))

    headers = [Paragraph("Descriptor", cell_header)]
    for m in molecule_list:
        headers.append(Paragraph(m.get("name", "Mol"), cell_header))

    rows = [headers]
    descs = [
        ("Formula", lambda p: p["formula"]),
        ("Molecular Weight", lambda p: f"{p['molecular_weight']:.2f} g/mol"),
        ("LogP", lambda p: f"{p['logp']:.2f}"),
        ("TPSA", lambda p: f"{p['tpsa']:.1f} Å²"),
        ("HBD", lambda p: str(p["hbd"])),
        ("HBA", lambda p: str(p["hba"])),
        ("Rotatable Bonds", lambda p: str(p["rotatable_bonds"])),
        ("Ring Count", lambda p: str(p["ring_count"])),
        ("Aromatic Rings", lambda p: str(p["aromatic_rings"])),
        ("Heavy Atoms", lambda p: str(p["heavy_atom_count"])),
    ]

    # Precalculate properties
    all_props = [calculate_properties(m["smiles"]) for m in molecule_list]

    for label, fn in descs:
        row = [Paragraph(label, cell_style)]
        for p in all_props:
            row.append(Paragraph(fn(p), cell_style))
        rows.append(row)

    col_w = [140] + [(400 // len(molecule_list))] * len(molecule_list)
    comp_table = Table(rows, colWidths=col_w)
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "<b>Disclaimer:</b> Comparative properties are generated via RDKit in silico models for educational and computational analysis.",
            ParagraphStyle("D2", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#64748b")),
        )
    )

    doc.build(story)
    return buffer.getvalue()
