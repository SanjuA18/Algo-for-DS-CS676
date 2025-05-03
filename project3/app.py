import streamlit as st
import pandas as pd
import requests
import base64
from main import summarize_and_visualize_data  # make sure this is imported correctly

st.set_page_config(page_title="Smart EDA Visualizer", layout="wide", page_icon="📊")

st.markdown("""
    <style>
        .main { background-color: #f9fbfc; }
        .stSidebar { background-color: #000000; }
        .metric-label, .metric-value { font-weight: bold; }
        .plot-title { font-size: 1.2em; margin-top: 10px; color: #336699; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("📁 Upload & Configure")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("File successfully uploaded")
    
    use_sample = st.sidebar.checkbox("Use only first 100 rows (for large files)")
    if use_sample and len(df) > 100:
        df = df.head(100)

    payload = {"data": df.to_dict(orient="records")}
    secrets = {}  
    event_stream = []

    st.title("📊 Exploratory Data Analysis Summary")
    st.write("Upload a dataset to get descriptive statistics and smart visualizations.")

    result = summarize_and_visualize_data(payload, secrets, event_stream)

    if result["status"] == "success":
        st.subheader(" Descriptive Statistics")
        desc_df = pd.DataFrame(result["description"])
        st.dataframe(desc_df.T)

        if result["visualizations"]:
            st.subheader("📉 Visualizations")
            for viz in result["visualizations"]:
                st.markdown(f"<div class='plot-title'>🔹 {viz['column']}</div>", unsafe_allow_html=True)
                img_bytes = base64.b64decode(viz["plot"])
                st.image(img_bytes, use_column_width=True)
        else:
            st.warning("No visualizations could be generated.")

    else:
        st.error(f" Error: {result['message']}")
else:
    st.info("📂 Upload a CSV file to begin analysis.")
