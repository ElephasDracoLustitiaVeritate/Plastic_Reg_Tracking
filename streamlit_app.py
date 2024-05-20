import streamlit as st
import os

DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
ARC_GIS_UNAME = st.secrets["ARC_GIS_UNAME"]
ARC_GIS_PWORD = st.secrets["ARC_GIS_PWORD"]

st.write("Secrets loaded successfully.")
