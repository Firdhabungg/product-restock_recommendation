import streamlit as st
from utils.data_loader import (
    load_cluster_data, 
    load_full_product_data,
    load_cluster_summary
)

st.set_page_config(
    page_title="Dashboard",
    page_icon="🛒",
    layout="wide"
)

cluster = load_cluster_data()
simulation = load_full_product_data()
cluster_summary = load_cluster_summary()

header1, header2 = st.columns([1,7])

with header1:
    st.image("assets/logo.png", width=80)

with header2:
    st.title("Dashboard Manajemen Stok")
    st.caption("Lestari Mart — Pantau kondisi gudang dan kebutuhan restock secara real-time")

st.markdown("---")

st.info("🟢 **Status Sistem:** Terhubung ke Database Gudang Utama | **Pembaruan Terakhir:** Sinkronisasi Hari Ini")

# ==========================================
# 1. OVERVIEW PERSEDIAAN
# ==========================================
with st.container(border=True):
    st.markdown("#### 📦 Overview Persediaan")
    
    total_produk = len(cluster)
    fast = len(cluster[cluster["Kategori"]=="Fast Moving"])
    medium = len(cluster[cluster["Kategori"]=="Medium Moving"])
    slow = len(cluster[cluster["Kategori"]=="Slow Moving"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total SKU Aktif", total_produk)
    c2.metric("🔴 Fast Moving", fast)
    c3.metric("🟡 Medium Moving", medium)
    c4.metric("🟢 Slow Moving", slow)

# ==========================================
# 2. TINGKAT LAYANAN PER KATEGORI
# ==========================================
with st.container(border=True):
    st.markdown("#### 📐 Tingkat Layanan per Kategori")
    
    sl_col1, sl_col2, sl_col3 = st.columns(3)
    
    for i, (col, emoji) in enumerate(zip(
        [sl_col1, sl_col2, sl_col3],
        ["🔴", "🟡", "🟢"]
    )):
        row = cluster_summary.iloc[i]
        kategori_name = row["Index"]
        with col:
            with st.container(border=True):
                st.markdown(f"**{emoji} {kategori_name}**")
                m1, m2 = st.columns(2)
                m1.metric("Service Level", f"{row['Service_Level']}%")
                m2.metric("Z-Score", f"{row['Z_Score']:.3f}")

# ==========================================
# 3. STATUS RESTOCK
# ==========================================
with st.container(border=True):
    st.markdown("#### ⚠️ Status Restock")

    restock_df = simulation[simulation["Status"]=="🔴 RESTOCK"]
    produk_restock = len(restock_df)
    total_pemesanan = restock_df["Qty_Order"].sum()

    if not restock_df.empty:
        top_priority_product = restock_df.sort_values("Stok_Aktual", ascending=True).iloc[0]["Barang Nama"]
    else:
        top_priority_product = "-"

    col1, col2, col3 = st.columns(3)
    col1.metric("Produk Butuh Restock", f"{produk_restock} SKU")
    col2.metric("Total Estimasi Order", f"{int(total_pemesanan)} Unit")
    col3.metric("Prioritas Tertinggi", top_priority_product)

# ==========================================
# 4. TABEL KRITIS + CHART
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_table, col_chart = st.columns([1.5, 1])

with col_table:
    with st.container(border=True):
        st.markdown("#### 🚨 10 Barang Paling Kritis")
        
        priority = simulation[simulation["Status"] == "🔴 RESTOCK"]
        priority = priority.sort_values("Stok_Aktual", ascending=True)
        priority = priority[["Barang Nama", "Kategori", "ROP", "Stok_Aktual"]].head(10)
        
        st.dataframe(
            priority,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Barang Nama": st.column_config.TextColumn("Nama Produk"),
                "Kategori": st.column_config.TextColumn("Kategori"),
                "ROP": st.column_config.NumberColumn("Batas Reorder", format="%.2f"),
                "Stok_Aktual": st.column_config.NumberColumn("Stok Saat Ini", format="%.1f"),
            }
        )

with col_chart:
    with st.container(border=True):
        st.markdown("#### 📊 Distribusi Kategori")
        chart = cluster["Kategori"].value_counts()
        st.bar_chart(chart)
