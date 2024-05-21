import streamlit as st
import os
import duckdb
import dropbox
import pandas as pd
import folium
from streamlit_folium import st_folium

# Load secrets
DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
DROPBOX_APP_KEY = st.secrets["DROPBOX_APP_KEY"]
DROPBOX_APP_SECRET = st.secrets["DROPBOX_APP_SECRET"]
ARC_GIS_UNAME = st.secrets["ARC_GIS_UNAME"]
ARC_GIS_PWORD = st.secrets["ARC_GIS_PWORD"]

# Initialize Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Path to the DuckDB database file in Dropbox
dbx_path = "/EDLV Sustainability Regulations/DVIPS.db"
local_db_path = "DVIPS.db"

# Download the database file from Dropbox
with open(local_db_path, "wb") as f:
    metadata, res = dbx.files_download(path=dbx_path)
    f.write(res.content)

# Connect to the DuckDB database
con = duckdb.connect(local_db_path)

# Load the geocoded regulations data
geo_regulations = con.execute("SELECT * FROM geo_regulations").fetchdf()

# Close the connection
con.close()

# Create a folium map centered on a default location
m = folium.Map(location=[0, 0], zoom_start=2)

# Add points to the map
for idx, row in geo_regulations.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"Title: {row['Title']}<br>Date: {row['Date']}<br>Status: {row['Status']}<br>URL: {row['URL']}",
    ).add_to(m)

# Display the map in Streamlit
st.title("Plastic Regulations Interactive Map")
st_folium(m, width=700, height=500)
