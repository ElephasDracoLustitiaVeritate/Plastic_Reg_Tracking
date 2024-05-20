import streamlit as st

st.title("Plastic Regulations Map")

try:
    DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
    ARC_GIS_UNAME = st.secrets["ARC_GIS_UNAME"]
    ARC_GIS_PWORD = st.secrets["ARC_GIS_PWORD"]
    st.write("Secrets loaded successfully.")
except KeyError as e:
    st.write(f"KeyError: {e}")

st.write("Available secrets:", st.secrets)
