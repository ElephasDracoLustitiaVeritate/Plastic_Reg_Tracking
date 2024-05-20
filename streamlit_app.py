import streamlit as st
import os
import duckdb
import dropbox
from arcgis.gis import GIS
from arcgis.geocoding import geocode
import pandas as pd
import folium
from streamlit_folium import st_folium

# Load secrets
DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]
ARC_GIS_UNAME = st.secrets["ARC_GIS_UNAME"]
ARC_GIS_PWORD = st.secrets["ARC_GIS_PWORD"]

# Initialize Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Path to the DuckDB database file in Dropbox
dbx_path = "/path/to/your/DVIPS.db"
local_db_path = "DVIPS.db"

# Download the database file from Dropbox
with open(local_db_path, "wb") as f:
    metadata, res = dbx.files_download(path=dbx_path)
    f.write(res.content)

# Connect to the DuckDB database
con = duckdb.connect(local_db_path)

# Load regulations and geocode data
regulations = con.execute("SELECT * FROM PlasticRegulations").fetchdf()
geo_countries = con.execute("SELECT * FROM geo_countries").fetchdf()
geo_territories = con.execute("SELECT * FROM geo_territories").fetchdf()

# Close the connection
con.close()

# Initialize ArcGIS
gis = GIS("https://www.arcgis.com", ARC_GIS_UNAME, ARC_GIS_PWORD)

# Merge regulations with geocode data
regulations_geo = regulations.merge(geo_countries, left_on='Country/Territory', right_on='Country', how='left')
regulations_geo = regulations_geo.merge(geo_territories, left_on='Country/Territory', right_on='Territory', how='left')

# Fill missing latitude and longitude
regulations_geo['Latitude'] = regulations_geo['Latitude_x'].combine_first(regulations_geo['Latitude_y'])
regulations_geo['Longitude'] = regulations_geo['Longitude_x'].combine_first(regulations_geo['Longitude_y'])

# Drop unnecessary columns
regulations_geo = regulations_geo.drop(columns=['Latitude_x', 'Longitude_x', 'Latitude_y', 'Longitude_y', 'Country', 'Territory'])

# Create a folium map centered at a default location
m = folium.Map(location=[20, 0], zoom_start=2)

# Add markers for each regulation
for _, row in regulations_geo.iterrows():
    if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['Title']} ({row['Date of original text']})",
            tooltip=row['Title']
        ).add_to(m)

# Display the map in Streamlit
st.title("Global Plastic Regulations Map")
st_folium(m, width=700, height=500)
