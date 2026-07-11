import pandas as pd

df = pd.read_excel('data/hasil_eksperimen_lestari_mart.xlsx', sheet_name='6_Simulasi_Rekomendasi', header=1)

with open('debug_output.txt', 'w', encoding='utf-8') as f:
    for _, row in df.iterrows():
        stok = float(row['Stok_Aktual'])
        rop = float(row['ROP'])
        calc_status = 'RESTOCK' if stok <= rop else 'CUKUP'
        f.write(f"{row['Barang Nama']}: Data={row['Status']} - Calc={calc_status}\n")
