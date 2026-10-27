
import duckdb
import streamlit as st

from src.common.config import DB_PATH


st.set_page_config(
    page_title="Cambodia Economic Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Cambodia Economic Development")
st.caption("Historical economic indicators · 2000–2024")

if not DB_PATH.exists():
    st.error("Database not found. Run `python -m src.pipeline` first.")
    st.stop()


with duckdb.connect(str(DB_PATH), read_only=True) as connection:
 
    history = connection.execute("""
        SELECT year, indicator_code, indicator_name, value, unit
        FROM economic_observations
        ORDER BY year
    """).df()

    latest = connection.execute("""
        SELECT indicator_code, value, unit, year
        FROM economic_observations AS e
        WHERE year = (
            SELECT MAX(e2.year)
            FROM economic_observations AS e2
            WHERE e2.indicator_code = e.indicator_code
        )
    """).df()


metrics = {
    row["indicator_code"]: row
    for _, row in latest.iterrows()
}

gdp = metrics.get("NY.GDP.MKTP.KD.ZG")
inflation = metrics.get("FP.CPI.TOTL.ZG")
gdp_per_capita = metrics.get("NY.GDP.PCAP.CD")
population = metrics.get("SP.POP.TOTL")

col1, col2, col3, col4 = st.columns(4)

if gdp is not None:
    col1.metric(
        "GDP Growth",
        f'{gdp["value"]:.2f}%',
        help=f'Latest available year: {int(gdp["year"])}',
    )

if inflation is not None:
    col2.metric(
        "Inflation",
        f'{inflation["value"]:.2f}%',
        help=f'Latest available year: {int(inflation["year"])}',
    )

if gdp_per_capita is not None:
    col3.metric(
        "GDP per Capita",
        f'${gdp_per_capita["value"]:,.0f}',
        help=f'Latest available year: {int(gdp_per_capita["year"])}',
    )

if population is not None:
    col4.metric(
        "Population",
        f'{population["value"] / 1_000_000:.2f}M',
        help=f'Latest available year: {int(population["year"])}',
    )


st.subheader("Historical Economic Trends")

indicator_options = {
    "GDP Growth": "NY.GDP.MKTP.KD.ZG",
    "Inflation": "FP.CPI.TOTL.ZG",
    "GDP per Capita": "NY.GDP.PCAP.CD",
    "Population": "SP.POP.TOTL",
}

selected_label = st.selectbox(
    "Choose an economic indicator",
    list(indicator_options.keys()),
)

selected_code = indicator_options[selected_label]

chart_data = history[
    history["indicator_code"] == selected_code
].sort_values("year")

year_min = int(chart_data["year"].min())
year_max = int(chart_data["year"].max())

selected_years = st.slider(
    "Select year range",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

chart_data = chart_data[
    chart_data["year"].between(
        selected_years[0],
        selected_years[1],
    )
]

st.subheader("Data Quality Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Observations", len(chart_data))

col2.metric(
    "First Year",
    int(chart_data["year"].min()) if not chart_data.empty else "N/A",
)

col3.metric(
    "Last Year",
    int(chart_data["year"].max()) if not chart_data.empty else "N/A",
)

expected_years = (
    selected_years[1] - selected_years[0] + 1
)

actual_years = chart_data["year"].nunique()

if actual_years < expected_years:
    st.warning(
        f"Missing data: expected {expected_years} years, "
        f"but found {actual_years}."
    )
else:
    st.success("Data completeness check passed.")

if not chart_data.empty:
    st.caption(f"Unit: {chart_data['unit'].iloc[0]}")

    st.line_chart(
        chart_data.set_index("year")["value"],
        x_label="Year",
        y_label=chart_data["unit"].iloc[0],
    )
    st.subheader("Historical Data")

    table_data = chart_data[
        ["year", "indicator_name", "value", "unit"]
    ].copy()

    table_data = table_data.rename(
        columns={
            "year": "Year",
            "indicator_name": "Indicator",
            "value": "Value",
            "unit": "Unit",
        }
    )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
    )
    
    csv_data = table_data.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download data as CSV",
        data=csv_data,
        file_name=f"{selected_label.lower().replace(' ', '_')}_data.csv",
        mime="text/csv",
    )
else:
    st.warning("No observations found for this indicator.")
