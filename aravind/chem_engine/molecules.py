"""
Cheminformatics Virtual Laboratory - Predefined Library & SMILES Parser
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, inchi


@dataclass
class MoleculeData:
    name: str
    smiles: str
    canonical_smiles: str
    isomeric_smiles: str
    formula: str
    molecular_weight: float
    heavy_atom_count: int
    inchi: str
    inchikey: str
    category: str = "General Molecule"
    description: str = ""
    is_predefined: bool = False
    chiral_centers: List[Tuple[int, str]] = field(default_factory=list)
    has_stereochemistry: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "smiles": self.smiles,
            "canonical_smiles": self.canonical_smiles,
            "isomeric_smiles": self.isomeric_smiles,
            "formula": self.formula,
            "molecular_weight": round(self.molecular_weight, 3),
            "heavy_atom_count": self.heavy_atom_count,
            "inchi": self.inchi,
            "inchikey": self.inchikey,
            "category": self.category,
            "description": self.description,
            "is_predefined": self.is_predefined,
            "chiral_centers": self.chiral_centers,
            "has_stereochemistry": self.has_stereochemistry,
        }


# 10 Predefined molecules strictly following specification:
# 1. Water — O
# 2. Methane — C
# 3. Ethanol — CCO
# 4. Acetic acid — CC(=O)O
# 5. Acetone — CC(=O)C
# 6. Benzene — c1ccccc1
# 7. Caffeine — Cn1c(=O)c2c(ncn2C)n(C)c1=O
# 8. Aspirin — CC(=O)Oc1ccccc1C(=O)O
# 9. Paracetamol — CC(=O)Nc1ccc(O)cc1
# 10. Ibuprofen — CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O

PREDEFINED_SPECS = [
    {
        "name": "Water",
        "smiles": "O",
        "category": "Universal Solvent",
        "description": "Essential polar inorganic solvent characterized by extensive hydrogen bonding networks."
    },
    {
        "name": "Methane",
        "smiles": "C",
        "category": "Aliphatic Hydrocarbon",
        "description": "Simplest tetrahedral alkane, primary component of natural gas, non-polar."
    },
    {
        "name": "Ethanol",
        "smiles": "CCO",
        "category": "Aliphatic Alcohol",
        "description": "Primary alcohol miscible with water, widely utilized solvent and chemical intermediate."
    },
    {
        "name": "Acetic acid",
        "smiles": "CC(=O)O",
        "category": "Carboxylic Acid",
        "description": "Weak organic carboxylic acid, key metabolite in biochemistry and industrial feedstock."
    },
    {
        "name": "Acetone",
        "smiles": "CC(=O)C",
        "category": "Ketone",
        "description": "Simplest aliphatic ketone, common polar aprotic solvent in organic synthesis."
    },
    {
        "name": "Benzene",
        "smiles": "c1ccccc1",
        "category": "Aromatic Hydrocarbon",
        "description": "Archetypal planar aromatic hydrocarbon with 6 delocalized pi electrons complying with Huckel's rule."
    },
    {
        "name": "Caffeine",
        "smiles": "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
        "category": "Methylxanthine Alkaloid",
        "description": "Purine alkaloid and central nervous system stimulant acting as a non-selective adenosine receptor antagonist."
    },
    {
        "name": "Aspirin",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "category": "Salicylate / NSAID",
        "description": "Acetylsalicylic acid, prototype nonsteroidal anti-inflammatory drug (NSAID) and irreversible COX-1 inhibitor."
    },
    {
        "name": "Paracetamol",
        "smiles": "CC(=O)Nc1ccc(O)cc1",
        "category": "Anilide Analgesic",
        "description": "Acetaminophen, widely used antipyretic and analgesic acting centrally via COX inhibition and endocannabinoid modulation."
    },
    {
        "name": "Ibuprofen",
        "smiles": "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
        "category": "Propionic Acid NSAID",
        "description": "(S)-(+)-Ibuprofen enantiomer, non-selective nonsteroidal anti-inflammatory agent with chiral alpha-methyl propionic acid core."
    },
]


def _build_molecule_data(name: str, smiles: str, category: str = "General Molecule", description: str = "", is_predefined: bool = False) -> MoleculeData:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Failed to parse SMILES: {smiles}")

    canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=False)
    isomeric = Chem.MolToSmiles(mol, isomericSmiles=True)
    formula = rdMolDescriptors.CalcMolFormula(mol)
    mw = Descriptors.MolWt(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()

    try:
        inchi_str = inchi.MolToInchi(mol)
        inchikey_str = inchi.MolToInchiKey(mol)
    except Exception:
        inchi_str = "Unavailable"
        inchikey_str = "Unavailable"

    chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)
    has_stereo = len(chiral_centers) > 0 or ("@" in smiles)

    return MoleculeData(
        name=name,
        smiles=smiles,
        canonical_smiles=canonical,
        isomeric_smiles=isomeric,
        formula=formula,
        molecular_weight=mw,
        heavy_atom_count=heavy_atoms,
        inchi=inchi_str,
        inchikey=inchikey_str,
        category=category,
        description=description,
        is_predefined=is_predefined,
        chiral_centers=chiral_centers,
        has_stereochemistry=has_stereo,
    )


# Pre-compute validated dictionary of predefined molecules
PREDEFINED_MOLECULES: Dict[str, MoleculeData] = {}
for spec in PREDEFINED_SPECS:
    mol_data = _build_molecule_data(
        name=spec["name"],
        smiles=spec["smiles"],
        category=spec["category"],
        description=spec["description"],
        is_predefined=True,
    )
    PREDEFINED_MOLECULES[spec["name"]] = mol_data


def list_predefined_molecules() -> List[MoleculeData]:
    """Return all 10 predefined molecules."""
    return list(PREDEFINED_MOLECULES.values())


def get_predefined_molecule(name: str) -> Optional[MoleculeData]:
    """Retrieve predefined molecule by name."""
    return PREDEFINED_MOLECULES.get(name)


def parse_and_validate_smiles(smiles_str: str, custom_name: Optional[str] = None) -> Tuple[Optional[MoleculeData], Optional[str]]:
    """
    Validate a user-supplied SMILES string with clear diagnostic error handling.
    Returns (MoleculeData, None) on success or (None, error_message) on failure.
    """
    if not smiles_str or not smiles_str.strip():
        return None, "Empty SMILES string. Please enter a valid chemical structure notation."

    clean_smiles = smiles_str.strip()

    # Attempt parsing with sanitization
    mol = Chem.MolFromSmiles(clean_smiles, sanitize=False)
    if mol is None:
        return None, (
            f"Invalid SMILES syntax: '{clean_smiles}'. "
            "Please check atom symbols, unclosed rings/branches, or syntax characters."
        )

    # Sanitize and validate valency
    try:
        Chem.SanitizeMol(mol)
    except Exception as val_err:
        return None, f"Chemical valence or aromaticity error: {str(val_err)}"

    name = custom_name.strip() if custom_name and custom_name.strip() else f"Molecule ({rdMolDescriptors.CalcMolFormula(mol)})"

    try:
        data = _build_molecule_data(
            name=name,
            smiles=clean_smiles,
            category="User Custom Molecule",
            description="Custom chemical structure validated via RDKit.",
            is_predefined=False,
        )
        return data, None
    except Exception as err:
        return None, f"Property calculation failure: {str(err)}"
