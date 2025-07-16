import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

# Constants
DATA_FILE = "Incident Details.xlsx"
ADMIN_PASSWORD = "Arpan@Nielsen123"

# Session state for admin login and navigation
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Load data
@st.cache_data
def load_data():
    return pd.read_excel(DATA_FILE, engine="openpyxl")

# Fuzzy search
def search_incidents(df, query, threshold=80):
    results = []
    for _, row in df.iterrows():
        combined_text = f"{row['Issue Summary']} {row['Issue Description']}"
        score = fuzz.partial_ratio(query.lower(), str(combined_text).lower())
        if score >= threshold:
            results.append(row)
    return results

# Sidebar: Admin Panel
with st.sidebar:
    st.header("🔐 Admin Panel")
    if not st.session_state.admin_logged_in:
        password = st.text_input("Enter admin password", type="password")
        if password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Logged in as admin.")
    else:
        uploaded_file = st.file_uploader("Upload new incident file", type=["xlsx"])
        if uploaded_file:
            with open(DATA_FILE, "wb") as f:
                f.write(uploaded_file.read())
            st.success("File uploaded successfully. Please refresh the app.")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()

    # Caller filter (always visible)
    st.markdown("---")
    st.subheader("📌 Filter by Caller")
    try:
        df_all = load_data()
        callers = sorted(df_all["Caller"].dropna().unique())
        selected_caller = st.selectbox("Select a caller", ["All"] + callers)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Main UI
st.title("📋 Incident Similarity Checker")

# Filtered data
df = df_all.copy()
if selected_caller != "All":
    df = df[df["Caller"] == selected_caller]

# Search bar
query = st.text_input("🔍 Describe your issue:")
if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a valid issue description.")
    else:
        st.session_state.search_results = search_incidents(df, query)
        st.session_state.current_index = 0

# Display search results
if st.session_state.search_results:
    results = st.session_state.search_results
    index = st.session_state.current_index
    incident = results[index]

    st.markdown(f"### 🧾 Incident {index + 1} of {len(results)}")
    st.markdown(f"**Incident Number:** {incident['Number']}")
    st.markdown(f"**Caller:** {incident['Caller']}")
    st.markdown(f"**Issue Summary:** {incident['Issue Summary']}")
    st.markdown(f"**Issue Description:** {incident['Issue Description']}")
    st.markdown(f"**Resolution Notes:** {incident['Resolution notes']}")
    st.markdown(f"**Assigned To:** {incident['Assigned to']}")
    st.markdown(f"**Assignment Group:** {incident['Assignment group']}")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=index == 0):
            st.session_state.current_index -= 1
            st.experimental_rerun()
    with col2:
        st.markdown(f"<center><b>{incident['Number']}</b></center>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡️", disabled=index == len(results) - 1):
            st.session_state.current_index += 1
            st.experimental_rerun()
