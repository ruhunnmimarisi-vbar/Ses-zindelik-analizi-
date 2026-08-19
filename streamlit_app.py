import streamlit as st
import librosa
import numpy as np
import io
import os
import urllib.parse
import noisereduce as nr
import ephem
from datetime import datetime, timedelta

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR Biyometrik Analiz", layout="centered", page_icon="🔬")

# ASTROLOJİ HESAPLAMA FONKSİYONU
def astroloji_analizi(gun, ay, yil):
    try:
        tarih_str = f"{yil}/{ay}/{gun}"
        sun = ephem.Sun(tarih_str)
        burc = ephem.constellation(sun)[0]
        # Basit astrolojik yorum promptu
        yorumlar = {
            "Aries": "Coşkulu, öncü ve mücadeleci bir enerjiye sahipsiniz. Sesinizdeki yüksek frekanslar, yaşamı hızla deneyimleme isteğinizi yansıtabilir.",
            "Taurus": "Sabırlı, kararlı ve toprak elementinin dinginliğini taşıyorsunuz. Sesinizde güven veren, tok bir tını hakim.",
            "Gemini": "Zihinsel hızınız sesinize de yansıyor; çevik, meraklı ve etkileşime açık bir enerji yaymaktasınız.",
            "Cancer": "Duygusal derinlik, sezgisellik ve koruyucu bir tını. Sesinizdeki yumuşaklık, şefkatli yanınızı ortaya koyuyor.",
            "Leo": "Sahne ışıkları sizin için var. Sesinizde dikkat çekici, canlı ve özgüvenli bir enerji dalgası hissediliyor.",
            "Virgo": "Analitik, titiz ve detaycı bir yapı. Ses tonunuzda düzen arayan ve mükemmeliyetçi bir frekans hakim.",
            "Libra": "Denge, estetik ve uyum arayışı. Sesinizde diplomatik, nazik ve birleştirici bir tonlama öne çıkıyor.",
            "Scorpio": "Tutkulu, derin ve gizemli. Sesiniz, güçlü bir içsel odaklanmayı ve dönüştürücü bir enerjiyi barındırıyor.",
            "Sagittarius": "Özgürlükçü, keşfedici ve iyimser. Sesinizde genişleyen, macera arayan bir tını hissediliyor.",
            "Capricorn": "Disiplinli, hedefe odaklı ve ciddi. Sesinizde sağlam, güvenilir ve otoriter bir frekans hakim.",
            "Aquarius": "Sıra dışı, vizyoner ve hümanist. Ses tonunuzda özgün, teknolojik ve toplumsal bir titreşim var.",
            "Pisces": "Sezgisel, hayalperest ve ruhsal. Sesinizde evrensel bir şefkat ve akışkanlık frekansı duyuluyor."
        }
        return burc, yorumlar.get(burc, "Farklı bir kozmik enerji akışı içindesiniz.")
    except:
        return "Bilinmiyor", "Kozmik veriler hesaplanırken bir hata oluştu."

# --- ARAYÜZ STİLLERİ ---
st.markdown("""
<style>
    .stApp { background-color: #fcfbfa; color: #2c2c2c; }
    .report-box { border: 1px solid #d4af37; padding: 20px; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .astro-box { background: #fdf6e3; border-left: 4px solid #d4af37; padding: 15px; border-radius: 8px; margin-top: 15px; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# GÖRSEL / BAŞLIK
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", use_container_width=True)
else:
    st.title("🔬 Ruhun Mimarisi | VBAR")

tab1, tab3, tab2 = st.tabs(["🔬 Biyometrik Analiz", "📜 Arşiv", "📖 Hakkında"])

with tab1:
    st.markdown("### Gelişmiş Spektral Akustik Analiz")
    upload_option = st.radio("Yöntem:", ["Mikrofon ile Kayıt", "Dosya Yükle"])
    audio_bytes = None
    
    if upload_option == "Mikrofon ile Kayıt":
        audio_file = st.audio_input("Sesinizi kaydedin")
        if audio_file: audio_bytes = audio_file.read()
    else:
        uploaded_file = st.file_uploader("Dosya yükleyin", type=["mp3", "wav"])
        if uploaded_file: audio_bytes = uploaded_file.read()

    # DOĞUM BİLGİLERİ (Astroloji için)
    col1, col2, col3 = st.columns(3)
    g = col1.selectbox("Gün", list(range(1, 32)), index=28)
    a = col2.selectbox("Ay", list(range(1, 13)), index=11)
    y = col3.selectbox("Yıl", list(range(1940, 2016)), index=45)

    if audio_bytes and st.button("🚀 Analizi Başlat"):
        with st.spinner("Analiz ediliyor..."):
            # Akustik Analiz
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
            pitches, _ = librosa.piptrack(y=y_denoised, sr=sr)
            f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
            
            # Astro Analiz
            burc, yorum = astroloji_analizi(g, a, y)
            
            st.markdown(f"""
            <div class="report-box">
                <h4>Akustik Rapor</h4>
                <p><b>Temel Frekans:</b> {f0:.1f} Hz</p>
            </div>
            <div class="astro-box">
                <h4>Kozmik Yansıma</h4>
                <p><b>Burcunuz:</b> {burc}</p>
                <p>{yorum}</p>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.write("Geçmiş analizleriniz burada görünecek.")

with tab3:
    st.write("VBAR: Ses spektrumu ile enerji dengesini buluşturma platformu.")
