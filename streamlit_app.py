import streamlit as st
import librosa
import numpy as np
import io
import noisereduce as nr
import ephem
from datetime import datetime

# --- ZİYARETÇİ SAYACI ---
if 'ziyaretci_sayisi' not in st.session_state:
    st.session_state.ziyaretci_sayisi = 124
else:
    st.session_state.ziyaretci_sayisi += 1

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="VBAR - Ses Zindelik", page_icon="🔬")

st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🔬 VBAR</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>Ses ve Biyo-Astrolojik Frekans Analizi</h3>", unsafe_allow_html=True)
st.markdown("---")

# --- KULLANICI GİRİŞİ ---
with st.form("analiz_formu"):
    ad_soyad = st.text_input("Adınız Soyadınız")
    dogum_gun = st.selectbox("Doğum Günü", list(range(1, 32)), index=28)
    dogum_ay = st.selectbox("Doğum Ayı", list(range(1, 13)), index=11)
    dogum_yil = st.selectbox("Doğum Yılı", list(range(1940, 2015)), index=44)
    uploaded_file = st.file_uploader("Ses Dosyanızı Yükleyin (WAV/MP3)", type=["wav", "mp3"])
    
    submitted = st.form_submit_button("Analizi Başlat")

if submitted and uploaded_file:
    with st.spinner("Analiz ediliyor..."):
        try:
            # Ses Analizi
            audio_bytes = uploaded_file.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
            y_denoised = nr.reduce_noise(y=y, sr=sr)
            f0 = librosa.yin(y_denoised, fmin=50, fmax=500)
            f0_clean = f0[~np.isnan(f0)]
            freq = np.mean(f0_clean) if len(f0_clean) > 0 else 150
            
            # Ephem ile Burç Tespiti (Basit güneş konumu)
            date_str = f"{dogum_yil}/{dogum_ay}/{dogum_gun}"
            sun = ephem.Sun(date_str)
            burc = ephem.constellation(sun)[0]
            
            st.success("Analiz Tamamlandı!")
            st.write(f"### Merhaba {ad_soyad}")
            st.write(f"- **Ortalama Frekans:** {freq:.2f} Hz")
            st.write(f"- **Güneş Burcunuz (Kozmik):** {burc}")
            
        except Exception as e:
            st.error(f"Hata oluştu: {e}")

# --- ZİYARETÇİ SAYACI ---
st.markdown("---")
if 'ziyaretci_sayisi' in st.session_state:
    st.markdown(f"<div style='text-align: center; color: #888; font-size: 0.8em;'>🔬 VBAR | Ziyaret: {st.session_state.ziyaretci_sayisi}</div>", unsafe_allow_html=True)
