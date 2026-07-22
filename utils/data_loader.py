import pandas as pd
import numpy as np

FILE_PATH = "data/hasil_eksperimen_lestari_mart.xlsx"

def load_cluster_data():
    """Load clustering results from sheet 4 (1036 products, Jan 2 - Jun 30 2026)."""
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="4_Hasil_Klusterisasi",
        header=1
    )
    return df

def load_cluster_summary():
    """Load cluster-level summary from sheet 5 (Service Level, Z-Score per cluster)."""
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="5_ROP_SS_per_Kluster",
        header=1
    )
    return df

def load_simulation_data():
    """Load simulation sample from sheet 6."""
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="6_Simulasi_Rekomendasi",
        header=1
    )
    return df

def load_full_product_data():
    """
    Load all 1036 products from sheet 4 (Hasil Klusterisasi) and generate
    realistic random Stok_Aktual for simulation. Computes Status and Qty_Order
    based on Stok_Aktual vs ROP comparison.
    
    Uses a fixed random seed for reproducibility across sessions.
    """
    df = pd.read_excel(
        FILE_PATH,
        sheet_name="4_Hasil_Klusterisasi",
        header=1
    )
    
    # Generate reproducible random stock levels
    rng = np.random.RandomState(42)
    
    # Generate Stok_Aktual: random between 0 and 2*ROP for realistic variation
    # This ensures ~50% products need restock and ~50% are sufficient
    df["Stok_Aktual"] = df.apply(
        lambda row: round(rng.uniform(0, max(row["ROP"] * 2.5, 1)), 1),
        axis=1
    )
    
    # Determine Status and Qty_Order based on Stok_Aktual vs ROP
    df["Status"] = df.apply(
        lambda row: "🔴 RESTOCK" if row["Stok_Aktual"] <= row["ROP"] else "🟢 CUKUP",
        axis=1
    )
    df["Qty_Order"] = df.apply(
        lambda row: round(max(0, row["ROP"] - row["Stok_Aktual"]), 2) if row["Stok_Aktual"] <= row["ROP"] else 0.0,
        axis=1
    )
    
    return df