import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import io

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Karargah ERP v8.0", layout="wide")

# --- HAFIZA SİSTEMİ (SESSION STATE) ---
if 'personel_listesi' not in st.session_state: st.session_state.personel_listesi = ["Seçiniz"]
if 'puantaj_verileri' not in st.session_state: st.session_state.puantaj_verileri = pd.DataFrame(columns=["Tarih", "Personel", "Yevmiye"])
if 'taseron_listesi' not in st.session_state: st.session_state.taseron_listesi = pd.DataFrame(columns=["Firma Adı", "İş Kolu", "Sözleşme Tutarı", "Kalan"])
if 'taseron_hakedis' not in st.session_state: st.session_state.taseron_hakedis = pd.DataFrame(columns=["Tarih", "Firma", "Ödenen Hakediş"])
if 'musteri_listesi' not in st.session_state: st.session_state.musteri_listesi = pd.DataFrame(columns=["Ad Soyad", "Şirket", "Telefon", "E-Mail", "Notlar"])
if 'masraf_kategorileri' not in st.session_state: st.session_state.masraf_kategorileri = ["Akaryakıt", "Yemek", "Demir", "Beton"]
if 'masraf_verileri' not in st.session_state: st.session_state.masraf_verileri = pd.DataFrame(columns=["Tarih", "Kategori", "Tutar", "Açıklama"])
if 'odeme_planlari' not in st.session_state: st.session_state.odeme_planlari = pd.DataFrame(columns=["Müşteri", "Toplam Tutar", "Taksit Sayısı", "Ödenen", "Kalan"])
if 'gunluk_defter' not in st.session_state: st.session_state.gunluk_defter = pd.DataFrame(columns=["Tarih", "Hava Durumu", "Yapılan İşler", "Notlar"])
if 'teklif_listesi' not in st.session_state: st.session_state.teklif_listesi = pd.DataFrame(columns=["Tarih", "Proje Adı", "Müşteri", "Teklif Tutarı", "Durum"])
if 'kurumsal_bilgiler' not in st.session_state:
    st.session_state.kurumsal_bilgiler = {"sirket_adi": "KOMUTANIM İNŞAAT", "adres": "Türkiye", "tel": "+90", "v_no": "12345"}

# --- PDF FONKSİYONU ---
def pdf_uret(teklif_verisi, kurumsal):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=kurumsal["sirket_adi"], ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(200, 10, txt=f"Adres: {kurumsal['adres']} | Tel: {kurumsal['tel']}", ln=True, align="C")
    pdf.line(10, 35, 200, 35)
    pdf.ln(15)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="RESMI TEKLIF BELGESI", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Tarih: {teklif_verisi['Tarih']} | Musteri: {teklif_verisi['Müşteri']}", ln=True)
    pdf.cell(200, 10, txt=f"Proje: {teklif_verisi['Proje Adı']}", ln=True)
    pdf.cell(200, 10, txt=f"Tutar: {teklif_verisi['Teklif Tutarı']:,.2f} TL", ln=True)
    return pdf.output(dest='S').encode('latin-1')

st.title("🏗️ Şantiye Karargah Pro v8.0")

# --- YAN PANEL ---
menu = st.sidebar.selectbox("ANA OPERASYON MERKEZİ", 
    ["📊 Dashboard", "📄 Teklif & PDF", "🏗️ Taşeron & Hakediş", "🤝 Müşteri & Ödeme Planı", "📑 Günlük Defter", "👷 Personel & Puantaj", "💸 Finans & Kategori", "📐 Metraj Hesabı"])

# --- 1. TEKLİF & PDF ---
if menu == "📄 Teklif & PDF":
    st.header("📄 Teklif Yönetimi ve Kurumsal Çıktı")
    t1, t2, t3 = st.tabs(["Yeni Teklif", "Teklif Listesi & PDF", "🏢 Kurumsal Ayarlar"])
    
    with t3:
        st.session_state.kurumsal_bilgiler["sirket_adi"] = st.text_input("Şirket Adı", st.session_state.kurumsal_bilgiler["sirket_adi"])
        st.session_state.kurumsal_bilgiler["adres"] = st.text_area("Adres", st.session_state.kurumsal_bilgiler["adres"])
        st.session_state.kurumsal_bilgiler["tel"] = st.text_input("Telefon", st.session_state.kurumsal_bilgiler["tel"])

    with t1:
        with st.form("tkf_form"):
            t_tar = st.date_input("Tarih", datetime.now())
            t_prj = st.text_input("Proje Adı")
            t_mus = st.selectbox("Müşteri", st.session_state.musteri_listesi["Ad Soyad"] if not st.session_state.musteri_listesi.empty else ["Müşteri Yok"])
            t_tut = st.number_input("Tutar (TL)", min_value=0.0)
            if st.form_submit_button("Teklifi Kaydet"):
                yeni = pd.DataFrame([[t_tar, t_prj, t_mus, t_tut, "⏳ Beklemede"]], columns=st.session_state.teklif_listesi.columns)
                st.session_state.teklif_listesi = pd.concat([st.session_state.teklif_listesi, yeni], ignore_index=True)
                st.success("Teklif başarıyla eklendi.")

    with t2:
        if not st.session_state.teklif_listesi.empty:
            st.dataframe(st.session_state.teklif_listesi)
            secilen = st.selectbox("PDF İçin Teklif Seç", st.session_state.teklif_listesi.index)
            if st.button("PDF Hazırla"):
                pdf_data = pdf_uret(st.session_state.teklif_listesi.loc[secilen], st.session_state.kurumsal_bilgiler)
                st.download_button("📥 PDF İndir", pdf_data, f"Teklif_{secilen}.pdf", "application/pdf")

# --- 2. TAŞERON & HAKEDİŞ ---
elif menu == "🏗️ Taşeron & Hakediş":
    st.header("🏗️ Taşeron ve Sözleşme Takibi")
    tas1, tas2 = st.tabs(["Taşeron Ekle", "Hakediş Ödemesi"])
    with tas1:
        with st.form("tas_ek"):
            f_ad = st.text_input("Firma/Usta")
            f_is = st.text_input("İş Kolu")
            f_tut = st.number_input("Sözleşme Tutarı", min_value=0.0)
            if st.form_submit_button("Kaydet"):
                yeni = pd.DataFrame([[f_ad, f_is, f_tut, f_tut]], columns=st.session_state.taseron_listesi.columns)
                st.session_state.taseron_listesi = pd.concat([st.session_state.taseron_listesi, yeni], ignore_index=True)
    st.table(st.session_state.taseron_listesi)

# --- 3. MÜŞTERİ & ÖDEME PLANI ---
elif menu == "🤝 Müşteri & Ödeme Planı":
    st.header("🤝 Müşteri CRM ve Taksitlendirme")
    m1, m2 = st.tabs(["Müşteri Kaydı", "Ödeme Planı Oluştur"])
    with m1:
        with st.form("m_form"):
            m_ad = st.text_input("Ad Soyad")
            m_tel = st.text_input("Telefon")
            if st.form_submit_button("Müşteriyi Kaydet"):
                yeni = pd.DataFrame([[m_ad, "", m_tel, "", ""]], columns=st.session_state.musteri_listesi.columns)
                st.session_state.musteri_listesi = pd.concat([st.session_state.musteri_listesi, yeni], ignore_index=True)
    st.dataframe(st.session_state.musteri_listesi)

# --- 4. GÜNLÜK DEFTER ---
elif menu == "📑 Günlük Defter":
    st.header("📑 Şantiye Günlük Defteri")
    with st.form("defter"):
        d_tar = st.date_input("Tarih", datetime.now())
        d_is = st.text_area("Yapılan İşler")
        if st.form_submit_button("Deftere Yaz"):
            yeni = pd.DataFrame([[d_tar, "", d_is, ""]], columns=st.session_state.gunluk_defter.columns)
            st.session_state.gunluk_defter = pd.concat([st.session_state.gunluk_defter, yeni], ignore_index=True)
    st.dataframe(st.session_state.gunluk_defter)

# --- 5. PERSONEL & PUANTAJ ---
elif menu == "👷 Personel & Puantaj":
    st.header("👷 Personel Yönetimi")
    p1, p2 = st.tabs(["Personel Kayıt", "Puantaj İşle"])
    with p1:
        yeni_p = st.text_input("Personel İsmi")
        if st.button("Kaydet"):
            st.session_state.personel_listesi.append(yeni_p)
    with p2:
        p_sec = st.selectbox("Personel", st.session_state.personel_listesi)
        p_yev = st.number_input("Yevmiye", min_value=0)
        if st.button("Puantaja İşle"):
            yeni = pd.DataFrame([[datetime.now().date(), p_sec, p_yev]], columns=st.session_state.puantaj_verileri.columns)
            st.session_state.puantaj_verileri = pd.concat([st.session_state.puantaj_verileri, yeni], ignore_index=True)
    st.dataframe(st.session_state.puantaj_verileri)

# --- 6. FİNANS ---
elif menu == "💸 Finans & Kategori":
    st.header("💸 Masraf Takibi")
    kat_ek = st.text_input("Yeni Kategori")
    if st.button("Kategori Ekle"):
        st.session_state.masraf_kategorileri.append(kat_ek)
    with st.form("mas_form"):
        m_kat = st.selectbox("Kategori", st.session_state.masraf_kategorileri)
        m_tut = st.number_input("Tutar", min_value=0.0)
        if st.form_submit_button("Harcamayı Kaydet"):
            yeni = pd.DataFrame([[datetime.now().date(), m_kat, m_tut, ""]], columns=st.session_state.masraf_verileri.columns)
            st.session_state.masraf_verileri = pd.concat([st.session_state.masraf_verileri, yeni], ignore_index=True)
    st.dataframe(st.session_state.masraf_verileri)

# --- 7. DASHBOARD ---
elif menu == "📊 Dashboard":
    st.header("📈 Genel Analiz")
    c1, c2, c3 = st.columns(3)
    c1.metric("Toplam Masraf", f"{st.session_state.masraf_verileri['Tutar'].sum():,.2f}")
    c2.metric("Toplam Hakediş", f"{st.session_state.taseron_hakedis['Ödenen Hakediş'].sum():,.2f}")
    c3.metric("Bekleyen Teklif", len(st.session_state.teklif_listesi))
    if not st.session_state.masraf_verileri.empty:
        st.bar_chart(st.session_state.masraf_verileri.groupby("Kategori")["Tutar"].sum())

# --- 8. METRAJ ---
elif menu == "📐 Metraj Hesabı":
    st.header("📐 Metraj Tahmini")
    m_alan = st.number_input("Alan (m2)", value=1000)
    st.write(f"Tahmini Demir: {m_alan * 0.038:.2f} Ton")
    st.write(f"Tahmini Beton: {m_alan * 0.42:.2f} m3")

# --- LÜKS TASARIM CSS KODU (Bunu kodun en başına, title'dan hemen sonra ekleyin) ---
st.markdown("""
    <style>
    /* Ana Arka Plan */
    .stApp {
        background-color: #f4f7f6;
    }
    /* Sidebar (Yan Menü) Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #1e2d3b;
        color: white;
    }
    /* Butonları Güzelleştirme */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: 2px solid white;
    }
    /* Kart Yapısı (Metrics) */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #e1e4e8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GÜZELLEŞTİRİLMİŞ DASHBOARD ÖRNEĞİ ---
st.header("🏢 Şantiye Komuta Merkezi")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(label="📊 Aktif Teklifler", value="12 Adet", delta="3 Yeni")
with c2:
    st.metric(label="💰 Toplam Ciro", value="1.2M TL", delta="15%")
with c3:
    st.metric(label="👷 Sahadaki Ekip", value="24 Kişi")
with c4:
    st.metric(label="📉 Geciken İşler", value="2", delta="-1", delta_color="inverse")
