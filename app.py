import streamlit as st
import pandas as pd
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Karargah ERP v11", layout="wide")

# --- AÇIK TEMA TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E9ECEF; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA HAFIZA (SESSION STATE) ---
# Sütun sayısını güncelledik (7 Sütun)
if 'projeler' not in st.session_state:
    st.session_state.projeler = pd.DataFrame(columns=[
        "Proje Adı", "Konum", "İnşaat m2", "Daire Sayısı", "Başlangıç", "Durum", "Fotoğraf"
    ])

# --- YAN PANEL (SIDEBAR) HİYERARŞİSİ ---
st.sidebar.title("🛡️ KARARGAH v11")
ana_secim = st.sidebar.radio("ANA MENÜ", ["🏠 Proje Kayıt Merkezi", "🛠️ Proje Operasyonları"])

if ana_secim == "🏠 Proje Kayıt Merkezi":
    menu = "PROJE_KAYIT"
else:
    st.sidebar.markdown("---")
    menu = st.sidebar.selectbox("İŞLEM SEÇİN", 
        ["💸 Finans & Giderler", "🏗️ Taşeron & Hakediş", "👷 Personel & Puantaj", "🚚 Malzeme Transferi", "🏠 Müşteri Paneli"])

# --- MODÜL 1: PROJE KAYIT (GÜNCELLENMİŞ) ---
if menu == "PROJE_KAYIT":
    st.header("🏗️ Proje Kayıt ve Teknik Künye")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Yeni Proje Girişi")
        with st.form("proje_form", clear_on_submit=True):
            p_ad = st.text_input("Proje Adı")
            p_kon = st.text_input("Konum")
            c_m2, c_dr = st.columns(2)
            p_m2 = c_m2.number_input("İnşaat m2", min_value=0)
            p_dr = c_dr.number_input("Daire Sayısı", min_value=0)
            p_dur = st.selectbox("Durum", ["Planlama", "Temel", "Kaba İnşaat", "İnce İşler", "Tamamlandı"])
            p_foto = st.file_uploader("Proje Fotoğrafı", type=['jpg','png'])
            
            if st.form_submit_button("Projeyi Veritabanına Ekle"):
                if p_ad:
                    yeni_satir = pd.DataFrame([[
                        p_ad, p_kon, p_m2, p_dr, datetime.now().date(), p_dur, (p_foto.name if p_foto else "Yok")
                    ]], columns=st.session_state.projeler.columns)
                    st.session_state.projeler = pd.concat([st.session_state.projeler, yeni_satir], ignore_index=True)
                    st.success("Kayıt Başarılı!")
                    st.rerun()
                else:
                    st.error("Lütfen Proje Adı girin!")

    with col2:
        st.subheader("📋 Kayıtlı Projeler")
        st.dataframe(st.session_state.projeler, use_container_width=True)

# --- MODÜL 2: FİNANS (HAZIRLIK) ---
elif menu == "💸 Finans & Giderler":
    st.header("💸 Finans Yönetimi")
    if st.session_state.projeler.empty:
        st.warning("Önce 'Proje Kayıt Merkezi'nden bir proje oluşturmalısınız!")
    else:
        st.success("Finans modülü aktif edilmeye hazır. Komutanım, harcama kalemlerini kodlayalım mı?")
