import streamlit as st
import os
import duckdb
import dropbox
import pandas as pd
import folium
from streamlit_folium import st_folium

# Load secrets
DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]

# Initialize Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Path to the DuckDB database file in Dropbox
dbx_path = "/Nicholas Polich/Apps/EDLV Sustainability Regulations/DVIPS.db"
local_db_path = "DVIPS.db"

# Function to download the database file from Dropbox
def download_db():
    try:
        metadata, res = dbx.files_download(path=dbx_path)
        with open(local_db_path, "wb") as f:
            f.write(res.content)
        st.success("Database downloaded successfully.")
    except dropbox.exceptions.ApiError as e:
        st.error(f"Dropbox API error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Download the database file from Dropbox
download_db()

# Connect to the DuckDB database
con = None
try:
    con = duckdb.connect(local_db_path)
    st.success("Connected to DuckDB successfully.")
except Exception as e:
    st.error(f"Error connecting to DuckDB: {e}")

# Load the geocoded regulations data
geo_regulations = pd.DataFrame()
if con:
    try:
        geo_regulations = con.execute("SELECT * FROM geo_regulations").fetchdf()
        st.success("Data loaded successfully.")
    except Exception as e:
        st.error(f"Error loading data from DuckDB: {e}")
    finally:
        con.close()

# Display the data
if not geo_regulations.empty:
    st.write(geo_regulations)

    # Create a folium map
    m = folium.Map(location=[20, 0], zoom_start=2)

    # Add regulations to the map
    for idx, row in geo_regulations.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=row['Title']
        ).add_to(m)

    # Display the map
    st_folium(m, width=725)
