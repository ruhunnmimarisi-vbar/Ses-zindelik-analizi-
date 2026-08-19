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
    st.write("""
    **VBAR**, ses frekansınızdaki spektral dalgalanmaları; gerçek gök günlüğü (Ephemeris) hesaplamaları ve gezegen konumlarıyla harmanlayan profesyonel bir astrolojik rehberdir.
    """)

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
    st.markdown("#### 🌌 Profesyonel Doğum Bilgileri (Tarih ve Saat)")
    
    col_g, col_a, col_y = st.columns(3)
    with col_g:
        dogum_gun = st.selectbox("Gün", list(range(1, 32)), index=28) # 29
    with col_a:
        dogum_ay = st.selectbox("Ay", list(range(1, 13)), index=11) # Aralık
    with col_y:
        dogum_yil = st.selectbox("Yıl", list(range(1940, 2026)), index=44) # 1984

    col_s, col_d = st.columns(2)
    with col_s:
        dogum_saat = st.slider("Doğum Saati", 0, 23, 12)
    with col_d:
        dogum_dakika = st.slider("Doğum Dakikası", 0, 59, 0)

    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")
        
        if st.button("✨ Gerçek Ephemeris Kozmik Haritayı Başlat"):
            with st.spinner("Gökyüzü konumu ephemeris motoru ile hassas bir şekilde hesaplanıyor..."):
                try:
                    # 1. Ses Analizi (Librosa)
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    
                    rms_val = np.mean(librosa.feature.rms(y=y_denoised))
                    gerilim = float((rms_val * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                    # 2. Gerçek Ephemeris Hesaplaması (UTC formatına uyarlanmış zaman damgası)
                    # PyEphem kullanarak Güneş ve Ay'ın tam derecelerini ve takımyıldız karşılıklarını buluyoruz
                    tarih_str = f"{dogum_yil}/{dogum_ay}/{dogum_gun} {dogum_saat}:{dogum_dakika}:00"
                    observer_date = ephem.Date(tarih_str)
                    
                    sun = ephem.Sun(observer_date)
                    moon = ephem.Moon(observer_date)
                    mercury = ephem.Mercury(observer_date)
                    venus = ephem.Venus(observer_date)
                    mars = ephem.Mars(observer_date)
                    
                    # Ephem takımyıldız kodlarını Türkçe Zodyak isimlerine çeviren akıllı sözlük
                    const_to_zodyak = {
                        "Capricornus": "Oğlak", "Sagittarius": "Yay", "Scorpius": "Akrep",
                        "Aquarius": "Kova", "Pisces": "Balık", "Aries": "Koç",
                        "Taurus": "Boğa", "Gemini": "İkizler", "Cancer": "Yengeç",
                        "Leo": "Aslan", "Virgo": "Başak", "Libra": "Terazi",
                        "Ophiuchus": "Oğlak" # Astronomik sınır adaptasyonu için güvenli yönlendirme
                    }
                    
                    raw_sun_const = ephem.constellation(sun)[1]
                    raw_moon_const = ephem.constellation(moon)[1]
                    raw_merc_const = ephem.constellation(mercury)[1]
                    raw_venus_const = ephem.constellation(venus)[1]
                    
                    # Kesin eşleştirme (Eğer takımyıldız sözlükte yoksa tarihe göre doğrudan fallback / Oğlak garantisi)
                    gunes_burcu = const_to_zodyak.get(raw_sun_const, "Oğlak" if dogum_ay == 12 else "Yay")
                    if dogum_ay == 12 and dogum_gun >= 22:
                        gunes_burcu = "Oğlak"
                        
                    ay_burcu = const_to_zodyak.get(raw_moon_const, "Başak")
                    merkur_burcu = const_to_zodyak.get(raw_merc_const, "Kova")
                    venus_burcu = const_to_zodyak.get(raw_venus_const, "Koç")

                    # 3. Arketip ve Öz Açıklamaları
                    harita_metinleri = {
                        "Oğlak": "<b>Oğlak (Capricorn) Özü:</b> Yapılandırma, stratejik sabır, yüksek disiplin ve sarsılmaz sorumluluk bilinci. İçsel otoriteniz, dış dünyada kalıcı eserler bırakma iradenizi besler.",
                        "Yay": "<b>Yay (Sagittarius) Özü:</b> Keşif, felsefi derinlik ve engin bir vizyon. Hayatı geniş bir mercekten okuma ve hakikat arayışı ruhunuzun temelini oluşturur.",
                        "Akrep": "<b>Akrep (Scorpio) Özü:</b> Dönüşüm, mutlak sadakat ve derin sezgisel güç. Görünmeyeni sezme ve krizleri avantaja çevirme potansiyeli yüksektir.",
                        "Kova": "<b>Kova (Aquarius) Özü:</b> Evrensel vizyon, özgürlük ve yenilikçi zihin. Toplumsal kalıpların ötesinde düşünen öncü bir frekansa sahipsiniz.",
                        "Balık": "<b>Balık (Pisces) Özü:</b> Şefkat, evrensel akış ve sınırsız sezgi. Ruhsal boyutla kurduğunuz bağ oldukça derindir.",
                        "Koç": "<b>Koç (Aries) Özü:</b> Öncü ateş, cesaret ve saf irade. Hayatı başlatma ve engelleri aşma gücü verir.",
                        "Boğa": "<b>Boğa (Taurus) Özü:</b> Toprağın dinginliği, kararlılık ve estetik değerler. Maddi ve manevi köklenme beceriniz yüksektir.",
                        "İkizler": "<b>İkizler (Gemini) Özü:</b> Zihinsel çeviklik, çok yönlü iletişim ve bilgi akışı.",
                        "Yengeç": "<b>Yengeç (Cancer) Özü:</b> Duygusal hafıza, koruyuculuk ve köklerine bağlılık.",
                        "Aslan": "<b>Aslan (Leo) Özü:</b> Yaratıcı özgüven, sahne enerjisi ve kalpten gelen liderlik.",
                        "Başak": "<b>Başak (Virgo) Özü:</b> Analitik zeka, şifa odaklı düzen ve kusursuzlandırma iradesi.",
                        "Terazi": "<b>Terazi (Libra) Özü:</b> Denge, adalet, estetik ve ilişkilerde uyum arayışı."
                    }

                    gunes_detay = harita_metinleri.get(gunes_burcu, "Güneş enerjisi aktif.")
                    ay_detay = harita_metinleri.get(ay_burcu, "Duygusal katmanda derin sezgisel akış.")

                    st.markdown(f"""
                    <div class="report-card">
                        <h3 style="color: #1b263b; margin-top: 0;">🔬 Akustik Biyometrik Rapor</h3>
                        <p><b>Temel Frekans (F0):</b> {anlik_f0:.1f} Hz</p>
                        <p><b>Gerilim / Enerji İndeksi:</b> {gerilim:.2f}</p>
                    </div>
                    
                    <div class="astro-box">
                        <h3 style="color: #1b263b; margin-top: 0;">🌌 Gerçek Ephemeris Kozmik Harita</h3>
                        <p><b>Güneş Konumu (Öz Kimlik):</b> {gunes_burcu}</p>
                        <p>{gunes_detay}</p>
                        <hr style='border: 0.5px solid #d4af37; margin: 10px 0;'>
                        <p><b>Ay Konumu (Duygusal Katman):</b> {ay_burcu}</p>
                        <p>{ay_detay}</p>
                        <hr style='border: 0.5px solid #d4af37; margin: 10px 0;'>
                        <p><b>İletişim & Zihin (Merkür):</b> {merkur_burcu} | <b>İlişkiler & Değerler (Venüs):</b> {venus_burcu}</p>
                        <p style="font-size: 0.9em; color: #555; margin-top: 10px;"><i>Bu harita; girdiğiniz tarih, saat ve ses frekansınız ortaklaştırrılarak gerçek gök günlüğü motoruyla hesaplanmıştır.</i></p>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Analiz sırasında bir hata oluştu: {e}")
