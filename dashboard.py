import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json

# -----------------------------#
# Page config & global styles  #
# -----------------------------#

st.set_page_config(
    page_title="Uganda Epidemic Risk & Response Dashboard",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fb;
    }
    .title-text {
        color: #1f4e79;
        font-weight: 700;
    }
    .subtitle-text {
        color: #4c4c4c;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------#
# Helper functions             #
# -----------------------------#


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
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
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_layout(title_x=0.5)
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
        color_continuous_scale="Blues",
    )
    fig.update_layout(title_x=0.5)
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
    )
    fig.update_layout(title_x=0.5)
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
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig.update_layout(title_x=0.5)
    return fig


def make_uganda_risk_map(df: pd.DataFrame, gdf_uga: gpd.GeoDataFrame):
    # Aggregate incidents by district
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
        color_continuous_scale="Reds",
        title="Disease risk map – Uganda (district hotspots)",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title_x=0.5,
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    return fig


# -----------------------------#
# Layout: header               #
# -----------------------------#

st.markdown(
    "<h1 class='title-text'>Uganda Epidemic Risk & Response Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='subtitle-text'>This dashboard summarizes historical outbreaks and "
    "current risk patterns by disease, year, and district in Uganda. "
    "Use it to prioritize surveillance, vaccination, and response resources.</p>",
    unsafe_allow_html=True,
)

with st.expander("How to read this dashboard"):
    st.markdown(
        """
        - See which **diseases** drive most reported outbreaks.
        - Track how **incidents change over time**.
        - Identify **district hotspots** for targeted interventions.
        - Adjust filters (year, disease, district) to explore specific scenarios.
        """
    )

st.markdown("---")

# -----------------------------#
# Data input & sidebar         #
# -----------------------------#

st.sidebar.header("Dashboard controls")

with st.sidebar.expander("Data source", expanded=True):
    uploaded_file = st.file_uploader(
        "Upload disease incidents Excel (.xlsx)",
        type=["xlsx"],
    )
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        st.info("Using local file: diseases_incidents.xlsx")
        df = load_data("diseases_incidents.xlsx")

with st.sidebar.expander("Filters", expanded=True):
    years = sorted(df["year"].dropna().unique())
    diseases = sorted(df["disease"].dropna().unique())
    districts = sorted(df["district"].dropna().unique())

    year_sel = st.multiselect("Year(s)", years)
    disease_sel = st.multiselect("Disease(s)", diseases)
    district_sel = st.multiselect("District(s)", districts)

filtered = filter_data(df, year_sel, disease_sel, district_sel)

# -----------------------------#
# KPI cards                    #
# -----------------------------#

st.markdown("### Situation at a glance")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown(
        f"<div class='metric-card'><h4>Total incidents</h4>"
        f"<h2 style='color:#1f4e79;'>{len(filtered):,}</h2>"
        f"<p style='font-size:0.85rem;color:#777;'>All reported outbreaks under the current filters.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

with col_kpi2:
    st.markdown(
        f"<div class='metric-card'><h4>Unique diseases</h4>"
        f"<h2 style='color:#d62828;'>{filtered['disease'].nunique()}</h2>"
        f"<p style='font-size:0.85rem;color:#777;'>Number of distinct pathogens in view.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

with col_kpi3:
    st.markdown(
        f"<div class='metric-card'><h4>Districts affected</h4>"
        f"<h2 style='color:#2a9d8f;'>{filtered['district'].nunique()}</h2>"
        f"<p style='font-size:0.85rem;color:#777;'>Geographical spread under current filters.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("")

# -----------------------------#
# Tabs: Overview / Trends / Map#
# -----------------------------#

tab_overview, tab_trends, tab_map = st.tabs(
    ["Overview – burden", "Trends over time", "Spatial risk & profiles"]
)

with tab_overview:
    st.markdown(
        "###### Distribution of incidents by disease and year under current filters."
    )
    col1, col2 = st.columns(2)
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

with tab_trends:
    st.markdown("###### How incident counts evolve over months and years.")
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

with tab_map:
    st.markdown("###### District-level hotspots and detailed profiles.")

    gdf_uga = load_uganda_shapefile()
    fig_map = make_uganda_risk_map(filtered, gdf_uga)

    col_map, col_details = st.columns([2, 1])

    with col_map:
        if fig_map:
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No incidents in the current filter, so the map is empty.")

    with col_details:
        st.markdown("##### District details")

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
            st.dataframe(top_d)

            counts_year = (
                df_d.groupby("year").size().reset_index(name="count")
            )
            if not counts_year.empty:
                fig_d = px.line(
                    counts_year,
                    x="year",
                    y="count",
                    markers=True,
                    title="Incidents over time (district)",
                )
                st.plotly_chart(fig_d, use_container_width=True)
            else:
                st.info("No time-series data for this district.")