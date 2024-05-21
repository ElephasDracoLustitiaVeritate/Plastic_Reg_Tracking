import streamlit as st
import dropbox
import duckdb
import pandas as pd

# Load secrets
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

    # Close the connection
    con.close()
except dropbox.exceptions.AuthError as e:
    st.error(f"Error authenticating with Dropbox: {e}")
except dropbox.exceptions.ApiError as e:
    st.error(f"API error: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")
