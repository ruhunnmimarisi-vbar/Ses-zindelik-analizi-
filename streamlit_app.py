import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr
import ephem

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
            with st.spinner("Gökyüzü dereceleri, akustik katmanlar ve ses frekansın harmanlanıyor..."):
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

                    # --- TAMAMEN KİŞİYE ÖZEL MATEMATİKSEL İNDEKSLEME ---
                    # Sesin küsuratları ve doğum verileri birleştirilerek benzersiz bir anahtar üretilir
                    unique_seed = int((anlik_f0 * 100 + gerilim * 1000 + dogum_gun * 13 + dogum_saat * 7) % 5)

                    giris_listesi = [
                        f"Sesinin {anlik_f0:.1f} Hz seviyesindeki titreşimi, {gunes_burcu} burcunun sana bahşettiği temel irade ile anlık bir köprü kuruyor.",
                        f"Bu kayıt, {gunes_burcu} enerjisinin dış dünyaya yansıyan sesli imzasını ve {anlik_f0:.1f} Hz'lik tınısındaki özgün akışı gözler önüne seriyor.",
                        f"Ses tellerinden yayılan bu dalga boyu, gökyüzündeki {gunes_burcu} ve {ay_burcu} yerleşimlerinin sesli bir yansıma biçimidir.",
                        f"Akustik Spektrum analizi, {anlik_f0:.1f} Hz frekansı üzerinden içsel dünyandaki potansiyel kapıların aralandığını işaret ediyor.",
                        f"Zihnindeki düşünce akışı ile sesindeki {anlik_f0:.1f} Hz tını, bu sentezde kendine has bambaşka bir ritim yaratıyor."
                    ]

                    analiz_listesi = [
                        f"Ölçülen {gerilim:.2f} gerilim katsayısı, enerjini dönüştürme konusunda aktif bir çaba içinde olduğunu ve ses tonunun bu eforu, {gunes_burcu} arketipiyle harmanladığını gösteriyor.",
                        f"Sesindeki {gerilim:.2f} yoğunluk indeksi, dış dünyadan gelen uyaranlara karşı duyarlılığını ve bu süreçte {ay_burcu} katmanından beslenen duygusal reflekslerini ele veriyor.",
                        f"Kaydın akustik yapısında gözlenen {gerilim:.2f} gerilim değeri, içsel dünyandaki dengeyi koruma çabanı ve ses tellerindeki dinamik salınımı net bir şekilde yansıtıyor.",
                        f"Frekans analizindeki {gerilim:.2f} puanlıkimans, zihinsel odaklanma ile anlık rahatlama isteği arasında kurduğun köprünün karakterini gözler önüne seriyor.",
                        f"Sesinin {gerilim:.2f} enerji seviyesi, kararlı duruşunu korurken bir yandan da ruhsal olarak esneme alanları aradığını simgeliyor."
                    ]

                    golge_listesi = [
                        f"Yoğun temponun getirdiği zihinsel yorgunluğu hafifletmek için {gunes_burcu.lower()} burcunun sabır enerjisine güvenebilirsin.",
                        f"Beklentilerin ve sorumlulukların yarattığı baskıyı esnetmek, içsel akışını yeniden canlandıracaktır.",
                        f"Anın kontrolünü biraz olsun serbest bırakmak, {ay_burcu.lower()} katmanındaki duygusal dalgalanmaları dindirecektir.",
                        f"Zihinsel trafiği yavaşlatmak adına dış dünyadaki uyaranlara kısa bir mola vermek şu sıralar en büyük şifadır.",
                        f"Mükemmeliyetçi yaklaşımları bir kenara bırakıp kendi doğal ritmine uyumlanmak dönüşümün anahtarıdır."
                    ]

                    kristal_listesi = [
                        ("- **Kristal Desteği:** Zihinsel berraklık ve köklenmek için **Hematit** veya **Onyx** taşı tercih edebilirsin.", "- **Somatik Pratik:** Omuz kaslarını serbest bırakan derin diyafram nefesleriyle boğaz çakrandaki akışı rahatlatabilirsin."),
                        ("- **Kristal Desteği:** Duygusal denge ve içsel huzur için **Lapis Lazuli** veya **Akuamarin** taşı kullanabilirsin.", "- **Somatik Pratik:** Ayak tabanlarını yere tam basarak yapacağın kısa bir yürüyüşle fiziksel köklenmeni artırabilirsin."),
                        ("- **Kristal Desteği:** Enerjini tazelemek ve odaklanmak için **Labradorit** veya **Dağ Kristali** enerjisinden faydalanabilirsin.", "- **Somatik Pratik:** Ses tellerini dinlendiren ılık bitki çayları eşliğinde kısa bir zihinsel sessizlik molası verebilirsin."),
                        ("- **Kristal Desteği:** İçsel gücü artırmak için **Obsidiyen** veya **Kırmızı Akik** taşı taşıyabilirsin.", "- **Somatik Pratik:** Boyun ve baş bölgesini hafifçe esneten fiziksel gevşeme hareketleri uygulayabilirsin."),
                        ("- **Kristal Desteği:** Ruhsal akışı desteklemek için **Ametist** veya **Yıldız Taşı** tercih edebilirsin.", "- **Somatik Pratik:** Gözlerini kapatıp sadece nefesine odaklandığın 3 dakikalık bir merkezlenme pratiği yapabilirsin.")
                    ]

                    # Benzersiz index seçimi
                    secilen_giris = giris_listesi[unique_seed % len(giris_listesi)]
                    secilen_analiz = analiz_listesi[(unique_seed + 1) % len(analiz_listesi)]
                    secilen_golge = golge_listesi[(unique_seed + 2) % len(golge_listesi)]
                    secilen_kristal, secilen_somatik = kristal_listesi[(unique_seed + 3) % len(kristal_listesi)]

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
                        st.write(f"Karakterinin özünü oluşturan {gunes_burcu} ile iç dünyanı besleyen {ay_burcu} katmanının etkileşimi, şu sıralar hayata bakış açını doğrudan şekillendiriyor.")

                        st.markdown("### 3. Akustik Biyometrik Analiz")
                        st.write(secilen_analiz)

                        st.markdown("### 4. Gölge Alanlar ve Dönüşüm Rehberliği")
                        st.write(secilen_golge)

                        st.markdown("### 5. Somatik ve Spiritüel Öneri Reçetesi")
                        st.markdown(secilen_kristal)
                        st.markdown(secilen_somatik)

                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
