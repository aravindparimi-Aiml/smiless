"""
Cheminformatics Virtual Laboratory - Interactive 3D Molecular Viewer Component
Embeds high-performance WebGL 3Dmol.js viewer with multiple representations,
spin control, surface rendering, and real-time atom coordinate inspection HUD.
"""

import json
from typing import Optional
import streamlit as st
import streamlit.components.v1 as components


def render_3d_molecular_viewer(
    mol_block: str,
    height: int = 480,
    style: str = "ball_and_stick",
    show_hydrogens: bool = True,
    auto_spin: bool = False,
    show_surface: bool = False,
    container_id: str = "mol_viewer_3d",
    element_id_prefix: str = "3dmol",
) -> None:
    """
    Renders an interactive 3D WebGL molecular visualizer using 3Dmol.js.
    """
    escaped_mol_block = json.dumps(mol_block)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"></script>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            }}
            body {{
                background-color: #0b0f19;
                color: #e2e8f0;
                overflow: hidden;
            }}
            #viewer-wrapper {{
                position: relative;
                width: 100%;
                height: {height}px;
                border-radius: 10px;
                border: 1px solid #1e293b;
                background: radial-gradient(circle at 50% 50%, #111827 0%, #0b0f19 100%);
                overflow: hidden;
            }}
            #{container_id} {{
                width: 100%;
                height: 100%;
                position: relative;
            }}
            /* Controls overlay bar */
            .controls-overlay {{
                position: absolute;
                top: 10px;
                left: 10px;
                right: 10px;
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                z-index: 100;
                pointer-events: none;
            }}
            .ctrl-btn {{
                pointer-events: auto;
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(51, 65, 85, 0.8);
                color: #94a3b8;
                padding: 5px 10px;
                font-size: 11px;
                font-weight: 500;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.15s ease;
            }}
            .ctrl-btn:hover {{
                background: rgba(30, 41, 59, 0.95);
                color: #00d2ff;
                border-color: #00d2ff;
            }}
            .ctrl-btn.active {{
                background: rgba(0, 210, 255, 0.2);
                color: #00d2ff;
                border-color: #00d2ff;
                font-weight: 600;
            }}
            /* Atom inspector HUD */
            #atom-inspector-hud {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                right: 10px;
                background: rgba(15, 23, 42, 0.9);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(0, 210, 255, 0.3);
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-family: 'JetBrains Mono', monospace;
                color: #cbd5e1;
                display: flex;
                justify-content: space-between;
                align-items: center;
                pointer-events: none;
                z-index: 100;
            }}
            .hud-highlight {{
                color: #00d2ff;
                font-weight: 700;
            }}
        </style>
    </head>
    <body>
        <div id="viewer-wrapper">
            <div class="controls-overlay">
                <button class="ctrl-btn" id="btn-ball-stick" onclick="setStyle('ball_and_stick')">Ball & Stick</button>
                <button class="ctrl-btn" id="btn-cpk" onclick="setStyle('cpk')">Space-Filling (CPK)</button>
                <button class="ctrl-btn" id="btn-stick" onclick="setStyle('stick')">Sticks</button>
                <button class="ctrl-btn" id="btn-wireframe" onclick="setStyle('wireframe')">Wireframe</button>
                <button class="ctrl-btn" id="btn-surface" onclick="toggleSurface()">Surface (VDW)</button>
                <button class="ctrl-btn" id="btn-spin" onclick="toggleSpin()">Auto-Spin</button>
                <button class="ctrl-btn" id="btn-recenter" onclick="recenter()">Recenter View</button>
                <button class="ctrl-btn" id="btn-fullscreen" onclick="toggleFullscreen()">Full Screen</button>
            </div>

            <div id="{container_id}"></div>

            <div id="atom-inspector-hud">
                <span id="hud-text">Click on any atom to inspect element, index, coordinates, and charges</span>
                <span style="font-size: 10px; color: #64748b;">3Dmol.js WebGL</span>
            </div>
        </div>

        <script>
            let viewer = null;
            let currentStyle = '{style}';
            let isSpinning = {str(auto_spin).lower()};
            let showHydrogens = {str(show_hydrogens).lower()};
            let showSurface = {str(show_surface).lower()};
            let surfaceObj = null;

            const molData = {escaped_mol_block};

            function initViewer() {{
                const element = document.getElementById('{container_id}');
                const config = {{ backgroundColor: '#0b0f19' }};
                viewer = $3Dmol.createViewer(element, config);

                viewer.addModel(molData, 'mol');
                applyStyle();
                viewer.zoomTo();
                viewer.render();

                if (isSpinning) {{
                    viewer.spin(true);
                    document.getElementById('btn-spin').classList.add('active');
                }}

                // Configure atom click inspection
                viewer.setClickable({{}}, true, function(atom, viewer, event, container) {{
                    const sym = atom.elem || 'Unknown';
                    const idx = atom.index !== undefined ? atom.index : atom.serial;
                    const x = atom.x ? atom.x.toFixed(3) : '0.000';
                    const y = atom.y ? atom.y.toFixed(3) : '0.000';
                    const z = atom.z ? atom.z.toFixed(3) : '0.000';
                    const chg = atom.charge ? atom.charge.toFixed(3) : '0.000';

                    document.getElementById('hud-text').innerHTML =
                        `Atom <span class="hud-highlight">[${{idx}}] ${{sym}}</span> | ` +
                        `Coords: <span class="hud-highlight">X:${{x}}, Y:${{y}}, Z:${{z}}</span> | ` +
                        `Partial Charge: <span class="hud-highlight">${{chg}}</span>`;

                    // Highlight clicked atom
                    viewer.removeAllLabels();
                    viewer.addLabel(`${{sym}}_${{idx}}`, {{
                        position: {{ x: atom.x, y: atom.y, z: atom.z }},
                        backgroundColor: '#00d2ff',
                        backgroundOpacity: 0.8,
                        fontColor: '#000000',
                        fontSize: 12,
                        font: 'sans-serif'
                    }});
                    viewer.render();
                }});
            }}

            function applyStyle() {{
                if (!viewer) return;
                viewer.setStyle({{}}, {{}});

                // Filter hydrogens if requested
                const atomFilter = showHydrogens ? {{}} : {{ elem: ['H'] }};

                if (currentStyle === 'ball_and_stick') {{
                    viewer.setStyle({{}}, {{
                        stick: {{ radius: 0.14, colorscheme: 'Jmol' }},
                        sphere: {{ scale: 0.32, colorscheme: 'Jmol' }}
                    }});
                }} else if (currentStyle === 'cpk') {{
                    viewer.setStyle({{}}, {{
                        sphere: {{ colorscheme: 'Jmol' }}
                    }});
                }} else if (currentStyle === 'stick') {{
                    viewer.setStyle({{}}, {{
                        stick: {{ radius: 0.24, colorscheme: 'Jmol' }}
                    }});
                }} else if (currentStyle === 'wireframe') {{
                    viewer.setStyle({{}}, {{
                        line: {{ colorscheme: 'Jmol' }}
                    }});
                }}

                if (!showHydrogens) {{
                    viewer.setStyle({{ elem: 'H' }}, {{ hidden: true }});
                }}

                // Update active button state
                ['ball-stick', 'cpk', 'stick', 'wireframe'].forEach(id => {{
                    const el = document.getElementById('btn-' + id);
                    if (el) el.classList.remove('active');
                }});
                const activeId = currentStyle === 'ball_and_stick' ? 'btn-ball-stick' : 'btn-' + currentStyle;
                const el = document.getElementById(activeId);
                if (el) el.classList.add('active');

                viewer.render();
            }}

            function setStyle(newStyle) {{
                currentStyle = newStyle;
                applyStyle();
            }}

            function toggleSpin() {{
                isSpinning = !isSpinning;
                viewer.spin(isSpinning);
                const btn = document.getElementById('btn-spin');
                if (isSpinning) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }}

            function toggleSurface() {{
                if (!viewer) return;
                showSurface = !showSurface;
                const btn = document.getElementById('btn-surface');

                if (showSurface) {{
                    surfaceObj = viewer.addSurface($3Dmol.SurfaceType.VDW, {{
                        opacity: 0.55,
                        color: 'white'
                    }});
                    btn.classList.add('active');
                }} else {{
                    if (surfaceObj) {{
                        viewer.removeSurface(surfaceObj);
                        surfaceObj = null;
                    }}
                    btn.classList.remove('active');
                }}
                viewer.render();
            }}

            function recenter() {{
                if (!viewer) return;
                viewer.zoomTo();
                viewer.render();
            }}

            function toggleFullscreen() {{
                const elem = document.getElementById('viewer-wrapper');
                if (!document.fullscreenElement) {{
                    elem.requestFullscreen().catch(err => {{
                        console.error('Fullscreen request error:', err);
                    }});
                }} else {{
                    document.exitFullscreen();
                }}
            }}

            window.addEventListener('DOMContentLoaded', initViewer);
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=height + 10, scrolling=False)
