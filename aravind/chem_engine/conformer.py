"""
Cheminformatics Virtual Laboratory - 3D Conformer Generation & Force Field Optimization
Uses RDKit ETKDGv3 distance geometry and MMFF94/UFF energy minimization.
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from rdkit import Chem
from rdkit.Chem import AllChem


@dataclass
class ConformerResult:
    mol_block: str
    pdb_block: str
    xyz_block: str
    force_field: str
    energy_kcal_mol: float
    optimization_converged: bool
    atom_count: int
    heavy_atom_count: int
    rdkit_mol: Any
    disclaimer: str = (
        "Computationally generated 3D conformer optimized via energy minimization. "
        "A calculated energy minimum represents a single low-energy conformation and "
        "does not necessarily capture all dynamic conformer ensembles or solvent effects in solution."
    )


def generate_3d_conformer(smiles: str, random_seed: int = 42) -> ConformerResult:
    """
    Generate an optimized 3D molecular conformer from SMILES.
    Workflow:
    1. Add explicit Hydrogens (Chem.AddHs).
    2. Embed coordinates via ETKDGv3 (Experimental-Torsion Knowledge Distance Geometry).
    3. Minimize energy using MMFF94 force field (fallback to UFF if MMFF parameters unavailable).
    4. Compute Gasteiger partial atomic charges.
    5. Return full coordinate blocks and energetic data.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Cannot generate conformer: invalid SMILES '{smiles}'")

    mol_h = Chem.AddHs(mol)

    # Step 1: 3D embedding with ETKDGv3
    params = AllChem.ETKDGv3()
    params.randomSeed = random_seed
    params.clearConfs = True
    params.maxIterations = 1000

    embed_status = AllChem.EmbedMolecule(mol_h, params)
    if embed_status != 0:
        # Fallback to standard ETKDG
        embed_status = AllChem.EmbedMolecule(mol_h, randomSeed=random_seed)
        if embed_status != 0:
            # Fallback to random coordinates
            embed_status = AllChem.EmbedMolecule(mol_h, useRandomCoords=True, randomSeed=random_seed)
            if embed_status != 0:
                raise RuntimeError(
                    f"3D conformer generation failed: could not generate valid geometric coordinates for SMILES '{smiles}'."
                )

    # Step 2: Force field optimization
    force_field_name = "MMFF94"
    energy_kcal = 0.0
    converged = False

    if AllChem.MMFFHasAllMoleculeParams(mol_h):
        try:
            mp = AllChem.MMFFGetMoleculeProperties(mol_h, mmffVariant="MMFF94")
            opt_res = AllChem.MMFFOptimizeMolecule(mol_h, mmffVariant="MMFF94", maxIters=500)
            converged = (opt_res == 0)
            ff = AllChem.MMFFGetMoleculeForceField(mol_h, mp)
            if ff is not None:
                energy_kcal = ff.CalcEnergy()
        except Exception:
            force_field_name = "UFF"
            opt_res = AllChem.UFFOptimizeMolecule(mol_h, maxIters=500)
            converged = (opt_res == 0)
            ff = AllChem.UFFGetMoleculeForceField(mol_h)
            if ff is not None:
                energy_kcal = ff.CalcEnergy()
    else:
        force_field_name = "UFF"
        opt_res = AllChem.UFFOptimizeMolecule(mol_h, maxIters=500)
        converged = (opt_res == 0)
        ff = AllChem.UFFGetMoleculeForceField(mol_h)
        if ff is not None:
            energy_kcal = ff.CalcEnergy()

    # Step 3: Compute Gasteiger partial charges
    try:
        AllChem.ComputeGasteigerCharges(mol_h)
    except Exception:
        pass

    mol_block = Chem.MolToMolBlock(mol_h)
    pdb_block = Chem.MolToPDBBlock(mol_h)

    # Generate XYZ block
    conf = mol_h.GetConformer()
    xyz_lines = [str(mol_h.GetNumAtoms()), f"{smiles} | Optimized via {force_field_name}"]
    for i in range(mol_h.GetNumAtoms()):
        atom = mol_h.GetAtomWithIdx(i)
        pos = conf.GetAtomPosition(i)
        xyz_lines.append(f"{atom.GetSymbol():<2} {pos.x:10.5f} {pos.y:10.5f} {pos.z:10.5f}")
    xyz_block = "\n".join(xyz_lines)

    return ConformerResult(
        mol_block=mol_block,
        pdb_block=pdb_block,
        xyz_block=xyz_block,
        force_field=force_field_name,
        energy_kcal_mol=round(energy_kcal, 3),
        optimization_converged=converged,
        atom_count=mol_h.GetNumAtoms(),
        heavy_atom_count=mol.GetNumHeavyAtoms(),
        rdkit_mol=mol_h,
    )


def extract_3d_coordinates(mol_with_conf: Any) -> List[Dict[str, Any]]:
    """
    Extract atom-level coordinates, formal charges, hybridization, and partial charges from conformer.
    """
    if not mol_with_conf.GetNumConformers():
        return []

    conf = mol_with_conf.GetConformer()
    atoms_data = []

    for i in range(mol_with_conf.GetNumAtoms()):
        atom = mol_with_conf.GetAtomWithIdx(i)
        pos = conf.GetAtomPosition(i)

        gasteiger = 0.0
        if atom.HasProp("_GasteigerCharge"):
            try:
                gasteiger = float(atom.GetProp("_GasteigerCharge"))
            except ValueError:
                gasteiger = 0.0

        atoms_data.append({
            "index": i,
            "symbol": atom.GetSymbol(),
            "atomic_num": atom.GetAtomicNum(),
            "x": round(pos.x, 4),
            "y": round(pos.y, 4),
            "z": round(pos.z, 4),
            "formal_charge": atom.GetFormalCharge(),
            "partial_charge": round(gasteiger, 4),
            "hybridization": str(atom.GetHybridization()),
            "is_aromatic": atom.GetIsAromatic(),
            "is_in_ring": atom.IsInRing(),
        })

    return atoms_data


def calculate_bond_distances(mol_with_conf: Any) -> List[Dict[str, Any]]:
    """
    Calculate Euclidean bond lengths and bond types from 3D conformer geometry.
    """
    if not mol_with_conf.GetNumConformers():
        return []

    conf = mol_with_conf.GetConformer()
    bonds_data = []

    for bond in mol_with_conf.GetBonds():
        idx1 = bond.GetBeginAtomIdx()
        idx2 = bond.GetEndAtomIdx()
        a1 = mol_with_conf.GetAtomWithIdx(idx1)
        a2 = mol_with_conf.GetAtomWithIdx(idx2)

        p1 = conf.GetAtomPosition(idx1)
        p2 = conf.GetAtomPosition(idx2)

        dist = math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2 + (p2.z - p1.z) ** 2)

        bonds_data.append({
            "bond_index": bond.GetIdx(),
            "atom1_index": idx1,
            "atom1_symbol": a1.GetSymbol(),
            "atom2_index": idx2,
            "atom2_symbol": a2.GetSymbol(),
            "bond_type": str(bond.GetBondType()),
            "is_aromatic": bond.GetIsAromatic(),
            "is_conjugated": bond.GetIsConjugated(),
            "length_angstrom": round(dist, 3),
        })

    return bonds_data
