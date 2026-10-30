"""
Cheminformatics Virtual Laboratory - Molecular Property Analysis Engine
Calculates descriptors, Lipinski/Veber drug-likeness rules, elemental composition, and fingerprints.
"""

from typing import Dict, Any, List, Tuple
from collections import Counter
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, Crippen, Lipinski
from rdkit.Chem import rdFingerprintGenerator, MACCSkeys


COMMON_SMARTS_PATTERNS = {
    "Carboxylic acid": Chem.MolFromSmarts("[CX3](=O)[OX2H1]"),
    "Ester": Chem.MolFromSmarts("[#6][CX3](=O)[OX2H0][#6]"),
    "Alcohol": Chem.MolFromSmarts("[#6][OX2H]"),
    "Phenol": Chem.MolFromSmarts("[c][OX2H]"),
    "Ketone": Chem.MolFromSmarts("[#6][CX3](=O)[#6]"),
    "Aldehyde": Chem.MolFromSmarts("[CX3H1](=O)[#6]"),
    "Amide": Chem.MolFromSmarts("[#6][CX3](=O)[NX3]"),
    "Primary amine": Chem.MolFromSmarts("[NX3;H2;!$(NC=O)]"),
    "Secondary amine": Chem.MolFromSmarts("[NX3;H1;!$(NC=O)]"),
    "Tertiary amine": Chem.MolFromSmarts("[NX3;H0;!$(NC=O)]"),
    "Ether": Chem.MolFromSmarts("[OD2]([#6])[#6]"),
    "Aromatic ring": Chem.MolFromSmarts("a1aaaaa1"),
    "Halogen": Chem.MolFromSmarts("[F,Cl,Br,I]"),
    "Nitro": Chem.MolFromSmarts("[$([NX3](=O)=O),$([NX3+](=O)[O-])]"),
    "Sulfonamide": Chem.MolFromSmarts("[#16X4](=[OX1])(=[OX1])([NX3])"),
}


def calculate_properties(smiles: str) -> Dict[str, Any]:
    """
    Calculate comprehensive molecular properties from a valid SMILES string.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: '{smiles}'")

    mol_with_h = Chem.AddHs(mol)

    mw = Descriptors.MolWt(mol)
    exact_mw = Descriptors.ExactMolWt(mol)
    formula = rdMolDescriptors.CalcMolFormula(mol)
    heavy_atoms = mol.GetNumHeavyAtoms()
    total_atoms = mol_with_h.GetNumAtoms()
    heavy_bonds = mol.GetNumBonds()
    total_bonds = mol_with_h.GetNumBonds()

    aromatic_bonds = sum(1 for b in mol.GetBonds() if b.GetIsAromatic())
    aromatic_atoms = sum(1 for a in mol.GetAtoms() if a.GetIsAromatic())

    hbd = Lipinski.NumHDonors(mol)
    hba = Lipinski.NumHAcceptors(mol)
    logp = Crippen.MolLogP(mol)
    mr = Crippen.MolMR(mol)
    tpsa = rdMolDescriptors.CalcTPSA(mol)
    rot_bonds = Lipinski.NumRotatableBonds(mol)
    ring_count = Lipinski.RingCount(mol)
    aromatic_rings = Lipinski.NumAromaticRings(mol)
    aliphatic_rings = Lipinski.NumAliphaticRings(mol)
    formal_charge = Chem.GetFormalCharge(mol)
    f_sp3 = rdMolDescriptors.CalcFractionCSP3(mol)

    chiral_centers = Chem.FindMolChiralCenters(mol, includeUnassigned=True)

    # Detect functional groups
    detected_groups = {}
    for name, query in COMMON_SMARTS_PATTERNS.items():
        if query is not None:
            matches = mol.GetSubstructMatches(query)
            if matches:
                detected_groups[name] = len(matches)

    return {
        "formula": formula,
        "molecular_weight": round(mw, 4),
        "exact_molecular_weight": round(exact_mw, 5),
        "heavy_atom_count": heavy_atoms,
        "total_atom_count": total_atoms,
        "heavy_bond_count": heavy_bonds,
        "total_bond_count": total_bonds,
        "aromatic_atom_count": aromatic_atoms,
        "aromatic_bond_count": aromatic_bonds,
        "hbd": hbd,
        "hba": hba,
        "logp": round(logp, 3),
        "molar_refractivity": round(mr, 3),
        "tpsa": round(tpsa, 2),
        "rotatable_bonds": rot_bonds,
        "ring_count": ring_count,
        "aromatic_rings": aromatic_rings,
        "aliphatic_rings": aliphatic_rings,
        "formal_charge": formal_charge,
        "fraction_csp3": round(f_sp3, 3),
        "chiral_centers_count": len(chiral_centers),
        "chiral_centers": chiral_centers,
        "functional_groups": detected_groups,
    }


def check_lipinski_rule_of_five(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate Lipinski's Rule of Five for oral drug-likeness.
    Criteria:
    - Molecular Weight <= 500 g/mol
    - LogP <= 5.0
    - Hydrogen Bond Donors <= 5
    - Hydrogen Bond Acceptors <= 10
    """
    mw = properties.get("molecular_weight", 0.0)
    logp = properties.get("logp", 0.0)
    hbd = properties.get("hbd", 0)
    hba = properties.get("hba", 0)

    violations = []
    if mw > 500:
        violations.append(f"Molecular weight ({mw:.2f} g/mol) exceeds 500 g/mol")
    if logp > 5.0:
        violations.append(f"LogP ({logp:.2f}) exceeds 5.0")
    if hbd > 5:
        violations.append(f"H-bond donors ({hbd}) exceeds 5")
    if hba > 10:
        violations.append(f"H-bond acceptors ({hba}) exceeds 10")

    num_violations = len(violations)
    is_compliant = num_violations <= 1  # Standard drug discovery tolerance allows at most 1 violation

    return {
        "is_compliant": is_compliant,
        "violation_count": num_violations,
        "violations": violations,
        "rules": {
            "Molecular Weight <= 500": {"value": mw, "threshold": 500, "pass": mw <= 500},
            "LogP <= 5.0": {"value": logp, "threshold": 5.0, "pass": logp <= 5.0},
            "H-Bond Donors <= 5": {"value": hbd, "threshold": 5, "pass": hbd <= 5},
            "H-Bond Acceptors <= 10": {"value": hba, "threshold": 10, "pass": hba <= 10},
        },
        "disclaimer": (
            "Lipinski's Rule of Five is an empirical screening heuristic for oral drug-likeness "
            "(evaluating intestinal absorption and solubility). It does not establish pharmacological "
            "efficacy, toxicity, biological safety, or clinical suitability."
        )
    }


def check_veber_rules(properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate Veber's Rules for oral bioavailability:
    - Rotatable bonds <= 10
    - TPSA <= 140 Å²
    """
    rot_bonds = properties.get("rotatable_bonds", 0)
    tpsa = properties.get("tpsa", 0.0)

    violations = []
    if rot_bonds > 10:
        violations.append(f"Rotatable bonds ({rot_bonds}) exceeds 10")
    if tpsa > 140.0:
        violations.append(f"TPSA ({tpsa:.1f} Å²) exceeds 140 Å²")

    num_violations = len(violations)
    is_compliant = num_violations == 0

    return {
        "is_compliant": is_compliant,
        "violation_count": num_violations,
        "violations": violations,
        "rules": {
            "Rotatable Bonds <= 10": {"value": rot_bonds, "threshold": 10, "pass": rot_bonds <= 10},
            "TPSA <= 140 Å²": {"value": tpsa, "threshold": 140.0, "pass": tpsa <= 140.0},
        },
        "disclaimer": (
            "Veber's rules predict passive oral bioavailability in rats based on molecular rigidity and polar surface area. "
            "They serve as screening guidelines rather than absolute predictors."
        )
    }


def calculate_elemental_composition(smiles: str) -> Dict[str, float]:
    """
    Calculate the elemental weight percentages (wt%) for all atoms including explicit hydrogens.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {}

    mol_with_h = Chem.AddHs(mol)
    total_mw = Descriptors.MolWt(mol)
    if total_mw == 0:
        return {}

    ptable = Chem.GetPeriodicTable()
    element_weights: Dict[str, float] = {}

    for atom in mol_with_h.GetAtoms():
        sym = atom.GetSymbol()
        mass = ptable.GetAtomicWeight(sym)
        element_weights[sym] = element_weights.get(sym, 0.0) + mass

    composition = {
        sym: round((mass / total_mw) * 100, 2)
        for sym, mass in sorted(element_weights.items(), key=lambda x: -x[1])
    }
    return composition


def generate_fingerprints(smiles: str) -> Dict[str, Any]:
    """
    Generate Morgan (ECFP4), MACCS keys, and topological fingerprints.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: '{smiles}'")

    # Morgan fingerprint (radius=2, 2048 bits) - standard ECFP4 equivalent
    morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    morgan_fp = morgan_gen.GetFingerprint(mol)

    # MACCS keys (166 structural keys)
    maccs_fp = MACCSkeys.GenMACCSKeys(mol)

    # RDKit topological fingerprint
    rdkit_gen = rdFingerprintGenerator.GetRDKitFPGenerator(fpSize=2048)
    rdkit_fp = rdkit_gen.GetFingerprint(mol)

    return {
        "morgan": {
            "name": "Morgan / ECFP4 Fingerprint",
            "size": 2048,
            "radius": 2,
            "on_bits_count": morgan_fp.GetNumOnBits(),
            "on_bit_indices": list(morgan_fp.GetOnBits())[:30],
            "fingerprint_obj": morgan_fp,
        },
        "maccs": {
            "name": "MACCS 166 Structural Keys",
            "size": 166,
            "on_bits_count": maccs_fp.GetNumOnBits(),
            "on_bit_indices": list(maccs_fp.GetOnBits()),
            "fingerprint_obj": maccs_fp,
        },
        "rdkit_topological": {
            "name": "RDKit Topological Daylight-type Fingerprint",
            "size": 2048,
            "on_bits_count": rdkit_fp.GetNumOnBits(),
            "on_bit_indices": list(rdkit_fp.GetOnBits())[:30],
            "fingerprint_obj": rdkit_fp,
        }
    }
