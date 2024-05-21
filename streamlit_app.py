import streamlit as st
import dropbox
import duckdb
import pandas as pd
import folium
from streamlit_folium import st_folium

# Access token
DROPBOX_ACCESS_TOKEN = st.secrets["DROPBOX_ACCESS_TOKEN"]

# Initialize Dropbox client
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Path to the DuckDB database file in Dropbox
dbx_path = "/DVIPS.db"
local_db_path = "DVIPS.db"

try:
    st.write("Authenticating with Dropbox...")
    # Get account information to verify authentication
    account_info = dbx.users_get_current_account()
    st.write(f"Authenticated as: {account_info.name.display_name}")

    # Download the database file from Dropbox
    with open(local_db_path, "wb") as f:
        metadata, res = dbx.files_download(path=dbx_path)
        f.write(res.content)
    st.write(f"Downloaded {dbx_path} to {local_db_path}")

    # Connect to the DuckDB database
    con = duckdb.connect(local_db_path)

    # Load the geo_regulations table into a DataFrame
    geo_regulations_df = con.execute("SELECT * FROM geo_regulations").fetchdf()
    st.write("Contents of geo_regulations table:")
    st.write(geo_regulations_df)

    # Check for 'Country_Latitude' and 'Country_Longitude' columns
    if 'Country_Latitude' in geo_regulations_df.columns and 'Country_Longitude' in geo_regulations_df.columns:
        # Create a folium map
        m = folium.Map(location=[geo_regulations_df['Country_Latitude'].mean(), geo_regulations_df['Country_Longitude'].mean()], zoom_start=2)

        # Add points to the map
        for _, row in geo_regulations_df.iterrows():
            folium.Marker(location=[row['Country_Latitude'], row['Country_Longitude']], popup=row['Regulation']).add_to(m)

        # Display the map in Streamlit
        st_data = st_folium(m, width=700, height=500)
    else:
        st.error("The required columns 'Country_Latitude' and 'Country_Longitude' are not present in the DataFrame.")

    # Close the connection
    con.close()
except dropbox.exceptions.AuthError as e:
    st.error(f"Error authenticating with Dropbox: {e}")
except dropbox.exceptions.ApiError as e:
    st.error(f"API error: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")
