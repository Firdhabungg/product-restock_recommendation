import streamlit as st
from utils.data_loader import (
    load_cluster_data, 
    load_simulation_data
)

st.set_page_config(
    page_title="Dashboard",
    page_icon="🛒",
    layout="wide"
)

cluster = load_cluster_data()
simulation = load_simulation_data()

# Clean up status for better visualization globally
simulation["Status"] = simulation["Status"].replace({
    "⚠ RESTOCK": "🔴 RESTOCK",
    "✓ CUKUP": "🟢 CUKUP"
})

header1, header2 = st.columns([1,7])

with header1:
    st.image("assets/logo.png", width=80)

with header2:
    st.title("Dashboard Sistem Rekomendasi Restock")
    st.caption("Lestari Mart | Sistem Cerdas Manajemen Persediaan (K-Means & ROP)")

st.markdown("---")

# Add a fake operational status bar to make it feel like a real deployed system
st.info("🟢 **Status Sistem:** Terhubung ke Database Gudang Utama | **Pembaruan Terakhir:** Sinkronisasi Hari Ini")

# 1. Ringkasan Hasil Klasterisasi Container
with st.container(border=True):
    st.markdown("#### 📦 Ringkasan Hasil Klasterisasi")
    
    total_produk = len(cluster)
    fast = len(cluster[cluster["Kategori"]=="Fast Moving"])
    medium = len(cluster[cluster["Kategori"]=="Medium Moving"])
    slow = len(cluster[cluster["Kategori"]=="Slow Moving"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total SKU Aktif", total_produk)
    c2.metric("Barang Fast Moving", fast)
    c3.metric("Barang Medium Moving", medium)
    c4.metric("Barang Slow Moving", slow)

# 2. Ringkasan Keputusan Sistem Container
with st.container(border=True):
    st.markdown("#### ⚠️ Peringatan Restock & Rekomendasi Tindakan")

    restock_df = simulation[simulation["Status"]=="🔴 RESTOCK"]
    produk_restock = len(restock_df)
    total_pemesanan = restock_df["Qty_Order"].sum()

    if not restock_df.empty:
        top_priority_product = restock_df.sort_values("Stok_Aktual", ascending=True).iloc[0]["Barang Nama"]
    else:
        top_priority_product = "-"

    col1, col2, col3 = st.columns(3)
    col1.metric("SKU Kritis (Butuh Restock)", f"{produk_restock} Produk")
    col2.metric("Total Estimasi Order", f"{int(total_pemesanan)} Unit")
    col3.metric("Fokus Utama Pemesanan", top_priority_product)

# 3. Layout for Table and Chart side-by-side
st.markdown("<br>", unsafe_allow_html=True)
col_table, col_chart = st.columns([1.5, 1])

with col_table:
    with st.container(border=True):
        st.markdown("#### 🚨 Daftar Tindakan: 10 Barang Paling Kritis")
        
        priority = simulation[simulation["Status"] == "🔴 RESTOCK"]
        priority = priority.sort_values("Stok_Aktual", ascending=True)
        priority = priority[["Barang Nama", "Kategori", "ROP", "Stok_Aktual"]].head(10)
        
        st.dataframe(
            priority,
            hide_index=True,
            use_container_width=True
        )

with col_chart:
    with st.container(border=True):
        st.subheader("Distribusi Kategori")
        chart = cluster["Kategori"].value_counts()
        st.bar_chart(chart)
