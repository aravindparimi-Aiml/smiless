"""
Cheminformatics Virtual Laboratory - Modern Dark Scientific Theme & UI Styles
"""

import streamlit as st


def get_custom_css() -> str:
    """Return comprehensive CSS stylesheet for dark scientific theme."""
    return """
    <style>
    /* Global scientific styling */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre, .mono-text {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main container styling */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Top banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(13, 17, 23, 0.95) 0%, rgba(22, 27, 34, 0.95) 100%);
        border: 1px solid rgba(0, 210, 255, 0.25);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 210, 255, 0.08);
    }

    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 50%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        color: #8b949e;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }

    .tag-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 20px;
        background: rgba(0, 210, 255, 0.12);
        color: #00d2ff;
        border: 1px solid rgba(0, 210, 255, 0.3);
        margin-right: 0.5rem;
    }

    /* Glass card containers */
    .glass-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }

    .glass-card:hover {
        border-color: #58a6ff;
    }

    .card-title {
        color: #58a6ff;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.8rem;
        margin: 1rem 0;
    }

    .metric-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 3px solid #00d2ff;
        border-radius: 8px;
        padding: 0.9rem 1rem;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }

    .metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #e6edf3;
        font-family: 'JetBrains Mono', monospace;
    }

    .metric-unit {
        font-size: 0.8rem;
        color: #8b949e;
        font-weight: 400;
        margin-left: 0.2rem;
    }

    /* Status indicators */
    .badge-pass {
        background: rgba(46, 160, 67, 0.2);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }

    .badge-fail {
        background: rgba(248, 81, 73, 0.2);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }

    /* Scientific Disclaimer Box */
    .disclaimer-box {
        background: rgba(210, 153, 34, 0.08);
        border: 1px solid rgba(210, 153, 34, 0.3);
        border-radius: 8px;
        padding: 0.8rem 1rem;
        color: #d29922;
        font-size: 0.82rem;
        line-height: 1.4;
        margin: 1rem 0;
    }

    /* 3D Conformer banner */
    .conformer-banner {
        background: rgba(88, 166, 255, 0.08);
        border: 1px solid rgba(88, 166, 255, 0.25);
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        color: #58a6ff;
        font-size: 0.82rem;
        margin-bottom: 0.8rem;
    }

    /* Molecule selection pill cards */
    .mol-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .mol-card:hover {
        border-color: #00d2ff;
        background: #1c2128;
    }

    /* Chat bubble styles */
    .chat-user {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }

    .chat-assistant {
        background: #0e1726;
        border: 1px solid rgba(0, 210, 255, 0.25);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """


def apply_dark_scientific_theme():
    """Apply the custom dark scientific stylesheet to the current Streamlit app."""
    st.markdown(get_custom_css(), unsafe_allow_html=True)
