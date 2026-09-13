import streamlit as st
import pandas as pd
import joblib
import os
import streamlit.components.v1 as components


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="EstateIQ | House Price Prediction",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "house_price_model.pkl")
    return joblib.load(model_path)


model = load_model()


# =========================================================
# THEME STATE
# =========================================================

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


PALETTES = {
    "dark": dict(
        bg1="#16295b", bg2="#08142f", bg3="#040916",
        surface="rgba(255,255,255,0.035)", border="rgba(255,255,255,0.10)",
        text="#eef2fc", text_muted="#93a0c2",
        accent="#4f6ef7", accent_light="#9db8ff", price="#34e0a1",
        field_bg="rgba(255,255,255,0.07)", field_border="rgba(255,255,255,0.16)",
        scroll_color="#566089", footer_color="#4f5670",
        badge_bg="rgba(79,110,247,0.10)", badge_border="rgba(130,160,255,0.35)",
        nav_scrolled_bg="rgba(10,17,48,0.72)",
        particle_dot="rgba(140,185,255,0.90)",
        particle_line_rgb="105,155,255", particle_line_alpha=0.18,
        toggle_icon="☀️", toggle_help="Switch to light mode",
    ),
    "light": dict(
        bg1="#dfeaff", bg2="#eef4ff", bg3="#f7faff",
        surface="rgba(20,30,70,0.04)", border="rgba(20,30,70,0.12)",
        text="#111935", text_muted="#57628a",
        accent="#4f6ef7", accent_light="#3552d8", price="#0f9d68",
        field_bg="rgba(255,255,255,0.92)", field_border="rgba(70,90,135,0.28)",
        scroll_color="#8792b5", footer_color="#8792b5",
        badge_bg="rgba(79,110,247,0.08)", badge_border="rgba(79,110,247,0.30)",
        nav_scrolled_bg="rgba(246,248,253,0.78)",
        particle_dot="rgba(56,92,190,0.78)",
        particle_line_rgb="70,100,190", particle_line_alpha=0.12,
        toggle_icon="🌙", toggle_help="Switch to dark mode",
    ),
}

p = PALETTES[st.session_state.theme]


# =========================================================
# ANIMATED BACKGROUND + SCROLL BEHAVIOR
# =========================================================
# IMPORTANT FIX: components.html runs in an iframe that Streamlit
# destroys and rebuilds on every rerun (every click, every keystroke).
# The canvas element itself lives in the parent document and survives
# that, but anything scheduled from inside the dying iframe --
# requestAnimationFrame loops, addEventListener callbacks -- dies with
# it. Previously the animation loop and scroll/resize listeners were
# only ever started ONCE, so the very first rerun after page load
# silently killed them. Now every rerun explicitly cancels the old
# loop/listeners and rebinds fresh ones from the current, still-alive
# iframe context. Node positions persist across reruns via
# window.parent.__estateiqBg so the animation doesn't jump/reset.

bg_script = """
<script>
(function() {
    const doc = window.parent.document;
    const win = window.parent;

    if (!win.__estateiqBg) { win.__estateiqBg = {}; }
    const state = win.__estateiqBg;
    state.dotColor = "__DOT_COLOR__";
    state.lineRgb = "__LINE_RGB__";
    state.lineAlpha = __LINE_ALPHA__;
    state.bg1 = "__BG1__";
    state.bg2 = "__BG2__";
    state.bg3 = "__BG3__";

    // ---- Fixed themed background layer + canvas: create once, reuse forever ----
    let bgLayer = doc.getElementById('estateiq-bg-layer');
    if (!bgLayer) {
        bgLayer = doc.createElement('div');
        bgLayer.id = 'estateiq-bg-layer';
        bgLayer.style.position = 'fixed';
        bgLayer.style.top = '0';
        bgLayer.style.left = '0';
        bgLayer.style.width = '100vw';
        bgLayer.style.height = '100vh';
        bgLayer.style.zIndex = '0';
        bgLayer.style.pointerEvents = 'none';
        bgLayer.style.transition = 'background 0.25s ease';
        doc.body.prepend(bgLayer);
    }
    bgLayer.style.background = 'radial-gradient(circle at 50% -10%, ' + state.bg1 + ' 0%, ' + state.bg2 + ' 45%, ' + state.bg3 + ' 100%)';

    let canvas = doc.getElementById('estateiq-bg-canvas');
    if (!canvas) {
        canvas = doc.createElement('canvas');
        canvas.id = 'estateiq-bg-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '1';
        canvas.style.pointerEvents = 'none';
        doc.body.prepend(canvas);
    }
    const ctx = canvas.getContext('2d');

    function resize() {
        canvas.width = win.innerWidth;
        canvas.height = win.innerHeight;
        // Sparser than a dense mesh: fewer nodes, spread wide, most of
        // them small "stars" with the occasional bigger hub point.
        const count = Math.max(28, Math.min(72, Math.floor((canvas.width * canvas.height) / 25000))); 
        if (!state.nodes || state.nodes.length !== count) {
            state.nodes = Array.from({ length: count }, () => {
                const isHub = Math.random() < 0.12;
                return {
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 0.14,
                    vy: (Math.random() - 0.5) * 0.14,
                    r: isHub ? (Math.random() * 0.8 + 2.0) : (Math.random() * 0.9 + 0.7),
                    twinklePhase: Math.random() * Math.PI * 2,
                    twinkleSpeed: Math.random() * 0.015 + 0.008
                };
            });
        }
    }

    // Rebind resize listener fresh every run (old one is dead anyway).
    if (state.resizeHandler) { win.removeEventListener('resize', state.resizeHandler); }
    state.resizeHandler = resize;
    win.addEventListener('resize', resize);
    if (!state.nodes) { resize(); }

    // Rebind the animation loop fresh every run.
    if (state.rafId) { win.cancelAnimationFrame(state.rafId); }

    const CONNECT_DIST = 235;

    function tick() {
        const w = canvas.width, h = canvas.height;
        ctx.clearRect(0, 0, w, h);
        const nodes = state.nodes;

        for (let i = 0; i < nodes.length; i++) {
            const a = nodes[i];
            a.x += a.vx;
            a.y += a.vy;
            if (a.x < 0 || a.x > w) a.vx *= -1;
            if (a.y < 0 || a.y > h) a.vy *= -1;
            a.twinklePhase += a.twinkleSpeed;

            for (let j = i + 1; j < nodes.length; j++) {
                const b = nodes[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECT_DIST) {
                    ctx.strokeStyle = 'rgba(' + state.lineRgb + ',' + (state.lineAlpha * (1 - dist / CONNECT_DIST)) + ')';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            }
        }

        for (const n of nodes) {
            const twinkle = 0.6 + 0.4 * Math.sin(n.twinklePhase);
            ctx.globalAlpha = twinkle;
            ctx.fillStyle = state.dotColor;
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;

        state.rafId = win.requestAnimationFrame(tick);
    }
    tick();

    // ---- Scroll-aware sticky navbar (also rebind fresh) ----
    const navRow = doc.querySelectorAll('[data-testid="stHorizontalBlock"]')[0];
    if (navRow) {
        navRow.style.position = 'sticky';
        navRow.style.top = '0px';
        navRow.style.zIndex = '999';
        navRow.style.transition = 'background 0.3s ease, backdrop-filter 0.3s ease, box-shadow 0.3s ease';
        navRow.style.padding = '10px 6px';
        navRow.style.borderRadius = '0 0 16px 16px';

        function onNavScroll() {
            if (win.scrollY > 40) {
                navRow.style.background = '__NAV_SCROLLED_BG__';
                navRow.style.backdropFilter = 'blur(10px)';
                navRow.style.boxShadow = '0 8px 30px rgba(0,0,0,0.20)';
            } else {
                navRow.style.background = 'transparent';
                navRow.style.backdropFilter = 'none';
                navRow.style.boxShadow = 'none';
            }
        }
        if (state.navScrollHandler) { win.removeEventListener('scroll', state.navScrollHandler); }
        state.navScrollHandler = onNavScroll;
        win.addEventListener('scroll', onNavScroll);
        onNavScroll();
    }

    // ---- Fade-up reveal on scroll (fresh observer every run) ----
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
            }
        });
    }, { threshold: 0.15 });
    doc.querySelectorAll('.reveal:not(.in-view)').forEach((el) => observer.observe(el));
})();
</script>
"""

bg_script = (
    bg_script
    .replace("__DOT_COLOR__", p["particle_dot"])
    .replace("__LINE_RGB__", p["particle_line_rgb"])
    .replace("__LINE_ALPHA__", str(p["particle_line_alpha"]))
    .replace("__NAV_SCROLLED_BG__", p["nav_scrolled_bg"])
    .replace("__BG1__", p["bg1"])
    .replace("__BG2__", p["bg2"])
    .replace("__BG3__", p["bg3"])
)

components.html(bg_script, height=0)


# =========================================================
# CUSTOM CSS
# =========================================================
# All HTML blocks below are written flush-left. Streamlit's markdown
# renderer treats any line indented 4+ spaces as a preformatted code
# block, which previously made the UI show raw <div> tags as text.
#
# Input/select field selectors are intentionally redundant (class,
# data-testid, and data-baseweb variants) because Streamlit's exact
# DOM markup for these widgets has changed across versions, and the
# app's own theme (config.toml, fixed to dark) otherwise wins over a
# selector that doesn't match.

st.markdown(f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

:root {{
--bg1: {p["bg1"]};
--bg2: {p["bg2"]};
--bg3: {p["bg3"]};
--surface: {p["surface"]};
--border: {p["border"]};
--text: {p["text"]};
--text-muted: {p["text_muted"]};
--accent: {p["accent"]};
--accent-light: {p["accent_light"]};
--price: {p["price"]};
--field-bg: {p["field_bg"]};
--field-border: {p["field_border"]};
--scroll-color: {p["scroll_color"]};
--footer-color: {p["footer_color"]};
--badge-bg: {p["badge_bg"]};
--badge-border: {p["badge_border"]};
}}

html, body, [class*="css"] {{
font-family: 'Inter', sans-serif;
}}

html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
section.main {{
background: transparent !important;
background-color: transparent !important;
color: var(--text) !important;
transition: color 0.25s ease;
}}

[data-testid="stHeader"] {{ background: transparent !important; }}

/* ===== Animated network background layer ===== */
body {{
background: transparent !important;
background-color: transparent !important;
}}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main {{
background: transparent !important;
}}

#estateiq-bg-layer {{
position: fixed !important;
top: 0 !important;
left: 0 !important;
width: 100vw !important;
height: 100vh !important;
z-index: 0 !important;
pointer-events: none !important;
}}

#estateiq-bg-canvas {{
position: fixed !important;
top: 0 !important;
left: 0 !important;
width: 100vw !important;
height: 100vh !important;
z-index: 1 !important;
pointer-events: none !important;
display: block !important;
opacity: 1 !important;
}}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stMainBlockContainer"] {{
background: transparent !important;
background-color: transparent !important;
}}

/* Every actual UI surface stays above the animation */
.block-container,
[data-testid="stHorizontalBlock"],
[data-testid="stVerticalBlock"],
[data-testid="stMainBlockContainer"] {{
position: relative;
z-index: 2;
}}

/* Never let Streamlit's base theme paint over the selected mode */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {{
background: transparent !important;
background-color: transparent !important;
}}

#estateiq-bg-layer {{
position: fixed !important;
top: 0 !important;
left: 0 !important;
width: 100vw !important;
height: 100vh !important;
z-index: 0 !important;
pointer-events: none !important;
}}

#estateiq-bg-canvas {{
position: fixed !important;
z-index: 1 !important;
}}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

.block-container {{
max-width: 1180px;
padding-top: 0.5rem;
padding-bottom: 3rem;
}}

/* Scroll reveal */
.reveal {{
opacity: 0;
transform: translateY(24px);
transition: opacity 0.6s ease, transform 0.6s ease, box-shadow 0.25s ease;
}}
.reveal.in-view {{
opacity: 1;
transform: translateY(0);
}}

/* Navbar */
.navbar-mark {{
font-family: 'Space Grotesk', sans-serif;
font-weight: 700;
font-size: 1.35rem;
color: var(--text);
}}
.navbar-links {{ display: flex; gap: 26px; align-items: center; height: 42px; }}
.navbar-links a {{
color: var(--text-muted);
font-size: 0.92rem;
font-weight: 500;
text-decoration: none;
}}
.navbar-links a:hover {{ color: var(--text); }}
.navbar-cta {{
display: inline-block;
background: var(--accent);
color: white !important;
padding: 9px 20px;
border-radius: 999px;
font-weight: 600;
font-size: 0.9rem;
text-decoration: none;
white-space: nowrap;
}}

/* Theme toggle button */
div[data-testid="column"]:has(button[kind="secondary"]) {{
display: flex;
align-items: center;
justify-content: center;
}}
button[kind="secondary"] {{
border-radius: 999px !important;
border: 1px solid var(--border) !important;
background: var(--surface) !important;
color: var(--text) !important;
width: 42px !important;
height: 42px !important;
padding: 0 !important;
font-size: 1.05rem !important;
min-height: 42px !important;
}}
button[kind="secondary"]:hover {{ border-color: var(--accent) !important; }}

/* Hero */
.hero-wrap {{ text-align: center; padding: 60px 20px 40px 20px; }}
.hero-badge {{
display: inline-block;
border: 1px solid var(--badge-border);
background: var(--badge-bg);
color: var(--accent-light);
font-size: 0.72rem;
font-weight: 700;
letter-spacing: 0.5px;
padding: 8px 18px;
border-radius: 999px;
margin-bottom: 30px;
}}
.hero-title {{
font-family: 'Space Grotesk', sans-serif;
font-size: 4.2rem;
font-weight: 700;
line-height: 1.12;
color: var(--text);
max-width: 900px;
margin: 0 auto 22px auto;
}}
.hero-title .accent {{ color: var(--accent-light); }}
.hero-subtitle {{
color: var(--text-muted);
font-size: 1.15rem;
max-width: 620px;
margin: 0 auto 34px auto;
}}
.hero-buttons {{ display: flex; justify-content: center; gap: 14px; margin-bottom: 46px; }}
.hero-btn-solid {{
background: var(--accent);
color: white !important;
padding: 13px 26px;
border-radius: 999px;
font-weight: 600;
font-size: 0.95rem;
text-decoration: none;
}}
.hero-btn-outline {{
border: 1px solid var(--border);
color: var(--text) !important;
padding: 13px 26px;
border-radius: 999px;
font-weight: 600;
font-size: 0.95rem;
text-decoration: none;
}}
.hero-scroll {{ color: var(--scroll-color); font-size: 0.7rem; font-weight: 600; letter-spacing: 2px; }}

/* Cards */
.card {{
background: var(--surface);
border: 1px solid var(--border);
border-radius: 18px;
padding: 26px;
backdrop-filter: blur(6px);
box-sizing: border-box;
}}
.card:hover {{ transform: translateY(-3px); box-shadow: 0 14px 34px rgba(0,0,0,0.16); }}

/* Top property/result cards: same footprint, no accidental stretching */
.property-card {{
height: 300px;
box-sizing: border-box;
display: flex;
flex-direction: column;
justify-content: space-between;
padding-bottom: 32px;
}}

.prediction-card {{
height: 300px;
min-height: 300px;
box-sizing: border-box;
}}

/* Feature cards: all four cards stay exactly the same size */
.feature-card {{
height: 225px;
min-height: 225px;
max-height: 225px;
box-sizing: border-box;
display: flex;
flex-direction: column;
justify-content: flex-start;
padding: 24px 24px 34px 24px;
}}

.feature-card .feature-copy {{
margin-top: auto;
padding-top: 14px;
}}

.card-title {{
font-family: 'Space Grotesk', sans-serif;
color: var(--text);
font-size: 1.15rem;
font-weight: 600;
margin-bottom: 6px;
}}
.card-subtitle {{ color: var(--text-muted); font-size: 0.86rem; line-height: 1.5; }}

/* Prediction card */
.prediction-card {{
background: var(--surface);
border: 1px solid var(--badge-border);
border-radius: 18px;
padding: 30px 30px 34px 30px;
height: 300px;
min-height: 300px;
max-height: 300px;
box-sizing: border-box;
backdrop-filter: blur(6px);
}}
.prediction-title {{
font-family: 'Space Grotesk', sans-serif;
font-size: 1.15rem;
font-weight: 600;
color: var(--text);
margin-bottom: 4px;
}}
.prediction-subtitle {{ color: var(--text-muted); font-size: 0.85rem; margin-bottom: 26px; }}
.prediction-price {{
font-family: 'Space Grotesk', sans-serif;
font-size: 2.5rem;
font-weight: 700;
color: var(--price);
margin: 6px 0 22px 0;
}}
.prediction-label {{ color: var(--text-muted); font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; }}
.prediction-note {{
background: var(--field-bg);
border: 1px solid var(--border);
border-radius: 12px;
padding: 13px;
font-size: 0.78rem;
line-height: 1.5;
color: var(--text-muted);
}}

/* Metrics */
.metric-card {{
background: var(--surface);
border: 1px solid var(--border);
border-radius: 14px;
padding: 22px 20px 26px 20px;
height: 160px;
min-height: 160px;
max-height: 160px;
box-sizing: border-box;
backdrop-filter: blur(6px);
}}
.metric-card:hover {{ transform: translateY(-3px); box-shadow: 0 14px 34px rgba(0,0,0,0.16); }}
.metric-icon {{ font-size: 1.25rem; }}
.metric-value {{
font-family: 'Space Grotesk', sans-serif;
color: var(--text);
font-size: 1.3rem;
font-weight: 600;
margin-top: 8px;
}}
.metric-label {{ color: var(--text-muted); font-size: 0.72rem; margin-top: 3px; }}
.metric-description {{ color: var(--text-muted); opacity: 0.75; font-size: 0.68rem; margin-top: 7px; }}

/* Section */
.section-title {{
font-family: 'Space Grotesk', sans-serif;
color: var(--text);
font-size: 1.35rem;
font-weight: 600;
margin-top: 34px;
margin-bottom: 4px;
}}
.section-subtitle {{ color: var(--text-muted); font-size: 0.84rem; margin-bottom: 18px; }}

/* Primary Streamlit button (Estimate house price) */
button[kind="primary"] {{
width: 100%;
border: none !important;
border-radius: 999px !important;
background: var(--accent) !important;
color: white !important;
font-weight: 700 !important;
font-size: 0.98rem !important;
padding: 0.7rem 1rem !important;
transition: 0.2s;
}}
button[kind="primary"]:hover {{ transform: translateY(-1px); filter: brightness(1.08); }}

/* ===== Input / select fields (broad, redundant selectors) ===== */

.stNumberInput label, .stSelectbox label {{
color: var(--text-muted) !important;
font-weight: 600 !important;
font-size: 0.8rem !important;
}}

.stNumberInput > div,
.stTextInput > div,
.stSelectbox > div,
[data-testid="stNumberInput"],
[data-testid="stNumberInputContainer"],
[data-testid="stSelectbox"] {{
background: var(--field-bg) !important;
background-color: var(--field-bg) !important;
border-radius: 10px !important;
}}

.stNumberInput input,
.stTextInput input,
[data-testid="stNumberInput"] input,
[data-testid="stNumberInputContainer"] input,
[data-testid="stTextInput"] input,
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {{
background-color: var(--field-bg) !important;
background: var(--field-bg) !important;
color: var(--text) !important;
-webkit-text-fill-color: var(--text) !important;
caret-color: var(--text) !important;
opacity: 1 !important;
border: 1px solid var(--field-border) !important;
border-radius: 10px !important;
}}

.stNumberInput input:focus,
[data-testid="stNumberInput"] input:focus,
div[data-baseweb="input"]:focus-within,
div[data-baseweb="base-input"]:focus-within {{
border-color: var(--accent) !important;
box-shadow: 0 0 0 3px rgba(79,110,247,0.18) !important;
}}

[data-testid="stNumberInput"] button,
[data-testid="stNumberInputContainer"] button {{
background-color: var(--field-bg) !important;
color: var(--text) !important;
border: 1px solid var(--field-border) !important;
}}

.stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
background-color: var(--field-bg) !important;
color: var(--text) !important;
border: 1px solid var(--field-border) !important;
border-radius: 10px !important;
}}
.stSelectbox div[data-baseweb="select"] span {{ color: var(--text) !important; }}

div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] {{ background-color: var(--surface) !important; }}
div[data-baseweb="menu"] li {{ color: var(--text) !important; background-color: transparent !important; }}
div[data-baseweb="menu"] li:hover {{ background-color: var(--field-bg) !important; }}

/* Footer */
.footer {{
text-align: center;
color: var(--footer-color);
font-size: 0.75rem;
margin-top: 46px;
padding-top: 20px;
border-top: 1px solid var(--border);
}}

</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVBAR
# =========================================================

nav_logo, nav_links, nav_toggle, nav_cta = st.columns([2.6, 4, 0.7, 1.7], gap="small")

with nav_logo:
    st.markdown("""
<div style="display:flex; align-items:center; gap:10px; height:42px;">
<span style="font-size:1.4rem;">🏠</span>
<span class="navbar-mark">EstateIQ</span>
</div>
""", unsafe_allow_html=True)

with nav_links:
    st.markdown("""
<div class="navbar-links">
<a href="#property">Property</a>
<a href="#performance">Performance</a>
<a href="#why">Why EstateIQ</a>
</div>
""", unsafe_allow_html=True)

with nav_toggle:
    if st.button(
        p["toggle_icon"],
        key="theme_toggle_btn",
        help=p["toggle_help"],
        type="secondary",
    ):
        st.session_state.theme = (
            "light" if st.session_state.theme == "dark" else "dark"
        )
        st.rerun()

with nav_cta:
    st.markdown("""
<div style="height:42px; display:flex; align-items:center; justify-content:flex-end;">
<a href="#property" class="navbar-cta">Get an Estimate</a>
</div>
""", unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero-wrap">
<div class="hero-badge">ESTATEIQ &nbsp;—&nbsp; AI VALUATION ENGINE</div>
<div class="hero-title">Find the <span class="accent">true value</span><br>of your next home.</div>
<div class="hero-subtitle">
One model, trained on real housing sales, turning your property details
into an instant, data-driven price estimate.
</div>
<div class="hero-buttons">
<a href="#property" class="hero-btn-solid">Estimate My Home ↓</a>
<a href="#performance" class="hero-btn-outline">See Model Performance →</a>
</div>
<div class="hero-scroll">SCROLL</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# MAIN LAYOUT
# =========================================================

st.markdown('<div id="property"></div>', unsafe_allow_html=True)

left, right = st.columns([1.55, 1], gap="large")


# =========================================================
# LEFT SIDE — PROPERTY INPUT
# =========================================================

with left:

    st.markdown("""
<div class="card property-card reveal">
<div class="card-title">Property details</div>
<div class="card-subtitle">Enter the key details of the property to get an estimated price.</div>
<div style="margin-top:auto; padding-top:18px; color:var(--accent-light); font-size:0.72rem; font-weight:700;">9 property signals · AI valuation engine</div>
</div>
""", unsafe_allow_html=True)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        area = st.number_input(
            "Living Area (sq ft)",
            min_value=100,
            value=1500,
            step=50
        )

        bedrooms = st.number_input(
            "Number of Bedrooms",
            min_value=0,
            max_value=10,
            value=3,
            step=1
        )

        bathrooms = st.number_input(
            "Number of Bathrooms",
            min_value=1,
            max_value=5,
            value=2,
            step=1
        )

        year = st.number_input(
            "Year Built",
            min_value=1800,
            max_value=2026,
            value=2000,
            step=1
        )

    with col2:

        quality = st.number_input(
            "Overall Quality (1-10)",
            min_value=1,
            max_value=10,
            value=7,
            step=1
        )

        garage = st.number_input(
            "Garage Capacity (cars)",
            min_value=0,
            max_value=5,
            value=2,
            step=1
        )

        basement = st.number_input(
            "Basement Area (sq ft)",
            min_value=0,
            value=800,
            step=50
        )

        first_floor = st.number_input(
            "1st Floor Area (sq ft)",
            min_value=100,
            value=800,
            step=50
        )

    neighborhood = st.selectbox(
        "Neighborhood",
        [
            "Blmngtn",
            "CollgCr",
            "Crawfor",
            "Edwards",
            "Gilbert",
            "NWAmes",
            "NAmes",
            "NoRidge",
            "NridgHt",
            "OldTown",
            "Sawyer",
            "Somerst",
            "StoneBr",
            "Timber",
            "Veenker"
        ]
    )

    st.write("")

    predict_button = st.button(
        "Estimate house price →",
        use_container_width=True,
        type="primary",
    )


# =========================================================
# RIGHT SIDE — PREDICTION
# =========================================================

with right:

    if "prediction" not in st.session_state:
        prediction = None
    else:
        prediction = st.session_state.prediction

    if prediction is None:

        st.markdown("""
<div class="prediction-card reveal">
<div class="prediction-title">Prediction result</div>
<div class="prediction-subtitle">Based on your property details</div>
<div class="prediction-price">₹ —</div>
<div class="prediction-label">ESTIMATED HOUSE PRICE</div>
<div class="prediction-note">
Enter your property details and click <b>Estimate house price</b> to generate a prediction.
</div>
</div>
""", unsafe_allow_html=True)

    else:

        st.markdown(f"""
<div class="prediction-card reveal">
<div class="prediction-title">Prediction result</div>
<div class="prediction-subtitle">Based on your property details</div>
<div class="prediction-price">₹ {prediction:,.0f}</div>
<div class="prediction-label">ESTIMATED HOUSE PRICE</div>
<div class="prediction-note">
This estimate is generated using a machine learning model trained on historical housing data.
Actual prices may vary.
</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# PREDICTION LOGIC
# =========================================================

if predict_button:

    new_house = pd.DataFrame([{
        "GrLivArea": area,
        "BedroomAbvGr": bedrooms,
        "FullBath": bathrooms,
        "YearBuilt": year,
        "OverallQual": quality,
        "GarageCars": garage,
        "TotalBsmtSF": basement,
        "1stFlrSF": first_floor,
        "Neighborhood": neighborhood
    }])

    predicted_price = model.predict(new_house)[0]

    st.session_state.prediction = predicted_price

    st.rerun()


# =========================================================
# MODEL PERFORMANCE
# =========================================================

st.markdown('<div id="performance"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-title">Model performance</div>
<div class="section-subtitle">Trained and evaluated on historical housing data</div>
""", unsafe_allow_html=True)


m1, m2, m3 = st.columns(3)

with m1:
    st.markdown("""
<div class="metric-card reveal" style="transition-delay:0s;">
<div class="metric-icon">🏆</div>
<div class="metric-value">90.19%</div>
<div class="metric-label">R² SCORE</div>
<div class="metric-description">Explains 90.19% of price variation</div>
</div>
""", unsafe_allow_html=True)


with m2:
    st.markdown("""
<div class="metric-card reveal" style="transition-delay:0.1s;">
<div class="metric-icon">🎯</div>
<div class="metric-value">₹18,080</div>
<div class="metric-label">MEAN ABSOLUTE ERROR</div>
<div class="metric-description">Average prediction error</div>
</div>
""", unsafe_allow_html=True)


with m3:
    st.markdown("""
<div class="metric-card reveal" style="transition-delay:0.2s;">
<div class="metric-icon">⚙️</div>
<div class="metric-value">Gradient Boosting</div>
<div class="metric-label">MODEL TYPE</div>
<div class="metric-description">Best performing of three models tested</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# WHY ESTATEIQ
# =========================================================

st.markdown('<div id="why"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-title">Why use EstateIQ?</div>
<div class="section-subtitle">Powered by data. Built for smarter real estate decisions.</div>
""", unsafe_allow_html=True)


w1, w2, w3, w4 = st.columns(4)

with w1:
    st.markdown("""
<div class="card feature-card reveal" style="transition-delay:0s;">
<div style="font-size:1.3rem;">📊</div>
<div class="feature-copy">
<b>Data-driven estimates</b>
<p style="color:var(--text-muted);font-size:0.75rem; margin-bottom:0;">Powered by real housing data and machine learning.</p>
</div>
</div>
""", unsafe_allow_html=True)


with w2:
    st.markdown("""
<div class="card feature-card reveal" style="transition-delay:0.1s;">
<div style="font-size:1.3rem;">⚙️</div>
<div class="feature-copy">
<b>Multiple models</b>
<p style="color:var(--text-muted);font-size:0.75rem; margin-bottom:0;">Compared Linear Regression, Random Forest and Gradient Boosting.</p>
</div>
</div>
""", unsafe_allow_html=True)


with w3:
    st.markdown("""
<div class="card feature-card reveal" style="transition-delay:0.2s;">
<div style="font-size:1.3rem;">🎯</div>
<div class="feature-copy">
<b>Accurate and reliable</b>
<p style="color:var(--text-muted);font-size:0.75rem; margin-bottom:0;">High prediction accuracy based on historical housing data.</p>
</div>
</div>
""", unsafe_allow_html=True)


with w4:
    st.markdown("""
<div class="card feature-card reveal" style="transition-delay:0.3s;">
<div style="font-size:1.3rem;">🏠</div>
<div class="feature-copy">
<b>Easy to use</b>
<p style="color:var(--text-muted);font-size:0.75rem; margin-bottom:0;">Get a price estimate by entering simple property details.</p>
</div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
🏠 EstateIQ &nbsp;|&nbsp; AI for a smarter real estate tomorrow.
<br><br>
EstateIQ · Machine Learning House Price Prediction
</div>
""", unsafe_allow_html=True)