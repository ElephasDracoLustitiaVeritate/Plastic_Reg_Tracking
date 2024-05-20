import streamlit as st
import os
import duckdb
import dropbox
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

st.title("Plastic Regulations Map")

# Load secrets
DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
ARC_GIS_UNAME = st.secrets["ARC_GIS_UNAME"]
ARC_GIS_PWORD = st.secrets["ARC_GIS_PWORD"]

# Connect to Dropbox
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Define the path to the DuckDB database file in Dropbox
dbx_path = 'DVIPS.db'

# Download the DuckDB file from Dropbox
local_path = 'DVIPS.db'
with open(local_path, "wb") as f:
    metadata, res = dbx.files_download(path=dbx_path)
    f.write(res.content)

# Connect to DuckDB
con = duckdb.connect(local_path)

# Load data from DuckDB
df = con.execute("SELECT * FROM PlasticRegulations LIMIT 100").fetchdf()

# Geocode using geopy
geolocator = Nominatim(user_agent="plastic-regulations-map")

def geocode_location(location):
    try:
        return geolocator.geocode(location)
    except GeocoderTimedOut:
        return None

# Add geocoded coordinates to DataFrame
df['Geocode'] = df['Country/Territory'].apply(geocode_location)
df['Latitude'] = df['Geocode'].apply(lambda loc: loc.latitude if loc else None)
df['Longitude'] = df['Geocode'].apply(lambda loc: loc.longitude if loc else None)

# Create a Folium map
m = folium.Map(location=[20, 0], zoom_start=2)

# Add data points to the map
for idx, row in df.iterrows():
    if not pd.isna(row['Latitude']) and not pd.isna(row['Longitude']):
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Title']} - {row['Country/Territory']}",
            tooltip=row['Title']
        ).add_to(m)

# Display the map in Streamlit
st_folium(m, width=700, height=500)
