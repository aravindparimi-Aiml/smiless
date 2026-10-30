"""
Cheminformatics Virtual Laboratory - Multi-Molecule Comparison Engine
Computes property comparisons and fingerprint similarity metrics (Tanimoto, Dice, Cosine).
"""

from typing import List, Dict, Any, Tuple
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator, MACCSkeys
from .properties import calculate_properties, check_lipinski_rule_of_five


def compare_molecules(molecule_list: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Compare two or more molecules by computing their full descriptor profiles,
    pairwise similarities, and structural differences.

    molecule_list: list of dicts with keys 'name' and 'smiles'.
    """
    if len(molecule_list) < 2:
        raise ValueError("At least two molecules are required for comparison.")

    data_entries = []
    rdkit_mols = []
    morgan_fps = []
    maccs_fps = []

    morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

    for item in molecule_list:
        name = item.get("name", "Unnamed")
        smiles = item.get("smiles", "").strip()

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError(f"Invalid molecule '{name}' with SMILES: '{smiles}'")

        props = calculate_properties(smiles)
        lipinski = check_lipinski_rule_of_five(props)

        m_fp = morgan_gen.GetFingerprint(mol)
        mc_fp = MACCSkeys.GenMACCSKeys(mol)

        rdkit_mols.append(mol)
        morgan_fps.append(m_fp)
        maccs_fps.append(mc_fp)

        data_entries.append({
            "name": name,
            "smiles": smiles,
            "canonical_smiles": Chem.MolToSmiles(mol, canonical=True),
            "properties": props,
            "lipinski": lipinski,
            "morgan_on_bits": m_fp.GetNumOnBits(),
            "maccs_on_bits": mc_fp.GetNumOnBits(),
        })

    # Compute pairwise similarity matrices
    n = len(data_entries)
    tanimoto_matrix = [[1.0] * n for _ in range(n)]
    dice_matrix = [[1.0] * n for _ in range(n)]
    maccs_tanimoto_matrix = [[1.0] * n for _ in range(n)]

    pairwise_comparisons = []

    for i in range(n):
        for j in range(i + 1, n):
            tan = round(DataStructs.TanimotoSimilarity(morgan_fps[i], morgan_fps[j]), 4)
            dice = round(DataStructs.DiceSimilarity(morgan_fps[i], morgan_fps[j]), 4)
            maccs_tan = round(DataStructs.TanimotoSimilarity(maccs_fps[i], maccs_fps[j]), 4)

            tanimoto_matrix[i][j] = tan
            tanimoto_matrix[j][i] = tan
            dice_matrix[i][j] = dice
            dice_matrix[j][i] = dice
            maccs_tanimoto_matrix[i][j] = maccs_tan
            maccs_tanimoto_matrix[j][i] = maccs_tan

            p1 = data_entries[i]["properties"]
            p2 = data_entries[j]["properties"]

            pairwise_comparisons.append({
                "mol1_name": data_entries[i]["name"],
                "mol2_name": data_entries[j]["name"],
                "tanimoto_morgan": tan,
                "dice_morgan": dice,
                "tanimoto_maccs": maccs_tan,
                "similarity_assessment": _interpret_similarity(tan),
                "mw_diff": round(p2["molecular_weight"] - p1["molecular_weight"], 3),
                "logp_diff": round(p2["logp"] - p1["logp"], 3),
                "tpsa_diff": round(p2["tpsa"] - p1["tpsa"], 2),
                "hbd_diff": p2["hbd"] - p1["hbd"],
                "hba_diff": p2["hba"] - p1["hba"],
                "rot_bonds_diff": p2["rotatable_bonds"] - p1["rotatable_bonds"],
            })

    names = [d["name"] for d in data_entries]

    return {
        "molecules": data_entries,
        "names": names,
        "tanimoto_matrix": tanimoto_matrix,
        "dice_matrix": dice_matrix,
        "maccs_tanimoto_matrix": maccs_tanimoto_matrix,
        "pairwise": pairwise_comparisons,
        "metrics_explanation": {
            "tanimoto": (
                "Morgan Tanimoto Similarity: Tc = c / (a + b - c), where a and b are the number of on-bits "
                "in molecules A and B, and c is the number of shared bits. Values range from 0.0 (no common circular fragments) "
                "to 1.0 (identical circular subgraphs up to radius 2). A threshold of Tc >= 0.85 often implies potential "
                "similar pharmacological activity."
            ),
            "dice": (
                "Dice Similarity: Dc = 2c / (a + b). Gives higher numerical weight to common features compared to Tanimoto."
            ),
            "maccs": (
                "MACCS Structural Keys Similarity: Tanimoto similarity over 166 predefined expert medicinal chemistry substructural keys."
            )
        }
    }


def calculate_similarity_matrix(smiles_list: List[str]) -> List[List[float]]:
    """Convenience helper to compute Tanimoto similarity matrix for a list of SMILES strings."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in smiles_list]
    n = len(fps)
    mat = [[1.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            sim = round(DataStructs.TanimotoSimilarity(fps[i], fps[j]), 4)
            mat[i][j] = sim
            mat[j][i] = sim
    return mat


def _interpret_similarity(tanimoto: float) -> str:
    if tanimoto >= 0.85:
        return "High Structural Similarity (Likely Bioisosteric / Analogous Activity)"
    elif tanimoto >= 0.60:
        return "Moderate Structural Similarity (Shared Core or Functional Clusters)"
    elif tanimoto >= 0.30:
        return "Low-to-Moderate Similarity (Divergent Scaffolds)"
    else:
        return "Distinct / Dissimilar Chemical Structures"
