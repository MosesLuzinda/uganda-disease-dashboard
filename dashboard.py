import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json
import base64
import os
from io import StringIO
from PIL import Image

# ============================================================
# Page config
# ============================================================

icon = Image.open("logo2.png")

st.set_page_config(
    page_title="Uganda Epidemic Risk & Response Dashboard",
    page_icon=icon,
    layout="wide",
)

# ============================================================
# Background image helper (optional)
# ============================================================

def set_background(image_path: str):
    if not os.path.exists(image_path):
        return

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image:
            linear-gradient(
                to bottom right,
                rgba(0, 0, 0, 0.80),
                rgba(0, 0, 0, 0.85)
            ),
            url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_background("uganda-epidemic-bg.png")

# ============================================================
# Global styles – text, cards, sidebar
# ============================================================

st.markdown(
    """
    <style>
    /* Main text – default black */
    .main {
        color: #000000;
    }
    h1, h2, h3, h4, h5 {
        color: #000000;
        letter-spacing: 0.03em;
    }
    p, li, label {
        color: #000000;
        font-size: 0.98rem;
    }

    /* Sidebar styling (grey) */
    section[data-testid="stSidebar"] {
        background: #e5e5e5;
        border-right: 1px solid #b0b0b0;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #333333;
    }
    .sidebar-header {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #555555;
        margin-top: 0.75rem;
        margin-bottom: 0.25rem;
    }

    /* Make logo area slightly darker grey with padding */
    section[data-testid="stSidebar"] img {
        background-color: #d4d4d4;
        padding: 8px;
        border-radius: 6px;
    }

    /* Top title in blue, subtitle in black */
    .title-text {
        color: #38bdf8;
        font-weight: 800;
        font-size: 2.3rem;
    }
    .subtitle-text {
        color: #000000;
        font-size: 1rem;
    }

    /* How to use styling in black */
    .howto-header {
        color: #000000;
        font-weight: 700;
    }
    .howto-text {
        color: #000000;
        font-size: 0.95rem;
    }

    /* Pill/tag */
    .pill {
        display:inline-block;
        padding: 0.2rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #000000, #facc15, #b91c1c);
        color: #fefce8;
        border: 1px solid #facc15;
    }

    /* Base metric card */
    .metric-card {
        padding: 1rem 1.1rem;
        border-radius: 0.9rem;
        text-align: left;
        box-shadow: 0 8px 20px rgba(0,0,0,0.25);
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out, border-color 0.15s ease-out;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 14px 32px rgba(0,0,0,0.4);
    }
    .metric-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.15rem;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
    }
    .metric-caption {
        font-size: 0.85rem;
    }

    /* Individual colors for each KPI card */
    .metric-card-total {
        background: linear-gradient(135deg, #fee2e2, #fecaca);
        border: 1px solid #ef4444;
    }
    .metric-card-total .metric-title {
        color: #7f1d1d;
    }
    .metric-card-total .metric-value {
        color: #111827;
    }
    .metric-card-total .metric-caption {
        color: #374151;
    }

    .metric-card-diseases {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        border: 1px solid #3b82f6;
    }
    .metric-card-diseases .metric-title {
        color: #1d4ed8;
    }
    .metric-card-diseases .metric-value {
        color: #0f172a;
    }
    .metric-card-diseases .metric-caption {
        color: #1f2937;
    }

    .metric-card-districts {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        border: 1px solid #22c55e;
    }
    .metric-card-districts .metric-title {
        color: #166534;
    }
    .metric-card-districts .metric-value {
        color: #052e16;
    }
    .metric-card-districts .metric-caption {
        color: #14532d;
    }

    /* Section card */
    .section-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 1rem;
        border: 1px solid #e5e7eb;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
        color: #000000;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.45rem 1rem;
        border-radius: 999px;
        font-size: 0.95rem;
        color: #000000;
        background: #f3f4f6;
        border: 1px solid #d4d4d8;
        transition: background 0.15s ease-out, box-shadow 0.15s ease-out, transform 0.15s ease-out;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #e5e7eb;
        color: #000000;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #facc15, #b91c1c);
        color: #000000;
        border-color: #facc15;
        font-weight: 700;
    }

    /* Buttons */
    button[kind="primary"] {
        border-radius: 999px !important;
        background: linear-gradient(135deg, #facc15, #b91c1c) !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 12px 26px rgba(0,0,0,0.25) !important;
        transition: transform 0.14s ease-out, box-shadow 0.14s ease-out, filter 0.14s ease-out !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 16px 35px rgba(0,0,0,0.35) !important;
        filter: brightness(1.04);
    }

    /* Dataframe row hover */
    .stDataFrame table tbody tr:hover {
        background-color: rgba(0,0,0,0.04) !important;
    }

    @media (max-width: 768px) {
        .main { padding: 0.7rem; }
        .section-card { padding: 0.9rem 1rem; }
        .metric-card { margin-bottom: 0.6rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Helper functions
# ============================================================

@st.cache_data
def load_data(path_or_file) -> pd.DataFrame:
    df = pd.read_excel(path_or_file)
    df["date_incident"] = pd.to_datetime(df["date_incident"])
    df["year"] = df["date_incident"].dt.year
    df["month"] = df["date_incident"].dt.to_period("M").dt.to_timestamp()
    df["district"] = df["district"].astype(str).str.strip().str.upper()
    df["disease"] = df["disease"].astype(str).str.strip()
    return df


@st.cache_data
def load_uganda_shapefile() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(
        "shapefiles/Uganda_Districts-2020---136-wgs84/Uganda_Districts-2020---136-wgs84.shp"
    )
    gdf["DISTRICT_NAME"] = gdf["dname2019"].astype(str).str.strip().str.upper()
    return gdf


def filter_data(df: pd.DataFrame, years, diseases, districts) -> pd.DataFrame:
    data = df.copy()
    if years:
        data = data[data["year"].isin(years)]
    if diseases:
        data = data[data["disease"].isin(diseases)]
    if districts:
        data = data[data["district"].isin(districts)]
    return data


def make_pie_by_disease(df: pd.DataFrame):
    counts = df.groupby("disease").size().reset_index(name="count")
    if counts.empty:
        return None
    fig = px.pie(
        counts,
        values="count",
        names="disease",
        title="Incidents by disease (share of total)",
        color_discrete_sequence=[
            "#facc15", "#b91c1c", "#fec89a", "#fee440",
            "#fb7185", "#f97316", "#fde047", "#fca5a5"
        ],
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        pull=[0.03] * len(counts),
    )
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        legend=dict(orientation="h", y=-0.25),
        height=460,
        font=dict(color="#000000", size=14),
    )
    return fig


def make_bar_by_year(df: pd.DataFrame):
    counts = df.groupby("year").size().reset_index(name="count")
    if counts.empty:
        return None
    fig = px.bar(
        counts,
        x="year",
        y="count",
        title="Incidents per year",
        color="count",
        color_continuous_scale=["#fee2e2", "#fca5a5", "#b91c1c"],
        hover_data={"count": ":,"},
    )
    fig.update_traces(
        marker_line_color="#000000",
        marker_line_width=0.5,
    )
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        height=460,
        font=dict(color="#000000", size=14),
    )
    return fig


def make_time_series_monthly(df: pd.DataFrame):
    counts = df.groupby("month").size().reset_index(name="count")
    if counts.empty:
        return None
    fig = px.line(
        counts,
        x="month",
        y="count",
        title="Time series of incidents (monthly)",
        markers=True,
        color_discrete_sequence=["#facc15"],
    )
    fig.update_traces(
        hovertemplate="<b>%{x|%b %Y}</b><br>Incidents: %{y:,}<extra></extra>",
        marker=dict(size=8, line=dict(width=1, color="#000000")),
    )
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        hovermode="x unified",
        height=460,
        font=dict(color="#000000", size=14),
    )
    return fig


def make_line_by_year_disease(df: pd.DataFrame):
    counts = (
        df.groupby(["year", "disease"])
        .size()
        .reset_index(name="count")
    )
    if counts.empty:
        return None
    fig = px.line(
        counts,
        x="year",
        y="count",
        color="disease",
        title="Incidents per year by disease",
        markers=True,
        color_discrete_sequence=[
            "#fde047", "#fbbf24", "#f59e0b", "#ef4444",
            "#22c55e", "#86efac", "#fef3c7", "#fef08a",
        ],
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{legendgroup}: %{y:,}<extra></extra>",
        marker=dict(size=8),
    )
    fig.update_layout(
        title_x=0.5,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        legend=dict(orientation="h", y=-0.25),
        height=460,
        font=dict(color="#000000", size=14),
    )
    return fig


def make_uganda_risk_map(df: pd.DataFrame, gdf_uga: gpd.GeoDataFrame):
    risk_df = (
        df.groupby("district")
        .size()
        .reset_index(name="risk_score")
    )
    if risk_df.empty:
        return None
    risk_df["district"] = risk_df["district"].astype(str).str.strip().str.upper()
    merged = gdf_uga.merge(
        risk_df,
        left_on="DISTRICT_NAME",
        right_on="district",
        how="left",
    )
    merged["risk_score"] = merged["risk_score"].fillna(0)
    geojson = json.loads(merged.to_json())
    fig = px.choropleth(
        merged,
        geojson=geojson,
        locations=merged.index,
        color="risk_score",
        projection="mercator",
        hover_name="DISTRICT_NAME",
        hover_data={"risk_score": True},
        color_continuous_scale=["#fee2e2", "#fecaca", "#fca5a5", "#f87171", "#ef4444"],
        title="Disease risk map – Uganda (district hotspots)",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Incidents: %{customdata[0]:,}<extra></extra>"
    )
    fig.update_layout(
        title_x=0.5,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        height=520,
        font=dict(color="#000000", size=14),
    )
    return fig


# simple population mapping (replace with real values later)
DISTRICT_POP = {
    # "KAMPALA": 1600000,
    # "WAKISO": 2500000,
    # ...
}

def national_incidence_per_100k(df: pd.DataFrame) -> float | None:
    if df.empty:
        return None
    if not DISTRICT_POP:
        return None
    merged = df.groupby("district").size().reset_index(name="cases")
    merged["district"] = merged["district"].astype(str).str.strip().str.upper()
    merged["pop"] = merged["district"].map(DISTRICT_POP)
    merged = merged.dropna(subset=["pop"])
    if merged.empty:
        return None
    total_cases = merged["cases"].sum()
    total_pop = merged["pop"].sum()
    rate = (total_cases / total_pop) * 100000
    return rate

# ============================================================
# Header & About
# ============================================================

st.markdown(
    "<h1 class='title-text'>Uganda Epidemic Risk & Response Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='subtitle-text'>Visual analytics of historical outbreaks and current "
    "risk patterns by disease, year, and district in Uganda.</p>",
    unsafe_allow_html=True,
)

st.markdown(
    "<span class='pill'>UGANDA • EPIDEMIC INTELLIGENCE</span>",
    unsafe_allow_html=True,
)

with st.expander("How to use this dashboard"):
    st.markdown(
        """
        <p class="howto-header">Quick guide</p>
        <ul class="howto-text">
            <li>See which <b>diseases</b> drive most reported outbreaks.</li>
            <li>Track how <b>incidents change over time</b>.</li>
            <li>Identify <b>district hotspots</b> to focus response.</li>
            <li>Adjust filters (year, disease, district) to explore specific scenarios.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============================================================
# Sidebar: logo, data, filters, data-entry button
# ============================================================

with st.sidebar:
    st.image("STI-logo/logo1.png", use_container_width=True)

st.sidebar.markdown("## Dashboard controls")

with st.sidebar.expander("📂 Data source", expanded=True):
    uploaded_file = st.file_uploader(
        "Upload disease incidents Excel (.xlsx)",
        type=["xlsx"],
    )
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.success("Using uploaded Excel file.")
    else:
        st.info("Using local file: diseases_incidents.xlsx")
        df = load_data("diseases_incidents.xlsx")

with st.sidebar.expander("🎛️ Filters", expanded=True):
    years = sorted(df["year"].dropna().unique())
    diseases = sorted(df["disease"].dropna().unique())
    districts = sorted(df["district"].dropna().unique())

    st.sidebar.markdown('<div class="sidebar-header">Time</div>', unsafe_allow_html=True)
    year_sel = st.multiselect("Year(s)", years)

    st.sidebar.markdown('<div class="sidebar-header">Disease</div>', unsafe_allow_html=True)
    disease_sel = st.multiselect("Disease(s)", diseases)

    st.sidebar.markdown('<div class="sidebar-header">Geography</div>', unsafe_allow_html=True)
    district_sel = st.multiselect("District(s)", districts)

with st.sidebar.expander("✏️ Data entry mode", expanded=False):
    data_entry_mode = st.checkbox(
        "Open data entry & editing panel",
        value=False,
        help="Turn this on to add or edit incident records."
    )

# ============================================================
# Data entry – allow user to add/edit incidents (toggled)
# ============================================================

if data_entry_mode:
    st.markdown("## Data entry – add or edit incidents")

    st.markdown(
        "Use this table to capture additional incident records (e.g. recent outbreaks "
        "not yet in the Excel file). These rows will be included in all analyses in this session."
    )

    edit_cols = [c for c in ["date_incident", "disease", "district", "cases", "deaths"] if c in df.columns]
    base_for_edit = df[edit_cols].copy()

    edited_df = st.data_editor(
        base_for_edit,
        num_rows="dynamic",
        use_container_width=True,
        key="incident_editor",
    )

    df_updated = df.copy()
    df_updated[edit_cols] = edited_df[edit_cols]
else:
    df_updated = df

# Apply filters on whichever dataframe is active
filtered = filter_data(df_updated, year_sel, disease_sel, district_sel)

# ============================================================
# Compact analysis controls strip
# ============================================================

st.markdown("## Analysis controls")

ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1, 1, 1, 1])

with ctrl1:
    st.markdown("**Years in view**")
    years_in_view = sorted(filtered["year"].dropna().unique())
    if years_in_view:
        st.markdown(f"{years_in_view[0]} – {years_in_view[-1]}")
    else:
        st.markdown("_No data_")

with ctrl2:
    st.markdown("**Top disease**")
    if not filtered.empty:
        top_dis = (
            filtered.groupby("disease")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(1)
        )
        st.markdown(f"{top_dis.iloc[0]['disease']} ({int(top_dis.iloc[0]['count'])})")
    else:
        st.markdown("_No data_")

with ctrl3:
    st.markdown("**Incidence (per 100k)**")
    rate = national_incidence_per_100k(filtered)
    if rate is not None:
        st.markdown(f"{rate:.1f}")
    else:
        st.markdown("_Needs population data_")

with ctrl4:
    st.markdown("**Export**")
    csv_buffer = StringIO()
    filtered.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name="filtered_incidents.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ============================================================
# KPI cards with detailed expanders
# ============================================================

st.markdown("## Situation at a glance")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

# Total incidents
with col_kpi1:
    total_incidents = len(filtered)
    st.markdown(
        f"""
        <div class="metric-card metric-card-total">
          <div class="metric-title">Total incidents</div>
          <div class="metric-value">{total_incidents:,}</div>
          <div class="metric-caption">All reported outbreaks under the current filters.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("View incident details"):
        st.markdown(
            """
            This section provides a **clinical and epidemiological overview** of the incidents currently in view.  
            Each row in the dataset typically represents one reported outbreak event or cluster.
            """
        )
        if not filtered.empty:
            st.markdown("**Most recent incidents**")
            recent_cols = [c for c in filtered.columns if c in ["date_incident", "disease", "district", "cases", "deaths"]]
            if recent_cols:
                st.dataframe(
                    filtered.sort_values("date_incident", ascending=False)[recent_cols].head(20),
                    use_container_width=True,
                )

            st.markdown("**How to interpret an incident**")
            st.markdown(
                """
                - **Incident date**: When the event was detected or reported.  
                - **Disease**: Suspected or confirmed pathogen.  
                - **District**: Geographic location of the primary focus.  
                - **Cases / deaths** (if available): Magnitude and severity of the event.  
                - **Filters**: The total incidents displayed change when you filter by year, disease or district.
                """
            )
        else:
            st.info("No incidents under the current filters.")

# Unique diseases
with col_kpi2:
    n_diseases = filtered["disease"].nunique()
    st.markdown(
        f"""
        <div class="metric-card metric-card-diseases">
          <div class="metric-title">Unique diseases</div>
          <div class="metric-value">{n_diseases}</div>
          <div class="metric-caption">Different pathogens represented.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("View disease intelligence"):
        st.markdown(
            """
            This section summarises **key diseases** in the current view and provides a short briefing that a clinician or policymaker can use for rapid orientation.
            """
        )
        if n_diseases > 0:
            top_diseases = (
                filtered.groupby("disease")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )
            st.dataframe(top_diseases, use_container_width=True)

            disease_choice = st.selectbox(
                "Select a disease to view a brief profile",
                options=top_diseases["disease"].tolist(),
            )

            if disease_choice:
                st.markdown(f"### Disease profile: {disease_choice}")
                st.markdown(
                    """
                    *This briefing is intended as a high-level support tool and does not replace official clinical guidelines.*
                    """
                )
                st.markdown(
                    """
                    - **Transmission & spread**: Consider routes such as person-to-person, water/food-borne, vector-borne, or zoonotic exposure.  
                    - **Clinical picture**: Typical syndrome may include fever, malaise, gastrointestinal symptoms, respiratory involvement, or haemorrhagic manifestations depending on the pathogen.  
                    - **Case management**: Focus on early recognition, prompt referral, supportive care and disease-specific therapies where available.  
                    - **Prevention & control**: Vaccination (if available), infection prevention and control, WASH, vector control, and risk communication.  
                    - **Surveillance history**: Patterns in this dashboard can indicate whether the disease is emerging, re-emerging, or seasonal by district.
                    """
                )
        else:
            st.info("No diseases under the current filters.")

# Districts affected
with col_kpi3:
    n_districts = filtered["district"].nunique()
    st.markdown(
        f"""
        <div class="metric-card metric-card-districts">
          <div class="metric-title">Districts affected</div>
          <div class="metric-value">{n_districts}</div>
          <div class="metric-caption">Geographical spread of the outbreaks.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("View geographic insight"):
        st.markdown(
            """
            Understanding **where** incidents occur is critical for targeting resources, logistics and risk communication.
            """
        )
        if n_districts > 0:
            district_counts = (
                filtered.groupby("district")
                .size()
                .reset_index(name="incidents")
                .sort_values("incidents", ascending=False)
            )
            st.dataframe(district_counts, use_container_width=True)

            district_choice = st.selectbox(
                "Select a district for a situational snapshot",
                options=district_counts["district"].tolist(),
            )
            if district_choice:
                df_d = filtered[filtered["district"] == district_choice]
                st.markdown(f"### District snapshot: {district_choice.title()}")
                st.markdown(
                    f"""
                    - **Total incidents in view**: **{len(df_d)}**  
                    - **Number of diseases**: **{df_d['disease'].nunique()}**  
                    - **Signal**: Recurrent incidents may reflect structural vulnerabilities (WASH, housing, vector ecology, health service access).  
                    - **Use case**: This view can inform district health teams and national emergency operations for prioritisation.
                    """
                )
        else:
            st.info("No districts under the current filters.")

st.markdown("")

# ============================================================
# Forward-looking and prediction section
# ============================================================

st.markdown("## Forward risk, predictions and future scenarios")

with st.expander("View prediction concepts and examples"):
    st.markdown(
        """
        This dashboard can support **anticipatory action** by linking incident trends with context such as climate, seasonality and population movement.

        ### Example model families actually used in practice

        - **Time series regression with weather**: Models that relate weekly or monthly cases to rainfall and temperature are widely used for climate‑sensitive infections such as malaria, cholera and influenza.  
        - **Distributed lag models**: These allow rainfall or temperature in previous weeks or months to influence current incidence, capturing realistic delays between climate shocks and outbreaks.  
        - **ARIMA / SARIMA**: Autoregressive integrated moving average models, sometimes with seasonal terms, are standard baselines for short‑term infectious disease forecasting and outbreak detection.  
        - **Hybrid and machine‑learning models**: Combinations of time‑series decomposition with regression or tree‑based / neural models have been explored for tuberculosis and vector‑borne diseases to improve forecast accuracy.

        ### How this dashboard would link to those models

        - Use the **time series by disease and district** as the outcome variable.  
        - Add climate inputs (rainfall, minimum temperature, humidity), population data, and intervention coverage as predictors.  
        - Train models to forecast 3–12 months ahead for priority districts.  
        - Surface the model outputs here as forward‑looking curves or risk bands, clearly labelled as **scenarios**, not certainties.
        """
    )

# ============================================================
# Tabs: Overview / Trends / Map
# ============================================================

tab_overview, tab_trends, tab_map = st.tabs(
    ["Overview – burden", "Trends over time", "Spatial risk & profiles"]
)

# Overview tab
with tab_overview:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        "### Burden distribution\n"
        "Distribution of incidents by disease and year under current filters.",
    )
    col1, col2 = st.columns([1.1, 1])

    with col1:
        fig_pie = make_pie_by_disease(filtered)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No data for the selected filters.")

    with col2:
        fig_bar = make_bar_by_year(filtered)
        if fig_bar:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No yearly data for the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)

# Trends tab
with tab_trends:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(
        "### Temporal dynamics\n"
        "How incident counts change over months and years.",
    )
    col3, col4 = st.columns(2)

    with col3:
        fig_ts = make_time_series_monthly(filtered)
        if fig_ts:
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No monthly time-series data for the selected filters.")

    with col4:
        fig_line = make_line_by_year_disease(filtered)
        if fig_line:
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No per-disease yearly data for the selected filters.")

    st.markdown("</div>", unsafe_allow_html=True)

# Map tab
with tab_map:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### Spatial risk & profiles")
    gdf_uga = load_uganda_shapefile()
    fig_map = make_uganda_risk_map(filtered, gdf_uga)
    col_map, col_details = st.columns([2, 1])

    with col_map:
        if fig_map:
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No incidents in the current filter, so the map is empty.")

    with col_details:
        st.markdown("#### District details")
        available_districts = sorted(filtered["district"].unique())
        selected_district = st.selectbox(
            "Select district",
            options=["-- choose district --"] + available_districts,
            index=0,
        )
        if selected_district and selected_district != "-- choose district --":
            df_d = filtered[filtered["district"] == selected_district]
            st.markdown(f"**Selected district:** {selected_district.title()}")
            st.markdown(
                f"- Total incidents in view: **{len(df_d)}**\n"
                f"- Number of diseases: **{df_d['disease'].nunique()}**"
            )
            top_d = (
                df_d.groupby("disease")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
                .head(5)
            )
            st.markdown("**Top diseases in this district:**")
            st.dataframe(top_d, use_container_width=True)
            counts_year = df_d.groupby("year").size().reset_index(name="count")
            if not counts_year.empty:
                fig_d = px.line(
                    counts_year,
                    x="year",
                    y="count",
                    markers=True,
                    title="Incidents over time (district)",
                    color_discrete_sequence=["#fde047"],
                )
                fig_d.update_traces(
                    hovertemplate="<b>%{x}</b><br>Incidents: %{y:,}<extra></extra>",
                    marker=dict(size=8, line=dict(width=1, color="#000000")),
                )
                fig_d.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#ffffff",
                    title_x=0.5,
                    height=360,
                    font=dict(color="#000000", size=14),
                )
                st.plotly_chart(fig_d, use_container_width=True)
            else:
                st.info("No time-series data for this district.")
    st.markdown("</div>", unsafe_allow_html=True)