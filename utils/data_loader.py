import pandas as pd

FILE_PATH = "data/hasil_eksperimen_lestari_mart.xlsx"

def load_cluster_data():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="4_Hasil_Klusterisasi",
        header=1
    )
    return df

def load_simulation_data():
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="6_Simulasi_Rekomendasi",
        header=1
    )
    return df