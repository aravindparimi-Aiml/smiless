"""
Cheminformatics Virtual Laboratory - Assessment & Examination Module
Provides tiered multiple-choice assessments (Beginner, Intermediate, Advanced)
with automated grading, performance analytics, and comprehensive scientific explanations.
"""

from typing import Dict, Any, List


ASSESSMENT_BANKS: Dict[str, List[Dict[str, Any]]] = {
    "Beginner": [
        {
            "id": "beg_1",
            "category": "SMILES Notation",
            "question": "In Simplified Molecular Input Line Entry System (SMILES), how are branching substituents typically represented?",
            "options": [
                "Enclosed within square brackets [ ]",
                "Enclosed within parentheses ( )",
                "Preceded by an asterisk *",
                "Enclosed within curly braces { }",
            ],
            "correct_index": 1,
            "explanation": (
                "In SMILES syntax, branches from the main chain are enclosed within parentheses, for example "
                "isobutane is represented as CC(C)C. Square brackets [ ] are reserved for explicit atom specifications "
                "(such as formal charges [O-], explicit hydrogens [NH4+], or isotopes [13C])."
            )
        },
        {
            "id": "beg_2",
            "category": "Molecular Formulas",
            "question": "What is the correct molecular formula for Ethanol, represented by the SMILES string 'CCO'?",
            "options": [
                "C2H4O",
                "C2H6O",
                "C2H5O2",
                "CH3O",
            ],
            "correct_index": 1,
            "explanation": (
                "Ethanol has two carbon atoms, six hydrogen atoms (three on the methyl carbon, two on the methylene "
                "carbon, and one on the hydroxyl group), and one oxygen atom: C2H6O. (Molecular weight ~ 46.07 g/mol)."
            )
        },
        {
            "id": "beg_3",
            "category": "Functional Groups",
            "question": "Which characteristic functional group is present in Acetic Acid, represented by SMILES 'CC(=O)O'?",
            "options": [
                "Ester",
                "Ketone",
                "Carboxylic acid",
                "Aldehyde",
            ],
            "correct_index": 2,
            "explanation": (
                "The substructure -C(=O)OH consists of a carbonyl group (C=O) directly bonded to a hydroxyl group (-OH), "
                "defining a carboxylic acid."
            )
        },
        {
            "id": "beg_4",
            "category": "Bond Types & Notation",
            "question": "In standard SMILES notation, which symbol represents a carbon-carbon double bond?",
            "options": [
                "- (hyphen)",
                "= (equals sign)",
                "# (hash)",
                ": (colon)",
            ],
            "correct_index": 1,
            "explanation": (
                "In SMILES notation: '-' indicates a single bond (often omitted as implicit), '=' represents a double bond, "
                "'#' represents a triple bond, and ':' represents an aromatic bond."
            )
        },
        {
            "id": "beg_5",
            "category": "Aromaticity",
            "question": "In SMILES, lowercase atom symbols such as 'c1ccccc1' denote what type of chemical bonding?",
            "options": [
                "Radical electrons",
                "Aromatic ring atoms",
                "Isotopic labeling",
                "Ionized formal charges",
            ],
            "correct_index": 1,
            "explanation": (
                "Lowercase letters (c, n, o, s) indicate aromatic atoms sharing delocalized pi electrons within a conjugated "
                "ring system, such as benzene (c1ccccc1)."
            )
        },
    ],
    "Intermediate": [
        {
            "id": "int_1",
            "category": "Aromaticity & Hückel's Rule",
            "question": "Benzene (c1ccccc1) contains 6 delocalized pi electrons. According to Hückel's Rule (4n + 2 pi electrons), what is the value of n?",
            "options": [
                "n = 0",
                "n = 1",
                "n = 2",
                "n = 6",
            ],
            "correct_index": 1,
            "explanation": (
                "Hückel's rule states that monocyclic planar conjugated systems with (4n + 2) pi electrons exhibit aromatic "
                "stability. For benzene, 4(1) + 2 = 6, yielding n = 1."
            )
        },
        {
            "id": "int_2",
            "category": "Stereochemistry & Chirality",
            "question": "Ibuprofen is represented by the SMILES 'CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O'. What does the '@' syntax indicate?",
            "options": [
                "An aromatic nitrogen atom",
                "A radical cation center",
                "Tetrahedral chiral center with specific enantiomeric spatial configuration",
                "A radioactive isotope marker",
            ],
            "correct_index": 2,
            "explanation": (
                "In SMILES, '@' and '@@' denote chiral orientation around a tetrahedral stereocenter: '@' signifies "
                "an anti-clockwise (counterclockwise) sequence of neighbors looking down the bond from the preceding atom, "
                "while '@@' signifies clockwise ordering."
            )
        },
        {
            "id": "int_3",
            "category": "Physicochemical Properties",
            "question": "What does a high positive LogP value (e.g. LogP = 3.8) indicate regarding a compound's physical behavior?",
            "options": [
                "High aqueous solubility and complete hydrophilicity",
                "Preference for non-polar lipid phases over water (high lipophilicity)",
                "Rapid gas-phase evaporation rate",
                "Strong acidic ionization in neutral water",
            ],
            "correct_index": 1,
            "explanation": (
                "LogP is the logarithm of the 1-octanol/water partition coefficient. A positive value above 0 indicates that "
                "the molecule partitions preferentially into the hydrophobic octanol phase, demonstrating significant lipophilicity."
            )
        },
        {
            "id": "int_4",
            "category": "Drug-Likeness Rules",
            "question": "Under Lipinski's Rule of Five for oral drug-likeness, what is the maximum recommended count for Hydrogen Bond Donors (HBD)?",
            "options": [
                "<= 10",
                "<= 5",
                "<= 2",
                "<= 140",
            ],
            "correct_index": 1,
            "explanation": (
                "Lipinski's Rule of Five defines optimal oral drug absorption criteria as: MW <= 500 g/mol, LogP <= 5.0, "
                "Hydrogen Bond Donors (HBD) <= 5, and Hydrogen Bond Acceptors (HBA) <= 10."
            )
        },
        {
            "id": "int_5",
            "category": "Topological Polar Surface Area",
            "question": "According to Veber's bioavailability rules, what is the upper threshold of TPSA for acceptable oral bioavailability in rats?",
            "options": [
                "<= 50 Å²",
                "<= 90 Å²",
                "<= 140 Å²",
                "<= 500 Å²",
            ],
            "correct_index": 2,
            "explanation": (
                "Veber et al. established that compounds with <= 10 rotatable bonds and a Topological Polar Surface Area "
                "(TPSA) <= 140 Å² have a significantly higher probability of exhibiting >= 20% oral bioavailability."
            )
        },
    ],
    "Advanced": [
        {
            "id": "adv_1",
            "category": "3D Conformer & Force Fields",
            "question": "In computational conformer optimization, why is MMFF94 typically preferred over UFF for organic drug-like molecules?",
            "options": [
                "MMFF94 requires no computer memory or matrix inversion",
                "MMFF94 is specifically parameterized for organic and drug-like functional groups and non-bonded interactions",
                "UFF cannot calculate carbon-carbon bonds",
                "MMFF94 performs full DFT quantum electronic wave equation solving",
            ],
            "correct_index": 1,
            "explanation": (
                "The Merck Molecular Force Field (MMFF94) was explicitly parameterized and validated against high-level "
                "ab initio quantum calculations and crystal structures for organic and medicinal compounds, delivering "
                "superior conformational geometries and non-bonded electrostatic interactions compared to the generic Universal Force Field (UFF)."
            )
        },
        {
            "id": "adv_2",
            "category": "Molecular Fingerprints",
            "question": "What is the algorithmic basis of Morgan / ECFP4 fingerprints in cheminformatics?",
            "options": [
                "Counting predefined substructure patterns from a dictionary of 166 keys",
                "Circular neighborhood atom environments iteratively gathered up to radius 2 and hashed to a bit vector",
                "Measuring Euclidean 3D atomic coordinates from X-ray diffraction",
                "Calculating ultraviolet absorption wavelengths",
            ],
            "correct_index": 1,
            "explanation": (
                "Morgan / Extended-Connectivity Fingerprints (ECFP4) apply the Morgan algorithm: each atom's initial state "
                "is updated in radial iterations (radius=2, diameter=4) incorporating topological neighbor pathways, "
                "which are hashed into integer identifiers and folded onto a fixed-length bit vector."
            )
        },
        {
            "id": "adv_3",
            "category": "Similarity Metrics",
            "question": "When comparing two molecular Morgan fingerprints with on-bit counts a and b and shared bit count c, what is the Tanimoto coefficient formula?",
            "options": [
                "Tc = c / (a + b)",
                "Tc = c / (a + b - c)",
                "Tc = 2c / (a + b)",
                "Tc = (a * b) / c",
            ],
            "correct_index": 1,
            "explanation": (
                "The Tanimoto (Jaccard) coefficient is defined as the size of the intersection divided by the size of the union: "
                "Tc = c / (a + b - c). Dice similarity is 2c / (a + b)."
            )
        },
        {
            "id": "adv_4",
            "category": "Medicinal Chemistry & Bioisosterism",
            "question": "Why does Aspirin act as an irreversible inhibitor of Cyclooxygenase (COX-1), while Paracetamol does not?",
            "options": [
                "Aspirin forms a covalent bond by transferring its acetyl group to the active site Ser529 hydroxyl",
                "Aspirin contains nitrogen which coordinates with active-site zinc",
                "Paracetamol destroys the enzyme via rapid hydrolysis",
                "Paracetamol is too large to enter the catalytic channel",
            ],
            "correct_index": 0,
            "explanation": (
                "Aspirin acts as an irreversible inhibitor because its reactive ester acetyl moiety undergoes transesterification "
                "with the nucleophilic hydroxyl group of Serine 529 in COX-1 (Ser516 in COX-2), permanently blocking arachidonic "
                "acid binding. Paracetamol lacks this reactive acetyl ester."
            )
        },
        {
            "id": "adv_5",
            "category": "Distance Geometry Algorithms",
            "question": "In RDKit, what primary advantage does the ETKDG (Experimental-Torsion Knowledge Distance Geometry) algorithm provide over classical distance geometry?",
            "options": [
                "It eliminates all hydrogen atoms from calculations",
                "It biases torsion angle sampling using experimentally determined dihedral angle distributions from the Cambridge Structural Database (CSD)",
                "It replaces Newtonian physics with quantum electrodynamics",
                "It guarantees zero conformational energy for any molecule",
            ],
            "correct_index": 1,
            "explanation": (
                "Riniker and Landrum's ETKDG incorporates empirical knowledge of favored torsion angles derived from small-molecule "
                "crystal structures in the CSD and PDB, producing chemically realistic starting conformers without requiring "
                "expensive exhaustive conformer searches."
            )
        },
    ]
}


def get_assessment_questions(tier: str = "Beginner") -> List[Dict[str, Any]]:
    """Retrieve question set for specified difficulty tier."""
    return ASSESSMENT_BANKS.get(tier, ASSESSMENT_BANKS["Beginner"])


def evaluate_assessment(tier: str, user_answers: Dict[str, int]) -> Dict[str, Any]:
    """
    Score the assessment submission, calculate percentages, and return itemized review data.
    """
    questions = get_assessment_questions(tier)
    total = len(questions)
    correct_count = 0
    review_details = []

    for q in questions:
        qid = q["id"]
        chosen = user_answers.get(qid)
        is_correct = (chosen == q["correct_index"])
        if is_correct:
            correct_count += 1

        review_details.append({
            "id": qid,
            "question": q["question"],
            "category": q["category"],
            "options": q["options"],
            "chosen_index": chosen,
            "chosen_text": q["options"][chosen] if chosen is not None and 0 <= chosen < len(q["options"]) else "Unanswered",
            "correct_index": q["correct_index"],
            "correct_text": q["options"][q["correct_index"]],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    score_pct = round((correct_count / total) * 100, 1) if total > 0 else 0.0

    if score_pct >= 90:
        grade = "Distinction (Mastery)"
    elif score_pct >= 75:
        grade = "Commended (Proficient)"
    elif score_pct >= 50:
        grade = "Pass (Competent)"
    else:
        grade = "Needs Review"

    return {
        "tier": tier,
        "total_questions": total,
        "correct_count": correct_count,
        "score_percentage": score_pct,
        "grade": grade,
        "review": review_details,
    }
