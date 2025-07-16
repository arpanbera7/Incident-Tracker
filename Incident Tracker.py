import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
import os

# Constants
DATA_FILE = "Incident Details.xlsx"
ADMIN_PASSWORD = "Arpan@Nielsen123"

# Load incident data
@st.cache_data
def load_data():
    return pd.read_excel(DATA_FILE, engine="openpyxl")

# Search for similar incidents
def search_incidents(df, query, threshold):
    results = []
    for _, row in df.iterrows():
        combined_text = f"{row['Issue Summary']} {row['Issue Description']}"
        score = fuzz.partial_ratio(query.lower(), str(combined_text).lower())
        if score >= threshold:
            results.append((score, row))
    results.sort(reverse=True, key=lambda x: x[0])
    return [r[1] for r in results]

# Streamlit UI
st.set_page_config(page_title="Incident Tracker", layout="wide")
st.title("🔍 Incident Similarity Checker")
st.write("Check if a similar issue has already been raised before submitting a new ticket.")

# Admin upload section
with st.sidebar:
    st.header("Admin Panel")
    password = st.text_input("Enter admin password", type="password")
    if password == ADMIN_PASSWORD:
        uploaded_file = st.file_uploader("Upload new incident file", type=["xlsx"])
        if uploaded_file:
            with open(DATA_FILE, "wb") as f:
                f.write(uploaded_file.read())
            st.success("✅ File uploaded successfully. Please refresh the app.")

# Load data
try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Search interface
st.subheader("Search for Similar Incidents")
query = st.text_input("Describe your issue:")
threshold = st.slider("Fuzzy match threshold", 50, 100, 80)

if st.button("Search"):
    if not query.strip():
        st.warning("⚠️ Please enter an issue description.")
    else:
        matches = search_incidents(df, query, threshold)
        if matches:
            st.success(f"✅ Found {len(matches)} similar incident(s):")
            for match in matches:
                st.markdown("---")
                st.markdown(f"**Incident Number:** {match['Number']}")
                st.markdown(f"**Issue Summary:** {match['Issue Summary']}")
                st.markdown(f"**Resolution Notes:** {match['Resolution notes']}")
                st.markdown(f"**Assigned To:** {match['Assigned to']}")
                st.markdown(f"**Assignment Group:** {match['Assignment group']}")
        else:
            st.info("ℹ️ No similar incidents found.")
