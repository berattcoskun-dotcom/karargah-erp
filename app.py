import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Karargah ERP v11.2", layout="wide")

# --- AÇIK TEMA TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E9ECEF; }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 8px; font-weight: bold; }
    .project-card { padding: 15px; border: 1px solid #E9ECEF; border-radius: 10px; margin-bottom: 10px; background-color: #FBFBFB; }
    </style>
    """, unsafe_allow_html=True)

# --- ANA HAFIZA (SESSION STATE) ---
if 'projeler' not in st.session_state:
    st.session_state.projeler = pd.DataFrame(columns=[
        "Proje Adı", "Konum", "İnşaat m2", "Daire Sayısı", "Başlangıç", "Durum", "FotoData"
    ])

# --- YAN PANEL HİYERARŞİSİ ---
st.sidebar.title("🛡️ KARARGAH v11.2")
ana_secim = st.sidebar.radio("ANA MENÜ", ["🏠 Proje Kayıt & Düzenle", "🛠️ Proje Operasyonları"])

if ana_secim == "🏠 Proje Kayıt & Düzenle":
    menu = "PROJE_YONETIM"
else:
    st.sidebar.markdown("---")
    menu = st.sidebar.selectbox("İŞLEM SEÇİN", ["💸 Finans & Giderler", "🏗️ Taşeron & Hakediş", "👷 Personel & Puantaj"])

# --- MODÜL: PROJE YÖNETİMİ ---
if menu == "PROJE_YONETIM":
    st.header("🏗️ Proje Yönetim Merkezi")
    
    tab_ekle, tab_duzenle = st.tabs(["➕ Yeni Proje Ekle", "✏️ Kayıtlı Projeyi Düzenle"])
    
    # --- YENİ KAYIT ---
    with tab_ekle:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            with st.form("yeni_proje_form", clear_on_submit=True):
                p_ad = st.text_input("Proje Adı")
                p_kon = st.text_input("Konum")
                # Küsüratlı rakam için step ve format ayarlandı
                p_m2 = st.number_input("İnşaat m2", min_value=0.0, step=0.01, format="%.2f")
                p_dr = st.number_input("Daire Sayısı", min_value=0)
                p_dur = st.selectbox("Durum", ["Planlama", "Temel", "Kaba İnşaat", "İnce İşler", "Tamamlandı"])
                p_foto = st.file_uploader("Proje Fotoğrafı", type=['jpg','png','jpeg'])
                
                if st.form_submit_button("Projeyi Veritabanına Ekle"):
                    if p_ad:
                        img_byte = None
                        if p_foto:
                            img_byte = p_foto.getvalue()
                        
                        yeni_satir = pd.DataFrame([[
                            p_ad, p_kon, p_m2, p_dr, datetime.now().date(), p_dur, img_byte
                        ]], columns=st.session_state.projeler.columns)
                        st.session_state.projeler = pd.concat([st.session_state.projeler, yeni_satir], ignore_index=True)
                        st.success("Yeni Proje Kaydedildi!")
                        st.rerun()
        
        with col2:
            st.subheader("📋 Mevcut Projeler Özet")
            if not st.session_state.projeler.empty:
                for idx, row in st.session_state.projeler.iterrows():
                    with st.container():
                        c_img, c_txt = st.columns([1, 2])
                        if row['FotoData']:
                            c_img.image(row['FotoData'], width=150)
                        else:
                            c_img.write("🖼️ Fotoğraf Yok")
                        c_txt.markdown(f"**{row['Proje Adı']}**")
                        c_txt.write(f"📍 {row['Konum']} | 📏 {row['İnşaat m2']} m2")
                        st.divider()

    # --- DÜZENLEME MODÜLÜ ---
    with tab_duzenle:
        if st.session_state.projeler.empty:
            st.info("Düzenlenecek proje bulunmuyor.")
        else:
            secilen_p_adi = st.selectbox("Düzenlemek istediğiniz projeyi seçin", st.session_state.projeler["Proje Adı"])
            idx = st.session_state.projeler[st.session_state.projeler["Proje Adı"] == secilen_p_adi].index[0]
            p_data = st.session_state.projeler.iloc[idx]
            
            with st.form("duzenle_form"):
                d_ad = st.text_input("Proje Adı", value=p_data["Proje Adı"])
                d_kon = st.text_input("Konum", value=p_data["Konum"])
                d_m2 = st.number_input("İnşaat m2", value=float(p_data["İnşaat m2"]), step=0.01, format="%.2f")
                d_dr = st.number_input("Daire Sayısı", value=int(p_data["Daire Sayısı"]))
                d_dur = st.selectbox("Durum", ["Planlama", "Temel", "Kaba İnşaat", "İnce İşler", "Tamamlandı"], 
                                     index=["Planlama", "Temel", "Kaba İnşaat", "İnce İşler", "Tamamlandı"].index(p_data["Durum"]))
                
                st.write("Not: Fotoğrafı değiştirmek için Yeni Ekle sekmesini kullanın veya mevcut kalsın.")
                
                if st.form_submit_button("Değişiklikleri Kaydet"):
                    st.session_state.projeler.at[idx, "Proje Adı"] = d_ad
                    st.session_state.projeler.at[idx, "Konum"] = d_kon
                    st.session_state.projeler.at[idx, "İnşaat m2"] = d_m2
                    st.session_state.projeler.at[idx, "Daire Sayısı"] = d_dr
                    st.session_state.projeler.at[idx, "Durum"] = d_dur
                    st.success("Proje Bilgileri Güncellendi!")
                    st.rerun()

# --- DİĞER MODÜLLER (HAZIRLIK) ---
elif menu == "💸 Finans & Giderler":
    st.header("💸 Finans Yönetimi")
    st.write("Proje bazlı gider kalemleri bir sonraki aşamada buraya eklenecektir.")

# --- ANA HAFIZA GÜNCELLEME (Session State kısmına ekleyin) ---
if 'gider_kategorileri' not in st.session_state:
    st.session_state.gider_kategorileri = ["Beton", "Demir", "İşçilik", "Akaryakıt", "Yemek", "Nalbur", "Diğer"]

if 'birimler' not in st.session_state:
    st.session_state.birimler = ["m2", "m3", "Ton", "Adet", "Sefer", "Gün", "Ay"]

if 'kasa_banka' not in st.session_state:
    st.session_state.kasa_banka = ["Merkez Kasa", "Banka Hesabı", "Şantiye Kasası"]

# --- YAN PANELDEKİ İŞLEM SEÇİN KISMINA EKLEME ---
# menu = st.sidebar.selectbox("İŞLEM SEÇİN", [..., "⚙️ Temel Ayarlar"])

# --- MODÜL: TEMEL AYARLAR (YENİ) ---
if menu == "⚙️ Temel Ayarlar":
    st.header("⚙️ Sistem Temel Ayarları")
    st.info("Bu bölümdeki tanımlamalar, finans ve puantaj modüllerinde seçenek olarak karşınıza çıkacaktır.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📁 Gider Kategorileri")
        yeni_kat = st.text_input("Yeni Kategori Ekle")
        if st.button("Kategoriyi Kaydet"):
            if yeni_kat and yeni_kat not in st.session_state.gider_kategorileri:
                st.session_state.gider_kategorileri.append(yeni_kat)
                st.success("Kategori Eklendi!")
        st.write(st.session_state.gider_kategorileri)

    with col2:
        st.subheader("📏 Birim Tanımları")
        yeni_birim = st.text_input("Yeni Birim Ekle")
        if st.button("Birimi Kaydet"):
            if yeni_birim and yeni_birim not in st.session_state.birimler:
                st.session_state.birimler.append(yeni_birim)
                st.success("Birim Eklendi!")
        st.write(st.session_state.birimler)

    with col3:
        st.subheader("🏦 Kasa / Banka")
        yeni_kasa = st.text_input("Yeni Kasa/Banka Ekle")
        if st.button("Kasayı Kaydet"):
            if yeni_kasa and yeni_kasa not in st.session_state.kasa_banka:
                st.session_state.kasa_banka.append(yeni_kasa)
                st.success("Kasa Eklendi!")
        st.write(st.session_state.kasa_banka)
