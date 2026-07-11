import streamlit as st

# Configure the pages
dashboard_page = st.Page(
    "pages/Dashboard.py",
    title="Dashboard",
    icon="📊",
    default=True
)

rekomendasi_page = st.Page(
    "pages/Rekomendasi_Restock.py",
    title="Rekomendasi Restock",
    icon="🛒"
)

# Setup navigation
pg = st.navigation([dashboard_page, rekomendasi_page])

# Run the selected page
pg.run()
