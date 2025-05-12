# app.py
import sqlite3
import pandas as pd
import streamlit as st
import altair as alt

DB_FILE = "data.db"

# Set the page configuration for the Streamlit app
st.set_page_config(page_title="台灣各區一週氣溫預報", page_icon=":partly_sunny:")

# ---------- Data Layer ----------
@st.cache_resource
# Establish a connection to the SQLite database
# The connection is cached to improve performance

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

@st.cache_data
# Fetch the list of distinct regions from the database
# The result is cached to avoid redundant queries

def get_regions(_conn):
    return pd.read_sql_query(
        "SELECT DISTINCT regionName FROM TemperatureForecasts", _conn
    )["regionName"].tolist()

@st.cache_data
# Load temperature data for a specific region from the database
# The result is cached to improve performance

def load_region_df(_conn, region):
    df = pd.read_sql_query("""
        SELECT dataDate, mint, maxt FROM TemperatureForecasts
        WHERE regionName = ? ORDER BY datetime(dataDate)
    """, _conn, params=(region,))
    df["dataDate"] = pd.to_datetime(df["dataDate"])
    return df

# ---------- UI Layer ----------
# Initialize database connection
conn = get_conn()
# Get the list of regions
regions = get_regions(conn)
if not regions:
    # Display an error message if no data is available in the database
    st.error("資料庫目前沒有資料，請先執行：python weather_data.py fetch")
    st.stop()

# Dropdown menu for selecting a region
region = st.selectbox("選擇地區", regions)
# Load temperature data for the selected region
df = load_region_df(conn, region)

# Display a subtitle for the selected region
st.subheader(f"{region} 未來一週最高 / 最低氣溫（℃）")

# Convert data to long format for plotting multiple lines with a legend
df_long = df.melt(
    id_vars=["dataDate"],
    value_vars=["maxt", "mint"],
    var_name="type",
    value_name="temperature"
)

# Map 'type' column values to more user-friendly labels
df_long["type"] = df_long["type"].map({"maxt": "最高溫", "mint": "最低溫"})

# Define color mapping and legend title
color_scale = alt.Scale(
    domain=["最高溫", "最低溫"],
    range=["#d62728", "#1f77b4"]
)

# Calculate the minimum and maximum temperatures in the data
min_temp = df_long["temperature"].min()
max_temp = df_long["temperature"].max()

# Create a line chart with a legend
chart = alt.Chart(df_long).mark_line(strokeWidth=2).encode(
    x=alt.X("dataDate:T", title="日期"),
    y=alt.Y("temperature:Q", title="溫度", scale=alt.Scale(domain=[min_temp - 3, max_temp + 3])),
    color=alt.Color("type:N", title="溫度類型", scale=color_scale)
).properties(
    width=600,
    height=400
)

# Display the chart in the Streamlit app
st.altair_chart(chart, use_container_width=True)

# Display the data table
st.write("表格資料")

# Function to style temperature values based on their magnitude
def style_temperature(val):
    if isinstance(val, (int, float)):
        # Define the absolute temperature range (e.g., 0°C to 40°C)
        min_temp, max_temp = 0, 40
        red = int(255 * (val - min_temp) / (max_temp - min_temp))
        blue = int(255 * (1 - (val - min_temp) / (max_temp - min_temp)))
        color = f"rgb({red}, 0, {blue})"

        # Adjust text color based on brightness (black or white)
        brightness = (red * 299 + 0 * 587 + blue * 114) / 1000
        text_color = "black" if brightness > 125 else "white"

        return f"background-color: {color}; color: {text_color}"
    return ""

# Apply styling to the temperature table
def highlight_temperatures(df):
    return df.style.applymap(style_temperature, subset=["最高溫", "最低溫"])

# Format the date column to display only the date
formatted_df = df.rename(columns={"dataDate": "日期", "mint": "最低溫", "maxt": "最高溫"})
formatted_df["日期"] = formatted_df["日期"].dt.date

# Round temperature values to integers
formatted_df["最低溫"] = formatted_df["最低溫"].round(0).astype(int)
formatted_df["最高溫"] = formatted_df["最高溫"].round(0).astype(int)

# Display the styled DataFrame in the Streamlit app
st.dataframe(
    highlight_temperatures(formatted_df),
    hide_index=True,
)

# Display the latest data date as a caption
st.caption(f"最新的資料日期：{df['dataDate'].max():%Y-%m-%d}")
