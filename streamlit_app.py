import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
import ephem
from datetime import datetime

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
    st.subheader("Ruhun Mimarisi ve Kozmik Harita Altyapısı")
    st.write("""
    **VBAR**, ses frekansınızdaki spektral dalgalanmaları ve enerji indeksini; **ephem** motoru ile hesaplanan kişiye özel doğum haritası arketipleri ve gezegen konumlarıyla harmanlayan bütüncül bir rehberdir.
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
    st.markdown("#### 🌌 Kişiye Özel Doğum Bilgileri")
    
    col_g, col_a, col_y = st.columns(3)
    with col_g:
        dogum_gun = st.selectbox("Gün", list(range(1, 32)), index=28)
    with col_a:
        dogum_ay = st.selectbox("Ay", list(range(1, 13)), index=11)
    with col_y:
        dogum_yil = st.selectbox("Yıl", list(range(1940, 2026)), index=44)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        
        if st.button("✨ Kişiye Özel Kozmik Harita Analizini Başlat"):
            with st.spinner("Ses spektrumu taranıyor ve ephem ile doğum haritası konumları hesaplanıyor..."):
                try:
                    # 1. Ses Analizi (Librosa)
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    
                    rms_val = np.mean(librosa.feature.rms(y=y_denoised))
                    gerilim = float((rms_val * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                    # 2. Ephem ile Gerçek Zamanlı Hesaplama
                    ephem_tarih = f"{dogum_yil}/{dogum_ay}/{dogum_gun}"
                    
                    sun = ephem.Sun(ephem_tarih)
                    moon = ephem.Moon(ephem_tarih)
                    mercury = ephem.Mercury(ephem_tarih)
                    venus = ephem.Venus(ephem_tarih)
                    
                    sun_const = ephem.constellation(sun)[1]
                    moon_const = ephem.constellation(moon)[1]
                    merc_const = ephem.constellation(mercury)[1]
                    venus_const = ephem.constellation(venus)[1]

                    # 3. Kapsamlı Harita ve Arketip Sözlüğü (İngilizce takımyıldız karşılıkları)
                    harita_metinleri = {
                        "Capricornus": "<b>Oğlak (Capricorn) Özü:</b> Yapılandırma, stratejik sabır, yüksek disiplin ve sarsılmaz sorumluluk bilinci. İçsel otoriteniz, dış dünyada kalıcı eserler bırakma iradenizi besler.",
                        "Sagittarius": "<b>Yay (Sagittarius) Özü:</b> Keşif, felsefi derinlik ve engin bir vizyon. Hayatı geniş bir mercekten okuma ve hakikat arayışı ruhunuzun temelini oluşturur.",
                        "Scorpius": "<b>Akrep (Scorpio) Özü:</b> Dönüşüm, mutlak sadakat ve derin sezgisel güç. Görünmeyeni sezme ve krizleri avantaja çevirme potansiyeli yüksektir.",
                        "Aquarius": "<b>Kova (Aquarius) Özü:</b> Evrensel vizyon, özgürlük ve yenilikçi zihin. Toplumsal kalıpların ötesinde düşünen öncü bir frekansa sahipsiniz.",
                        "Pisces": "<b>Balık (Pisces) Özü:</b> Şefkat, evrensel akış ve sınırsız sezgi. Ruhsal boyutla kurduğunuz bağ oldukça derindir.",
                        "Aries": "<b>Koç (Aries) Özü:</b> Öncü ateş, cesaret ve saf irade. Hayatı başlatma ve engelleri aşma gücü verir.",
                        "Taurus": "<b>Boğa (Taurus) Özü:</b> Toprağın dinginliği, kararlılık ve estetik değerler. Maddi ve manevi köklenme beceriniz yüksektir.",
                        "Gemini": "<b>İkizler (Gemini) Özü:</b> Zihinsel çeviklik, çok yönlü iletişim ve bilgi akışı.",
                        "Cancer": "<b>Yengeç (Cancer) Özü:</b> Duygusal hafıza, koruyuculuk ve köklerine bağlılık.",
                        "Leo": "<b>Aslan (Leo) Özü:</b> Yaratıcı özgüven, sahne enerjisi ve kalpten gelen liderlik.",
                        "Virgo": "<b>Başak (Virgo) Özü:</b> Analitik zeka, şifa odaklı düzen ve kusursuzlandırma iradesi.",
                        "Libra": "<b>Terazi (Libra) Özü:</b> Denge, adalet, estetik ve ilişkilerde uyum arayışı.",
                        "Ophiuchus": "<b>Yılancı (Ophiuchus) Özü:</b> Şifacılık, derin dönüşüm ve bilgelik arayışı."
                    }

                    gunes_detay = harita_metinleri.get(sun_const, "Göksel güneş döngüsü aktif.")
                    ay_detay = harita_metinleri.get(moon_const, "Duygusal katmanda derin sezgisel akış.")

                    st.markdown(f"""
                    <div class="report-card">
                        <h3 style="color: #1b263b; margin-top: 0;">🔬 Akustik Biyometrik Rapor</h3>
                        <p><b>Temel Frekans (F0):</b> {anlik_f0:.1f} Hz</p>
                        <p><b>Gerilim / Enerji İndeksi:</b> {gerilim:.2f}</p>
                    </div>
                    
                    <div class="astro-box">
                        <h3 style="color: #1b263b; margin-top: 0;">🌌 Ephem Kozmik Harita ve Gezegen Konumları</h3>
                        <p><b>Güneş Konumu (Öz Kimlik / Takımyıldız):</b> {sun_const}</p>
                        <p>{gunes_detay}</p>
                        <hr style='border: 0.5px solid #d4af37; margin: 10px 0;'>
                        <p><b>Ay Konumu (Duygusal Katman):</b> {moon_const}</p>
                        <p>{ay_detay}</p>
                        <hr style='border: 0.5px solid #d4af37; margin: 10px 0;'>
                        <p><b>İletişim & Zihin (Merkür):</b> {merc_const} | <b>İlişkiler & Değerler (Venüs):</b> {venus_const}</p>
                        <p style="font-size: 0.9em; color: #555; margin-top: 10px;"><i>Bu harita verileri, girdiğiniz doğum tarihine göre hesaplanmış ve ses spektrumunuzla harmanlanmıştır.</i></p>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")
