import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
import ephem
import random

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | Bütünsel Farkındalık Sentezi", layout="centered", page_icon="🏛️")

# 1. LOGO KONTROLÜ
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)
else:
    st.title("🏛️ Ruhun Mimarisi | VBAR")

# SEKME YAPISI
tab1, tab2 = st.tabs(["🔬 Makro Sentez & Kozmik Harita", "📖 Rehber Hakkında"])

with tab2:
    st.subheader("Ruhun Mimarisi ve Derin Sentez Altyapısı")
    st.write("""
    **VBAR**, ses frekansınızdaki spektral dalgalanmaları ve gerilim indekslerini; gerçek gök günlüğü (Ephemeris) hesaplamalarıyla harmanlayan, her an güncellenen özgün bir farkındalık platformudur.
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
    col_g, col_a, col_y = st.columns(3)
    dogum_gun = col_g.selectbox("Gün", list(range(1, 32)), index=28)
    dogum_ay = col_a.selectbox("Ay", list(range(1, 13)), index=11)
    dogum_yil = col_y.selectbox("Yıl", list(range(1940, 2026)), index=44)

    col_s, col_d = st.columns(2)
    dogum_saat = col_s.slider("Doğum Saati", 0, 23, 12)
    dogum_dakika = col_d.slider("Doğum Dakikası", 0, 59, 0)

    if audio_bytes:
        if st.button("✨ Makro Ephemeris Sentezini Başlat"):
            with st.spinner("Gökyüzü dereceleri, akustik katmanlar ve arketip havuzları harmanlanıyor..."):
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

                    gunes_burcu = get_zodiac_sign(sun, observer_date)
                    ay_burcu = get_zodiac_sign(moon, observer_date)
                    merkur_burcu = get_zodiac_sign(mercury, observer_date)
                    venus_burcu = get_zodiac_sign(venus, observer_date)

                    # Tamamen Ayrıştırılmış Özgün Havuzlar
                    giris_havuzu = [
                        "Ses tellerinden yayılan bu ilk dalga, bilinç altındaki potansiyel enerjinin dış dünyayla kurduğu ilk temestir.",
                        "Kozmik haritanın mimarisi ile sesinin anlık frekans tınısı, bu sentezde benzersiz bir ritim oluşturuyor.",
                        "Konuşurken sergilediğin akustik akış, içsel dünyandaki arketipsel dengenin dışa vurulan sesli haritasıdır."
                    ]
                    secilen_giris = random.choice(giris_havuzu)

                    golge_havuzu = [
                        "Zihinsel planlar ile duygusal beklentiler arasında sıkışma hissedildiğinde, bedeni topraklamak en güvenli limandır.",
                        "Mükemmeliyetçi ya da aşırı denetleyici tutumlar anın akışını kısıtlayabilir; bırak gitsin.",
                        "Dış dünyadan gelen uyaranların sesine yansıyan yorgunluğu, ancak öz şefkat ve yavaşlama adımlarıyla şifalandırabilirsin."
                    ]
                    secilen_golge = random.choice(golge_havuzu)

                    reçete_havuzu = [
                        "- **Kristal ve Doğal Taş Desteği:** Enerji alanını dengelemek için **Hematit** veya **Labradorit** bilekliği kullanabilirsin.\n- **Somatik Pratik:** Omuzları serbest bırakıp derin karın nefesleriyle boğaz çakrasındaki blokajı esnetebilirsin.",
                        "- **Kristal ve Doğal Taş Desteği:** Duygusal akışını şifalandırmak adına **Lapis Lazuli** veya **Akuamarin** taşıyla odaklanabilirsin.\n- **Somatik Pratik:** Ayak tabanlarını yere tam basarak kısa bir yürüyüşle fiziksel köklenmeni güçlendirebilirsin.",
                        "- **Kristal ve Doğal Taş Desteği:** Zihinsel berraklık için **Onyx** veya **Dağ Kristali** enerjisinden faydalanabilirsin.\n- **Somatik Pratik:** Ses tellerini dinlendiren ılık bitki çayları eşliğinde sessizlik molaları verebilirsin."
                    ]
                    secilen_recete = random.choice(reçete_havuzu)

                    ses_durum_yorumu = "Ses enerjisindeki yoğun ivme, harekete geçme arzusunun ve dönüştürücü motivasyonun yüksek olduğunu gösteriyor." if gerilim > 3.5 else "Ses tonundaki sükunet ve dengeli frekans, stratejik bir içsel dinginlik inşa ettiğini simgeliyor."

                    harita_metinleri = {
                        "Oğlak": "Yapılandırma, stratejik sabır, sarsılmaz sorumluluk bilinci.",
                        "Koç": "Öncü ateş, mutlak cesaret, yenilikçi başlatma gücü.",
                        "Yay": "Keşif tutkusu, felsefi derinlik, özgürlük arayışı.",
                        "Kova": "Evrensel vizyon, toplumsal yenilik, entelektüel özgürlük.",
                        "Balık": "Şefkat, evrensel akış, sınırsız sezgi.",
                        "Akrep": "Derin dönüşüm, mutlak sadakat, kriz anı dayanıklılığı.",
                        "Boğa": "Toprağın dinginliği, kararlılık, somutlaştırma gücü.",
                        "İkizler": "Zihinsel çeviklik, bilgi akışı, adaptasyon.",
                        "Yengeç": "Derin duygusal hafıza, koruyuculuk, yuva bilinci.",
                        "Aslan": "Yaratıcı özgüven, sahne ışığı, kalpten liderlik.",
                        "Başak": "Analitik zeka, detaylardaki mükemmellik, hizmet bilinci.",
                        "Terazi": "İlahi denge, adalet, estetik uyum."
                    }

                    gunes_detay = harita_metinleri.get(gunes_burcu, "")
                    ay_detay = harita_metinleri.get(ay_burcu, "")

                    # --- ARAYÜZ SUNUMU ---
                    with st.container(border=True):
                        st.subheader("🔬 Makro Akustik Biyometrik Rapor")
                        st.metric("Ortalama Ses Frekansı (F0)", f"{anlik_f0:.1f} Hz")
                        st.metric("Gerilim / Enerji İndeksi", f"{gerilim:.2f}")

                    with st.container(border=True):
                        st.subheader("🌌 Gerçek Ephemeris Kozmik Harita")
                        st.markdown(f"**Güneş Konumu (Öz Kimlik):** {gunes_burcu} — *{gunes_detay}*")
                        st.divider()
                        st.markdown(f"**Ay Konumu (Duygusal Katman):** {ay_burcu} — *{ay_detay}*")
                        st.divider()
                        st.markdown(f"**Merkür (Zihin):** {merkur_burcu}  |  **Venüs (İlişkiler):** {venus_burcu}")

                    with st.container(border=True):
                        st.subheader("🏛️ Ruhun Mimarisi | Makro Bütünsel Sentez")
                        
                        st.markdown("### 1. Giriş ve Bütünsel Atmosfer")
                        st.write(secilen_giris)

                        st.markdown("### 2. Göksel Potansiyeller ve Element Sentezi")
                        st.write(f"Karakterinin ana omurgasını oluşturan {gunes_burcu} ateşi/özü ile iç dünyanı besleyen {ay_burcu} dalgalanması, dış dünyaya verdiğin yanıtları biçimlendiriyor.")

                        st.markdown("### 3. Akustik Biyometrik Analiz")
                        st.write(f"Ses kaydındaki {anlik_f0:.1f} Hz taban frekansı ve ölçülen {gerilim:.2f} gerilim katsayısı incelendiğinde: {ses_durum_yorumu}")

                        st.markdown("### 4. Gölge Alanlar ve Dönüşüm Rehberliği")
                        st.write(secilen_golge)

                        st.markdown("### 5. Somatik ve Spiritüel Öneri Reçetesi")
                        st.markdown(secilen_recete)

                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
