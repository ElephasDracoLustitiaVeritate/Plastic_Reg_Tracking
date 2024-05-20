import streamlit as st
import pandas as pd
import duckdb
import folium
from streamlit_folium import st_folium
import dropbox
import os
from arcgis.gis import GIS
from arcgis.geocoding import geocode

# Retrieve secrets from environment variables
dbx_token = os.getenv("DROPBOX_ACCESS_TOKEN")
arcgis_uname = os.getenv("ARC_GIS_UNAME")
arcgis_pword = os.getenv("ARC_GIS_PWORD")

st.title("Plastic Regulations Map")

# Dropbox section
st.header("Dropbox Data")
if dbx_token:
    st.write("Dropbox token found.")
    # Initialize Dropbox client
    dbx = dropbox.Dropbox(dbx_token)
    dbx_path = "/Plastic Regulations Database/DVIPS.db"

    # Download the DuckDB file from Dropbox
    try:
        _, res = dbx.files_download(dbx_path)
        with open("DVIPS.db", "wb") as f:
            f.write(res.content)
        st.write("Downloaded DVIPS.db from Dropbox.")

        # Connect to the DuckDB database
        con = duckdb.connect("DVIPS.db")

        # Load data from the database
        df = con.execute("SELECT * FROM PlasticRegulations").fetchdf()
        st.write("Data loaded from database.")

        # Display data in a table
        st.dataframe(df)

        # Create a map using Folium
        m = folium.Map(location=[0, 0], zoom_start=2)

        # Add markers to the map
        for _, row in df.iterrows():
            if pd.notna(row["Latitude"]) and pd.notna(row["Longitude"]):
                folium.Marker(
                    location=[row["Latitude"], row["Longitude"]],
                    popup=row["Title"]
                ).add_to(m)

        # Display the map in Streamlit
        st_folium(m, width=700, height=500)

    except dropbox.exceptions.ApiError as e:
        st.error(f"Failed to download file from Dropbox: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.error("Dropbox access token not found. Please add it as a GitHub secret.")

# ArcGIS section
st.header("ArcGIS Geocoding")
if arcgis_uname and arcgis_pword:
    st.write("ArcGIS credentials found.")
    try:
        # Connect to ArcGIS
        gis = GIS("https://www.arcgis.com", arcgis_uname, arcgis_pword)
        st.write("Connected to ArcGIS.")

        # Geocode example
        result = geocode("United States", max_locations=1, out_sr={"wkid": 4326})
        if result and len(result) > 0:
            location_data = result[0]
            st.write(f"Geocode result for United States: {location_data['location']}")
        else:
            st.write("No geocode result found for United States.")
    except Exception as e:
        st.error(f"An error occurred while geocoding: {e}")
else:
    st.error("ArcGIS credentials not found. Please add them as GitHub secrets.")
