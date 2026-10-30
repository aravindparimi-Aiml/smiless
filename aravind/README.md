# Cheminformatics Virtual Laboratory

[![CI/CD Pipeline](https://github.com/parimigowtham1432-stack/cheminformatics-virtual-laboratory/actions/workflows/ci.yml/badge.svg)](https://github.com/parimigowtham1432-stack/cheminformatics-virtual-laboratory/actions)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
![RDKit](https://img.shields.io/badge/RDKit-2026.09-brightgreen.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.66-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A modern, scientifically accurate, full-stack cheminformatics laboratory and molecular exploration platform. Engineered for computational chemistry research, chemical education, and in silico drug discovery screening.

---

## 🌟 Key Features

### 1. 📚 Predefined Chemical Library
- Includes **10 structurally and pharmacologically diverse reference compounds**:
  1. **Water** (`O`) — Universal polar solvent and hydrogen-bonding prototype.
  2. **Methane** (`C`) — Simplest tetrahedral alkane.
  3. **Ethanol** (`CCO`) — Primary aliphatic alcohol.
  4. **Acetic acid** (`CC(=O)O`) — Carboxylic acid.
  5. **Acetone** (`CC(=O)C`) — Polar aprotic ketone.
  6. **Benzene** (`c1ccccc1`) — Planar aromatic hydrocarbon conforming to Hückel's Rule ($4n + 2 = 6\pi$).
  7. **Caffeine** (`Cn1c(=O)c2c(ncn2C)n(C)c1=O`) — Purine alkaloid stimulant.
  8. **Aspirin** (`CC(=O)Oc1ccccc1C(=O)O`) — Acetylsalicylic acid NSAID and irreversible COX-1 inhibitor.
  9. **Paracetamol** (`CC(=O)Nc1ccc(O)cc1`) — Acetaminophen analgesic and antipyretic.
  10. **Ibuprofen** (`CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O`) — Chiral $\alpha$-methyl propionic acid NSAID.
- Automated chemical formula, exact monoisotopic weight, heavy atom count, InChI, and InChIKey resolution.

### 2. ✏️ Custom SMILES Validation & Processing
- Live syntax sanitization and valence verification via **RDKit**.
- Clear diagnostic error messages for unclosed rings, invalid atom symbols, or non-physical valence configurations.
- Automatic canonicalization and isomeric SMILES determination.

### 3. 📐 Accurate 2D Structure Depiction
- High-contrast vector **SVG** rendering with stereochemical wedge/dash notation and aromatic ring markers.
- Atom and bond highlighting for substructure focus.
- One-click downloads for SVG and PNG raster formats.

### 4. 🌐 Signature Interactive 3D Conformer Studio
- **Distance Geometry Embedding:** Generated via **ETKDGv3** (Experimental-Torsion Knowledge Distance Geometry).
- **Energy Minimization:** Optimized using the **Merck Molecular Force Field (MMFF94)** with automatic fallback to the **Universal Force Field (UFF)**.
- **WebGL Rendering:** Powered by **3Dmol.js** supporting:
  - Ball-and-Stick mode
  - Space-Filling (CPK / Van der Waals spheres)
  - Sticks representation
  - Wireframe mode
  - Van der Waals surface overlay
  - Real-time continuous auto-rotation (spin)
  - Fullscreen toggle and view recentering
  - Toggleable explicit hydrogen atoms
- **Geometric HUD Inspector:** Real-time atom inspection displaying atom index, 3D Cartesian coordinates ($X, Y, Z$), Gasteiger partial charges, and formal charges.
- **Bond Geometry Table:** Bond order classification, aromaticity, and Euclidean bond lengths in Ångströms ($\text{Å}$).
- Direct downloads for **MOL / SDF**, **PDB**, and **XYZ** coordinate files.

### 5. 📊 Physicochemical Descriptors & Screening
- Calculates:
  - Molecular Formula & Exact Molecular Weight (g/mol)
  - Crippen Partition Coefficient ($\text{LogP}$)
  - Topological Polar Surface Area ($\text{TPSA}$ in $\text{Å}^2$)
  - Hydrogen-Bond Donors ($\text{HBD}$) & Acceptors ($\text{HBA}$)
  - Rotatable Bonds count & Ring counts (aromatic and aliphatic)
  - Formal charge & Fraction $\text{Csp3}$
  - Stereochemical chiral center identification
  - Elemental composition breakdown (% weight)
- **Oral Drug-Likeness Screening:**
  - **Lipinski's Rule of Five:** $\text{MW} \le 500$, $\text{LogP} \le 5.0$, $\text{HBD} \le 5$, $\text{HBA} \le 10$.
  - **Veber's Bioavailability Filter:** $\text{RotBonds} \le 10$, $\text{TPSA} \le 140\text{ Å}^2$.
- **Molecular Fingerprints:** Morgan circular fingerprints (ECFP4 equivalent, 2048 bits), MACCS 166 structural keys, and RDKit topological fingerprints.

### 6. ⚖️ Multi-Molecule Comparative Studio
- Side-by-side 2D structure and property comparison across 2 or more compounds.
- **Interactive Radar Chart:** Normalized radar plot covering MW, LogP, TPSA, HBD, HBA, and rotatable bonds.
- **Fingerprint Similarity Matrices:**
  - Morgan / ECFP4 Tanimoto Similarity ($T_c = \frac{c}{a + b - c}$)
  - Morgan Dice Similarity ($D_c = \frac{2c}{a + b}$)
  - MACCS 166 Keys Tanimoto Similarity
- Pairwise delta table summarizing exact physical property shifts.

### 7. 🤖 AI Chemistry Assistant
- Context-aware chemistry conversational agent providing insights on active molecules.
- Queries supported: functional group inventory, LogP interpretation, H-bonding dynamics, mechanism comparisons (e.g. Aspirin vs Paracetamol), and stereochemistry.
- Configurable with LLM APIs (`OPENAI_API_KEY`) with an automatic, robust **local expert cheminformatics knowledge engine** fallback.

### 8. 📄 Publication-Quality PDF Lab Reports
- Automated PDF report compilation using **ReportLab**.
- Embedded high-resolution 2D depictions, conformer optimization parameters, complete property tables, Lipinski/Veber evaluations, and scientific disclaimers.
- Supports both single-molecule and multi-compound comparative PDF exports.

### 9. 🎓 Interactive Assessment & Examination Lab
- Tiered examination module with **Beginner**, **Intermediate**, and **Advanced** tiers.
- Topics: SMILES syntax, functional groups, aromaticity & Hückel's rule, stereochemistry, force fields (MMFF94 vs UFF), and similarity metrics.
- Instant automated grading, percentage score, grade tier, and detailed scientific explanations for every question.

### 10. 📁 Session History & Project Persistence
- Session history of all analyzed compounds.
- Export and import session workspaces via structured JSON format.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend & UI** | Streamlit, Custom Dark Scientific CSS, Glassmorphism, 3Dmol.js (WebGL), Plotly |
| **Cheminformatics Engine** | RDKit 2026.09 (Descriptors, AllChem, ETKDGv3, rdMolDraw2D, MorganGenerator) |
| **3D Force Field Optimization**| MMFF94 & UFF (Energy minimization, Gasteiger charges, Euclidean geometries) |
| **Document Generation** | ReportLab 5.1 (Platypus flowables, custom palettes, embedded vector depictions) |
| **Testing & CI/CD** | Pytest, JUnit XML reporting, GitHub Actions CI/CD matrix (Python 3.11 & 3.12) |

---

## 🚀 Quick Start & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/parimigowtham1432-stack/cheminformatics-virtual-laboratory.git
cd cheminformatics-virtual-laboratory
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
```bash
cp .env.example .env
# Edit .env to add OPENAI_API_KEY if desired for external LLM reasoning.
```

### 5. Launch the Virtual Laboratory
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Automated Testing

The project includes an extensive automated test suite covering SMILES parsing, descriptor calculations, 3D conformer optimization, 2D depictions, PDF generation, similarity metrics, and assessment grading:

```bash
# Run pytest with concise summary and JUnit XML export
pytest --junitxml=reports/test-results.xml
```

All 32 tests execute in under 2 seconds.

---

## 🔄 GitHub Actions CI/CD & Downloadable Artifacts

The repository includes a comprehensive GitHub Actions workflow located at `.github/workflows/ci.yml`.

### Workflow Pipeline Jobs
1. **Automated Testing & Chemistry Verification:** Runs test suites concurrently on Python 3.11 and 3.12. Generates machine-readable JUnit XML reports.
2. **Build & Architecture Validation:** Byte-compiles all modules, checks dependencies and configuration files, and bundles a clean deployment package.
3. **Artifact Publishing:** Automatically publishes downloadable artifacts to the GitHub Actions run:
   - `cheminformatics-test-reports-py3.11`: XML test logs and diagnostic reports.
   - `cheminformatics-test-reports-py3.12`: XML test logs and diagnostic reports.
   - `cheminformatics-deployment-package`: Production-ready bundle containing verified application files.
4. **Deployment Readiness:** Verifies prerequisites for cloud hosting.

### How to Download Artifacts from GitHub
1. Navigate to the **Actions** tab of the repository on GitHub.
2. Click on the latest workflow run on `main`.
3. Scroll down to the **Artifacts** section at the bottom of the summary page.
4. Click on `cheminformatics-test-reports` or `cheminformatics-deployment-package` to download the zip archives.

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

This application is natively configured for deployment to **Streamlit Community Cloud**:

1. Fork or push this repository to your GitHub account.
2. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub credentials.
3. Click **"New app"**.
4. Select your repository: `cheminformatics-virtual-laboratory`.
5. Specify the branch: `main`.
6. Specify the main file path: `app.py`.
7. (Optional) In **Advanced Settings**, add secrets:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
8. Click **"Deploy!"**. Streamlit Community Cloud will automatically install dependencies from `requirements.txt` and launch the application.

---

## ⚖️ Scientific Disclaimer

*The Cheminformatics Virtual Laboratory provides in silico computational chemistry models, force field approximations, and empirical screening heuristics for academic and research purposes. Calculated properties (such as LogP, TPSA, HBD, and HBA) and screening rules (such as Lipinski's Rule of Five) do not establish pharmacological efficacy, safety, metabolic stability, or clinical suitability. Conformer models represent single calculated energy minima and do not account for dynamic solvent interactions or conformational ensembles.*

---

## 📄 License
This project is licensed under the MIT License.
