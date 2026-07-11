import streamlit as st
import pandas as pd
from utils.data_loader import load_simulation_data

st.set_page_config(
    page_title="Rekomendasi Restock",
    page_icon="🛒",
    layout="wide"
)

st.title("Rekomendasi Restock")
st.caption("Implementasi sistem rekomendasi. Halaman ini menjawab: 'apa rekomendasi sistem untuk produk yang dipilih berdasarkan stok aktual?'.")

simulation = load_simulation_data()

# Clean up status for better visualization
simulation["Status"] = simulation["Status"].replace({
    "⚠ RESTOCK": "🔴 RESTOCK",
    "✓ CUKUP": "🟢 CUKUP"
})

# Manage session state for displaying results
if "show_result" not in st.session_state:
    st.session_state.show_result = False

def hide_result():
    st.session_state.show_result = False

st.markdown("---")

# ==========================================
# 1. KALKULATOR KEPUTUSAN RESTOCK
# ==========================================
st.markdown("### 🧮 Kalkulator Keputusan Restock per Produk")
st.markdown("Ikuti alur di bawah ini untuk melihat bagaimana sistem merespons perubahan kondisi stok secara dinamis.")

with st.container(border=True):
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        product_list = simulation["Barang Nama"].tolist()
        selected_product_name = st.selectbox(
            "1. Pilih Produk:", 
            options=product_list,
            on_change=hide_result
        )
        
        product_data = simulation[simulation["Barang Nama"] == selected_product_name].iloc[0]

    with sim_col2:
        stok_simulasi = st.number_input(
            "2. Masukkan Stok Aktual saat ini:", 
            min_value=0.0, 
            value=float(product_data["Stok_Aktual"]), 
            step=1.0,
            key=f"stok_{selected_product_name}",
            on_change=hide_result
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Proses Rekomendasi", type="primary", use_container_width=True):
        st.session_state.show_result = True


# Display Results if button was pressed
if st.session_state.show_result:
    rop = product_data["ROP"]
    if stok_simulasi <= rop:
        status_sim = "🔴 RESTOCK"
        qty_sim = round(max(0, rop - stok_simulasi), 2)
    else:
        status_sim = "🟢 CUKUP"
        qty_sim = 0.0

    st.markdown("---")
    
    col_res1, col_res2 = st.columns([1.5, 1])
    
    with col_res1:
        with st.container(border=True):
            st.markdown("#### 📊 HASIL ANALISIS")
            st.markdown("<br>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            c1.metric("Kategori", product_data["Kategori"])
            c2.metric("Average Daily Usage", f"{product_data['ADU']:.2f} unit/hari")
            
            st.markdown("<br>", unsafe_allow_html=True)
            c3, c4, c5 = st.columns(3)
            c3.metric("Safety Stock", f"{product_data['Safety_Stock']:.2f} unit")
            c4.metric("Reorder Point", f"{rop:.2f} unit")
            c5.metric("Stok Aktual", f"{stok_simulasi:.2f} unit")

    with col_res2:
        with st.container(border=True):
            st.markdown("#### 🎯 KEPUTUSAN SISTEM")
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            if status_sim == "🔴 RESTOCK":
                st.error(f"### {status_sim}")
            else:
                st.success(f"### {status_sim}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(f"**Rekomendasi Pemesanan:** {qty_sim} unit")


st.markdown("---")

# ==========================================
# 2. TABEL REKOMENDASI KESELURUHAN
# ==========================================
with st.container(border=True):
    st.markdown("### 📋 Daftar Rekomendasi Keseluruhan")
    st.caption("Gunakan filter di bawah ini untuk mencari data rekomendasi secara kolektif.")

    col1, col2 = st.columns(2)
    with col1:
        kategori = st.selectbox(
            "Kategori Pergerakan Barang",
            options=["Semua", "Fast Moving", "Medium Moving", "Slow Moving"],
            on_change=hide_result
        )

    with col2:
        keyword = st.text_input(
            "Cari Nama Barang", 
            placeholder="Ketik nama produk (Contoh: Sabun)...",
            on_change=hide_result
        )

    show = simulation.copy()

    if kategori != "Semua":
        show = show[show["Kategori"] == kategori]

    if keyword:
        show = show[show["Barang Nama"].str.contains(keyword, case=False)]

    show["Priority"] = show["Status"].map({
        "🔴 RESTOCK": 0,
        "🟢 CUKUP": 1
    })
    show = show.sort_values(by=["Priority", "Stok_Aktual"], ascending=[True, True])
    show = show.drop(columns=["Priority", "Index"], errors="ignore")

    display_cols = ["Barang Nama", "Kategori", "Stok_Aktual", "ROP", "Qty_Order", "Status"]
    show_display = show[display_cols]

    st.dataframe(
        show_display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Barang Nama": st.column_config.TextColumn("Nama Produk"),
            "Kategori": st.column_config.TextColumn("Kategori"),
            "Stok_Aktual": st.column_config.NumberColumn("Stok Aktual", format="%d"),
            "ROP": st.column_config.NumberColumn("Reorder Point", format="%d"),
            "Qty_Order": st.column_config.NumberColumn("Qty Order", format="%d"),
            "Status": st.column_config.TextColumn("Status")
        }
    )

    st.caption(f"Menampilkan {len(show)} produk sesuai kriteria pencarian.")
