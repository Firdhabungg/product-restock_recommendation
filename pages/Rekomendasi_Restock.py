import streamlit as st
import pandas as pd
from utils.data_loader import load_full_product_data, load_cluster_summary

st.set_page_config(
    page_title="Rekomendasi Restock",
    page_icon="🛒",
    layout="wide"
)

st.title("Rekomendasi Restock")
st.caption("Cek kebutuhan restock produk dan lihat rekomendasi pemesanan berdasarkan kategori pergerakan barang.")

# Load data
products = load_full_product_data()
cluster_summary = load_cluster_summary()

# Manage session state for displaying results
if "show_result" not in st.session_state:
    st.session_state.show_result = False

def hide_result():
    st.session_state.show_result = False

# ==========================================
# 1. RINGKASAN KATEGORI
# ==========================================
st.markdown("---")
st.markdown("### 📐 Tingkat Layanan per Kategori")

with st.container(border=True):
    cl1, cl2, cl3 = st.columns(3)
    
    for i, (col, emoji) in enumerate(zip(
        [cl1, cl2, cl3],
        ["🔴", "🟡", "🟢"]
    )):
        row = cluster_summary.iloc[i]
        kategori = row["Index"]
        with col:
            with st.container(border=True):
                st.markdown(f"#### {emoji} {kategori}")
                m1, m2, m3 = st.columns(3)
                m1.metric("Service Level", f"{row['Service_Level']}%")
                m2.metric("Z-Score", f"{row['Z_Score']:.3f}")
                m3.metric("Avg Safety Stock", f"{row['SS_mean']:.2f}")

st.markdown("---")

# ==========================================
# 2. KALKULATOR RESTOCK
# ==========================================
st.markdown("### 🧮 Cek Restock Produk")

with st.container(border=True):
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        product_list = products["Barang Nama"].tolist()
        selected_product_name = st.selectbox(
            "Pilih Produk", 
            options=product_list,
            on_change=hide_result
        )
        
        product_data = products[products["Barang Nama"] == selected_product_name].iloc[0]

    with sim_col2:
        stok_simulasi = st.number_input(
            "Stok Aktual", 
            min_value=0.0, 
            value=float(product_data["Stok_Aktual"]), 
            step=1.0,
            key=f"stok_{selected_product_name}",
            on_change=hide_result
        )
    
    # Show cluster info badge
    kategori = product_data["Kategori"]
    service_level = product_data["Service_Level"]
    z_score = product_data["Z_Score"]
    
    badge_map = {"Fast Moving": "🔴", "Medium Moving": "🟡", "Slow Moving": "🟢"}
    badge = badge_map.get(kategori, "⚪")
    
    st.markdown(f"> {badge} **{kategori}** — Service Level: **{service_level}%** | Z-Score: **{z_score:.3f}**")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Proses Rekomendasi", type="primary", use_container_width=True):
        st.session_state.show_result = True


# Display Results
if st.session_state.show_result:
    rop = product_data["ROP"]
    safety_stock = product_data["Safety_Stock"]
    adu = product_data["ADU"]
    kategori = product_data["Kategori"]
    service_level = product_data["Service_Level"]
    z_score = product_data["Z_Score"]
    
    if stok_simulasi <= rop:
        status_sim = "🔴 RESTOCK"
        qty_sim = round(max(0, rop - stok_simulasi), 2)
    else:
        status_sim = "🟢 CUKUP"
        qty_sim = 0.0

    st.markdown("---")
    st.markdown("#### 📊 Hasil Analisis")
    
    # Row 1: Identifikasi & Parameter
    with st.container(border=True):
        r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
        r1c1.metric("Kategori", kategori)
        r1c2.metric("Service Level", f"{service_level}%")
        r1c3.metric("Pemakaian/Hari", f"{adu:.4f}")
        r1c4.metric("Safety Stock", f"{safety_stock:.4f}")
        r1c5.metric("Batas Reorder", f"{rop:.4f}")
    
    # Row 2: Keputusan
    col_res1, col_res2 = st.columns([1.5, 1])
    
    with col_res1:
        with st.container(border=True):
            st.markdown("##### 📦 Perbandingan Stok")
            step3_col1, step3_col2 = st.columns(2)
            step3_col1.metric("Stok Saat Ini", f"{stok_simulasi:.2f} unit")
            step3_col2.metric("Batas Reorder", f"{rop:.4f} unit")
            
            if stok_simulasi <= rop:
                st.warning(f"Stok ({stok_simulasi:.2f}) sudah di bawah batas reorder ({rop:.4f}) — **segera lakukan pemesanan**")
            else:
                st.success(f"Stok ({stok_simulasi:.2f}) masih di atas batas reorder ({rop:.4f}) — **stok aman**")

    with col_res2:
        with st.container(border=True):
            st.markdown("##### 🎯 Keputusan")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if status_sim == "🔴 RESTOCK":
                st.error(f"### {status_sim}")
            else:
                st.success(f"### {status_sim}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"**Jumlah Pemesanan:** {qty_sim} unit")


st.markdown("---")

# ==========================================
# 3. DAFTAR SELURUH PRODUK
# ==========================================
with st.container(border=True):
    st.markdown(f"### 📋 Daftar Rekomendasi Seluruh Produk ({len(products)} SKU)")

    col1, col2 = st.columns(2)
    with col1:
        kategori_filter = st.selectbox(
            "Filter Kategori",
            options=["Semua", "Fast Moving", "Medium Moving", "Slow Moving"],
            on_change=hide_result
        )

    with col2:
        keyword = st.text_input(
            "Cari Produk", 
            placeholder="Ketik nama produk...",
            on_change=hide_result
        )

    show = products.copy()

    if kategori_filter != "Semua":
        show = show[show["Kategori"] == kategori_filter]

    if keyword:
        show = show[show["Barang Nama"].str.contains(keyword, case=False)]

    show["Priority"] = show["Status"].map({
        "🔴 RESTOCK": 0,
        "🟢 CUKUP": 1
    })
    show = show.sort_values(by=["Priority", "Stok_Aktual"], ascending=[True, True])
    show = show.drop(columns=["Priority", "Index"], errors="ignore")

    display_cols = ["Barang Nama", "Kategori", "Service_Level", "Z_Score", "Safety_Stock", "ROP", "Stok_Aktual", "Qty_Order", "Status"]
    show_display = show[display_cols]

    st.dataframe(
        show_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Barang Nama": st.column_config.TextColumn("Nama Produk"),
            "Kategori": st.column_config.TextColumn("Kategori"),
            "Service_Level": st.column_config.NumberColumn("Service Level (%)", format="%.1f"),
            "Z_Score": st.column_config.NumberColumn("Z-Score", format="%.3f"),
            "Safety_Stock": st.column_config.NumberColumn("Safety Stock", format="%.4f"),
            "ROP": st.column_config.NumberColumn("Batas Reorder", format="%.4f"),
            "Stok_Aktual": st.column_config.NumberColumn("Stok Saat Ini", format="%.1f"),
            "Qty_Order": st.column_config.NumberColumn("Qty Order", format="%.2f"),
            "Status": st.column_config.TextColumn("Status")
        }
    )

    total = len(show)
    restock_count = len(show[show["Status"] == "🔴 RESTOCK"])
    cukup_count = len(show[show["Status"] == "🟢 CUKUP"])
    
    st.caption(f"Menampilkan **{total}** produk — 🔴 Restock: **{restock_count}** | 🟢 Cukup: **{cukup_count}**")
