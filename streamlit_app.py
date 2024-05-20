import streamlit as st
import pandas as pd
import duckdb
import folium
from streamlit_folium import st_folium
import dropbox
import os
from arcgis.gis import GIS
from arcgis.geocoding import geocode

st.title("Plastic Regulations Map")

# Test imports by displaying simple messages
st.write("All imports successful.")
