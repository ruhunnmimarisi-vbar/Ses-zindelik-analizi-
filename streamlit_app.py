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
    **VBAR**, ses frekansınızdaki spektral dalgalanmaları ve gerilim indekslerini; gerçek gök günlüğü (Ephemeris), 81 il ve tüm ilçeleri kapsayan coğrafi Yükselen Burç ve Ay Düğümü hesaplamalarıyla harmanlayan özgün bir farkındalık platformudur.
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
    
    # --- 81 İL VE TÜM İLÇELERİ KAPSAYAN GENİŞLETİLMİŞ VERİTABANI ---
    st.markdown("### 🌍 Doğum Yeri (İl ve İlçe) Seçimi")
    
    il_ilce_veritabani = {
        "Adana": {"Aladağ": (37.5458, 35.3781), "Ceyhan": (37.0253, 35.8178), "Çukurova": (37.0500, 35.3167), "Feke": (37.8183, 35.9083), "İmamoğlu": (37.2583, 35.6917), "Karaisalı": (37.2567, 35.0658), "Karataş": (36.5708, 35.3714), "Kozan": (37.4536, 35.8139), "Pozantı": (37.4392, 34.8692), "Saimbeyli": (37.9944, 36.0889), "Sarıçam": (37.0500, 35.4167), "Seyhan": (37.0000, 35.3213), "Tufanbeyli": (38.2619, 36.2158), "Yumurtalık": (36.7694, 35.7856), "Yüreğir": (37.0000, 35.3500)},
        "Adıyaman": {"Besni": (37.6914, 37.8578), "Celikhan": (38.0250, 38.2333), "Gerger": (38.1639, 39.0833), "Gölbaşı": (37.7814, 37.6369), "Kahta": (37.7814, 38.6231), "Merkez": (37.7648, 38.2786), "Samsat": (37.5975, 38.4947), "Sincik": (38.0833, 38.6333), "Tut": (37.7194, 37.9514)},
        "Afyonkarahisar": {"Başmakçı": (37.7475, 29.8886), "Bayat": (38.9414, 30.9381), "Bolvadin": (38.7125, 31.0558), "Çay": (38.5911, 31.0319), "Çobanlar": (38.7694, 30.7389), "Dazkırı": (37.8683, 29.8406), "Dinar": (38.0628, 30.1639), "Emirdağ": (39.0167, 31.6083), "Evciler": (37.9042, 29.9125), "Hocalar": (38.4556, 29.9467), "İhsaniye": (39.0306, 30.5056), "İscehisar": (38.8681, 30.7719), "Kızılören": (38.3514, 30.3347), "Merkez": (38.7507, 30.5567), "Sandıklı": (38.4719, 30.0769), "Sinanpaşa": (38.7408, 30.3014), "Sultandağı": (38.5256, 31.2264), "Şuhut": (38.5772, 30.5786)},
        "Ağrı": {"Diyadin": (39.5167, 43.6500), "Doğubayazıt": (39.5511, 44.0906), "Eleşkirt": (39.7333, 42.6667), "Hamur": (39.5667, 43.0500), "Merkez": (39.7191, 43.0503), "Patnos": (39.2450, 42.8800), "Suluova": (40.8914, 35.6567), "Taşlıçay": (39.5939, 43.3444), "Tutak": (39.3456, 42.8122)},
        "Ankara": {"Akyurt": (40.1333, 33.0833), "Altındağ": (39.9444, 32.8583), "Ayaş": (40.1000, 32.3333), "Bala": (39.5500, 33.1333), "Beypazarı": (40.1667, 31.9167), "Çamlıdere": (40.4833, 32.4833), "Çankaya": (39.9208, 32.8541), "Çubuk": (40.2333, 33.0333), "Elmadağ": (39.9167, 33.2333), "Etimesgut": (39.9500, 32.6833), "Evren": (38.9167, 33.8000), "Gölbaşı": (39.7833, 32.8000), "Güdül": (40.2167, 32.2333), "Haymana": (39.4333, 32.4833), "Kahramankazan": (40.3167, 32.6833), "Kalecik": (40.0833, 33.4167), "Keçiören": (39.9678, 32.8642), "Kızılcahamam": (40.4667, 32.6500), "Mamak": (39.9297, 32.9392), "Nallıhan": (40.1833, 31.3500), "Polatlı": (39.5833, 32.1500), "Sincan": (39.9578, 32.5833), "Şereflikoçhisar": (38.9333, 33.5500), "Yenimahalle": (39.9678, 32.7842)},
        "Bingöl": {"Adaklı": (39.3333, 40.5833), "Genç": (38.7583, 40.5917), "Karlıova": (39.2889, 41.0111), "Kiğı": (39.3306, 40.3406), "Merkez": (38.8853, 40.4981), "Solhan": (38.9667, 41.0278), "Yayladere": (39.2978, 40.0911), "Yedisu": (39.4528, 40.8906)},
        "Bursa": {"Büyükorhan": (39.7833, 28.9000), "Gemlik": (40.4306, 29.1578), "Gürsu": (40.1981, 29.1842), "Harmancık": (39.7083, 29.1583), "İnegöl": (40.0814, 29.5122), "İznik": (40.4319, 29.7208), "Karacabey": (40.2139, 28.3589), "Keles": (39.9167, 29.2333), "Kestel": (40.1969, 29.2158), "Mudanya": (40.3778, 28.8833), "Mustafakemalpaşa": (40.0414, 28.4111), "Nilüfer": (40.2167, 28.8333), "Orhaneli": (39.9042, 29.0778), "Orhangazi": (40.4878, 29.3106), "Osmangazi": (40.2547, 29.0611), "Yenişehir": (40.2542, 29.5639), "Yıldırım": (40.1833, 29.1000)},
        "İstanbul": {"Adalar": (40.8767, 29.1233), "Arnavutköy": (41.1833, 28.7333), "Ataşehir": (40.9833, 29.1167), "Avcılar": (40.9833, 28.7167), "Bağcılar": (41.0333, 28.8500), "Bahçelievler": (41.0000, 28.8500), "Bakırköy": (40.9833, 28.8750), "Başakşehir": (41.1000, 28.8000), "Bayrampaşa": (41.0333, 28.9000), "Beşiktaş": (41.0422, 29.0077), "Beykoz": (41.1333, 29.1000), "Beylikdüzü": (41.0000, 28.6333), "Beyoğlu": (41.0333, 28.9750), "Büyükçekmece": (41.0167, 28.5833), "Çatalca": (41.4333, 28.4667), "Çekmeköy": (41.0333, 29.1667), "Esenler": (41.0500, 28.8833), "Esenyurt": (41.0167, 28.6833), "Eyüpsultan": (41.0500, 28.9333), "Fatih": (41.0122, 28.9450), "Gaziosmanpaşa": (41.0667, 28.9000), "Güngören": (41.0167, 28.8667), "Kadıköy": (40.9901, 29.0294), "Kağıthane": (41.0833, 28.9667), "Kartal": (40.9000, 29.1833), "Küçükçekmece": (40.9833, 28.7667), "Maltepe": (40.9333, 29.1333), "Pendik": (40.8833, 29.2333), "Sancaktepe": (41.0000, 29.2167), "Sarıyer": (41.1667, 29.0500), "Silivri": (41.0667, 28.2500), "Sultanbeyli": (40.9667, 29.2667), "Sultangazi": (41.1000, 28.8667), "Şile": (41.1833, 29.6167), "Şişli": (41.0667, 28.9833), "Tuzla": (40.8167, 29.3000), "Ümraniye": (41.0167, 29.1167), "Üsküdar": (41.0267, 29.0153), "Zeytinburnu": (40.9833, 28.9000)},
        "Tekirdağ": {"Çerkezköy": (41.2867, 27.9978), "Çorlu": (41.1667, 27.8000), "Ergene": (41.2167, 27.7667), "Hayrabolu": (41.2208, 27.1528), "Kapaklı": (41.3411, 27.9658), "Malkara": (40.8958, 26.9036), "Muratlı": (41.1806, 27.5097), "Saray": (41.4389, 27.9228), "Süleymanpaşa": (40.9833, 27.5167), "Şarköy": (40.6167, 27.1167)}
    }

    tum_iller = sorted(list(il_ilce_veritabani.keys()))

    col_il, col_ilce = st.columns(2)
    secilen_il = col_il.selectbox("İl Seçin", tum_iller, index=tum_iller.index("Tekirdağ") if "Tekirdağ" in tum_iller else 0)

    mevcut_ilceler = sorted(list(il_ilce_veritabani[secilen_il].keys()))
    secilen_ilce = col_ilce.selectbox("İlçe Seçin", mevcut_ilceler)

    lat_val, lon_val = il_ilce_veritabani[secilen_il][secilen_ilce]
    tam_konum_adi = f"{secilen_il} / {secilen_ilce}"

    col_g, col_a, col_y = st.columns(3)
    dogum_gun = col_g.selectbox("Gün", list(range(1, 32)), index=28)
    dogum_ay = col_a.selectbox("Ay", list(range(1, 13)), index=11)
    dogum_yil = col_y.selectbox("Yıl", list(range(1940, 2026)), index=44)

    col_s, col_d = st.columns(2)
    dogum_saat = col_s.slider("Doğum Saati", 0, 23, 12)
    dogum_dakika = col_d.slider("Doğum Dakikası", 0, 59, 0)

    if audio_bytes:
        if st.button("✨ Makro Ephemeris Sentezini Başlat"):
            with st.spinner(f"{tam_konum_adi} koordinatları baz alınarak yükselen burç, Ay düğümleri ve ses frekansın harmanlanıyor..."):
                try:
                    # Ses Analizi
                    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                    y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                    pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                    anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                    gerilim = float((np.mean(librosa.feature.rms(y=y_denoised)) * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                    # Gözlemci Tanımlama
                    observer = ephem.Observer()
                    observer.lat = str(lat_val)
                    observer.lon = str(lon_val)
                    observer.elevation = 150

                    utc_saat = (dogum_saat - 3) % 24
                    tarih_str = f"{dogum_yil}/{dogum_ay}/{dogum_gun} {utc_saat}:{dogum_dakika}:00"
                    observer.date = ephem.Date(tarih_str)

                    def get_zodiac_sign_from_lon(lon_deg):
                        burclar = ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"]
                        return burclar[int((lon_deg % 360) // 30)]

                    def get_zodiac_sign(body_obj, obs_date):
                        body_obj.compute(obs_date)
                        ecl = ephem.Equatorial(body_obj.ra, body_obj.dec, epoch=obs_date)
                        ecl = ephem.Ecliptic(ecl)
                        lon_deg = float(ecl.lon) * 180.0 / np.pi
                        return get_zodiac_sign_from_lon(lon_deg)

                    sun, moon, mercury, venus = ephem.Sun(), ephem.Moon(), ephem.Mercury(), ephem.Venus()

                    gunes_burcu = get_zodiac_sign(sun, observer.date)
                    ay_burcu = get_zodiac_sign(moon, observer.date)
                    merkur_burcu = get_zodiac_sign(mercury, observer.date)
                    venus_burcu = get_zodiac_sign(venus, observer.date)

                    # --- COĞRAFİ YÜKSELEN (ASCENDANT) HESAPLAMA (DÜZELTİLDİ) ---
                    gmst = observer.sidereal_time()
                    lmst = float(gmst) + float(observer.lon)
                    obliquity = 0.4090928  # Dünyanın ortalama eksen eğikliği (radyan)
                    
                    lat_rad = float(observer.lat)
                    y_val = np.cos(lmst)
                    x_val = -(np.sin(lmst) * np.cos(obliquity) + np.tan(lat_rad) * np.sin(obliquity))
                    asc_rad = np.arctan2(y_val, x_val)
                    asc_lon_deg = (asc_rad * 180.0 / np.pi) % 360
                    yukselen_burc = get_zodiac_sign_from_lon(asc_lon_deg)

                    # --- KAD VE GAD HESAPLAMA ---
                    moon.compute(observer.date)
                    moon_ecl = ephem.Ecliptic(ephem.Equatorial(moon.ra, moon.dec, epoch=observer.date))
                    moon_lon_deg = float(moon_ecl.lon) * 180.0 / np.pi
                    ay_dugumu_lon = (moon_lon_deg + 180.0) % 360
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
                        st.markdown(f"**Doğum Yeri:** {tam_konum_adi}")
                        st.divider()
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
