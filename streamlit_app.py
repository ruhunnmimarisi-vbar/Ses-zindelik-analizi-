import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
import ephem

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Biyometrik & Kozmik Harita", layout="centered", page_icon="🏛️")

st.markdown("""
<style>
    .stApp { background-color: #fcfbfa; color: #2c2c2c; }
    .report-card { border: 1px solid #d4af37; padding: 20px; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 15px; }
    .title-box { text-align: center; color: #1b263b; border-bottom: 2px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .astro-box { background: #fdf6e3; border-left: 4px solid #d4af37; padding: 15px; border-radius: 8px; margin-top: 15px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# 1. LOGO KONTROLÜ
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)
else:
    st.markdown("<div class='title-box'><h1>🏛️ Ruhun Mimarisi | VBAR</h1></div>", unsafe_allow_html=True)

# SEKME YAPISI
tab1, tab2 = st.tabs(["🔬 Biyometrik & Kozmik Harita", "📖 Hakkında"])

with tab2:
    st.subheader("Ruhun Mimarisi ve Gerçek Kozmik Harita Altyapısı")
    st.write("VBAR, ses frekansınızı gerçek astronomik konumlarla harmanlayan profesyonel bir kozmik rehberdir.")

with tab1:
    st.subheader("Ses Kaydı ve Doğum Haritası Verileri")
    
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
    col_g, col_a, col_y = st.columns(3)
    dogum_gun = col_g.selectbox("Gün", list(range(1, 32)), index=28)
    dogum_ay = col_a.selectbox("Ay", list(range(1, 13)), index=11)
    dogum_yil = col_y.selectbox("Yıl", list(range(1940, 2026)), index=44)

    col_s, col_d = st.columns(2)
    dogum_saat = col_s.slider("Doğum Saati", 0, 23, 12)
    dogum_dakika = col_d.slider("Doğum Dakikası", 0, 59, 0)

    if audio_bytes:
        if st.button("✨ Gerçek Ephemeris Kozmik Haritayı Başlat"):
            with st.spinner("Hesaplanıyor..."):
                try:
                    # Ses Analizi
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    gerilim = float((np.mean(librosa.feature.rms(y=y_denoised)) * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                    # Astronomik Hesaplama
                    def get_zodiac_sign(body_obj, obs_date):
                        ecl = ephem.Equatorial(body_obj.ra, body_obj.dec, epoch=obs_date)
                        ecl = ephem.Ecliptic(ecl)
                        lon_deg = float(ecl.lon) * 180.0 / np.pi
                        burclar = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
                        return burclar[int((lon_deg % 360) // 30)]

                    tarih_str = f"{dogum_yil}/{dogum_ay}/{dogum_gun} {dogum_saat}:{dogum_dakika}:00"
                    observer_date = ephem.Date(tarih_str)
                    
                    sun, moon, mercury, venus = ephem.Sun(), ephem.Moon(), ephem.Mercury(), ephem.Venus()
                    sun.compute(observer_date); moon.compute(observer_date); mercury.compute(observer_date); venus.compute(observer_date)

                    st.markdown(f"""
                    <div class="report-card">
                        <h3>🔬 Akustik Biyometrik Rapor</h3>
                        <p><b>F0:</b> {anlik_f0:.1f} Hz | <b>Enerji:</b> {gerilim:.2f}</p>
                    </div>
                    <div class="astro-box">
                        <h3>🌌 Kozmik Harita</h3>
                        <p><b>Güneş:</b> {get_zodiac_sign(sun, observer_date)}</p>
                        <p><b>Ay:</b> {get_zodiac_sign(moon, observer_date)}</p>
                        <p><b>Merkür:</b> {get_zodiac_sign(mercury, observer_date)} | <b>Venüs:</b> {get_zodiac_sign(venus, observer_date)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")
