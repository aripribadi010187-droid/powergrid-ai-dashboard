import io
import pandas as pd
import requests
import streamlit as st

SHEET_URLS = {
    "gardu_induk": "https://docs.google.com/spreadsheets/d/1TNqQ_2p77uw6Acv3bGq78pV5XDkAeRZazkIsqkZUpm0/export?format=csv",
    "transmisi": "https://docs.google.com/spreadsheets/d/1FqZQpQOOnR8oonnXWw7UlIkIX5rk1IuRLZW2VRwvvmI/export?format=csv",
    "distribusi": "https://docs.google.com/spreadsheets/d/1F5N-BOZ3udBywzhEMbxnshpa7NXoEQzAHStwChdeQek/export?format=csv",
    "pembangkit": "https://docs.google.com/spreadsheets/d/14Z4W20lV_ACa1ZoFMrUKc3RHzI4OGudrdLbriTBLzT4/export?format=csv",
}

def fetch_csv_data(url: str) -> pd.DataFrame:
    """Fetch CSV data from Google Sheets export URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        csv_data = response.content.decode("utf-8", errors="replace")
        df = pd.read_csv(io.StringIO(csv_data))
        # Strip whitespace from column names and string cells
        df.columns = [col.strip() for col in df.columns]
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.warning(f"Gagal mengambil data dari Google Sheets ({url}): {e}. Menggunakan cache lokal jika ada.")
        raise e

@st.cache_data(ttl=300, show_spinner=False)
def load_all_data():
    """Load all 4 datasets with caching."""
    data = {}
    
    # 1. Gardu Induk
    try:
        df_gi = fetch_csv_data(SHEET_URLS["gardu_induk"])
        if "Kapasitas (MVA)" in df_gi.columns:
            df_gi["Kapasitas (MVA)"] = pd.to_numeric(df_gi["Kapasitas (MVA)"], errors="coerce").fillna(0)
        data["gardu_induk"] = df_gi
    except Exception:
        data["gardu_induk"] = pd.DataFrame()

    # 2. Transmisi
    try:
        df_tr = fetch_csv_data(SHEET_URLS["transmisi"])
        if "Panjang (km)" in df_tr.columns:
            df_tr["Panjang (km)"] = pd.to_numeric(df_tr["Panjang (km)"], errors="coerce").fillna(0)
        if "Tegangan (kV)" in df_tr.columns:
            df_tr["Tegangan (kV)"] = pd.to_numeric(df_tr["Tegangan (kV)"], errors="coerce").fillna(0)
        data["transmisi"] = df_tr
    except Exception:
        data["transmisi"] = pd.DataFrame()

    # 3. Distribusi
    try:
        df_dis = fetch_csv_data(SHEET_URLS["distribusi"])
        if "Panjang Jaringan (km)" in df_dis.columns:
            df_dis["Panjang Jaringan (km)"] = pd.to_numeric(df_dis["Panjang Jaringan (km)"], errors="coerce").fillna(0)
        data["distribusi"] = df_dis
    except Exception:
        data["distribusi"] = pd.DataFrame()

    # 4. Pembangkit
    try:
        df_pem = fetch_csv_data(SHEET_URLS["pembangkit"])
        if "Kapasitas (MW)" in df_pem.columns:
            df_pem["Kapasitas (MW)"] = pd.to_numeric(df_pem["Kapasitas (MW)"], errors="coerce").fillna(0)
        data["pembangkit"] = df_pem
    except Exception:
        data["pembangkit"] = pd.DataFrame()

    return data

def clear_data_cache():
    """Clear cached data to force reload."""
    st.cache_data.clear()

