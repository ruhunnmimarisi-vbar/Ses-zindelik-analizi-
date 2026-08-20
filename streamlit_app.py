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

                    # --- SES DEĞERLERİNE GÖRE DİNAMİK METİN ÜRETİMİ ---
                    if anlik_f0 > 230:
                        f0_yorum = f"Sesinin tınısındaki yüksek frekans ({anlik_f0:.1f} Hz), zihinsel hareketliliğin, üretkenlik coşkunun ve anlık heyecanların ses tellerine doğrudan yansıdığını gösteriyor."
                    else:
                        f0_yorum = f"Sesinin {anlik_f0:.1f} Hz seviyesindeki daha tok ve bas tınısı, içine dönük, derin düşünen ve enerjisini merkeze alan sakin bir duruşu temsil ediyor."

                    if gerilim > 4.5:
                        gerilim_yorum = f"Ölçülen {gerilim:.2f} gerilim indeksi, omuzlarında taşıdığın yoğun sorumlulukları veya bir konuyu çözme konusundaki kararlı ama yorucu çabanı ele veriyor."
                    elif gerilim > 3.0:
                        gerilim_yorum = f"Ölçülen {gerilim:.2f} gerilim indeksi, dış dünya ile iç dünyan arasında kurmaya çalıştığın dengeli ve temkinli çabayı yansıtıyor."
                    else:
                        gerilim_yorum = f"Ölçülen {gerilim:.2f} gerilim indeksi, sesinde son derece akışkan, rahat ve dirençsiz bir sükunet hâkim olduğunu gösteriyor."

                    harita_metinleri = {
                        "Oğlak": ("Yapılandırma ve sabır", "köklenmek ve sorumlulukları hafifletmek"),
                        "Koç": ("Öncü ateş ve cesaret", "enerjiyi kontrollü yönlendirmek"),
                        "Yay": ("Keşif ve vizyon", "zihinsel ufukları genişletmek"),
                        "Kova": ("Evrensel bilinç ve yenilik", "toplumsal uyaranlardan arınmak"),
                        "Balık": ("Şefkat ve sınırsız sezgi", "duygusal sınırları korumak"),
                        "Akrep": ("Derin dönüşüm ve kriz direnci", "kontrolü bırakıp akışa güvenmek"),
                        "Boğa": ("Toprak dinginliği ve kararlılık", "bedensel konfora odaklanmak"),
                        "İkizler": ("Zihinsel çeviklik ve iletişim", "zihinsel kalabalığı sakinleştirmek"),
                        "Yengeç": ("Duygusal hafıza ve koruyuculuk", "öz şefkat alanları yaratmak"),
                        "Aslan": ("Yaratıcı özgüven ve liderlik", "kalpten gelen ifadelere alan açmak"),
                        "Başak": ("Analitik düzen ve şifa bilinci", "mükemmeliyetçi baskıyı hafifletmek"),
                        "Terazi": ("İlahi denge ve uyum", "karar aşamasındaki tereddütleri aşmak")
                    }

                    gunes_ozellik, gunes_tavsiye = harita_metinleri.get(gunes_burcu, ("Denge", "merkezlenmek"))
                    ay_ozellik, ay_tavsiye = harita_metinleri.get(ay_burcu, ("Akış", "huzur bulmak"))

                    # --- ARAYÜZ SUNUMU ---
                    with st.container(border=True):
                        st.subheader("🔬 Makro Akustik Biyometrik Rapor")
                        st.metric("Ortalama Ses Frekansı (F0)", f"{anlik_f0:.1f} Hz")
                        st.metric("Gerilim / Enerji İndeksi", f"{gerilim:.2f}")

                    with st.container(border=True):
                        st.subheader("🌌 Gerçek Ephemeris Kozmik Harita")
                        st.markdown(f"**Güneş Konumu (Öz Kimlik):** {gunes_burcu} — *{gunes_ozellik}*")
                        st.divider()
                        st.markdown(f"**Ay Konumu (Duygusal Katman):** {ay_burcu} — *{ay_ozellik}*")
                        st.divider()
                        st.markdown(f"**Merkür (Zihin):** {merkur_burcu}  |  **Venüs (İlişkiler):** {venus_burcu}")

                    with st.container(border=True):
                        st.subheader("🏛️ Ruhun Mimarisi | Makro Bütünsel Sentez")
                        
                        st.markdown("### 1. Giriş ve Bütünsel Atmosfer")
                        st.write(f"Doğum haritandaki {gunes_burcu} enerjisi ile sesinin anlık akustik dalgalanması ({anlik_f0:.1f} Hz) bu analizde buluşarak sana özel bir frekans portresi çiziyor.")

                        st.markdown("### 2. Göksel Potansiyeller ve Element Sentezi")
                        st.write(f"Kimliğinin temelini oluşturan {gunes_burcu} burcu ({gunes_ozellik}), iç dünyanı besleyen {ay_burcu} katmanı ise ({ay_ozellik}) ile harmanlanarak şu sıralar hayatı algılayış biçimini şekillendiriyor.")

                        st.markdown("### 3. Akustik Biyometrik Analiz")
                        st.write(f"{f0_yorum} {gerilim_yorum}")

                        st.markdown("### 4. Gölge Alanlar ve Dönüşüm Rehberliği")
                        st.write(f"Bu dönemde {gunes_tavsiye.lower()} ve {ay_tavsiye.lower()} konularında esneklik göstermek, zihinsel trafiğini rahatlatacaktır.")

                        st.markdown("### 5. Somatik ve Spiritüel Öneri Reçetesi")
                        if anlik_f0 > 230:
                            st.markdown("- **Kristal Desteği:** Zihinsel ve sessel sakinlik için **Lapis Lazuli** veya **Akuamarin** taşı tercih edebilirsin.")
                            st.markdown("- **Somatik Pratik:** Omuz ve boyun bölgesini esneten derin nefes çalışmalarıyla boğaz çakrandaki yoğunluğu dengeleyebilirsin.")
                        else:
                            st.markdown("- **Kristal Desteği:** Enerjini canlandırmak ve köklenmek için **Hematit** veya **Onyx** taşı kullanabilirsin.")
                            st.markdown("- **Somatik Pratik:** Topraklanma egzersizleri ve tempolu yürüyüşlerle fiziksel enerjini yukarı taşıyabilirsin.")

                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
