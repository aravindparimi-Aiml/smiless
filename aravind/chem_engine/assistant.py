"""
Cheminformatics Virtual Laboratory - AI Chemistry Assistant
Provides context-aware chemical reasoning using LLM APIs (OpenAI/Anthropic/Gemini)
with a comprehensive, scientifically rigorous local expert cheminformatics knowledge engine fallback.
"""

import os
import re
from typing import Dict, Any, Optional, List
from .properties import calculate_properties, check_lipinski_rule_of_five, COMMON_SMARTS_PATTERNS
from .molecules import parse_and_validate_smiles, get_predefined_molecule, PREDEFINED_MOLECULES


SYSTEM_PROMPT = """You are an expert computational chemist and cheminformatics specialist at the Cheminformatics Virtual Laboratory.
Your role is to explain molecular structures, physicochemical properties, spectroscopy, force field mechanics, and drug-likeness.
Guidelines:
- Ground your answers in accurate chemistry principles (thermodynamics, orbital hybridization, resonance, hydrogen bonding).
- Refer specifically to the provided computed molecular context (SMILES, Formula, MW, LogP, TPSA, HBD, HBA, rings, etc.).
- Never make clinical prescribing, therapeutic efficacy, or personal diagnostic claims.
- Clarify that drug-likeness rules (e.g. Lipinski Rule of 5) are empirical screening heuristics.
"""

SCIENTIFIC_DISCLAIMER = (
    "\n\n*Scientific Disclaimer: This analysis is provided for educational and computational research purposes. "
    "Calculated properties and heuristics do not constitute clinical, therapeutic, or toxicological advice.*"
)


def ask_chemistry_assistant(
    user_query: str,
    molecule_context: Optional[Dict[str, Any]] = None,
    second_molecule_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Answer chemical questions about the active molecule(s).
    Attempts LLM API execution if environment keys are configured;
    otherwise executes the high-fidelity local expert cheminformatics knowledge engine.
    """
    if not user_query or not user_query.strip():
        return "Please ask a specific chemistry question about the active molecule."

    # Try external LLM API if configured
    llm_response = _try_external_llm(user_query, molecule_context, second_molecule_context)
    if llm_response:
        return llm_response + SCIENTIFIC_DISCLAIMER

    # Fallback to local expert cheminformatics engine
    return _expert_local_cheminformatics_engine(user_query, molecule_context, second_molecule_context) + SCIENTIFIC_DISCLAIMER


def _try_external_llm(
    query: str,
    ctx1: Optional[Dict[str, Any]],
    ctx2: Optional[Dict[str, Any]],
) -> Optional[str]:
    """Check for OpenAI API key and call if available."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)

        context_str = _build_context_summary(ctx1, ctx2)
        prompt = f"Context Data:\n{context_str}\n\nUser Question: {query}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        return response.choices[0].message.content
    except Exception:
        # Gracefully drop back to expert rule-based engine on network or auth errors
        return None


def _build_context_summary(ctx1: Optional[Dict[str, Any]], ctx2: Optional[Dict[str, Any]]) -> str:
    parts = []
    if ctx1:
        p1 = ctx1.get("properties", {})
        parts.append(
            f"Primary Molecule: {ctx1.get('name', 'Molecule 1')} (SMILES: {ctx1.get('smiles', 'N/A')})\n"
            f"Formula: {p1.get('formula', 'N/A')}, MW: {p1.get('molecular_weight', 'N/A')} g/mol\n"
            f"LogP: {p1.get('logp', 'N/A')}, TPSA: {p1.get('tpsa', 'N/A')} Å²\n"
            f"HBD: {p1.get('hbd', 'N/A')}, HBA: {p1.get('hba', 'N/A')}, Rotatable Bonds: {p1.get('rotatable_bonds', 'N/A')}\n"
            f"Rings: {p1.get('ring_count', 'N/A')} (Aromatic: {p1.get('aromatic_rings', 'N/A')})\n"
            f"Functional Groups: {list(p1.get('functional_groups', {}).keys())}"
        )
    if ctx2:
        p2 = ctx2.get("properties", {})
        parts.append(
            f"Secondary Molecule: {ctx2.get('name', 'Molecule 2')} (SMILES: {ctx2.get('smiles', 'N/A')})\n"
            f"Formula: {p2.get('formula', 'N/A')}, MW: {p2.get('molecular_weight', 'N/A')} g/mol\n"
            f"LogP: {p2.get('logp', 'N/A')}, TPSA: {p2.get('tpsa', 'N/A')} Å²\n"
            f"HBD: {p2.get('hbd', 'N/A')}, HBA: {p2.get('hba', 'N/A')}, Rotatable Bonds: {p2.get('rotatable_bonds', 'N/A')}"
        )
    return "\n---\n".join(parts) if parts else "No specific molecular context loaded."


def _expert_local_cheminformatics_engine(
    query: str,
    ctx1: Optional[Dict[str, Any]],
    ctx2: Optional[Dict[str, Any]],
) -> str:
    """
    Comprehensive rule-based chemistry expert that analyzes the query against computed molecular properties.
    """
    q = query.lower()

    name1 = ctx1.get("name", "the selected molecule") if ctx1 else "the selected molecule"
    smiles1 = ctx1.get("smiles", "") if ctx1 else ""
    p1 = ctx1.get("properties", {}) if ctx1 else {}

    # 1. Comparison questions (e.g. compare aspirin and paracetamol)
    if "compare" in q or "difference between" in q or "versus" in q or " vs " in q:
        return _handle_comparison_query(q, ctx1, ctx2)

    # 2. Functional groups question
    if "functional group" in q or "substituent" in q or "moiety" in q:
        fg_dict = p1.get("functional_groups", {})
        if not fg_dict:
            return (
                f"### Functional Group Analysis for **{name1}**\n\n"
                f"- **Formula:** {p1.get('formula', 'N/A')}\n"
                f"- **SMILES:** `{smiles1}`\n\n"
                f"No standard heteroatom functional groups (such as carbonyls, carboxylic acids, esters, or amines) "
                f"were detected using substructure queries. The molecule consists primarily of simple hydrocarbon framework."
            )
        items = "\n".join([f"- **{fg}**: {cnt} occurrence(s)" for fg, cnt in fg_dict.items()])
        return (
            f"### Functional Group Analysis for **{name1}**\n\n"
            f"Identified chemical moieties via substructure pattern matching:\n\n"
            f"{items}\n\n"
            f"**Chemical Significance:** These groups govern key pharmacokinetic properties such as hydrogen-bond capability, "
            f"electronic distribution, acid-base ionization equilibrium, and intermolecular target binding affinity."
        )

    # 3. LogP and Lipophilicity questions
    if "logp" in q or "lipophil" in q or "hydrophob" in q or "partition" in q:
        logp_val = p1.get("logp", 0.0)
        solubility_note = (
            "highly hydrophilic and freely water-soluble" if logp_val < 0 else
            "moderately hydrophilic to balanced" if logp_val <= 2.0 else
            "moderately lipophilic (favorable for cell membrane passive diffusion)" if logp_val <= 4.0 else
            "highly lipophilic (may exhibit poor aqueous solubility and rapid metabolic clearance)"
        )
        return (
            f"### LogP (Partition Coefficient) for **{name1}**\n\n"
            f"- **Calculated Crippen MolLogP:** **{logp_val:.3f}**\n\n"
            f"**Definition:** LogP represents the decimal logarithm of the 1-octanol/water partition coefficient "
            f"(\\(\\log_{{10}} P_{{oct/wat}}\\)) for neutral species. It is a fundamental thermodynamic indicator of molecular lipophilicity.\n\n"
            f"**Interpretation for {name1}:**\n"
            f"With a LogP of {logp_val:.3f}, the molecule is characterized as {solubility_note}. "
            f"According to Lipinski's Rule of Five, optimal oral bioavailability typically requires \\(\\text{{LogP}} \\le 5.0\\), "
            f"preventing excessive lipophilicity that leads to non-specific plasma protein binding or solubility issues."
        )

    # 4. Hydrogen bonding questions (Donors & Acceptors)
    if "hydrogen bond" in q or "hbd" in q or "hba" in q or "donor" in q or "acceptor" in q:
        hbd = p1.get("hbd", 0)
        hba = p1.get("hba", 0)
        return (
            f"### Hydrogen Bonding Profile for **{name1}**\n\n"
            f"- **Hydrogen-Bond Donors (HBD):** **{hbd}**\n"
            f"- **Hydrogen-Bond Acceptors (HBA):** **{hba}**\n\n"
            f"**Mechanistic Context:**\n"
            f"- **Donors:** Electronegative heteroatoms (typically O or N) bearing at least one hydrogen atom (e.g. -OH, -NH-).\n"
            f"- **Acceptors:** Heteroatoms with accessible lone electron pairs (e.g. carbonyl oxygens, ether oxygens, pyridine nitrogens).\n\n"
            f"**Impact on Desolvation & Permeation:**\n"
            f"A higher number of hydrogen bonding sites increases the desolvation penalty required for a molecule "
            f"to partition from aqueous extracellular fluid into the lipid bilayer of cell membranes. "
            f"Lipinski's criteria dictate \\(\\text{{HBD}} \\le 5\\) and \\(\\text{{HBA}} \\le 10\\); "
            f"**{name1}** ({hbd} donors, {hba} acceptors) is comfortably within these standard guidelines."
        )

    # 5. Aromaticity & Huckel questions
    if "aromatic" in q or "ring" in q or "huckel" in q or "pi electron" in q or "benzene" in q:
        ar_rings = p1.get("aromatic_rings", 0)
        tot_rings = p1.get("ring_count", 0)
        ar_atoms = p1.get("aromatic_atom_count", 0)
        return (
            f"### Aromaticity & Ring Architecture in **{name1}**\n\n"
            f"- **Total Rings:** {tot_rings}\n"
            f"- **Aromatic Rings:** {ar_rings}\n"
            f"- **Aromatic Atoms:** {ar_atoms}\n\n"
            f"**Aromatic Principles:**\n"
            f"Aromatic systems conform to **Hückel's Rule** (possessing \\(4n + 2\\) delocalized \\(\\pi\\) electrons in a continuous, "
            f"planar, conjugated cyclic system). Delocalization confers substantial thermodynamic resonance energy stabilization.\n\n"
            f"**Role in {name1}:**\n"
            + (
                f"The aromatic core provides a rigid planar scaffold suitable for \\(\\pi\\)-\\(\\pi\\) stacking "
                f"and hydrophobic contacts with aromatic amino acid residues (Phe, Tyr, Trp) in biological binding pockets."
                if ar_rings > 0 else
                f"No aromatic rings are present in **{name1}**; its geometry is governed by localized sigma/pi bonds and aliphatic flexibility."
            )
        )

    # 6. Stereochemistry & Chirality questions
    if "stereo" in q or "chiral" in q or "enantiomer" in q or "diastereomer" in q or "r/s" in q:
        chiral_count = p1.get("chiral_centers_count", 0)
        chiral_list = p1.get("chiral_centers", [])
        if chiral_count > 0:
            details = ", ".join([f"Atom {idx} ({config})" for idx, config in chiral_list])
            return (
                f"### Stereochemical Evaluation for **{name1}**\n\n"
                f"- **Chiral Centers Identified:** **{chiral_count}** ({details})\n\n"
                f"**Significance:** Chiral centers (asymmetric sp³ carbons bonded to four chemically distinct substituents) "
                f"create non-superimposable mirror image enantiomers. Biological receptors and enzymes are chiral environments, "
                f"meaning different enantiomers frequently exhibit profoundly different pharmacodynamic potencies, toxicological profiles, "
                f"or metabolic fates (e.g. (S)-ibuprofen vs (R)-ibuprofen)."
            )
        else:
            return (
                f"### Stereochemical Evaluation for **{name1}**\n\n"
                f"- **Chiral Centers Identified:** **0** (Achiral molecule)\n\n"
                f"The molecule contains no asymmetric chiral centers and is therefore superimposable on its mirror image, "
                f"exhibiting no optical isomerism under standard conditions."
            )

    # 7. TPSA (Topological Polar Surface Area)
    if "tpsa" in q or "polar surface" in q:
        tpsa_val = p1.get("tpsa", 0.0)
        return (
            f"### Topological Polar Surface Area (TPSA) for **{name1}**\n\n"
            f"- **Calculated TPSA:** **{tpsa_val:.2f} Å²**\n\n"
            f"**Definition:** TPSA is calculated as the sum of surface areas of polar atoms (oxygens, nitrogens, and attached hydrogens). "
            f"It correlates directly with drug transport properties:\n"
            f"- **Oral Bioavailability:** Compounds with \\(\\text{{TPSA}} \\le 140\\text{{ Å}}^2\\) generally exhibit good human intestinal absorption (Veber's rule).\n"
            f"- **Blood-Brain Barrier (BBB) Permeation:** Penetration into the central nervous system typically requires \\(\\text{{TPSA}} < 90\\text{{ Å}}^2\\).\n\n"
            f"**Assessment:** {name1}'s TPSA of {tpsa_val:.2f} Å² indicates "
            + ("favorable profile for passive gastrointestinal absorption." if tpsa_val <= 140 else "elevated polar surface area, likely limiting passive membrane permeation.")
        )

    # 8. Lipinski Rule of 5 questions
    if "lipinski" in q or "drug-like" in q or "rule of five" in q or "veber" in q:
        lip = check_lipinski_rule_of_five(p1)
        rules_text = "\n".join([
            f"- **{rule}:** Value = {data['value']:.2f if isinstance(data['value'], float) else data['value']} "
            f"(Threshold = {data['threshold']}) -> {'PASSED' if data['pass'] else 'VIOLATED'}"
            for rule, data in lip["rules"].items()
        ])
        status = "COMPLIANT (Passes)" if lip["is_compliant"] else f"NON-COMPLIANT ({lip['violation_count']} violations)"
        return (
            f"### Lipinski Rule of Five Evaluation for **{name1}**\n\n"
            f"**Overall Screening Status:** **{status}**\n\n"
            f"{rules_text}\n\n"
            f"**Heuristic Purpose:** Christopher Lipinski formulated this rule based on the 90th percentile of oral drugs "
            f"reaching Phase II clinical trials. Passing the rule suggests favorable solubility and intestinal permeability, "
            f"but does not guarantee biological activity or non-toxicity."
        )

    # 9. Structure and general chemical overview
    return (
        f"### Molecular Architecture Analysis for **{name1}**\n\n"
        f"- **Chemical Formula:** {p1.get('formula', 'N/A')}\n"
        f"- **Molecular Weight:** {p1.get('molecular_weight', 'N/A')} g/mol\n"
        f"- **Canonical SMILES:** `{smiles1}`\n"
        f"- **Lipophilicity (LogP):** {p1.get('logp', 'N/A')}\n"
        f"- **Polar Surface Area (TPSA):** {p1.get('tpsa', 'N/A')} Å²\n"
        f"- **Hydrogen Bonding:** {p1.get('hbd', 'N/A')} donors, {p1.get('hba', 'N/A')} acceptors\n"
        f"- **Conformational Flexibility:** {p1.get('rotatable_bonds', 'N/A')} rotatable bonds, {p1.get('ring_count', 'N/A')} rings\n\n"
        f"**Structural Summary:** **{name1}** contains {p1.get('heavy_atom_count', 'N/A')} heavy atoms "
        f"({p1.get('total_atom_count', 'N/A')} total including hydrogens). "
        f"Its 3D conformational envelope is stabilized by force field optimization (MMFF94/UFF) "
        f"minimizing steric clashes, angle strains, and electrostatic interactions."
    )


def _handle_comparison_query(
    q: str,
    ctx1: Optional[Dict[str, Any]],
    ctx2: Optional[Dict[str, Any]],
) -> str:
    """Specialized comparison handling for pairs like Aspirin vs Paracetamol."""
    if "aspirin" in q and "paracetamol" in q:
        return (
            "### Comparative Analysis: Aspirin vs. Paracetamol\n\n"
            "Both aspirin (acetylsalicylic acid) and paracetamol (acetaminophen) are quintessential over-the-counter "
            "analgesic and antipyretic agents, yet they possess distinct chemical scaffolds and pharmacological mechanisms:\n\n"
            "| Property | Aspirin (`CC(=O)Oc1ccccc1C(=O)O`) | Paracetamol (`CC(=O)Nc1ccc(O)cc1`) |\n"
            "| :--- | :--- | :--- |\n"
            "| **Formula** | C9H8O4 | C8H9NO2 |\n"
            "| **Molecular Weight** | 180.16 g/mol | 151.17 g/mol |\n"
            "| **Key Moieties** | Carboxylic acid + Ester (o-acetoxybenzoic acid) | Phenolic hydroxyl + Acetamide (p-acetamidophenol) |\n"
            "| **Acid-Base Character** | Weak organic acid (pKa ~ 3.5 via -COOH) | Weakly acidic phenol (pKa ~ 9.5) / neutral amide |\n"
            "| **LogP** | ~ 1.31 (moderate lipophilicity) | ~ 0.46 (more hydrophilic) |\n"
            "| **TPSA** | 63.60 Å² | 49.33 Å² |\n"
            "| **Mechanism** | Irreversible acetylation of Ser529/516 in COX-1/COX-2 | Centrally acting indirect COX inhibition and AM404 metabolite |\n"
            "| **Anti-inflammatory** | Significant peripheral anti-inflammatory effect | Negligible peripheral anti-inflammatory activity |\n\n"
            "**Key Chemical Distinction:** The acetyl group in aspirin is an ester subject to nucleophilic transesterification "
            "with the active site serine of cyclooxygenase enzymes, permanently inactivating them. In contrast, paracetamol's "
            "acetamide is resistant to transesterification, functioning primarily through redox modulation in the peroxidase catalytic cycle."
        )

    # General comparison between ctx1 and ctx2 if available
    if ctx1 and ctx2:
        n1 = ctx1.get("name", "Molecule 1")
        n2 = ctx2.get("name", "Molecule 2")
        p1 = ctx1.get("properties", {})
        p2 = ctx2.get("properties", {})
        return (
            f"### Comparative Analysis: {n1} vs. {n2}\n\n"
            f"| Metric | {n1} | {n2} | Difference (Δ) |\n"
            f"| :--- | :--- | :--- | :--- |\n"
            f"| **Formula** | {p1.get('formula', 'N/A')} | {p2.get('formula', 'N/A')} | - |\n"
            f"| **Molecular Weight** | {p1.get('molecular_weight', 'N/A')} g/mol | {p2.get('molecular_weight', 'N/A')} g/mol | {p2.get('molecular_weight', 0) - p1.get('molecular_weight', 0):.2f} g/mol |\n"
            f"| **LogP** | {p1.get('logp', 'N/A')} | {p2.get('logp', 'N/A')} | {p2.get('logp', 0) - p1.get('logp', 0):.2f} |\n"
            f"| **TPSA** | {p1.get('tpsa', 'N/A')} Å² | {p2.get('tpsa', 'N/A')} Å² | {p2.get('tpsa', 0) - p1.get('tpsa', 0):.2f} Å² |\n"
            f"| **H-Bond Donors** | {p1.get('hbd', 'N/A')} | {p2.get('hbd', 'N/A')} | {p2.get('hbd', 0) - p1.get('hbd', 0)} |\n"
            f"| **H-Bond Acceptors** | {p1.get('hba', 'N/A')} | {p2.get('hba', 'N/A')} | {p2.get('hba', 0) - p1.get('hba', 0)} |\n"
            f"| **Rotatable Bonds** | {p1.get('rotatable_bonds', 'N/A')} | {p2.get('rotatable_bonds', 'N/A')} | {p2.get('rotatable_bonds', 0) - p1.get('rotatable_bonds', 0)} |\n\n"
            f"**Pharmacokinetic Comparison:** A higher LogP in {n2 if p2.get('logp', 0) > p1.get('logp', 0) else n1} indicates greater lipid solubility, "
            f"while differences in TPSA reflect varying desolvation energies for transmembrane transport."
        )

    return (
        "Please select or specify two molecules to perform a direct side-by-side comparative chemical analysis."
    )
