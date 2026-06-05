"""
PolyStoreBench Dashboard
Run from project root: streamlit run dashboard/app.py
"""
import ast
import sys
from pathlib import Path
from datetime import datetime
import json
import os
import socket
import subprocess

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Path bootstrap ────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PolyStoreBench",
    page_icon="Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme / CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* light background */
.stApp { background: #f8fafc; }

/* sidebar */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* hide streamlit chrome */
#MainMenu, footer { visibility: hidden; }

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
</style>
""", unsafe_allow_html=True)

# ── System colour palette ─────────────────────────────────────────────────────
SYSTEM_COLORS = {
    "mongodb":   "#00ED64",
    "redis":     "#FF4438",
    "cassandra": "#1287B1",
    "spark":     "#E25A1C",
    "hive":      "#FDB97D",
    "hadoop":    "#60B515",
}
PLOTLY_TEMPLATE = "plotly_white"

# ── Data loading (real data only) ────────────────────────────────────────────
@st.cache_data(ttl=15)
def load_data() -> pd.DataFrame:
    """Load real benchmark results — tries PostgreSQL first, then SQLite."""
    import os
    from sqlalchemy import create_engine, text

    # Always try PostgreSQL first (even if module-level engine cached SQLite)
    pg_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://psb_user:psb_pass@127.0.0.1:5432/polystorebench"
    )
    for url in [pg_url, f"sqlite:///{ROOT}/storage/results.db"]:
        try:
            eng = create_engine(url, pool_pre_ping=True,
                                connect_args={"connect_timeout": 3} if "postgresql" in url else {})
            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
            df = pd.read_sql(
                "SELECT * FROM benchmark_results ORDER BY created_at DESC", eng
            )
            return df
        except Exception:
            continue
    return pd.DataFrame()


def check_service(host: str, port: int, label: str) -> tuple[str, str]:
    """Quick TCP reachability check."""
    import socket
    try:
        with socket.create_connection((host, port), timeout=1):
            return label, "Online"
    except Exception:
        return label, "Offline"


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:28px 0 12px; display:flex; align-items:center; gap:16px;">
  
  <div>
    <div style="font-size:30px;font-weight:900;color:#0f172a;letter-spacing:-1px;">
      PolyStore<span style="color:#6366f1;">Bench</span>
    </div>
    <div style="font-size:13px;color:#64748b;">
      Unified Benchmarking · Hadoop · Spark · Hive · MongoDB · Cassandra · Redis
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Logo Carousel ─────────────────────────────────────────────────────────────
import base64
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

logos_config = {
    "cassandra.png": 1.5,
    "hadoop.png": 1.7,
    "MongoDB.png": 1.4,
    "hive.png": 1.0,
    "redis.png": 1.0,
    "spark.png": 1.0
}

slides_html = ""
for logo, scale in logos_config.items():
    b64 = get_base64_of_bin_file(str(ROOT / logo))
    if b64:
        slides_html += f'<div class="carousel-slide"><img style="transform: scale({scale});" src="data:image/png;base64,{b64}"></div>'

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


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")

    raw_df = load_data()

    if not raw_df.empty:
        all_systems   = sorted(raw_df["system_name"].unique())
        all_ops       = sorted(raw_df["operation"].unique())
        all_sizes     = sorted(raw_df["dataset_size"].unique())
        all_scenarios = sorted(raw_df["scenario_name"].unique())

        # Auto-select newly discovered values by tracking them in session_state
        if "prev_sizes" not in st.session_state:
            st.session_state.sel_systems = all_systems
            st.session_state.sel_ops = all_ops
            st.session_state.sel_sizes = all_sizes
            st.session_state.sel_scenarios = all_scenarios
            st.session_state.prev_sizes = all_sizes
            st.session_state.prev_systems = all_systems
            st.session_state.prev_ops = all_ops
            st.session_state.prev_scenarios = all_scenarios

        # If new data appeared, add it to the current selection
        for s in all_systems:
            if s not in st.session_state.prev_systems and s not in st.session_state.sel_systems:
                st.session_state.sel_systems.append(s)
        for o in all_ops:
            if o not in st.session_state.prev_ops and o not in st.session_state.sel_ops:
                st.session_state.sel_ops.append(o)
        for sz in all_sizes:
            if sz not in st.session_state.prev_sizes and sz not in st.session_state.sel_sizes:
                st.session_state.sel_sizes.append(sz)
        for sc in all_scenarios:
            if sc not in st.session_state.prev_scenarios and sc not in st.session_state.sel_scenarios:
                st.session_state.sel_scenarios.append(sc)

        st.session_state.prev_systems = all_systems
        st.session_state.prev_ops = all_ops
        st.session_state.prev_sizes = all_sizes
        st.session_state.prev_scenarios = all_scenarios

        sel_scenarios = st.multiselect("Scenarios / Uploads", all_scenarios, default=st.session_state.sel_scenarios, key="sel_scenarios")
        sel_systems   = st.multiselect("Systems",      all_systems, default=st.session_state.sel_systems, key="sel_systems")
        sel_ops       = st.multiselect("Operations",   all_ops,     default=st.session_state.sel_ops, key="sel_ops")
        sel_sizes     = st.multiselect("Dataset size", all_sizes,   default=st.session_state.sel_sizes, key="sel_sizes")

    st.markdown("---")
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("### Service Status")
    for host, port, label in [
        ("127.0.0.1", 27018, "MongoDB"),
        ("127.0.0.1", 6379,  "Redis"),
        ("127.0.0.1", 9042,  "Cassandra"),
        ("127.0.0.1", 5432,  "PostgreSQL"),
    ]:
        _, status = check_service(host, port, label)
        st.markdown(f"`{label}` &nbsp; {status}")

# ── Empty state ───────────────────────────────────────────────────────────────
if raw_df.empty:
    st.markdown("""
    <div style="text-align:center; padding:60px 40px;">
      
      <h2 style="color:#0f172a; font-size:28px; font-weight:800;">No Benchmark Results Yet</h2>
      <p style="color:#64748b; font-size:16px; max-width:520px; margin:0 auto 32px;">
        The database is empty. Start the Docker services, initialise the DB,
        then run the benchmark suite to populate real data.
      </p>
      <div style="background:#f1f5f9; border:1px solid #e2e8f0; border-radius:12px;
                  padding:24px 32px; display:inline-block; text-align:left;">
        <p style="color:#4f46e5; font-weight:700; margin-bottom:12px;">Quick Start</p>
        <code style="color:#10b981; display:block; margin-bottom:6px;">docker compose up -d</code>
        <code style="color:#10b981; display:block; margin-bottom:6px;">python scripts/init_db.py</code>
        <code style="color:#10b981; display:block;">scripts\\run_all.bat</code>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Apply filters ─────────────────────────────────────────────────────────────
df = raw_df[
    raw_df["scenario_name"].isin(sel_scenarios) &
    raw_df["system_name"].isin(sel_systems) &
    raw_df["operation"].isin(sel_ops) &
    raw_df["dataset_size"].isin(sel_sizes)
].copy()

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

colors_used = {s: SYSTEM_COLORS.get(s, "#a78bfa") for s in df["system_name"].unique()}

# ── KPI cards ─────────────────────────────────────────────────────────────────
total_runs   = len(df)
n_systems    = df["system_name"].nunique()
best_tput    = df["throughput_ops_sec"].max()
avg_lat      = df["latency_avg_ms"].mean()
fastest_sys  = df.groupby("system_name")["execution_time_sec"].mean().idxmin()

kpis = [
    ("", "#6366f1", "Total Benchmark Runs",  f"{total_runs:,}",       "across all systems"),
    ("", "#22d3ee", "Systems Tested",         f"{n_systems}",          ", ".join(df["system_name"].unique()[:4])),
    ("", "#10b981", "Peak Throughput",         f"{best_tput:,.0f}",     "ops / second"),
    ("", "#f59e0b", "Avg Latency",             f"{avg_lat:.2f} ms",     "across all ops"),
    ("", "#a78bfa", "Fastest System",          fastest_sys.upper(),     "by avg exec time"),
]

cards_html = '<div class="kpi-grid">'
for icon, accent, label, value, delta in kpis:
    cards_html += f"""<div class="kpi-card" style="--accent:{accent};">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-delta">{delta}</div>
</div>"""
cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Overview", "Execution Time", "Latency",
    "Throughput", "Scalability", "Resources", "Raw Data",
    "Run Benchmark"
])


# helper: bar grouped by system+operation
def grouped_bar(metric, title, y_label):
    agg = df.groupby(["system_name","operation"], as_index=False)[metric].mean()
    fig = px.bar(
        agg, x="operation", y=metric, color="system_name",
        barmode="group", template=PLOTLY_TEMPLATE, title=title,
        color_discrete_map=colors_used, labels={metric: y_label},
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      legend_title="System", height=420)
    return fig


# ── Tab 1: Overview ───────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    # Radar chart
    with c1:
        st.markdown('<div class="section-title">Multi-Metric Radar</div>', unsafe_allow_html=True)
        metrics = ["execution_time_sec","latency_avg_ms","throughput_ops_sec","cpu_percent","memory_percent"]
        labels  = ["Exec Time","Latency","Throughput","CPU %","Memory %"]
        radar_df = df.groupby("system_name")[metrics].mean()
        # normalise 0-1
        norm = (radar_df - radar_df.min()) / (radar_df.max() - radar_df.min() + 1e-9)
        fig = go.Figure()
        for sys_ in norm.index:
            vals = norm.loc[sys_].tolist()
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=labels + [labels[0]],
                fill="toself", name=sys_,
                line_color=colors_used.get(sys_, "#fff"),
                fillcolor=colors_used.get(sys_, "#fff"),
                opacity=0.25,
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1])),
            template=PLOTLY_TEMPLATE, height=420,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, theme=None, use_container_width=True)

    # Heatmap
    with c2:
        st.markdown('<div class="section-title">Performance Heatmap</div>', unsafe_allow_html=True)
        heat = df.groupby(["system_name","operation"])["execution_time_sec"].mean().unstack(fill_value=0)
        fig2 = px.imshow(
            heat, text_auto=".2f", aspect="auto", template=PLOTLY_TEMPLATE,
            color_continuous_scale="Viridis",
            labels=dict(color="Exec Time (s)"),
            title="Avg Execution Time (s) — System × Operation",
        )
        fig2.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, theme=None, use_container_width=True)

    # Summary table
    st.markdown('<div class="section-title">Summary Statistics</div>', unsafe_allow_html=True)
    summary = df.groupby("system_name").agg(
        runs=("id","count"),
        avg_exec=("execution_time_sec","mean"),
        avg_lat=("latency_avg_ms","mean"),
        avg_tput=("throughput_ops_sec","mean"),
        avg_cpu=("cpu_percent","mean"),
    ).round(3).reset_index()
    summary.columns = ["System","Runs","Avg Exec (s)","Avg Latency (ms)","Avg Throughput (ops/s)","Avg CPU %"]
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ── Tab 2: Execution Time ─────────────────────────────────────────────────────
with tab2:
    st.plotly_chart(grouped_bar("execution_time_sec","Execution Time by System & Operation","Seconds"),
                    theme=None, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        avg_exec = df.groupby("system_name")["execution_time_sec"].mean().reset_index()
        fig = px.bar(avg_exec, x="system_name", y="execution_time_sec",
                     color="system_name", template=PLOTLY_TEMPLATE,
                     color_discrete_map=colors_used,
                     title="Overall Avg Execution Time per System",
                     labels={"execution_time_sec":"Seconds","system_name":"System"})
        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", height=380)
        st.plotly_chart(fig, theme=None, use_container_width=True)

    with c2:
        fig2 = px.box(df, x="system_name", y="execution_time_sec",
                      color="system_name", template=PLOTLY_TEMPLATE,
                      color_discrete_map=colors_used,
                      title="Execution Time Distribution",
                      labels={"execution_time_sec":"Seconds","system_name":"System"})
        fig2.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", height=380)
        st.plotly_chart(fig2, theme=None, use_container_width=True)


# ── Tab 3: Latency ────────────────────────────────────────────────────────────
with tab3:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(df, x="system_name", y="latency_avg_ms",
                     color="system_name", template=PLOTLY_TEMPLATE,
                     color_discrete_map=colors_used,
                     title="Latency Distribution per System",
                     labels={"latency_avg_ms":"Avg Latency (ms)","system_name":"System"})
        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", height=420)
        st.plotly_chart(fig, theme=None, use_container_width=True)

    with c2:
        lat_df = df.groupby(["system_name","operation"])["latency_avg_ms"].mean().reset_index()
        fig2 = px.bar(lat_df, x="operation", y="latency_avg_ms", color="system_name",
                      barmode="group", template=PLOTLY_TEMPLATE,
                      color_discrete_map=colors_used,
                      title="Avg Latency by Operation",
                      labels={"latency_avg_ms":"ms"})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420)
        st.plotly_chart(fig2, theme=None, use_container_width=True)

    # Min/Avg/Max latency grouped bar
    lat_agg = df.groupby("system_name").agg(
        Min=("latency_min_ms","mean"),
        Avg=("latency_avg_ms","mean"),
        Max=("latency_max_ms","mean"),
    ).reset_index()
    fig3 = go.Figure()
    for col, color in [("Min","#10b981"),("Avg","#6366f1"),("Max","#ef4444")]:
        fig3.add_trace(go.Bar(name=col, x=lat_agg["system_name"], y=lat_agg[col],
                              marker_color=color))
    fig3.update_layout(barmode="group", template=PLOTLY_TEMPLATE,
                       title="Min / Avg / Max Latency per System",
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       height=380, yaxis_title="ms")
    st.plotly_chart(fig3, theme=None, use_container_width=True)


# ── Tab 4: Throughput ─────────────────────────────────────────────────────────
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        tput = df.groupby("system_name")["throughput_ops_sec"].mean().reset_index()
        fig = px.bar(tput, x="system_name", y="throughput_ops_sec",
                     color="system_name", template=PLOTLY_TEMPLATE,
                     color_discrete_map=colors_used,
                     title="Avg Throughput per System",
                     labels={"throughput_ops_sec":"ops/sec","system_name":"System"})
        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", height=420)
        st.plotly_chart(fig, theme=None, use_container_width=True)

    with c2:
        fig2 = px.scatter(df, x="latency_avg_ms", y="throughput_ops_sec",
                          color="system_name", size="dataset_size",
                          hover_data=["operation","dataset_size"],
                          template=PLOTLY_TEMPLATE, color_discrete_map=colors_used,
                          title="Latency vs Throughput (bubble=dataset size)",
                          labels={"latency_avg_ms":"Latency (ms)","throughput_ops_sec":"ops/sec"})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420)
        st.plotly_chart(fig2, theme=None, use_container_width=True)


# ── Tab 5: Scalability ────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">Execution Time vs Dataset Size</div>', unsafe_allow_html=True)
    scale_df = df.groupby(["system_name","dataset_size"])["execution_time_sec"].mean().reset_index()
    fig = px.line(scale_df, x="dataset_size", y="execution_time_sec",
                  color="system_name", markers=True,
                  template=PLOTLY_TEMPLATE, color_discrete_map=colors_used,
                  title="Scalability: Avg Exec Time vs Dataset Size",
                  labels={"execution_time_sec":"Exec Time (s)","dataset_size":"Dataset Size"})
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
    st.plotly_chart(fig, theme=None, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        tput_scale = df.groupby(["system_name","dataset_size"])["throughput_ops_sec"].mean().reset_index()
        fig2 = px.line(tput_scale, x="dataset_size", y="throughput_ops_sec",
                       color="system_name", markers=True,
                       template=PLOTLY_TEMPLATE, color_discrete_map=colors_used,
                       title="Throughput vs Dataset Size",
                       labels={"throughput_ops_sec":"ops/sec","dataset_size":"Dataset Size"})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
        st.plotly_chart(fig2, theme=None, use_container_width=True)

    with c2:
        lat_scale = df.groupby(["system_name","dataset_size"])["latency_avg_ms"].mean().reset_index()
        fig3 = px.line(lat_scale, x="dataset_size", y="latency_avg_ms",
                       color="system_name", markers=True,
                       template=PLOTLY_TEMPLATE, color_discrete_map=colors_used,
                       title="Latency vs Dataset Size",
                       labels={"latency_avg_ms":"Latency (ms)","dataset_size":"Dataset Size"})
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
        st.plotly_chart(fig3, theme=None, use_container_width=True)


# ── Tab 6: Resources ──────────────────────────────────────────────────────────
with tab6:
    res = df.groupby("system_name")[["cpu_percent","memory_percent","disk_percent"]].mean().reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for metric, color, label in [
            ("cpu_percent","#6366f1","CPU %"),
            ("memory_percent","#22d3ee","Memory %"),
            ("disk_percent","#f59e0b","Disk %"),
        ]:
            fig.add_trace(go.Bar(name=label, x=res["system_name"], y=res[metric],
                                 marker_color=color))
        fig.update_layout(barmode="group", template=PLOTLY_TEMPLATE,
                          title="Avg Resource Usage per System",
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          height=420, yaxis_title="%")
        st.plotly_chart(fig, theme=None, use_container_width=True)

    with c2:
        fig2 = px.scatter(df, x="cpu_percent", y="memory_percent",
                          color="system_name", size="execution_time_sec",
                          template=PLOTLY_TEMPLATE, color_discrete_map=colors_used,
                          title="CPU vs Memory Usage (bubble=exec time)",
                          labels={"cpu_percent":"CPU %","memory_percent":"Memory %"})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420)
        st.plotly_chart(fig2, theme=None, use_container_width=True)

    # Stacked resource breakdown
    res_melt = res.melt(id_vars="system_name",
                        value_vars=["cpu_percent","memory_percent","disk_percent"],
                        var_name="Resource", value_name="Percent")
    fig3 = px.bar(res_melt, x="system_name", y="Percent", color="Resource",
                  barmode="stack", template=PLOTLY_TEMPLATE,
                  color_discrete_map={"cpu_percent":"#6366f1","memory_percent":"#22d3ee","disk_percent":"#f59e0b"},
                  title="Stacked Resource Utilisation",
                  labels={"system_name":"System"})
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380)
    st.plotly_chart(fig3, theme=None, use_container_width=True)


# ── Tab 7: Raw Data ───────────────────────────────────────────────────────────
with tab7:
    st.markdown('<div class="section-title">Raw Benchmark Results</div>', unsafe_allow_html=True)
    st.markdown(f"**{len(df):,} rows** matching current filters")
    cols_order = [
        "system_name","operation","scenario_name","dataset_size","run_number",
        "execution_time_sec","latency_avg_ms","latency_min_ms","latency_max_ms",
        "throughput_ops_sec","concurrency_level","cpu_percent","memory_percent","disk_percent",
    ]
    show_cols = [c for c in cols_order if c in df.columns]
    st.dataframe(df[show_cols].sort_values(["system_name","operation"]),
                 use_container_width=True, height=500)

    csv = df[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "polystorebench_results.csv", "text/csv")


# ── Tab 8: Run Benchmark ─────────────────────────────────────────────────
with tab8:
    st.markdown('<div class="section-title">Run Benchmark from Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    Upload a **CSV** or **JSON** dataset file, select systems and operations,
    then click **Run**. Results are saved to the database and charts update automatically.
    """)

    uploaded = st.file_uploader(
        "Upload Dataset (CSV or JSON)",
        type=["csv", "json"],
        help="Any CSV or JSON dataset is accepted; no fixed schema is required."
    )

    if uploaded is not None:
        # ── Save the uploaded file ───────────────────────────────────────────
        data_dir = ROOT / "data"
        data_dir.mkdir(exist_ok=True)
        saved_path = data_dir / uploaded.name
        saved_path.write_bytes(uploaded.getbuffer())

        # Auto-detect size
        raw_bytes = uploaded.getvalue()
        try:
            if uploaded.name.endswith(".json"):
                raw_text = raw_bytes.decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(raw_text)
                    if isinstance(parsed, list):
                        detected_size = len(parsed)
                    else:
                        detected_size = 1
                except Exception:
                    detected_size = sum(
                        1 for line in raw_text.splitlines()
                        if line.strip().startswith("{")
                    )
            else:
                import io
                detected_size = max(1, sum(1 for _ in io.StringIO(raw_bytes.decode("utf-8", errors="replace"))) - 1)
        except Exception:
            detected_size = 10000

        st.success(f"Saved to `{saved_path.name}` — detected **{detected_size:,} rows**")

        # ── Options ─────────────────────────────────────────────────────────────
        col1, col2, col3 = st.columns(3)
        with col1:
            run_systems = st.multiselect(
                "Systems",
                ["mongodb", "redis", "cassandra", "spark", "hadoop", "hive"],
                default=["mongodb", "redis"],
                help="hadoop and hive require Docker containers running"
            )
        with col2:
            run_ops = st.multiselect(
                "Operations",
                ["insert", "read", "update", "delete", "query"],
                default=["insert", "read"]
            )
        with col3:
            dataset_size_inp = st.number_input(
                "Dataset size (rows)",
                value=int(detected_size),
                min_value=1,
                max_value=10_000_000
            )

        c1, c2 = st.columns([2, 1])
        with c1:
            scenario_inp = st.text_input(
                "Scenario name",
                value="dashboard_bench",
                help="Label stored in the database with these results"
            )
        with c2:
            concurrency_inp = st.number_input(
                "Concurrency level",
                value=1, min_value=1, max_value=50
            )

        st.markdown("---")

        # ── CMD preview ──────────────────────────────────────────────────────────
        if run_systems and run_ops:
            with st.expander("Equivalent CMD commands (copy to run manually)", expanded=False):
                lines = ["@echo off", f"REM Dataset: {saved_path.name}  Size: {int(dataset_size_inp):,}"]
                for s in run_systems:
                    ds = str(saved_path)
                    for op in run_ops:
                        cmd_str = (f"python main.py --system {s} --operation {op} "
                                   f"--dataset \"{ds}\" --size {int(dataset_size_inp)} "
                                   f"--scenario {scenario_inp} "
                                   f"--concurrency {int(concurrency_inp)}")
                        lines.append(cmd_str)
                st.code("\n".join(lines), language="bat")

        # ── Run button ────────────────────────────────────────────────────────────
        # ── Hive readiness warning ───────────────────────────────────────────
        if "hive" in run_systems:
            try:
                with socket.create_connection(("127.0.0.1", 10000), timeout=2):
                    hive_ok = True
            except Exception:
                hive_ok = False
            if not hive_ok:
                st.warning("**Hive** port 10000 is not reachable. "
                           "HiveServer2 may still be starting up — wait 2–3 minutes after `docker compose up -d` before running Hive benchmarks.")

        if st.button("Run Benchmarks", type="primary",
                     disabled=(not run_systems or not run_ops)):

            if not raw_df.empty and scenario_inp in all_scenarios:
                st.error(f"❌ Scenario name '{scenario_inp}' already exists in the database. Please choose a different name to avoid mixing data.")
                st.stop()

            total_jobs = len(run_systems) * len(run_ops)
            results_list = []
            errors_list  = []

            with st.status(f"Running {total_jobs} benchmark job(s)...", expanded=True) as bench_status:
                for sys_name in run_systems:
                    for op in run_ops:
                        ds_path = str(saved_path)

                        with st.spinner(f"**{sys_name.upper()}** → `{op}` (this may take a moment)..."):

                            cmd = [
                                sys.executable,
                                str(ROOT / "main.py"),
                                "--system",      sys_name,
                                "--operation",   op,
                                "--dataset",     ds_path,
                                "--size",        str(int(dataset_size_inp)),
                                "--scenario",    str(scenario_inp),
                                "--concurrency", str(int(concurrency_inp)),
                            ]

                            proc = subprocess.run(
                                cmd, capture_output=True, text=True, cwd=str(ROOT)
                            )

                            if proc.returncode == 0:
                                # Last non-empty line starting with { is the result dict
                                lines_out = [l.strip() for l in proc.stdout.strip().splitlines() if l.strip().startswith("{")]
                                if lines_out:
                                    try:
                                        r = ast.literal_eval(lines_out[-1])
                                        results_list.append(r)
                                        t    = r.get("execution_time_sec", "?")
                                        tput = r.get("throughput_ops_sec", 0)
                                        st.write(f"**{sys_name}** `{op}` — `{t}s` | `{tput:,.0f} ops/s`")
                                    except Exception as parse_err:
                                        st.write(f"**{sys_name}** `{op}` done (result parse error: {parse_err})")
                                else:
                                    st.write(f"**{sys_name}** `{op}` done")
                            else:
                                # Extract the most informative error line from stderr
                                err_lines = [l.strip() for l in proc.stderr.strip().splitlines() if l.strip()]
                                # Find the last non-traceback line (the actual exception message)
                                short_err = "unknown error"
                                for line in reversed(err_lines):
                                    if not line.startswith("at ") and not line.startswith("File ") and line:
                                        short_err = line
                                        break
                                errors_list.append(f"{sys_name}/{op}: {short_err}")
                                st.write(f"**{sys_name}** `{op}` failed: `{short_err}`")
                                with st.expander(f"Full error log — {sys_name}/{op}"):
                                    st.code(proc.stderr[-3000:] if proc.stderr else "(no stderr)", language="text")

                if errors_list:
                    bench_status.update(label=f"Completed with {len(errors_list)} error(s)", state="error")
                else:
                    bench_status.update(label=f"All {total_jobs} benchmarks complete!", state="complete")

            # ── Show result table ──────────────────────────────────────────────────────
            if results_list:
                st.markdown("### Results")
                res_df = pd.DataFrame(results_list)
                cols_show = [
                    "system_name", "operation", "dataset_size",
                    "execution_time_sec", "latency_avg_ms", "throughput_ops_sec",
                    "cpu_percent", "memory_percent",
                ]
                st.dataframe(
                    res_df[[c for c in cols_show if c in res_df.columns]]
                        .style.background_gradient(subset=["execution_time_sec"], cmap="RdYlGn_r"),
                    use_container_width=True
                )

                # Inline bar chart
                if len(results_list) > 1:
                    fig_run = px.bar(
                        res_df, x="operation", y="execution_time_sec",
                        color="system_name", barmode="group",
                        color_discrete_map=SYSTEM_COLORS,
                        template=PLOTLY_TEMPLATE,
                        title="Benchmark Run — Execution Time",
                        labels={"execution_time_sec": "Seconds"}
                    )
                    fig_run.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=380
                    )
                    st.plotly_chart(fig_run, theme=None, use_container_width=True)

                st.info("Click **Refresh** in the sidebar to see updated charts in all other tabs.")
                st.cache_data.clear()

    else:
        # Prompt when no file is uploaded yet
        st.markdown("""
        <div style="text-align:center; padding:40px 20px;">
          
          <p style="color:#64748b; font-size:15px; margin-top:12px;">
            Drag a <strong>CSV</strong> or <strong>JSON</strong> dataset above to get started.<br>
                        Any schema is accepted; benchmarks use a generic format when needed.
          </p>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#4b5563;font-size:12px;">'
    'PolyStoreBench &mdash; Unified Big Data Benchmarking Framework &mdash; '
    f'Last refresh: {datetime.now().strftime("%H:%M:%S")}'
    '</div>',
    unsafe_allow_html=True
)