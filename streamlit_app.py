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

@st.cache_data
def get_dbx_file(dbx_path, local_db_path):
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
    except dropbox.exceptions.AuthError as e:
        st.error(f"Error authenticating with Dropbox: {e}")
    except dropbox.exceptions.ApiError as e:
        st.error(f"API error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def load_data_in_chunks(con, chunk_size=1000):
    offset = 0
    while True:
        query = f"SELECT * FROM geo_regulations LIMIT {chunk_size} OFFSET {offset}"
        df_chunk = con.execute(query).fetchdf()
        if df_chunk.empty:
            break
        yield df_chunk
        offset += chunk_size

# Get the database file from Dropbox
get_dbx_file(dbx_path, local_db_path)

try:
    # Connect to the DuckDB database
    con = duckdb.connect(local_db_path)

    # Initialize an empty DataFrame
    geo_regulations_df = pd.DataFrame()

    # Load the data in chunks
    for chunk in load_data_in_chunks(con):
        geo_regulations_df = pd.concat([geo_regulations_df, chunk], ignore_index=True)
        st.write(f"Loaded {len(geo_regulations_df)} records")

    st.write("Contents of geo_regulations table:")
    st.write(geo_regulations_df)

    # Check for latitude and longitude columns
    if 'Country_Latitude' in geo_regulations_df.columns and 'Country_Longitude' in geo_regulations_df.columns:
        # Create a folium map
        m = folium.Map(location=[geo_regulations_df['Country_Latitude'].mean(), geo_regulations_df['Country_Longitude'].mean()], zoom_start=2)

        # Add points to the map
        for _, row in geo_regulations_df.iterrows():
            lat = row['Country_Latitude'] if pd.notna(row['Country_Latitude']) else row['Territory_Latitude']
            lon = row['Country_Longitude'] if pd.notna(row['Country_Longitude']) else row['Territory_Longitude']
            if pd.notna(lat) and pd.notna(lon):
                folium.Marker(location=[lat, lon], popup=row['Title']).add_to(m)

        # Display the map in Streamlit
        st_data = st_folium(m, width=700, height=500)
    else:
        st.error("The required columns 'Country_Latitude' and 'Country_Longitude' are not present in the DataFrame.")

    # Close the connection
    con.close()
except Exception as e:
    st.error(f"An error occurred: {e}")
