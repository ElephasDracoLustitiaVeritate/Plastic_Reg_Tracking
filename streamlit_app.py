import streamlit as st
import duckdb
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# URL to the Dropbox file
dropbox_url = "https://www.dropbox.com/scl/fi/lcw0m38r8ky2xqa4p1vhn/DVIPS.db?rlkey=gstg6qpawkxfl3sx7xagylqz8&st=zo86erew&dl=1"

# Local path to save the downloaded file
local_db_path = "DVIPS.db"

# Download the file from Dropbox
with requests.get(dropbox_url, stream=True) as r:
    with open(local_db_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

# Connect to the local DuckDB database
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
