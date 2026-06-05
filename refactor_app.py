import re
import sys

filepath = 'c:/Users/hp/Desktop/polystorebench/polystorebench/polystorebench/dashboard/app.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS
old_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* dark gradient background */
.stApp { background: linear-gradient(135deg, #0d0f1a 0%, #111827 60%, #0d1117 100%); }

/* sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #1a2035 100%);
    border-right: 1px solid #2d3748;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* KPI cards */
.kpi-grid { display:flex; gap:16px; margin-bottom:24px; flex-wrap:wrap; }
.kpi-card {
    flex:1; min-width:160px;
    background: linear-gradient(135deg, #1e2a45 0%, #162032 100%);
    border: 1px solid #2d3748;
    border-radius: 16px;
    padding: 20px 24px;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background: var(--accent, #6366f1);
    border-radius:16px 16px 0 0;
}
.kpi-label { font-size:11px; font-weight:600; color:#94a3b8; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px; }
.kpi-value { font-size:32px; font-weight:900; color:#f1f5f9; line-height:1; }
.kpi-delta { font-size:12px; color:#64748b; margin-top:6px; }
.kpi-icon  { font-size:28px; position:absolute; top:16px; right:16px; opacity:.35; }

/* section headers */
.section-title {
    font-size:18px; font-weight:700; color:#e2e8f0;
    border-left:4px solid #6366f1; padding-left:12px; margin:24px 0 16px;
}

/* tab styling */
[data-testid="stTabs"] button { color:#94a3b8 !important; font-weight:600; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#a5b4fc !important; border-bottom-color:#6366f1 !important; }

/* plotly chart background */
.js-plotly-plot .plotly { border-radius:12px; }

/* divider */
hr { border-color: #2d3748; }
</style>"""

new_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* light background */
.stApp { background: #f8fafc; }

/* sidebar */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] * { color: #334155 !important; }

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* KPI cards */
.kpi-grid { display:flex; gap:16px; margin-bottom:24px; flex-wrap:wrap; }
.kpi-card {
    flex:1; min-width:160px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    border-radius: 16px;
    padding: 20px 24px;
    position: relative; overflow: hidden;
}
.kpi-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:3px;
    background: var(--accent, #6366f1);
    border-radius:16px 16px 0 0;
}
.kpi-label { font-size:11px; font-weight:600; color:#64748b; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px; }
.kpi-value { font-size:32px; font-weight:900; color:#0f172a; line-height:1; }
.kpi-delta { font-size:12px; color:#64748b; margin-top:6px; }

/* section headers */
.section-title {
    font-size:18px; font-weight:700; color:#0f172a;
    border-left:4px solid #6366f1; padding-left:12px; margin:24px 0 16px;
}

/* tab styling */
[data-testid="stTabs"] button { color:#64748b !important; font-weight:600; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#4f46e5 !important; border-bottom-color:#4f46e5 !important; }

/* plotly chart background */
.js-plotly-plot .plotly { border-radius:12px; }

/* divider */
hr { border-color: #e2e8f0; }

/* Carousel Animation */
@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(calc(-200px * 6)); }
}
.carousel-container {
    width: 100%;
    overflow: hidden;
    background: #ffffff;
    padding: 16px 0;
    border-top: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05);
    display: flex;
}
.carousel-track {
    display: flex;
    width: calc(200px * 12);
    animation: scroll 20s linear infinite;
}
.carousel-slide {
    width: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0 24px;
}
.carousel-slide img {
    max-width: 100%;
    max-height: 60px;
    object-fit: contain;
}
</style>"""

content = content.replace(old_css, new_css)

# 2. Plotly template
content = content.replace('PLOTLY_TEMPLATE = "plotly_dark"', 'PLOTLY_TEMPLATE = "plotly_white"')

# 3. Text & Emojis Replacements
replacements = {
    'page_icon="⚡",': 'page_icon="Dashboard",',
    '"🟢 Online"': '"Online"',
    '"🔴 Offline"': '"Offline"',
    '### ⚙️ Filters': '### Filters',
    '🔄 Refresh': 'Refresh',
    '### 📡 Service Status': '### Service Status',
    '<div style="font-size:64px; margin-bottom:16px;">📊</div>': '',
    '<div style="font-size:44px;">⚡</div>': '',
    'color:#e2e8f0;': 'color:#0f172a;', # for empty state
    'color:#f1f5f9;': 'color:#0f172a;', # header text
    'color:#a5b4fc;': 'color:#4f46e5;', # quick start label
    'background:#1e2a45; border:1px solid #2d3748;': 'background:#f1f5f9; border:1px solid #e2e8f0;', # quick start block
    '("🏃",': '("",',
    '("🖥️",': '("",',
    '("⚡",': '("",',
    '("⏱️",': '("",',
    '("🥇",': '("",',
    '"📊 Overview", "⏳ Execution Time", "⏱ Latency",': '"Overview", "Execution Time", "Latency",',
    '"🚀 Throughput", "📈 Scalability", "🖥️ Resources", "📋 Raw Data",': '"Throughput", "Scalability", "Resources", "Raw Data",',
    '"⚡ Run Benchmark"': '"Run Benchmark"',
    '⬇️ Download CSV': 'Download CSV',
    '🖥️ Systems': 'Systems',
    '⚙️ Operations': 'Operations',
    '📊 Dataset size (rows)': 'Dataset size (rows)',
    '🏷️ Scenario name': 'Scenario name',
    '🔀 Concurrency level': 'Concurrency level',
    '💻 Equivalent CMD commands': 'Equivalent CMD commands',
    '▶️ Run Benchmarks': 'Run Benchmarks',
    '✅ **': '**',
    '❌ **': '**',
    '⚠️ **': '**',
    '⏳ **': '**',
    '✅ Saved': 'Saved',
    '📊 Results': 'Results',
    '🔄 Click **Refresh**': 'Click **Refresh**',
    '<div style="font-size:48px;">⬆️</div>': '',
    '<div class="kpi-icon">{icon}</div>': '',
}

for old_str, new_str in replacements.items():
    content = content.replace(old_str, new_str)

# Add base64 carousel logic right after header
header_block = 'st.markdown("---")'
carousel_logic = '''
# ── Logo Carousel ─────────────────────────────────────────────────────────────
import base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

logos = ["cassandra.png", "hadoop.png", "hive.png", "MongoDB.png", "redis.png", "spark.png"]
slides_html = ""
for logo in logos:
    b64 = get_base64_of_bin_file(str(ROOT / logo))
    if b64:
        slides_html += f'<div class="carousel-slide"><img src="data:image/png;base64,{b64}"></div>'

# duplicate for infinite scroll effect
carousel_html = f"""
<div class="carousel-container">
    <div class="carousel-track">
        {slides_html}
        {slides_html}
    </div>
</div>
"""
st.markdown(carousel_html, unsafe_allow_html=True)
st.markdown("---")
'''
content = content.replace(header_block, carousel_logic, 1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete.")
