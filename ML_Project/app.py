import streamlit as st
import pandas as pd
import joblib
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
    return joblib.load("house_price_model.pkl")


model = load_model()


# =========================================================
# THEME STATE
# =========================================================
# Streamlit's own theme (see .streamlit/config.toml) sets a stable
# dark baseline so the page never flashes back to Streamlit's default
# light theme on refresh. This toggle is a second, independent layer:
# our own CSS palette drawn on top of that stable baseline, switched
# with a button instead of Streamlit's built-in theme (which can't be
# swapped at runtime without a restart).

if "theme" not in st.session_state:
    st.session_state.theme = "dark"


def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


PALETTES = {
    "dark": dict(
        bg1="#16224f", bg2="#0a1130", bg3="#050813",
        surface="rgba(255,255,255,0.035)", border="rgba(255,255,255,0.10)",
        text="#eef2fc", text_muted="#93a0c2",
        accent="#4f6ef7", accent_light="#9db8ff", price="#34e0a1",
        input_bg="rgba(255,255,255,0.05)", scroll_color="#566089",
        footer_color="#4f5670", badge_bg="rgba(79,110,247,0.10)",
        badge_border="rgba(130,160,255,0.35)",
        particle_dot="rgba(150,180,255,0.65)",
        particle_line_rgb="130,160,255", particle_line_alpha=0.16,
        toggle_icon="☀️", toggle_help="Switch to light mode",
    ),
    "light": dict(
        bg1="#eef2ff", bg2="#f6f8fd", bg3="#ffffff",
        surface="rgba(20,30,70,0.04)", border="rgba(20,30,70,0.12)",
        text="#111935", text_muted="#57628a",
        accent="#4f6ef7", accent_light="#3552d8", price="#0f9d68",
        input_bg="rgba(20,30,70,0.05)", scroll_color="#8792b5",
        footer_color="#8792b5", badge_bg="rgba(79,110,247,0.08)",
        badge_border="rgba(79,110,247,0.30)",
        particle_dot="rgba(70,95,200,0.55)",
        particle_line_rgb="70,95,200", particle_line_alpha=0.11,
        toggle_icon="🌙", toggle_help="Switch to dark mode",
    ),
}

p = PALETTES[st.session_state.theme]


# =========================================================
# ANIMATED BACKGROUND (particle / valuation network)
# =========================================================
# st.markdown() strips <script> tags, so a plain markdown block can't
# animate anything. This uses components.html (a real iframe that runs
# JS) to draw a full-page canvas, then reaches into the parent
# document to pin that canvas behind the Streamlit app as a fixed,
# full-viewport background. On re-renders (e.g. the theme toggle) it
# only updates the dot/line colors on the existing canvas instead of
# rebuilding it, so there's no flicker or duplicate animation loops.

bg_script = """
<script>
(function() {
    const doc = window.parent.document;
    const win = window.parent;

    if (!win.__estateiqBg) { win.__estateiqBg = {}; }
    win.__estateiqBg.dotColor = "__DOT_COLOR__";
    win.__estateiqBg.lineRgb = "__LINE_RGB__";
    win.__estateiqBg.lineAlpha = __LINE_ALPHA__;

    if (doc.getElementById('estateiq-bg-canvas')) { return; }

    const canvas = doc.createElement('canvas');
    canvas.id = 'estateiq-bg-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    doc.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let w, h, nodes;

    function resize() {
        w = canvas.width = win.innerWidth;
        h = canvas.height = win.innerHeight;
        const count = Math.max(28, Math.min(70, Math.floor((w * h) / 26000)));
        nodes = Array.from({ length: count }, () => ({
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.22,
            vy: (Math.random() - 0.5) * 0.22,
            r: Math.random() * 1.4 + 0.8
        }));
    }
    win.addEventListener('resize', resize);
    resize();

    function tick() {
        ctx.clearRect(0, 0, w, h);
        const lineRgb = win.__estateiqBg.lineRgb;
        const lineAlpha = win.__estateiqBg.lineAlpha;

        for (let i = 0; i < nodes.length; i++) {
            const a = nodes[i];
            a.x += a.vx;
            a.y += a.vy;
            if (a.x < 0 || a.x > w) a.vx *= -1;
            if (a.y < 0 || a.y > h) a.vy *= -1;

            for (let j = i + 1; j < nodes.length; j++) {
                const b = nodes[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 140) {
                    ctx.strokeStyle = 'rgba(' + lineRgb + ',' + (lineAlpha * (1 - dist / 140)) + ')';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            }
        }

        ctx.fillStyle = win.__estateiqBg.dotColor;
        for (const n of nodes) {
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
            ctx.fill();
        }

        win.requestAnimationFrame(tick);
    }
    tick();
})();
</script>
"""

bg_script = (
    bg_script
    .replace("__DOT_COLOR__", p["particle_dot"])
    .replace("__LINE_RGB__", p["particle_line_rgb"])
    .replace("__LINE_ALPHA__", str(p["particle_line_alpha"]))
)

components.html(bg_script, height=0)


# =========================================================
# CUSTOM CSS
# =========================================================
# All HTML blocks below are written flush-left. Streamlit's markdown
# renderer treats any line indented 4+ spaces as a preformatted code
# block, which previously made the UI show raw <div> tags as text.
# Backgrounds are also forced with !important on every Streamlit
# container test-id, not just .stApp, since some containers ship
# their own opaque background in the default theme.

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
--input-bg: {p["input_bg"]};
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
background: radial-gradient(circle at 50% -10%, var(--bg1) 0%, var(--bg2) 45%, var(--bg3) 100%) !important;
color: var(--text) !important;
transition: background 0.25s ease, color 0.25s ease;
}}

[data-testid="stHeader"] {{ background: transparent !important; }}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}

.block-container {{
max-width: 1180px;
padding-top: 0.5rem;
padding-bottom: 3rem;
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

/* Theme toggle button (a real Streamlit button, styled as a small
   round icon pill so it reads as a control, not a text link) */
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
button[kind="secondary"]:hover {{
border-color: var(--accent) !important;
}}

/* Hero */
.hero-wrap {{
text-align: center;
padding: 60px 20px 40px 20px;
}}
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
.hero-scroll {{
color: var(--scroll-color);
font-size: 0.7rem;
font-weight: 600;
letter-spacing: 2px;
}}

/* Cards */
.card {{
background: var(--surface);
border: 1px solid var(--border);
border-radius: 18px;
padding: 26px;
backdrop-filter: blur(6px);
}}
.card-title {{
font-family: 'Space Grotesk', sans-serif;
color: var(--text);
font-size: 1.15rem;
font-weight: 600;
margin-bottom: 6px;
}}
.card-subtitle {{
color: var(--text-muted);
font-size: 0.86rem;
line-height: 1.5;
}}

/* Prediction card */
.prediction-card {{
background: var(--surface);
border: 1px solid var(--badge-border);
border-radius: 18px;
padding: 30px;
min-height: 300px;
backdrop-filter: blur(6px);
}}
.prediction-title {{
font-family: 'Space Grotesk', sans-serif;
font-size: 1.15rem;
font-weight: 600;
color: var(--text);
margin-bottom: 4px;
}}
.prediction-subtitle {{
color: var(--text-muted);
font-size: 0.85rem;
margin-bottom: 26px;
}}
.prediction-price {{
font-family: 'Space Grotesk', sans-serif;
font-size: 2.5rem;
font-weight: 700;
color: var(--price);
margin: 6px 0 22px 0;
}}
.prediction-label {{
color: var(--text-muted);
font-size: 0.78rem;
font-weight: 600;
margin-bottom: 12px;
}}
.prediction-note {{
background: var(--input-bg);
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
padding: 20px;
height: 140px;
backdrop-filter: blur(6px);
}}
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
button[kind="primary"]:hover {{
transform: translateY(-1px);
filter: brightness(1.08);
}}

/* Inputs */
.stNumberInput label, .stSelectbox label {{
color: var(--text-muted) !important;
font-weight: 600 !important;
font-size: 0.8rem !important;
}}
.stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
background-color: var(--input-bg) !important;
color: var(--text) !important;
border-color: var(--border) !important;
}}

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
    st.button(
        p["toggle_icon"],
        key="theme_toggle_btn",
        on_click=toggle_theme,
        help=p["toggle_help"],
        type="secondary",
    )

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
<div class="card">
<div class="card-title">Property details</div>
<div class="card-subtitle">Enter the key details of the property to get an estimated price.</div>
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
<div class="prediction-card">
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
<div class="prediction-card">
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
<div class="metric-card">
<div class="metric-icon">🏆</div>
<div class="metric-value">90.19%</div>
<div class="metric-label">R² SCORE</div>
<div class="metric-description">Explains 90.19% of price variation</div>
</div>
""", unsafe_allow_html=True)


with m2:
    st.markdown("""
<div class="metric-card">
<div class="metric-icon">🎯</div>
<div class="metric-value">₹18,080</div>
<div class="metric-label">MEAN ABSOLUTE ERROR</div>
<div class="metric-description">Average prediction error</div>
</div>
""", unsafe_allow_html=True)


with m3:
    st.markdown("""
<div class="metric-card">
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
<div class="card">
<div style="font-size:1.3rem;">📊</div>
<b>Data-driven estimates</b>
<p style="color:var(--text-muted);font-size:0.75rem;">Powered by real housing data and machine learning.</p>
</div>
""", unsafe_allow_html=True)


with w2:
    st.markdown("""
<div class="card">
<div style="font-size:1.3rem;">⚙️</div>
<b>Multiple models</b>
<p style="color:var(--text-muted);font-size:0.75rem;">Compared Linear Regression, Random Forest and Gradient Boosting.</p>
</div>
""", unsafe_allow_html=True)


with w3:
    st.markdown("""
<div class="card">
<div style="font-size:1.3rem;">🎯</div>
<b>Accurate and reliable</b>
<p style="color:var(--text-muted);font-size:0.75rem;">High prediction accuracy based on historical housing data.</p>
</div>
""", unsafe_allow_html=True)


with w4:
    st.markdown("""
<div class="card">
<div style="font-size:1.3rem;">🏠</div>
<b>Easy to use</b>
<p style="color:var(--text-muted);font-size:0.75rem;">Get a price estimate by entering simple property details.</p>
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