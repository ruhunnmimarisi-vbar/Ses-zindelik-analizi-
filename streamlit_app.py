import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
import ephem
from datetime import datetime

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Biyometrik & Kozmik Analiz", layout="centered", page_icon="🏛️")

st.markdown("""
<style>
    .stApp { background-color: #fcfbfa; color: #2c2c2c; }
    .report-card { border: 1px solid #d4af37; padding: 20px; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 15px; }
    .title-box { text-align: center; color: #1b263b; border-bottom: 2px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .astro-box { background: #fdf6e3; border-left: 4px solid #d4af37; padding: 15px; border-radius: 8px; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-box'><h1>🏛️ Ruhun Mimarisi | VBAR</h1><p>Ses Frekansı ve Ephem Tabanlı Kozmik Harmanlama</p></div>", unsafe_allow_html=True)

# SEKME YAPISI
tab1, tab2 = st.tabs(["🔬 Biyometrik & Kozmik Analiz", "📖 Hakkında"])

with tab2:
    st.subheader("Ruhun Mimarisi ve Ephem Altyapısı Hakkında")
    st.write("""
    **VBAR**, sesinizdeki mikro akustik değişimler ile **ephem** kütüphanesi aracılığıyla gökyüzünün o anki matematiksel konumlarını harmanlayan profesyonel bir farkındalık aracıdır.
    """)

with tab1:
    st.subheader("Ses Kaydı ve Doğum Bilgileri")
    
    upload_option = st.radio("Veri Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle"])
    audio_bytes = None

    if upload_option == "Mikrofon ile Kayıt Yap":
        audio_file = st.audio_input("Lütfen konuşun")
        if audio_file:
            audio_bytes = audio_file.read()
    else:
        uploaded_file = st.file_uploader("Ses dosyanızı seçin", type=["mp3", "wav", "m4a"])
        if uploaded_file:
            audio_bytes = uploaded_file.read()

    st.markdown("---")
    st.markdown("#### 🌌 Doğum Bilgileri (Kozmik Konum İçin)")
    col_g, col_a, col_y = st.columns(3)
    with col_g:
        dogum_gun = st.selectbox("Gün", list(range(1, 32)), index=28) # 29
    with col_a:
        dogum_ay = st.selectbox("Ay", list(range(1, 13)), index=11) # Aralık (12)
    with col_y:
        dogum_yil = st.selectbox("Yıl", list(range(1940, 2016)), index=44) # 1984

    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        
        if st.button("✨ Ephem Destekli Akustik-Kozmik Analizi Başlat"):
            with st.spinner("Ses dalgaları taranıyor ve ephem göksel konumları hesaplanıyor..."):
                try:
                    # 1. Ses Analizi (Librosa)
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    
                    rms_val = np.mean(librosa.feature.rms(y=y_denoised))
                    gerilim = float((rms_val * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                    # 2. Ephem ile Gerçek Göksel / Burç Hesaplaması
                    tarih_str = f"{doguv_yil_safe if 'doguv_yil_safe' in locals() else dogum_yil}/{dogum_ay}/{dogum_gun}"
                    # Ephem formatına uygun tarih stringi
                    ephem_tarih = f"{dogum_yil}/{dogum_ay}/{dogum_gun}"
                    sun = ephem.Sun(ephem_tarih)
                    constellation = ephem.constellation(sun)
                    burc = constellation[1] # Gökyüzündeki takımyıldız adı

                    st.markdown(f"""
                    <div class="report-card">
                        <h3 style="color: #1b263b; margin-top: 0;">🔬 Akustik Biyometrik Rapor</h3>
                        <p><b>Temel Frekans (F0):</b> {anlik_f0:.1f} Hz</p>
                        <p><b>Gerilim / Enerji İndeksi:</b> {gerilim:.2f}</p>
                    </div>
                    
                    <div class="astro-box">
                        <h3 style="color: #1b263b; margin-top: 0;">🌌 Ephem Kozmik Yansıma</h3>
                        <p><b>Hesaplanan Konum / Takımyıldız:</b> {burc}</p>
                        <p><i>Göksel döngüleriniz ile ses frekansınız bu alanda bütüncül bir akış sergilemektedir.</i></p>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")
