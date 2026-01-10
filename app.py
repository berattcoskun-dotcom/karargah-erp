import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Karargah ERP v10.0", layout="wide")

# --- PROFESYONEL AÇIK TEMA TASARIMI (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; color: #212529; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #E9ECEF; }
    .stMetric { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #DEE2E6; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { background-color: #007BFF; color: white; border-radius: 8px; width: 100%; font-weight: bold; border: none; height: 3em; }
    .stButton>button:hover { background-color: #0056B3; border: 1px solid #000; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #E9ECEF; border-radius: 5px; color: #495057; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #007BFF !important; color: white !important; }
    h1, h2, h3 { color: #343A40; }
    </style>
    """, unsafe_allow_html=True)

# --- HAFIZA SİSTEMİ (SESSION STATE) ---
state_keys = {
    'projeler': pd.DataFrame(columns=["Proje Adı", "Konum", "Başlangıç", "Durum"]),
    'personel_listesi': pd.DataFrame(columns=["Ad Soyad", "Görevi", "Bağlı Proje"]),
    'puantaj_verileri': pd.DataFrame(columns=["Tarih", "Personel", "Yevmiye", "Proje"]),
    'taseron_listesi': pd.DataFrame(columns=["Firma Adı", "İş Kolu", "Sözleşme Tutarı", "Kalan", "Bağlı Proje"]),
    'taseron_odemeleri': pd.DataFrame(columns=["Tarih", "Firma", "Tutar", "Durum", "Vade Tarihi", "Proje"]),
    'masraf_verileri': pd.DataFrame(columns=["Tarih", "Kategori", "Tutar", "Proje", "Açıklama"]),
    'teklif_listesi': pd.DataFrame(columns=["Tarih", "Proje Adı", "Müşteri", "Teklif Tutarı", "Durum"]),
    'malzeme_transferleri': pd.DataFrame(columns=["Tarih", "Kaynak Proje", "Hedef Proje", "Malzeme", "Miktar"]),
    'proje_asama': pd.DataFrame(columns=["Proje Adı", "İlerleme %", "Güncel Aşama"]),
    'kurumsal_bilgiler': {"sirket_adi": "KOMUTANIM İNŞAAT", "adres": "Türkiye", "tel": "+90", "v_no": "12345"}
}

for key, default in state_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- PDF FONKSİYONU ---
def pdf_uret(teklif_verisi, kurumsal):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=kurumsal["sirket_adi"], ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Musteri: {teklif_verisi['Müşteri']}", ln=True)
    pdf.cell(200, 10, txt=f"Proje: {teklif_verisi['Proje Adı']}", ln=True)
    pdf.cell(200, 10, txt=f"Tutar: {teklif_verisi['Teklif Tutarı']:,.2f} TL", ln=True)
    pdf.cell(200, 10, txt=f"Tarih: {teklif_verisi['Tarih']}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- YAN PANEL ---
st.sidebar.title("🛡️ KARARGAH v10.0")
menu = st.sidebar.selectbox("KOMUTA MERKEZİ", 
    ["🏗️ Proje Yönetimi", "📊 Proje Dashboard", "📄 Teklif & PDF", "🏗️ Taşeron & Hakediş", 
     "👷 Personel & Puantaj", "💸 Finans & Giderler", "🚚 Malzeme Transferi", "🏠 Müşteri Paneli"])

# --- 1. PROJE YÖNETİMİ ---
if menu == "🏗️ Proje Yönetimi":
    st.header("🏗️ Proje Kayıt ve Yönetimi")
    t1, t2 = st.tabs(["Yeni Proje Aç", "Projeleri Düzenle"])
    with t1:
        with st.form("p_ekle"):
            p_ad = st.text_input("Proje Adı")
            p_kon = st.text_input("Konum")
            p_dur = st.selectbox("Durum", ["Devam Ediyor", "Planlama", "Tamamlandı"])
            if st.form_submit_button("Projeyi Kaydet"):
                yeni = pd.DataFrame([[p_ad, p_kon, datetime.now().date(), p_dur]], columns=st.session_state.projeler.columns)
                st.session_state.projeler = pd.concat([st.session_state.projeler, yeni], ignore_index=True)
                st.success("Proje eklendi.")
    with t2:
        st.dataframe(st.session_state.projeler, use_container_width=True)
        if not st.session_state.projeler.empty:
            sil_p = st.selectbox("Silinecek Proje", st.session_state.projeler["Proje Adı"])
            if st.button("🚨 Projeyi Sil"):
                st.session_state.projeler = st.session_state.projeler[st.session_state.projeler["Proje Adı"] != sil_p]
                st.rerun()

# --- 2. DASHBOARD ---
elif menu == "📊 Proje Dashboard":
    st.header("📊 Proje Analiz Merkezi")
    if not st.session_state.projeler.empty:
        p_sec = st.selectbox("Analiz Edilecek Proje", st.session_state.projeler["Proje Adı"])
        c1, c2, c3 = st.columns(3)
        p_masraf = st.session_state.masraf_verileri[st.session_state.masraf_verileri["Proje"] == p_sec]
        p_puan = st.session_state.puantaj_verileri[st.session_state.puantaj_verileri["Proje"] == p_sec]
        c1.metric("Toplam Harcama", f"{p_masraf['Tutar'].sum():,.2f} TL")
        c2.metric("İşçilik Maliyeti", f"{p_puan['Yevmiye'].sum():,.2f} TL")
        c3.metric("Kayıtlı Taşeron", len(st.session_state.taseron_listesi[st.session_state.taseron_listesi["Bağlı Proje"] == p_sec]))
        if not p_masraf.empty:
            st.bar_chart(p_masraf.groupby("Kategori")["Tutar"].sum())
    else: st.info("Henüz proje yok.")

# --- 3. TEKLİF ---
elif menu == "📄 Teklif & PDF":
    st.header("📄 Teklif ve Kurumsal Ayarlar")
    t1, t2 = st.tabs(["Teklif Oluştur", "Kurumsal Bilgiler"])
    with t2:
        st.session_state.kurumsal_bilgiler["sirket_adi"] = st.text_input("Şirket Adı", st.session_state.kurumsal_bilgiler["sirket_adi"])
    with t1:
        with st.form("tkf"):
            prj = st.selectbox("Proje", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Yok"])
            mus = st.text_input("Müşteri Adı")
            tut = st.number_input("Tutar", min_value=0.0)
            if st.form_submit_button("Kaydet"):
                yeni = pd.DataFrame([[datetime.now().date(), prj, mus, tut, "Beklemede"]], columns=st.session_state.teklif_listesi.columns)
                st.session_state.teklif_listesi = pd.concat([st.session_state.teklif_listesi, yeni], ignore_index=True)
        st.dataframe(st.session_state.teklif_listesi)

# --- 4. TAŞERON ---
elif menu == "🏗️ Taşeron & Hakediş":
    st.header("🏗️ Taşeron Yönetimi")
    t1, t2, t3 = st.tabs(["Taşeron Ekle/Sil", "Hakediş Planla", "Takvim"])
    with t1:
        colA, colB = st.columns(2)
        with colA:
            with st.form("ts_ek"):
                f_ad = st.text_input("Firma")
                f_pro = st.selectbox("Proje", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Yok"])
                f_tut = st.number_input("Sözleşme Tutarı")
                if st.form_submit_button("Ekle"):
                    yeni = pd.DataFrame([[f_ad, "", f_tut, f_tut, f_pro]], columns=st.session_state.taseron_listesi.columns)
                    st.session_state.taseron_listesi = pd.concat([st.session_state.taseron_listesi, yeni], ignore_index=True)
        with colB:
            if not st.session_state.taseron_listesi.empty:
                sil_f = st.selectbox("Sil", st.session_state.taseron_listesi["Firma Adı"])
                if st.button("🚨 Taşeronu Sil"):
                    st.session_state.taseron_listesi = st.session_state.taseron_listesi[st.session_state.taseron_listesi["Firma Adı"] != sil_f]
                    st.rerun()

# --- 5. PERSONEL ---
elif menu == "👷 Personel & Puantaj":
    st.header("👷 Personel Takibi")
    p1, p2 = st.tabs(["Personel Kayıt", "Puantaj Gir"])
    with p1:
        with st.form("per_ek"):
            p_ad = st.text_input("Ad Soyad")
            p_pr = st.selectbox("Proje", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Yok"])
            if st.form_submit_button("Kaydet"):
                yeni = pd.DataFrame([[p_ad, "", p_pr]], columns=st.session_state.personel_listesi.columns)
                st.session_state.personel_listesi = pd.concat([st.session_state.personel_listesi, yeni], ignore_index=True)
    with p2:
        if not st.session_state.personel_listesi.empty:
            p_sec = st.selectbox("Personel", st.session_state.personel_listesi["Ad Soyad"])
            yev = st.number_input("Yevmiye")
            if st.button("Puantaj İşle"):
                pro = st.session_state.personel_listesi[st.session_state.personel_listesi["Ad Soyad"] == p_sec]["Bağlı Proje"].values[0]
                yeni = pd.DataFrame([[datetime.now().date(), p_sec, yev, pro]], columns=st.session_state.puantaj_verileri.columns)
                st.session_state.puantaj_verileri = pd.concat([st.session_state.puantaj_verileri, yeni], ignore_index=True)

# --- 6. FİNANS ---
elif menu == "💸 Finans & Giderler":
    st.header("💸 Gider Takibi")
    with st.form("fin"):
        g_pr = st.selectbox("Proje", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Yok"])
        g_kt = st.selectbox("Kategori", ["Demir", "Beton", "Akaryakit", "Yemek", "Diger"])
        g_tt = st.number_input("Tutar")
        if st.form_submit_button("Harcamayı İşle"):
            yeni = pd.DataFrame([[datetime.now().date(), g_kt, g_tt, g_pr, ""]], columns=st.session_state.masraf_verileri.columns)
            st.session_state.masraf_verileri = pd.concat([st.session_state.masraf_verileri, yeni], ignore_index=True)
    st.dataframe(st.session_state.masraf_verileri)

# --- 7. TRANSFER ---
elif menu == "🚚 Malzeme Transferi":
    st.header("🚚 Projeler Arası Transfer")
    if len(st.session_state.projeler) > 1:
        with st.form("tr"):
            k = st.selectbox("Kaynak", st.session_state.projeler["Proje Adı"])
            h = st.selectbox("Hedef", st.session_state.projeler[st.session_state.projeler["Proje Adı"] != k]["Proje Adı"])
            m = st.text_input("Malzeme")
            q = st.number_input("Miktar")
            if st.form_submit_button("Transfer Et"):
                yeni = pd.DataFrame([[datetime.now().date(), k, h, m, q]], columns=st.session_state.malzeme_transferleri.columns)
                st.session_state.malzeme_transferleri = pd.concat([st.session_state.malzeme_transferleri, yeni], ignore_index=True)
        st.dataframe(st.session_state.malzeme_transferleri)

# --- 8. MÜŞTERİ PANELİ ---
elif menu == "🏠 Müşteri Paneli":
    st.header("🏠 Proje İlerleme Durumu")
    m1, m2 = st.tabs(["Yönetici Güncelleme", "Müşteri İzleme"])
    with m1:
        with st.form("isl"):
            p = st.selectbox("Proje", st.session_state.projeler["Proje Adı"] if not st.session_state.projeler.empty else ["Yok"])
            yz = st.slider("İlerleme %", 0, 100)
            if st.form_submit_button("Güncelle"):
                st.session_state.proje_asama = st.session_state.proje_asama[st.session_state.proje_asama["Proje Adı"] != p]
                yeni = pd.DataFrame([[p, yz, ""]], columns=st.session_state.proje_asama.columns)
                st.session_state.proje_asama = pd.concat([st.session_state.proje_asama, yeni], ignore_index=True)
    with m2:
        for i, r in st.session_state.proje_asama.iterrows():
            st.write(f"**{r['Proje Adı']}**")
            st.progress(r['İlerleme %'] / 100)
