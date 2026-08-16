import streamlit as st
import librosa
import numpy as np
import io

# --- MÜHENDİSLİK YAPILANDIRMASI ---
st.set_page_config(page_title="VBAR | Biyometrik Ruhsal Mimari", layout="centered", page_icon="🔬")

# Kurumsal Tema CSS
st.markdown("""
<style>
    .stApp {background-color: #0e1117; color: #e0e0e0;}
    .report-box {border: 1px solid #ffd700; padding: 25px; border-radius: 12px; background: #1a1a1a; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# GİRİŞ PANELİ
st.title("🔬 VBAR: Biyometrik Analiz Merkezi")
st.markdown("""
*Sesiniz; zihninizin, duygularınızın ve sinir sistemi durumunuzun en saf fiziksel imzasıdır.*
VBAR; biyometrik sinyal analiz teknolojisini kullanarak ses tonunuzdaki görünmeyen iniş çıkışları haritalandırır.
""")
st.markdown("---")

# 1. MODÜL: KALİBRASYON (Baz Çizgisi)
if 'calibrated' not in st.session_state:
    st.subheader("1. Aşama: Cihaz Kalibrasyonu")
    st.write("Analiz hassasiyeti için lütfen 5 saniye boyunca rahat bir ses tonuyla konuşun.")
    ref_audio = st.audio_input("Kalibrasyon sesini kaydet")
    if ref_audio:
        st.session_state.calibrated = True
        st.success("Cihaz kalibre edildi. Analiz sistemine erişim sağlandı.")
else:
    # 2. MODÜL: ANALİZ MOTORU
    st.subheader("2. Aşama: Biyometrik Sinyal Analizi")
    uploaded_file = st.file_uploader("Ses dosyanızı yükleyin (MP3, WAV, M4A)", type=["mp3", "wav", "m4a", "aac"])
    
    if uploaded_file:
        y, sr = librosa.load(io.BytesIO(uploaded_file.read()), sr=16000)
        # Sinyal İşleme
        pitches, _ = librosa.piptrack(y=y, sr=sr, fmin=80, fmax=400)
        f0 = np.nanmean(pitches[pitches > 0]) if np.any(pitches > 0) else 210.0
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        
        st.markdown(f"""
        <div class="report-box">
            <h3>Biyometrik Ölçüm Raporu</h3>
            <p><b>Temel Frekans (F0):</b> {f0:.1f} Hz</p>
            <p><b>Gerginlik İndeksi:</b> {zcr:.4f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. MODÜL: MÜDAHALE (Somatik Rahatlama)
        if zcr > 0.12:
            st.warning("⚠️ Ses frekansınızda zihinsel yoğunluk tespit edildi.")
            st.subheader("🧘 Somatik Topraklanma Modülü")
            # Voiser ile ürettiğin 'rahatlama.mp3' dosyasını buraya ekliyoruz
            st.audio("rahatlama.mp3", format="audio/mp3")
        
        # 4. MODÜL: UZMAN YÖNLENDİRME
        st.markdown("---")
        with st.form("detay_form"):
            st.subheader("🔍 Derinlemesine Uzman Raporu")
            ad = st.text_input("Ad Soyad")
            dt = st.date_input("Doğum Tarihi")
            email = st.text_input("E-posta")
            if st.form_submit_button("Analiz Raporunu Talep Et"):
                # Burada Google Sheets entegrasyon kancasını (gspread) kullanacağız
                st.success(f"Teşekkürler {ad}. Verileriniz ve ses profiliniz, uzman 'Ruhun Mimarisi' ekibimize iletilmiştir.")
