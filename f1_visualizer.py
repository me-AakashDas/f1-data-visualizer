# f1_visualizer.py
# F1 Data Visualizer with Streamlit Dashboard
# Displays all plots in browser

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="F1 Data Visualizer",
    page_icon="🏎️",
    layout="wide"
)

# -------------------------------
# App Title & Description
# -------------------------------
st.title("🏎️ F1 Data Visualizer (2015–2024)")
st.markdown("""
This dashboard shows **Formula 1 race data** from 2015 to 2024.  
Even if you don’t know F1, you can see who the top drivers and teams are — using data and visualizations.

All data is loaded from a CSV file — no internet required!
""")

# -------------------------------
# Load Data
# -------------------------------
CSV_FILE = "f1_data_2015_2024.csv"

if not os.path.exists(CSV_FILE):
    st.error(f"❌ File '{CSV_FILE}' not found!")
    st.markdown("💡 Please make sure you've saved the CSV file in the same folder as this script.")
    st.stop()

try:
    df = pd.read_csv(CSV_FILE)
    df['position'] = pd.to_numeric(df['position'], errors='coerce')
    st.success(f"✅ Loaded {len(df)} race results from {df['year'].min()} to {df['year'].max()}")
except Exception as e:
    st.error(f"❌ Error loading  {e}")
    st.stop()

# Show sample data
with st.expander("📊 View Sample Data"):
    st.dataframe(df.head(10))

# -------------------------------
# Prepare Data for Visualizations
# -------------------------------

# Top 6 drivers by total points
top_drivers = df.groupby('driver')['points'].sum().nlargest(6).index
driver_trend = df[df['driver'].isin(top_drivers)].groupby(['driver', 'year'])['points'].sum().reset_index()

# Constructor trends
cons_trend = df.groupby(['constructor', 'year'])['points'].sum().reset_index()
top_constructors = cons_trend.groupby('constructor')['points'].sum().nlargest(6).index
cons_trend = cons_trend[cons_trend['constructor'].isin(top_constructors)]

# Podium heatmap
podium = df[df['position'].isin([1, 2, 3])]
podium_count = podium.pivot_table(
    index='driver',
    columns='position',
    aggfunc='size',
    fill_value=0
).astype(int)
podium_count.columns = ['1st', '2nd', '3rd']
podium_count['Total'] = podium_count.sum(axis=1)
podium_count = podium_count.sort_values('Total', ascending=False).head(10).drop('Total', axis=1)

# -------------------------------
# Display All Plots in Tabs
# -------------------------------

tab1, tab2, tab3, tab4 = st.tabs(["📊 Driver Performance", "🏭 Constructor Trends", " 🏆 Podium Heatmap", "🌐 Interactive"])

with tab1:
    st.subheader("Top 6 Drivers: Points per Season")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=driver_trend, x='year', y='points', hue='driver', marker='o', ax=ax1)
    ax1.set_title("Driver Performance (2015–2024)")
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

with tab2:
    st.subheader("Top Constructors: Points Over Time")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=cons_trend, x='year', y='points', hue='constructor', marker='s', ax=ax2)
    ax2.set_title("Constructor Trends (2015–2024)")
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

with tab3:
    st.subheader("Top 10 Drivers: Podium Finishes (1st, 2nd, 3rd)")
    fig3, ax3 = plt.subplots(figsize=(9, 6))
    sns.heatmap(podium_count, annot=True, fmt="d", cmap="YlOrRd", cbar_kws={'label': 'Count'}, ax=ax3)
    ax3.set_title("Podium Appearances")
    st.pyplot(fig3)

with tab4:
    st.subheader("Interactive Constructor Chart (Plotly)")
    fig4 = px.line(
        cons_trend,
        x='year',
        y='points',
        color='constructor',
        markers=True,
        title="Constructor Points (Interactive)"
    )
    fig4.update_layout(hovermode="x unified")
    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# Footer
# -------------------------------
# -------------------------------
# 🧠 Prediction: Who Will Be Top 3 in 2025?
# -------------------------------
st.markdown("---")
st.header("🔮 Predicting the Top 3 Drivers for 2025")

st.markdown("""
This prediction is based on **average points per race** from 2020 to 2024.  
We assume:
- 20 races in 2025
- Drivers continue performing at their recent average level
""")

# Filter recent years (2020–2024)
recent_years = df[df['year'] >= 2020]

# Calculate points per race for each driver
driver_race_count = recent_years.groupby('driver').size()
driver_total_points = recent_years.groupby('driver')['points'].sum()

# Avoid division by zero
driver_avg = driver_total_points / driver_race_count
driver_avg = driver_avg.dropna().sort_values(ascending=False)

# Project 2025 points (20 races)
projection_2025 = (driver_avg * 20).round(1).nlargest(10)

# Get top 3
top3 = projection_2025.head(3)

# Display
st.subheader("📊 Projected Points in 2025 (Top 10)")
st.bar_chart(projection_2025)

st.subheader("🏆 Predicted Top 3 Drivers for 2025")
for i, (driver, pts) in enumerate(top3.items(), 1):
    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
    st.markdown(f"{medal} **{driver}**: ~{int(pts)} points")

st.markdown("**Note**: This is a trend-based estimate — real results depend on car performance, injuries, team changes, and luck!")
st.markdown("---")
st.markdown("🎯 Built with Python | pandas | matplotlib | seaborn | plotly | streamlit")
st.markdown("🎓 Data covers 2015–2024 — perfect for data storytelling!")