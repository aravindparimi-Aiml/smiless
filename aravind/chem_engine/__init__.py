"""
Cheminformatics Virtual Laboratory - Chemistry Engine
Core cheminformatics calculations, conformer generation, depictions, and AI assistant.
"""

from .molecules import (
    PREDEFINED_MOLECULES,
    MoleculeData,
    parse_and_validate_smiles,
    get_predefined_molecule,
    list_predefined_molecules,
)
from .properties import (
    calculate_properties,
    check_lipinski_rule_of_five,
    check_veber_rules,
    calculate_elemental_composition,
    generate_fingerprints,
)
from .conformer import (
    generate_3d_conformer,
    extract_3d_coordinates,
    calculate_bond_distances,
)
from .depict import (
    generate_2d_svg,
    generate_2d_png,
)
from .comparison import (
    compare_molecules,
    calculate_similarity_matrix,
)
from .assistant import (
    ask_chemistry_assistant,
)
from .pdf_report import (
    generate_molecule_pdf_report,
    generate_comparison_pdf_report,
)
from .assessment import (
    get_assessment_questions,
    evaluate_assessment,
)

__all__ = [
    "PREDEFINED_MOLECULES",
    "MoleculeData",
    "parse_and_validate_smiles",
    "get_predefined_molecule",
    "list_predefined_molecules",
    "calculate_properties",
    "check_lipinski_rule_of_five",
    "check_veber_rules",
    "calculate_elemental_composition",
    "generate_fingerprints",
    "generate_3d_conformer",
    "extract_3d_coordinates",
    "calculate_bond_distances",
    "generate_2d_svg",
    "generate_2d_png",
    "compare_molecules",
    "calculate_similarity_matrix",
    "ask_chemistry_assistant",
    "generate_molecule_pdf_report",
    "generate_comparison_pdf_report",
    "get_assessment_questions",
    "evaluate_assessment",
]
