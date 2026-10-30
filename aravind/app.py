"""
Cheminformatics Virtual Laboratory
A modern, scientifically rigorous web application for molecular exploration, 2D/3D visualization,
physicochemical analysis, drug-likeness screening, comparative cheminformatics, and AI assistance.
"""

import os
import sys
from pathlib import Path

# Ensure application directory and modules are in sys.path (supports nested repo paths in Streamlit Cloud)
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import json
from datetime import datetime, timezone
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from chem_engine.molecules import (
    PREDEFINED_MOLECULES,
    MoleculeData,
    list_predefined_molecules,
    get_predefined_molecule,
    parse_and_validate_smiles,
)
from chem_engine.properties import (
    calculate_properties,
    check_lipinski_rule_of_five,
    check_veber_rules,
    calculate_elemental_composition,
    generate_fingerprints,
)
from chem_engine.conformer import (
    generate_3d_conformer,
    extract_3d_coordinates,
    calculate_bond_distances,
)
from chem_engine.depict import (
    generate_2d_svg,
    generate_2d_png,
)
from chem_engine.comparison import (
    compare_molecules,
)
from chem_engine.assistant import (
    ask_chemistry_assistant,
)
from chem_engine.pdf_report import (
    generate_molecule_pdf_report,
    generate_comparison_pdf_report,
)
from chem_engine.assessment import (
    get_assessment_questions,
    evaluate_assessment,
)
from ui.styles import apply_dark_scientific_theme
from ui.viewer3d import render_3d_molecular_viewer


# Page Configuration
st.set_page_config(
    page_title="Cheminformatics Virtual Laboratory",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Dark Scientific Theme Styles
apply_dark_scientific_theme()


# Session State Initialization
if "active_molecule" not in st.session_state:
    st.session_state.active_molecule = get_predefined_molecule("Aspirin")

if "history" not in st.session_state:
    st.session_state.history = [m.to_dict() for m in list_predefined_molecules()]

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Welcome to the Cheminformatics Virtual Laboratory Assistant. Ask me about functional groups, molecular properties, aromaticity, stereochemistry, or compare drug molecules like aspirin and paracetamol."
        }
    ]

if "assessment_answers" not in st.session_state:
    st.session_state.assessment_answers = {}

if "assessment_submitted" not in st.session_state:
    st.session_state.assessment_submitted = False


# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🧪 Virtual Laboratory")
    st.markdown(
        "<span style='color: #00d2ff; font-weight: 600; font-size: 0.85rem;'>RDKit 2026.09 • MMFF94 • 3Dmol.js</span>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    nav_selection = st.radio(
        "Laboratory Workspaces",
        [
            "🧪 Molecular Explorer",
            "📊 Property Analysis",
            "⚖️ Molecule Comparison",
            "🤖 AI Chemistry Assistant",
            "📄 PDF Lab Reports",
            "🎓 Assessment Lab",
            "📁 Saved Projects & History",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("#### ⚡ Quick Switch Molecule")
    predefined_names = [m.name for m in list_predefined_molecules()]
    current_name = st.session_state.active_molecule.name if st.session_state.active_molecule else "Aspirin"
    default_idx = predefined_names.index(current_name) if current_name in predefined_names else 0

    selected_quick_name = st.selectbox("Library Preset", predefined_names, index=default_idx)
    if selected_quick_name and (not st.session_state.active_molecule or st.session_state.active_molecule.name != selected_quick_name):
        st.session_state.active_molecule = get_predefined_molecule(selected_quick_name)
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='font-size: 0.75rem; color: #64748b; line-height: 1.4;'>"
        "Cheminformatics Virtual Laboratory<br/>"
        "Advanced In Silico Molecular Modeling & Chemical Property Analytics"
        "</div>",
        unsafe_allow_html=True,
    )


# Top Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-title">Cheminformatics Virtual Laboratory</div>
        <div class="hero-subtitle">
            Advanced computational chemistry workspace: 2D structure depiction, 3D force field conformer optimization,
            physicochemical descriptor computation, and drug-likeness screening.
        </div>
        <div>
            <span class="tag-badge">10 Predefined Standards</span>
            <span class="tag-badge">Custom SMILES Validator</span>
            <span class="tag-badge">ETKDGv3 + MMFF94</span>
            <span class="tag-badge">Lipinski & Veber Screening</span>
            <span class="tag-badge">ReportLab PDF Export</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Active Molecule Reference
active_mol: MoleculeData = st.session_state.active_molecule


# ==============================================================================
# WORKSPACE 1: MOLECULAR EXPLORER
# ==============================================================================
if nav_selection == "🧪 Molecular Explorer":
    st.markdown("### 🧪 Molecular Explorer & 3D Conformer Studio")

    # Tabs: Predefined Library vs Custom SMILES
    tab_lib, tab_custom = st.tabs(["📚 Predefined Chemical Library (10 Compounds)", "✏️ Custom SMILES Input & Validation"])

    with tab_lib:
        st.markdown("Select a molecule from the validated library of 10 reference compounds:")

        cols = st.columns(5)
        all_predefined = list_predefined_molecules()
        for idx, mol_item in enumerate(all_predefined):
            col_target = cols[idx % 5]
            with col_target:
                is_selected = (active_mol and active_mol.name == mol_item.name)
                card_border = "#00d2ff" if is_selected else "#30363d"
                st.markdown(
                    f"""
                    <div style="background: #161b22; border: 1.5px solid {card_border}; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                        <div style="font-weight: 700; color: #e6edf3; font-size: 0.95rem;">{mol_item.name}</div>
                        <div style="font-size: 0.75rem; color: #00d2ff;">{mol_item.formula}</div>
                        <div style="font-size: 0.75rem; color: #8b949e;">{mol_item.molecular_weight:.1f} g/mol</div>
                        <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 4px;">{mol_item.category}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Load {mol_item.name}", key=f"btn_load_{mol_item.name}", use_container_width=True):
                    st.session_state.active_molecule = mol_item
                    st.rerun()

    with tab_custom:
        st.markdown("#### Enter Custom SMILES String")
        col_input, col_meta = st.columns([3, 1])

        with col_input:
            custom_smiles_input = st.text_input(
                "SMILES String",
                value=active_mol.smiles if active_mol else "CCO",
                placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O or [C@@H](N)C(=O)O",
                help="Enter valid chemical SMILES syntax. Automatic valence check and sanitization will execute.",
            )

        with col_meta:
            custom_name_input = st.text_input(
                "Molecule Label",
                value=active_mol.name if active_mol and not active_mol.is_predefined else "",
                placeholder="Optional Name",
            )

        col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
        with col_act1:
            validate_btn = st.button("🔬 Validate & Load", type="primary", use_container_width=True)
        with col_act2:
            reset_btn = st.button("↺ Reset to Aspirin", use_container_width=True)

        if reset_btn:
            st.session_state.active_molecule = get_predefined_molecule("Aspirin")
            st.rerun()

        if validate_btn:
            with st.spinner("Sanitizing and validating SMILES via RDKit..."):
                mol_data, err_msg = parse_and_validate_smiles(custom_smiles_input, custom_name_input)
                if err_msg:
                    st.error(f"❌ Validation Error: {err_msg}")
                else:
                    st.success(f"✅ Successfully validated: **{mol_data.name}** ({mol_data.formula}, MW: {mol_data.molecular_weight:.2f} g/mol)")
                    st.session_state.active_molecule = mol_data
                    # Add to session history if not already present
                    exists = any(h["canonical_smiles"] == mol_data.canonical_smiles for h in st.session_state.history)
                    if not exists:
                        st.session_state.history.append(mol_data.to_dict())
                    st.rerun()

    st.markdown("---")

    # Display Active Molecule Workspace
    st.markdown(f"#### 🔍 Active Structure: <span style='color: #00d2ff;'>{active_mol.name}</span>", unsafe_allow_html=True)
    if active_mol.description:
        st.markdown(f"*{active_mol.description}*")

    # Metadata Pills
    st.markdown(
        f"""
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
            <span class="tag-badge">Formula: <b>{active_mol.formula}</b></span>
            <span class="tag-badge">MW: <b>{active_mol.molecular_weight:.3f} g/mol</b></span>
            <span class="tag-badge">Heavy Atoms: <b>{active_mol.heavy_atom_count}</b></span>
            <span class="tag-badge">Class: <b>{active_mol.category}</b></span>
            <span class="tag-badge">Chiral Centers: <b>{len(active_mol.chiral_centers)}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Side-by-Side 2D Depiction and 3D Interactive Conformer
    col_2d, col_3d = st.columns([1, 1])

    with col_2d:
        st.markdown("##### 📐 Accurate 2D Depiction (RDKit)")
        try:
            svg_content = generate_2d_svg(active_mol.smiles, width=500, height=380, dark_theme=False)
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                    {svg_content}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Export Controls
            subcol_a, subcol_b = st.columns(2)
            with subcol_a:
                st.download_button(
                    "⬇️ Download 2D SVG",
                    data=svg_content,
                    file_name=f"{active_mol.name.lower().replace(' ', '_')}_2d.svg",
                    mime="image/svg+xml",
                    use_container_width=True,
                )
            with subcol_b:
                png_bytes = generate_2d_png(active_mol.smiles, width=600, height=450)
                st.download_button(
                    "⬇️ Download 2D PNG",
                    data=png_bytes,
                    file_name=f"{active_mol.name.lower().replace(' ', '_')}_2d.png",
                    mime="image/png",
                    use_container_width=True,
                )
        except Exception as e:
            st.error(f"Error rendering 2D depiction: {e}")

        # Canonical & InChI Strings
        with st.expander("📋 Chemical Identifiers & Notation", expanded=False):
            st.text_input("Canonical SMILES", value=active_mol.canonical_smiles, disabled=True)
            st.text_input("Isomeric SMILES", value=active_mol.isomeric_smiles, disabled=True)
            st.text_input("InChI", value=active_mol.inchi, disabled=True)
            st.text_input("InChIKey", value=active_mol.inchikey, disabled=True)

    with col_3d:
        st.markdown("##### 🌐 Interactive 3D Molecular Conformer (3Dmol.js)")
        try:
            with st.spinner("Generating 3D conformer with ETKDGv3 and MMFF94 force field..."):
                conf_result = generate_3d_conformer(active_mol.smiles)

            st.markdown(
                f"""
                <div class="conformer-banner">
                    <b>3D Conformer:</b> Force Field: <b>{conf_result.force_field}</b> |
                    Min. Energy: <b>{conf_result.energy_kcal_mol:.2f} kcal/mol</b> |
                    Total Atoms: <b>{conf_result.atom_count}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Render 3D WebGL Viewer
            render_3d_molecular_viewer(
                mol_block=conf_result.mol_block,
                height=380,
                auto_spin=False,
            )

            # Conformer Scientific Disclaimer
            st.markdown(
                f"<div class='disclaimer-box'><b>Conformer Note:</b> {conf_result.disclaimer}</div>",
                unsafe_allow_html=True,
            )

            # 3D Structure File Downloads
            dl_c1, dl_c2, dl_c3 = st.columns(3)
            with dl_c1:
                st.download_button(
                    "⬇️ MOL / SDF",
                    data=conf_result.mol_block,
                    file_name=f"{active_mol.name.lower().replace(' ', '_')}_3d.mol",
                    mime="chemical/x-mdl-molfile",
                    use_container_width=True,
                )
            with dl_c2:
                st.download_button(
                    "⬇️ PDB Block",
                    data=conf_result.pdb_block,
                    file_name=f"{active_mol.name.lower().replace(' ', '_')}_3d.pdb",
                    mime="chemical/x-pdb",
                    use_container_width=True,
                )
            with dl_c3:
                st.download_button(
                    "⬇️ XYZ Coordinates",
                    data=conf_result.xyz_block,
                    file_name=f"{active_mol.name.lower().replace(' ', '_')}_3d.xyz",
                    mime="chemical/x-xyz",
                    use_container_width=True,
                )

        except Exception as e:
            st.error(f"❌ 3D Conformer Generation Error: {e}")
            st.info("Conformer generation requires valid molecular connectivity and force field parameterization.")

    # Atom Coordinates & Bond Distances Inspector
    st.markdown("---")
    st.markdown("#### 🔬 Conformer Geometric Inspector")
    tab_atoms, tab_bonds = st.tabs(["🧬 Atomic Coordinates & Partial Charges", "📏 Bond Lengths & Types"])

    try:
        conf_res = generate_3d_conformer(active_mol.smiles)
        coords_data = extract_3d_coordinates(conf_res.rdkit_mol)
        bonds_data = calculate_bond_distances(conf_res.rdkit_mol)

        with tab_atoms:
            df_coords = pd.DataFrame(coords_data)
            st.dataframe(
                df_coords.rename(columns={
                    "index": "Atom #",
                    "symbol": "Element",
                    "atomic_num": "Atomic #",
                    "x": "X (Å)",
                    "y": "Y (Å)",
                    "z": "Z (Å)",
                    "formal_charge": "Formal Charge",
                    "partial_charge": "Gasteiger Charge",
                    "hybridization": "Hybridization",
                    "is_aromatic": "Aromatic",
                    "is_in_ring": "Ring Atom",
                }),
                use_container_width=True,
                height=260,
            )

        with tab_bonds:
            df_bonds = pd.DataFrame(bonds_data)
            st.dataframe(
                df_bonds.rename(columns={
                    "bond_index": "Bond #",
                    "atom1_index": "Atom 1 #",
                    "atom1_symbol": "Elem 1",
                    "atom2_index": "Atom 2 #",
                    "atom2_symbol": "Elem 2",
                    "bond_type": "Bond Order",
                    "length_angstrom": "Bond Length (Å)",
                    "is_aromatic": "Aromatic",
                    "is_conjugated": "Conjugated",
                }),
                use_container_width=True,
                height=260,
            )
    except Exception as e:
        st.warning(f"Could not load geometric tables: {e}")


# ==============================================================================
# WORKSPACE 2: PROPERTY ANALYSIS
# ==============================================================================
elif nav_selection == "📊 Property Analysis":
    st.markdown(f"### 📊 Molecular Property Analysis: <span style='color: #00d2ff;'>{active_mol.name}</span>", unsafe_allow_html=True)
    st.markdown("Accurately calculated physicochemical descriptors, rule-based screening, and fingerprint features.")

    props = calculate_properties(active_mol.smiles)
    lipinski = check_lipinski_rule_of_five(props)
    veber = check_veber_rules(props)

    # Key Metric Cards Grid
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-label">Molecular Weight</div>
                <div class="metric-value">{props['molecular_weight']:.2f}<span class="metric-unit">g/mol</span></div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Crippen LogP</div>
                <div class="metric-value">{props['logp']:.2f}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Polar Surface (TPSA)</div>
                <div class="metric-value">{props['tpsa']:.1f}<span class="metric-unit">Å²</span></div>
            </div>
            <div class="metric-box">
                <div class="metric-label">H-Bond Donors</div>
                <div class="metric-value">{props['hbd']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">H-Bond Acceptors</div>
                <div class="metric-value">{props['hba']}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Rotatable Bonds</div>
                <div class="metric-value">{props['rotatable_bonds']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_prop_left, col_prop_right = st.columns([1, 1])

    with col_prop_left:
        st.markdown("#### 💊 Oral Drug-Likeness Screening")

        # Lipinski Summary
        lip_status = "PASS (Compliant)" if lipinski["is_compliant"] else f"FAIL ({lipinski['violation_count']} Violations)"
        lip_color = "#3fb950" if lipinski["is_compliant"] else "#f85149"

        st.markdown(
            f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 700; color: #58a6ff; font-size: 1.05rem;">Lipinski Rule of Five</span>
                    <span style="background: {lip_color}22; color: {lip_color}; border: 1px solid {lip_color}; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem;">
                        {lip_status}
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: #cbd5e1;">
                    Evaluates solubility and intestinal permeability criteria for small molecule oral bioavailability.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Lipinski detailed rules table
        lip_rows = []
        for r_name, r_info in lipinski["rules"].items():
            lip_rows.append({
                "Rule": r_name,
                "Value": f"{r_info['value']:.2f}" if isinstance(r_info['value'], float) else r_info['value'],
                "Threshold": f"<= {r_info['threshold']}",
                "Evaluation": "PASSED" if r_info["pass"] else "VIOLATED",
            })
        st.table(pd.DataFrame(lip_rows))

        # Veber Rules
        veber_status = "PASS (Compliant)" if veber["is_compliant"] else f"FAIL ({veber['violation_count']} Violations)"
        veber_color = "#3fb950" if veber["is_compliant"] else "#f85149"
        st.markdown(
            f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 700; color: #58a6ff; font-size: 1.05rem;">Veber Bioavailability Filter</span>
                    <span style="background: {veber_color}22; color: {veber_color}; border: 1px solid {veber_color}; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem;">
                        {veber_status}
                    </span>
                </div>
                <div style="font-size: 0.85rem; color: #cbd5e1;">
                    Criteria: Rotatable bonds &le; 10 and TPSA &le; 140 Å² (permeability & passive transport).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='disclaimer-box'><b>Screening Disclaimer:</b> {lipinski['disclaimer']}</div>",
            unsafe_allow_html=True,
        )

    with col_prop_right:
        st.markdown("#### 🧪 Elemental Composition & Topology")

        # Elemental Composition
        comp = calculate_elemental_composition(active_mol.smiles)
        if comp:
            df_comp = pd.DataFrame(list(comp.items()), columns=["Element", "Weight %"])
            fig_comp = px.pie(
                df_comp,
                names="Element",
                values="Weight %",
                color_discrete_sequence=px.colors.sequential.Teal,
                hole=0.45,
            )
            fig_comp.update_layout(
                paper_bgcolor="#161b22",
                plot_bgcolor="#161b22",
                font=dict(color="#e6edf3"),
                margin=dict(l=20, r=20, t=20, b=20),
                height=220,
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        # Functional Groups
        st.markdown("##### 🏷️ Detected Functional Groups")
        fg = props.get("functional_groups", {})
        if fg:
            fg_items = "".join([f"<span class='tag-badge' style='margin-bottom: 6px;'>{k}: <b>{v}</b></span> " for k, v in fg.items()])
            st.markdown(f"<div>{fg_items}</div>", unsafe_allow_html=True)
        else:
            st.info("No common heteroatom functional groups detected.")

        # Additional Physical Descriptors
        st.markdown("##### 📐 Topology & Constitution")
        top_data = {
            "Total Atoms (with H)": props["total_atom_count"],
            "Heavy Atoms": props["heavy_atom_count"],
            "Total Bonds": props["total_bond_count"],
            "Aromatic Rings": props["aromatic_rings"],
            "Aliphatic Rings": props["aliphatic_rings"],
            "Molar Refractivity": f"{props['molar_refractivity']} cm³/mol",
            "Fraction Csp3": props["fraction_csp3"],
            "Formal Charge": props["formal_charge"],
        }
        df_top = pd.DataFrame(list(top_data.items()), columns=["Descriptor", "Value"])
        st.dataframe(df_top, use_container_width=True, height=200)

    # Fingerprints Explorer
    st.markdown("---")
    st.markdown("#### 🧬 Molecular Fingerprints")
    fps = generate_fingerprints(active_mol.smiles)

    fp_col1, fp_col2, fp_col3 = st.columns(3)
    with fp_col1:
        st.markdown(
            f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px;">
                <div style="color: #00d2ff; font-weight: 600;">Morgan / ECFP4</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #fff;">{fps['morgan']['on_bits_count']} / {fps['morgan']['size']} <span style="font-size: 0.8rem; color: #8b949e;">bits on</span></div>
                <div style="font-size: 0.75rem; color: #8b949e; margin-top: 4px;">Radius = 2 circular atomic environments</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with fp_col2:
        st.markdown(
            f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px;">
                <div style="color: #00d2ff; font-weight: 600;">MACCS Structural Keys</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #fff;">{fps['maccs']['on_bits_count']} / {fps['maccs']['size']} <span style="font-size: 0.8rem; color: #8b949e;">keys on</span></div>
                <div style="font-size: 0.75rem; color: #8b949e; margin-top: 4px;">166 predefined structural keys</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with fp_col3:
        st.markdown(
            f"""
            <div style="background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px;">
                <div style="color: #00d2ff; font-weight: 600;">RDKit Topological</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #fff;">{fps['rdkit_topological']['on_bits_count']} / {fps['rdkit_topological']['size']} <span style="font-size: 0.8rem; color: #8b949e;">bits on</span></div>
                <div style="font-size: 0.75rem; color: #8b949e; margin-top: 4px;">Daylight-type linear path hashing</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# WORKSPACE 3: MOLECULE COMPARISON
# ==============================================================================
elif nav_selection == "⚖️ Molecule Comparison":
    st.markdown("### ⚖️ Multi-Molecule Comparison & Similarity Studio")
    st.markdown("Compare chemical scaffolds, physicochemical properties, and Tanimoto/Dice fingerprint similarity.")

    # Selection multi-select
    all_names = [m.name for m in list_predefined_molecules()]
    selected_comp_names = st.multiselect(
        "Select molecules to compare (minimum 2):",
        options=all_names,
        default=["Aspirin", "Paracetamol"],
    )

    if len(selected_comp_names) < 2:
        st.warning("⚠️ Please select at least two molecules from the library to perform comparative analysis.")
    else:
        # Build comparison inputs
        comp_inputs = []
        for name in selected_comp_names:
            m = get_predefined_molecule(name)
            if m:
                comp_inputs.append({"name": m.name, "smiles": m.smiles})

        comp_data = compare_molecules(comp_inputs)

        # Side-by-side 2D Structures
        st.markdown("#### 📐 Side-by-Side 2D Scaffolds")
        cols_2d = st.columns(len(comp_inputs))
        for idx, item in enumerate(comp_inputs):
            with cols_2d[idx]:
                st.markdown(f"**{item['name']}**")
                svg_img = generate_2d_svg(item["smiles"], width=300, height=220, dark_theme=False)
                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
                        {svg_img}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Interactive Radar Property Chart
        st.markdown("---")
        st.markdown("#### 🎯 Interactive Physicochemical Radar Comparison")

        radar_categories = ["MW / 100", "LogP", "TPSA / 20", "H-Bond Donors", "H-Bond Acceptors", "Rotatable Bonds"]
        fig_radar = go.Figure()

        palette = ["#00d2ff", "#f59e0b", "#10b981", "#ec4899", "#8b5cf6"]

        for idx, mol_entry in enumerate(comp_data["molecules"]):
            p = mol_entry["properties"]
            r_vals = [
                round(p["molecular_weight"] / 100.0, 2),
                round(p["logp"], 2),
                round(p["tpsa"] / 20.0, 2),
                p["hbd"],
                p["hba"],
                p["rotatable_bonds"],
            ]
            fig_radar.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=radar_categories,
                fill="toself",
                name=mol_entry["name"],
                line=dict(color=palette[idx % len(palette)], width=2),
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, color="#8b949e", gridcolor="#30363d"),
                angularaxis=dict(color="#cbd5e1", gridcolor="#30363d"),
                bgcolor="#161b22",
            ),
            paper_bgcolor="#0d1117",
            font=dict(color="#e6edf3"),
            margin=dict(l=40, r=40, t=30, b=30),
            height=380,
            showlegend=True,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Fingerprint Similarity Matrices
        st.markdown("---")
        st.markdown("#### 🧬 Molecular Similarity Matrices")

        sim_tab1, sim_tab2, sim_tab3 = st.tabs([
            "Morgan Tanimoto Similarity (ECFP4)",
            "Morgan Dice Similarity",
            "MACCS Keys Similarity",
        ])

        with sim_tab1:
            df_tan = pd.DataFrame(comp_data["tanimoto_matrix"], index=comp_data["names"], columns=comp_data["names"])
            st.dataframe(df_tan.style.format("{:.4f}").background_gradient(cmap="Blues", vmin=0, vmax=1), use_container_width=True)
            st.caption(comp_data["metrics_explanation"]["tanimoto"])

        with sim_tab2:
            df_dice = pd.DataFrame(comp_data["dice_matrix"], index=comp_data["names"], columns=comp_data["names"])
            st.dataframe(df_dice.style.format("{:.4f}").background_gradient(cmap="GnBu", vmin=0, vmax=1), use_container_width=True)
            st.caption(comp_data["metrics_explanation"]["dice"])

        with sim_tab3:
            df_maccs = pd.DataFrame(comp_data["maccs_tanimoto_matrix"], index=comp_data["names"], columns=comp_data["names"])
            st.dataframe(df_maccs.style.format("{:.4f}").background_gradient(cmap="Purples", vmin=0, vmax=1), use_container_width=True)
            st.caption(comp_data["metrics_explanation"]["maccs"])

        # Pairwise Differences Table
        st.markdown("---")
        st.markdown("#### 📊 Pairwise Property Differences")
        df_pair = pd.DataFrame(comp_data["pairwise"])
        st.dataframe(
            df_pair.rename(columns={
                "mol1_name": "Molecule 1",
                "mol2_name": "Molecule 2",
                "tanimoto_morgan": "Tanimoto (ECFP4)",
                "similarity_assessment": "Structural Relationship",
                "mw_diff": "Δ MW (g/mol)",
                "logp_diff": "Δ LogP",
                "tpsa_diff": "Δ TPSA (Å²)",
                "hbd_diff": "Δ HBD",
                "hba_diff": "Δ HBA",
                "rot_bonds_diff": "Δ Rot. Bonds",
            })[[
                "Molecule 1", "Molecule 2", "Tanimoto (ECFP4)", "Structural Relationship",
                "Δ MW (g/mol)", "Δ LogP", "Δ TPSA (Å²)", "Δ HBD", "Δ HBA", "Δ Rot. Bonds"
            ]],
            use_container_width=True,
        )


# ==============================================================================
# WORKSPACE 4: AI CHEMISTRY ASSISTANT
# ==============================================================================
elif nav_selection == "🤖 AI Chemistry Assistant":
    st.markdown(f"### 🤖 AI Chemistry Assistant: <span style='color: #00d2ff;'>{active_mol.name}</span>", unsafe_allow_html=True)
    st.markdown(
        "Ask questions regarding molecular structure, functional groups, LogP, stereochemistry, "
        "or compare drug mechanisms. Backed by LLM API with an expert cheminformatics fallback."
    )

    # Prompt chips
    st.markdown("##### 💡 Suggested Questions")
    chip_col1, chip_col2, chip_col3 = st.columns(3)
    with chip_col1:
        if st.button("What functional groups are present?", use_container_width=True):
            user_msg = "What functional groups are present in this molecule?"
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            with st.spinner("Analyzing functional groups..."):
                ans = ask_chemistry_assistant(user_msg, {"name": active_mol.name, "smiles": active_mol.smiles, "properties": calculate_properties(active_mol.smiles)})
            st.session_state.chat_messages.append({"role": "assistant", "content": ans})
            st.rerun()

    with chip_col2:
        if st.button("What does the LogP value mean?", use_container_width=True):
            user_msg = "What does the LogP value mean for this molecule?"
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            with st.spinner("Interpreting LogP and lipophilicity..."):
                ans = ask_chemistry_assistant(user_msg, {"name": active_mol.name, "smiles": active_mol.smiles, "properties": calculate_properties(active_mol.smiles)})
            st.session_state.chat_messages.append({"role": "assistant", "content": ans})
            st.rerun()

    with chip_col3:
        if st.button("Compare aspirin and paracetamol", use_container_width=True):
            user_msg = "Compare aspirin and paracetamol mechanisms and structures."
            st.session_state.chat_messages.append({"role": "user", "content": user_msg})
            with st.spinner("Performing comparative cheminformatics analysis..."):
                ans = ask_chemistry_assistant(user_msg, {"name": active_mol.name, "smiles": active_mol.smiles, "properties": calculate_properties(active_mol.smiles)})
            st.session_state.chat_messages.append({"role": "assistant", "content": ans})
            st.rerun()

    st.markdown("---")

    # Conversation History Display
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="chat-user">
                    <b>👤 You:</b><br/>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="chat-assistant">
                    <b>🤖 Chemistry Assistant:</b><br/>{msg['content']}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Chat Input Box
    user_query = st.chat_input("Ask a question about the active molecule...")
    if user_query:
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        with st.spinner("Consulting cheminformatics knowledge base..."):
            ctx = {
                "name": active_mol.name,
                "smiles": active_mol.smiles,
                "properties": calculate_properties(active_mol.smiles),
            }
            response = ask_chemistry_assistant(user_query, ctx)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()


# ==============================================================================
# WORKSPACE 5: PDF LAB REPORTS
# ==============================================================================
elif nav_selection == "📄 PDF Lab Reports":
    st.markdown("### 📄 Publication-Quality PDF Lab Reports")
    st.markdown("Generate and download comprehensive molecular analysis reports formatted with ReportLab.")

    tab_single_pdf, tab_comp_pdf = st.tabs(["Single Molecule Lab Report", "Multi-Molecule Comparative Report"])

    with tab_single_pdf:
        st.markdown(f"#### Target Molecule: **{active_mol.name}**")
        st.write(f"- Formula: `{active_mol.formula}` | MW: `{active_mol.molecular_weight:.2f} g/mol`")
        st.write(f"- Canonical SMILES: `{active_mol.canonical_smiles}`")

        st.markdown(
            """
            **Included in Report:**
            - High-resolution 2D molecular depiction
            - 3D conformer coordinates summary & force field minimization details
            - Comprehensive physicochemical descriptors table
            - Lipinski Rule of Five & Veber oral bioavailability screening
            - Atomic & bond inventory
            - Full scientific limitations & methodology disclaimer
            """
        )

        if st.button("📑 Generate Single Molecule PDF", type="primary"):
            with st.spinner("Assembling document and embedding vector depictions..."):
                pdf_bytes = generate_molecule_pdf_report(
                    name=active_mol.name,
                    smiles=active_mol.smiles,
                    category=active_mol.category,
                    description=active_mol.description,
                    canonical_smiles=active_mol.canonical_smiles,
                    inchi_str=active_mol.inchi,
                    inchikey_str=active_mol.inchikey,
                )
                filename = f"{active_mol.name.lower().replace(' ', '_')}_cheminformatics_report.pdf"
                st.download_button(
                    label=f"⬇️ Download {filename} ({len(pdf_bytes) // 1024} KB)",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True,
                )
                st.success("✅ PDF report successfully generated!")

    with tab_comp_pdf:
        st.markdown("#### Comparative Multi-Molecule Report")
        comp_pdf_selection = st.multiselect(
            "Select compounds for comparative PDF report:",
            options=[m.name for m in list_predefined_molecules()],
            default=["Aspirin", "Paracetamol", "Ibuprofen"],
        )

        if len(comp_pdf_selection) < 2:
            st.info("Select at least 2 molecules to compile a comparative report.")
        else:
            if st.button("📑 Generate Comparative Multi-Molecule PDF", type="primary"):
                with st.spinner("Compiling multi-molecule comparison document..."):
                    mols = [{"name": n, "smiles": get_predefined_molecule(n).smiles} for n in comp_pdf_selection]
                    comp_pdf_bytes = generate_comparison_pdf_report(mols)
                    filename = "comparative_cheminformatics_report.pdf"
                    st.download_button(
                        label=f"⬇️ Download {filename} ({len(comp_pdf_bytes) // 1024} KB)",
                        data=comp_pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True,
                    )
                    st.success("✅ Comparative PDF report successfully generated!")


# ==============================================================================
# WORKSPACE 6: ASSESSMENT LAB
# ==============================================================================
elif nav_selection == "🎓 Assessment Lab":
    st.markdown("### 🎓 Cheminformatics Assessment & Knowledge Examination")
    st.markdown("Test your expertise in SMILES notation, molecular properties, 3D conformer optimization, and drug-likeness.")

    tier_choice = st.radio(
        "Select Examination Difficulty Tier:",
        ["Beginner", "Intermediate", "Advanced"],
        horizontal=True,
    )

    questions = get_assessment_questions(tier_choice)

    st.markdown("---")
    with st.form("assessment_form"):
        user_choices = {}
        for idx, q in enumerate(questions, 1):
            st.markdown(f"**Question {idx}:** {q['question']}")
            st.markdown(f"<span class='tag-badge'>Category: {q['category']}</span>", unsafe_allow_html=True)
            chosen = st.radio(
                f"Options for Q{idx}",
                q["options"],
                key=f"q_{q['id']}",
                label_visibility="collapsed",
            )
            user_choices[q["id"]] = q["options"].index(chosen)
            st.markdown("<br/>", unsafe_allow_html=True)

        submitted = st.form_submit_button("📝 Submit Assessment for Grading", type="primary")

    if submitted:
        eval_result = evaluate_assessment(tier_choice, user_choices)
        st.session_state.assessment_result = eval_result
        st.session_state.assessment_submitted = True

    if st.session_state.get("assessment_submitted") and "assessment_result" in st.session_state:
        res = st.session_state.assessment_result
        pct = res["score_percentage"]
        badge_cls = "badge-pass" if pct >= 50 else "badge-fail"

        st.markdown("---")
        st.markdown("### 📋 Examination Report Card")
        st.markdown(
            f"""
            <div style="background: #161b22; border: 1.5px solid #00d2ff; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 1.4rem; font-weight: 700; color: #fff;">Tier: {res['tier']}</div>
                        <div style="color: #8b949e; font-size: 0.9rem;">Total Questions: {res['total_questions']} | Correct: {res['correct_count']}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 2rem; font-weight: 800; color: #00d2ff;">{pct}%</div>
                        <div style="font-weight: 600; color: #cbd5e1;">Grade: {res['grade']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Itemized Explanations & Review")
        for item in res["review"]:
            icon = "✅" if item["is_correct"] else "❌"
            border_col = "#2ea043" if item["is_correct"] else "#f85149"
            st.markdown(
                f"""
                <div style="background: #161b22; border-left: 4px solid {border_col}; border-radius: 6px; padding: 10px 14px; margin-bottom: 10px;">
                    <div style="font-weight: 600; color: #e6edf3;">{icon} {item['question']}</div>
                    <div style="font-size: 0.85rem; margin: 4px 0;">
                        <b>Your Answer:</b> <span style="color: {'#3fb950' if item['is_correct'] else '#f85149'}">{item['chosen_text']}</span><br/>
                        <b>Correct Answer:</b> <span style="color: #3fb950;">{item['correct_text']}</span>
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8; background: #0d1117; padding: 6px 10px; border-radius: 4px; margin-top: 6px;">
                        <b>Scientific Explanation:</b> {item['explanation']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# WORKSPACE 7: SAVED PROJECTS & HISTORY
# ==============================================================================
elif nav_selection == "📁 Saved Projects & History":
    st.markdown("### 📁 Saved Projects & Chemical History")
    st.markdown("Inspect, export, and restore your virtual laboratory session history and custom validated molecules.")

    history_records = st.session_state.history

    st.markdown(f"#### Active Session Molecules ({len(history_records)} tracked)")
    df_hist = pd.DataFrame(history_records)
    if not df_hist.empty:
        st.dataframe(
            df_hist[["name", "formula", "molecular_weight", "canonical_smiles", "category", "is_predefined"]].rename(columns={
                "name": "Molecule",
                "formula": "Formula",
                "molecular_weight": "MW (g/mol)",
                "canonical_smiles": "Canonical SMILES",
                "category": "Category",
                "is_predefined": "Preset Standard",
            }),
            use_container_width=True,
        )

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.markdown("##### 💾 Export Session Workspace")
        export_json = json.dumps(history_records, indent=2)
        st.download_button(
            "⬇️ Download Session State (JSON)",
            data=export_json,
            file_name=f"cheminformatics_lab_session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_exp2:
        st.markdown("##### 📂 Restore Workspace Session")
        uploaded_json = st.file_uploader("Upload JSON Session State", type=["json"])
        if uploaded_json is not None:
            try:
                imported_data = json.load(uploaded_json)
                if isinstance(imported_data, list):
                    st.session_state.history = imported_data
                    st.success(f"Successfully loaded {len(imported_data)} molecules into session history!")
                else:
                    st.error("Invalid session format: expected list of molecule records.")
            except Exception as e:
                st.error(f"Failed to parse uploaded JSON file: {e}")
