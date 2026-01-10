import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Karargah ERP v9.0", layout="wide")

# --- LÜKS TASARIM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stMetric { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; width: 100%; border: none; }
    .stButton>button:hover { background-color: #2ea043; border: 1px solid #ffffff; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #161b22; border-radius: 5px 5px 0 0; color: #8b949e; }
    </style>
    """, unsafe_allow_html=True)

# --- HAFIZA SİSTEMİ (SESSION STATE) ---
if 'projeler' not in st.session_state: st.session_state.projeler = pd.DataFrame(columns=["Proje Adı", "Konum", "Başlangıç", "Durum"])
if 'personel_listesi' not in st.session_state: st.session_state.personel_listesi = pd.DataFrame(columns=["Ad Soyad", "Görevi", "Bağlı Proje"])
if 'puantaj_verileri' not in st.session_state: st.session_state.puantaj_verileri = pd.DataFrame(columns=["Tarih", "Personel", "Yevmiye", "Proje"])
if 'taseron_listesi' not in st.session_state: st.session_state.taseron_listesi = pd.DataFrame(columns=["Firma Adı", "İş Kolu", "Sözleşme Tutarı", "Kalan", "Bağlı Proje"])
if 'taseron_odemeleri' not in st.session_state: st.session_state.taseron_odemeleri = pd.DataFrame(columns=["Tarih", "Firma", "Tutar", "Durum", "Vade Tarihi", "Proje"])
if 'masraf_verileri' not in st.session_state: st.session_state.masraf_verileri = pd.DataFrame(columns=["Tarih", "Kategori", "Tutar", "Proje", "Açıklama"])
if 'teklif_listesi' not in st.session_state: st.session_state.teklif_listesi = pd.DataFrame(columns=["Tarih", "Proje Adı", "Müşteri", "Teklif Tutarı", "Durum"])

# --- YAN PANEL ---
st.sidebar.title("🛡️ KARARGAH v9.0")
menu = st.sidebar.selectbox("KOMUTA MERKEZİ", 
    ["🏗️ Proje Yönetimi", "📊 Proje Dashboard", "📄 Teklif & Satış", "🏗️ Taşeron & Hakediş", "👷 Personel & Puantaj", "💸 Finans & Giderler"])

# --- 1. PROJE YÖNETİMİ (ANA MODÜL) ---
if menu == "🏗️ Proje Yönetimi":
    st.header("🏗️ Ana Proje Kayıt ve Yönetimi")
    p1, p2 = st.tabs(["Yeni Proje Aç", "Mevcut Projeler"])
    
    with p1:
        with st.form("proje_ekle"):
            p_ad = st.text_input("Proje Adı (Örn: Karargah Rezidans)")
            p_konum = st.text_input("Konum / Şehir")
            p_basla = st.date_input("Başlangıç Tarihi")
            p_durum = st.selectbox("Durum", ["Planlama", "Devam Ediyor", "Tamamlandı", "Durduruldu"])
            if st.form_submit_button("Projeyi Başlat"):
                yeni_p = pd.DataFrame([[p_ad, p_konum, p_basla, p_durum]], columns=st.session_state.projeler.columns)
                st.session_state.projeler = pd.concat([st.session_state.projeler, yeni_p], ignore_index=True)
                st.success(f"{p_ad} projesi başarıyla açıldı!")

    with p2:
        st.dataframe(st.session_state.projeler, use_container_width=True)
        if not st.session_state.projeler.empty:
            sil_p = st.selectbox("Kapatılacak Proje", st.session_state.projeler["Proje Adı"])
            if st.button("🚨 Seçili Projeyi Arşivle/Sil"):
                st.session_state.projeler = st.session_state.projeler[st.session_state.projeler["Proje Adı"] != sil_p]
                st.rerun()

# --- 2. PROJE DASHBOARD (PROFESYONEL FİLTRELEME) ---
elif menu == "📊 Proje Dashboard":
    st.header("📊 Stratejik Proje Analizi")
    if not st.session_state.projeler.empty:
        secilen_p = st.selectbox("Analiz Edilecek Projeyi Seçin", st.session_state.projeler["Proje Adı"])
        
        # Filtreleme İşlemleri
        p_masraf = st.session_state.masraf_verileri[st.session_state.masraf_verileri["Proje"] == secilen_p]
        p_taseron = st.session_state.taseron_listesi[st.session_state.taseron_listesi["Bağlı Proje"] == secilen_p]
        p_isci = st.session_state.puantaj_verileri[st.session_state.puantaj_verileri["Proje"] == secilen_p]
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Gider", f"{p_masraf['Tutar'].sum():,.2f} TL")
        c2.metric("Aktif Taşeron", len(p_taseron))
        c3.metric("İşçilik Maliyeti", f"{p_isci['Yevmiye'].sum():,.2f} TL")
        
        st.subheader("Proje Gider Dağılımı")
        if not p_masraf.empty:
            st.bar_chart(p_masraf.groupby("Kategori")["Tutar"].sum())
    else:
        st.warning("Henüz aktif bir proje bulunmuyor.")

# --- 3. TAŞERON & HAKEDİŞ (PROJE BAĞLANTILI) ---
elif menu == "🏗️ Taşeron & Hakediş":
    st.header("🏗️ Proje Bazlı Taşeron Yönetimi")
    t1, t2 = st.tabs(["Taşeron Kaydı", "Hakediş Ödemeleri"])
    
    with t1:
        if not st.session_state.projeler.empty:
            with st.form("t_form"):
                f_ad = st.text_input("Taşeron Firma")
                f_proje = st.selectbox("Bağlı Olduğu Proje", st.session_state.projeler["Proje Adı"])
                f_is = st.text_input("Yaptığı İş")
                f_tut = st.number_input("Sözleşme Bedeli", min_value=0.0)
                if st.form_submit_button("Taşeronu Kaydet"):
                    yeni_t = pd.DataFrame([[f_ad, f_is, f_tut, f_tut, f_proje]], columns=st.session_state.taseron_listesi.columns)
                    st.session_state.taseron_listesi = pd.concat([st.session_state.taseron_listesi, yeni_t], ignore_index=True)
            st.dataframe(st.session_state.taseron_listesi)
        else: st.error("Önce Proje Yönetimi kısmından bir proje açmalısınız!")

# --- 4. PERSONEL & PUANTAJ (PROJE BAĞLANTILI) ---
elif menu == "👷 Personel & Puantaj":
    st.header("👷 Şantiye Personel Dağılımı")
    per1, per2 = st.tabs(["Personel Ekle", "Günlük Puantaj"])
    
    with per1:
        with st.form("p_ek"):
            p_ad = st.text_input("Ad Soyad")
            p_pro = st.selectbox("Görev Yeri (Proje)", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Proje Yok"])
            p_gor = st.text_input("Görevi (Örn: Forman)")
            if st.form_submit_button("Personeli Kaydet"):
                yeni_p = pd.DataFrame([[p_ad, p_gor, p_pro]], columns=st.session_state.personel_listesi.columns)
                st.session_state.personel_listesi = pd.concat([st.session_state.personel_listesi, yeni_p], ignore_index=True)

    with per2:
        if not st.session_state.personel_listesi.empty:
            with st.form("puan_form"):
                p_sec = st.selectbox("Personel Seç", st.session_state.personel_listesi["Ad Soyad"])
                # Personelin projesini otomatik getir
                p_proje = st.session_state.personel_listesi[st.session_state.personel_listesi["Ad Soyad"] == p_sec]["Bağlı Proje"].values[0]
                p_yev = st.number_input(f"Yevmiye ({p_proje} projesi için)", min_value=0)
                if st.form_submit_button("Puantajı İşle"):
                    yeni_pu = pd.DataFrame([[datetime.now().date(), p_sec, p_yev, p_proje]], columns=st.session_state.puantaj_verileri.columns)
                    st.session_state.puantaj_verileri = pd.concat([st.session_state.puantaj_verileri, yeni_pu], ignore_index=True)
            st.dataframe(st.session_state.puantaj_verileri)

# --- 5. FİNANS (PROJE BAZLI GİDERLER) ---
elif menu == "💸 Finans & Giderler":
    st.header("💸 Şantiye Gider Takibi")
    with st.form("gider_form"):
        col1, col2 = st.columns(2)
        with col1:
            g_tar = st.date_input("Gider Tarihi")
            g_pro = st.selectbox("İlgili Proje", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Proje Yok"])
        with col2:
            g_kat = st.selectbox("Kategori", ["Demir", "Beton", "Akaryakıt", "Yemek", "Ofis", "Diğer"])
            g_tut = st.number_input("Tutar (TL)", min_value=0.0)
        
        if st.form_submit_button("Gideri Kaydet"):
            yeni_g = pd.DataFrame([[g_tar, g_kat, g_tut, g_pro, ""]], columns=st.session_state.masraf_verileri.columns)
            st.session_state.masraf_verileri = pd.concat([st.session_state.masraf_verileri, yeni_g], ignore_index=True)
    
    st.subheader("Son Harcamalar")
    st.dataframe(st.session_state.masraf_verileri.tail(10))



