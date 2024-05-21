import streamlit as st
import duckdb
import pandas as pd
import folium
from streamlit_folium import st_folium

# Connect to the local DuckDB database
db_path = "DVIPS.db"
con = duckdb.connect(db_path)

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
st_folium(m, width=700, height=500) Map")
st_folium(m, width=700, height=500)
