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
    **VBAR**, ses frekansınızdaki spektral dalgalanmaları ve gerilim indekslerini; gerçek gök günlüğü (Ephemeris), Yükselen Burç ve Ay Düğümü (KAD/GAD) hesaplamalarıyla harmanlayan özgün bir farkındalık platformudur.
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
            with st.spinner("Yükselen burç, Ay düğümleri (KAD/GAD), akustik katmanlar ve ses frekansın harmanlanıyor..."):
                try:
                    # Ses Analizi
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    gerilim = float((np.mean(librosa.feature.rms(y=y_denoised)) * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                    # Astronomik Hesaplama Yardımcısı
                    def get_zodiac_sign_from_lon(lon_deg):
                        burclar = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
                        return burclar[int((lon_deg % 360) // 30)]

                    def get_zodiac_sign(body_obj, obs_date):
                        ecl = ephem.Equatorial(body_obj.ra, body_obj.dec, epoch=obs_date)
                        ecl = ephem.Ecliptic(ecl)
                        lon_deg = float(ecl.lon) * 180.0 / np.pi
                        return get_zodiac_sign_from_lon(lon_deg)

                    tarih_str = f"{dogum_yil}/{dogum_ay}/{dogum_gun} {dogum_saat}:{dogum_dakika}:00"
                    observer_date = ephem.Date(tarih_str)
                    
                    sun, moon, mercury, venus = ephem.Sun(), ephem.Moon(), ephem.Mercury(), ephem.Venus()
                    sun.compute(observer_date); moon.compute(observer_date); mercury.compute(observer_date); venus.compute(observer_date)

                    gunes_burcu = get_zodiac_sign(sun, observer_date)
                    ay_burcu = get_zodiac_sign(moon, observer_date)
                    merkur_burcu = get_zodiac_sign(mercury, observer_date)
                    venus_burcu = get_zodiac_sign(venus, observer_date)

                    # --- YÜKSELEN (ASCENDANT) HESAPLAMA ---
                    # Türkiye ortalama boylamı (~27-35° E) baz alınarak yaklaşık Sidereal/House hesaplama yaklaşımı
                    sidereal_time = (observer_date - int(observer_date)) * 360.0 + (dogum_saat * 15.0) + 28.0
                    asc_lon = (sidereal_time + (dogum_dakika * 0.25)) % 360
                    yukselen_burc = get_zodiac_sign_from_lon(asc_lon)

                    # --- KAD VE GAD HESAPLAMA (Kuzey ve Güney Ay Düğümü) ---
                    # Ay düğümleri zodyakta zıt burçlardadır; yaklaşık bir döngü hesaplaması
                    ay_dugumu_lon = (float(moon.ecliptic_lon) * 180.0 / np.pi + 180.0) % 360
                    kad_burcu = get_zodiac_sign_from_lon(ay_dugumu_lon)
                    gad_lon = (ay_dugumu_lon + 180.0) % 360
                    gad_burcu = get_zodiac_sign_from_lon(gad_lon)

                    # --- KİŞİYE ÖZEL MATEMATİKSEL İNDEKSLEME ---
                    unique_seed = int((anlik_f0 * 100 + gerilim * 1000 + dogum_gun * 13 + dogum_saat * 7) % 5)

                    giris_listesi = [
                        f"Sesinin {anlik_f0:.1f} Hz seviyesindeki titreşimi, Yükselen {yukselen_burc} maskesinin dış dünyaya açtığı ilk kapıyla kusursuz bir uyum sergiliyor.",
                        f"Bu akustik kayıt, {yukselen_burc} yükseleninin getirdiği duruş ile ses tellerindeki {anlik_f0:.1f} Hz'lik tınısındaki özgün enerjiyi harmanlıyor.",
                        f"Konuşurken sergilediğin ses dalgası, gökyüzündeki {gunes_burcu} güneş kimliğin ile {yukselen_burc} yükseleninin dışa yansıyan ortak imzasıdır.",
                        f"Akustik Spektrum analizi, {anlik_f0:.1f} Hz frekansı üzerinden içsel potansiyellerinin ve yükselen burç karakterinin zihnindeki izdüşümünü yakalıyor.",
                        f"Zihnindeki düşünce akışı ile sesindeki {anlik_f0:.1f} Hz tını, {yukselen_burc} yükseleninin çevrenle kurduğu köprüyü yeniden şekillendiriyor."
                    ]

                    analiz_listesi = [
                        f"Ölçülen {gerilim:.2f} gerilim katsayısı, enerjini dönüştürme çabanı; GAD ({gad_burcu}) köklerinden gelen alışkanlıkları bırakıp KAD ({kad_burcu}) yönüne doğru gelişme isteğini ele veriyor.",
                        f"Sesindeki {gerilim:.2f} yoğunluk indeksi, dış dünyadan gelen uyaranlara karşı duyarlılığını ve bu süreçte {ay_burcu} katmanındaki duygusal reflekslerini simgeliyor.",
                        f"Kaydın akustik yapısında gözlenen {gerilim:.2f} gerilim değeri, {yukselen_burc} burcunun dış dünyaya gösterdiği yüz ile içsel dünyandaki denge arayışını yansıtıyor.",
                        f"Frekans analizindeki {gerilim:.2f} puanlık ivme, geçmiş karmik kalıplardan (GAD: {gad_burcu}) sıyrılıp ruhsal hedefine (KAD: {kad_burcu}) odaklanma çabanı gösteriyor.",
                        f"Sesinin {gerilim:.2f} enerji seviyesi, kararlı duruşunu korurken bir yandan da ruhsal olarak esneme alanları aradığını net bir biçimde gözler önüne seriyor."
                    ]

                    golge_listesi = [
                        f"Geçmişin güvenli ama artık tüketici alışkanlıklarından ({gad_burcu}) sıyrılıp, {kad_burcu} yönündeki yeniliklere adım atmak şu sıralar zihinsel trafiğini rahatlatacaktır.",
                        f"Beklentilerin ve sorumlulukların yarattığı baskıyı esnetmek, {yukselen_burc} yükseleninin getirdiği yorgunluğu hafifletecektir.",
                        f"Anın kontrolünü biraz olsun serbest bırakmak, {ay_burcu} katmanındaki duygusal dalgalanmaları dindirecek ve ruhsal eksenini güçlendirecektir.",
                        f"Zihinsel trafiği yavaşlatmak adına dış dünyadaki uyaranlara kısa bir mola vermek ve GAD ({gad_burcu}) tuzaklarından kaçınmak en büyük şifadır.",
                        f"Mükemmeliyetçi yaklaşımları bir kenara bırakıp kendi doğal ritmine uyumlanmak, KAD ({kad_burcu}) yolculuğunun anahtarıdır."
                    ]

                    kristal_listesi = [
                        ("- **Kristal Desteği:** Zihinsel berraklık ve köklenmek için **Hematit** veya **Onyx** taşı tercih edebilirsin.", "- **Somatik Pratik:** Omuz kaslarını serbest bırakan derin diyafram nefesleriyle boğaz çakrandaki akışı rahatlatabilirsin."),
                        ("- **Kristal Desteği:** Duygusal denge ve içsel huzur için **Lapis Lazuli** veya **Akuamarin** taşı kullanabilirsin.", "- **Somatik Pratik:** Ayak tabanlarını yere tam basarak yapacağın kısa bir yürüyüşle fiziksel köklenmeni artırabilirsin."),
                        ("- **Kristal Desteği:** Enerjini tazelemek ve odaklanmak için **Labradorit** veya **Dağ Kristali** enerjisinden faydalanabilirsin.", "- **Somatik Pratik:** Ses tellerini dinlendiren ılık bitki çayları eşliğinde kısa bir zihinsel sessizlik molası verebilirsin."),
                        ("- **Kristal Desteği:** İçsel gücü artırmak için **Obsidiyen** veya **Kırmızı Akik** taşı taşıyabilirsin.", "- **Somatik Pratik:** Boyun ve baş bölgesini hafifçe esneten fiziksel gevşeme hareketleri uygulayabilirsin."),
                        ("- **Kristal Desteği:** Ruhsal akışı desteklemek için **Ametist** veya **Yıldız Taşı** tercih edebilirsin.", "- **Somatik Pratik:** Gözlerini kapatıp sadece nefesine odaklandığın 3 dakikalık bir merkezlenme pratiği yapabilirsin.")
                    ]

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
                    yukselen_detay = harita_metinleri.get(yukselen_burc, "")

                    # --- ARAYÜZ SUNUMU ---
                    with st.container(border=True):
                        st.subheader("🔬 Makro Akustik Biyometrik Rapor")
                        st.metric("Ortalama Ses Frekansı (F0)", f"{anlik_f0:.1f} Hz")
                        st.metric("Gerilim / Enerji İndeksi", f"{gerilim:.2f}")

                    with st.container(border=True):
                        st.subheader("🌌 Gerçek Ephemeris Kozmik Harita & Kader Aksı")
                        st.markdown(f"**Yükselen Burç (Maske & Duruş):** {yukselen_burc} — *{yukselen_detay}*")
                        st.divider()
                        st.markdown(f"**Güneş Konumu (Öz Kimlik):** {gunes_burcu} — *{gunes_detay}*")
                        st.divider()
                        st.markdown(f"**Ay Konumu (Duygusal Katman):** {ay_burcu} — *{ay_detay}*")
                        st.divider()
                        st.markdown(f"**Kuzey Ay Düğümü (KAD - Ruhsal Hedefin):** **{kad_burcu}**  |  **Güney Ay Düğümü (GAD - Geçmiş Yükün):** **{gad_burcu}**")
                        st.divider()
                        st.markdown(f"**Merkür (Zihin):** {merkur_burcu}  |  **Venüs (İlişkiler):** {venus_burcu}")

                    with st.container(border=True):
                        st.subheader("🏛️ Ruhun Mimarisi | Makro Bütünsel Sentez")
                        
                        st.markdown("### 1. Giriş ve Bütünsel Atmosfer")
                        st.write(secilen_giris)

                        st.markdown("### 2. Göksel Potansiyeller ve Element Sentezi")
                        st.write(f"Dış dünyaya gösterdiğin yüzü belirleyen **Yükselen {yukselen_burc}** ile öz kimliğin olan **{gunes_burcu}** ve ruhsal gelişim aksın olan **GAD {gad_burcu} -> KAD {kad_burcu}** hattı, bu dönemsel dönüşümünün ana hatlarını çiziyor.")

                        st.markdown("### 3. Akustik Biyometrik Analiz")
                        st.write(secilen_analiz)

                        st.markdown("### 4. Gölge Alanlar ve Dönüşüm Rehberliği")
                        st.write(secilen_golge)

                        st.markdown("### 5. Somatik ve Spiritüel Öneri Reçetesi")
                        st.markdown(secilen_kristal)
                        st.markdown(secilen_somatik)

                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
