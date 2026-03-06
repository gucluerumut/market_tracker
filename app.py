import streamlit as st

st.set_page_config(page_title="Piyasa Takipçisi", layout="centered")

st.markdown("""
    <style>
    .main {
        display: flex;
        justify_content: center;
        align-items: center;
        height: 100vh;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.header("🛑 Sistem Kapalı / System Offline")
st.write("Uygulama şu anda bakımda veya kapalıdır.")
st.write("Application is currently under maintenance or offline.")
