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

st.markdown("""
<style>
    .stApp { background-color: #fcfbfa; color: #2c2c2c; }
    .report-card { border: 1px solid #d4af37; padding: 20px; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 15px; }
    .title-box { text-align: center; color: #1b263b; border-bottom: 2px solid #d4af37; padding-bottom: 10px; margin-bottom: 20px; }
    .astro-box { background: #fdf6e3; border-left: 4px solid #d4af37; padding: 15px; border-radius: 8px; margin-top: 15px; line-height: 1.6; }
    .ai-insight-box { background: #ffffff; border: 1.5px solid #1b263b; padding: 20px; border-radius: 12px; margin-top: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

# 1. LOGO KONTROLÜ
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)
else:
    st.markdown("<div class='title-box'><h1>🏛️ Ruhun Mimarisi | VBAR</h1></div>", unsafe_allow_html=True)

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

                    # --- GENİŞLETİLMİŞ ARKETİP VE BİLGELİK HAVUZLARI ---
                    giris_havuzu = [
                        "Sesinin tınısındaki bu anlık dalgalanma, gökyüzünün sana sunduğu potansiyel kapıların doğrudan bir yansımasıdır.",
                        "Zihnindeki kadim bilgelik ile sesinin taşıdığı fiziksel frekans, şu an ortak bir paydada buluşuyor.",
                        "Bu analiz, varlığının hem göksel mimarisini hem de sesindeki anlık titreşim gerilimini derinlemesine harmanlar.",
                        "Derinlerden gelen bu akustik akış, içsel pusulânın şu sıralar hangi odak noktasına kilitlendiğini ele veriyor."
                    ]
                    secilen_giris = random.choice(giris_havuzu)

                    golge_havuzu = [
                        "Aşırı odaklanma ya da kontrol etme isteği, bazen içsel akışını yavaşlatabilir; esneklik burada en büyük anahtardır.",
                        "Beklentilerin yoğunluğu ile zihinsel trafik arasında denge kurmak, enerjini doğru yere kanalize etmeni sağlayacaktır.",
                        "İçsel sesindeki yoğunluk, bazen dış dünyadan gelen uyaranlara karşı duyarlılığını artırabilir; kabulleniş şifadır."
                    ]
                    secilen_golge = random.choice(golge_havuzu)

                    # Ses Durum Yorumu
                    if gerilim > 3.5:
                        ses_durum_yorumu = "Ses enerjindeki yüksek yoğunluk ve ivme, içsel dünyandaki dönüştürücü ateşin ve eyleme geçme arzusunun dışa vurduğunu gösteriyor."
                    else:
                        ses_durum_yorumu = "Ses tonundaki sakin, yumuşak ve ölçülü frekans; enerjini stratejik bir dinginlikle koruduğunu, içsel bir sükunet inşa ettiğini yansıtıyor."

                    # Arketip Sözlükleri (Detaylı)
                    harita_metinleri = {
                        "Oğlak": "<b>Oğlak Arketipi:</b> Yapılandırma, stratejik sabır, sarsılmaz sorumluluk bilinci ve dağın zirvesine tırmanan kararlı irade.",
                        "Koç": "<b>Koç Arketipi:</b> Öncü ateş, mutlak cesaret, yenilikçi başlatma gücü ve saf irade.",
                        "Yay": "<b>Yay Arketipi:</b> Keşif tutkusu, felsefi derinlik, özgürlük arayışı ve engin bir vizyon.",
                        "Kova": "<b>Kova Arketipi:</b> Evrensel vizyon, toplumsal yenilik, entelektüel özgürlük ve futurist zihin.",
                        "Balık": "<b>Balık Arketipi:</b> Şefkat, evrensel akış, sınırsız sezgi ve ruhsal coşku.",
                        "Akrep": "<b>Akrep Arketipi:</b> Derin dönüşüm, mutlak sadakat, kriz anındaki dayanıklılık ve keskin sezgisel güç.",
                        "Boğa": "<b>Boğa Arketipi:</b> Toprağın dinginliği, kararlılık, somutlaştırma gücü ve rafine estetik değerler.",
                        "İkizler": "<b>İkizler Arketipi:</b> Zihinsel çeviklik, bilgi akışı, adaptasyon ve çok yönlü iletişim.",
                        "Yengeç": "<b>Yengeç Arketipi:</b> Derin duygusal hafıza, koruyuculuk, yuva bilinci ve sezgisel anaçlık.",
                        "Aslan": "<b>Aslan Arketipi:</b> Yaratıcı özgüven, sahne ışığı, kalpten gelen liderlik ve cömert neşe.",
                        "Başak": "<b>Başak Arketipi:</b> Analitik zeka, detaylardaki mükemmellik, hizmet bilinci ve şifa odaklı düzen.",
                        "Terazi": "<b>Terazi Arketipi:</b> İlahi denge, adalet, estetik uyum ve ilişkilerde köprü kurma yeteneği."
                    }

                    gunes_detay = harita_metinleri.get(gunes_burcu, "")
                    ay_detay = harita_metinleri.get(ay_burcu, "")

                    # --- MAKRO DETAYLI METİN ÜRETİMİ ---
                    ai_yorum = f"""
### 1. Giriş ve Bütünsel Atmosfer
{secilen_giris}

### 2. Göksel Potansiyeller ve Element Sentezi
* **Güneş Burcu ({gunes_burcu}):** Öz kimliğinin, yaşam amacının ve temel iradenin yapı taşını oluşturur. {gunes_detay}
* **Ay Burcu ({ay_burcu}):** Duygusal reflekslerinin, iç dünyandaki huzur arayışının ve sezgisel akışının merkezidir. {ay_detay}
* **Zihin ve İletişim ({merkur_burcu}) / Değerler ve Bağlar ({venus_burcu}):** Düşüncelerini ifade ediş biçimin ile hayatı kavrayış estetiğin bu iki gezegenin arketipleriyle şekillenir.

### 3. Akustik Biyometrik ve Enerjitik Analiz
* **Temel Frekans (F0):** `{anlik_f0:.1f} Hz` değerindeki bu frekans, ses tellerinin o anki fiziksel ve enerjik salınımını temsil eder.
* **Gerilim / Yoğunluk İndeksi:** `{gerilim:.2f}` seviyesi, sesindeki anlık eforu ve parlaklığı simgeler.
* **Akustik Yansıma:** {ses_durum_yorumu}

### 4. Gölge Alanlar ve Dönüşüm Rehberliği
{secilen_golge} Bu potansiyeli dengelemek için farkındalığını anın içine demirlemek oldukça kıymetlidir.

### 5. Somatik ve Spiritüel Öneri Reçetesi
* **Kristal Teması:** Enerjini dengelemek ve köklenmek için **Hematit**, **Lapis Lazuli** veya **Labradorit** taşlarıyla temas edebilirsin.
* **Nefes ve Ses Çalışması:** Diyaframını aktif kullanarak yapacağın derin nefes egzersizleri, ses frekansındaki gerilimi dengeleyerek boğaz çakrandaki akışı özgürleştirecektir.
"""

                    # Arayüze Basma
                    st.markdown(f"""
                    <div class="report-card">
                        <h3 style="color: #1b263b; margin-top: 0;">🔬 Makro Akustik Biyometrik Rapor</h3>
                        <p><b>Ortalama Ses Frekansı (F0):</b> {anlik_f0:.1f} Hz</p>
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
                        <p><b>Merkür (Zihin):</b> {merkur_burcu} | <b>Venüs (İlişkiler):</b> {venus_burcu}</p>
                        <p style="font-size: 0.9em; color: #555; margin-top: 10px;"><i>Bu rapor; doğum verilerinin ekliptik koordinatları ile sesinin anlık frekanslarının yerel algoritmayla harmanlanmasıyla üretilmiştir.</i></p>
                    </div>
                    
                    <div class="ai-insight-box">
                        <h3 style="color: #1b263b; margin-top: 0;">🏛️ Ruhun Mimarisi | Makro Bütünsel Sentez</h3>
                        {ai_yorum}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Hata oluştu: {e}")
