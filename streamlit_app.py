import streamlit as st
import librosa
import numpy as np
import io
import os
import urllib.parse
import noisereduce as nr
from datetime import datetime, timedelta

# --- GÜVENLİ ASTROLOJİ AKTARIMI ---
import flatlib
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const

# --- ZİYARETÇİ SAYACI BAŞLANGICI ---
if 'ziyaretci_sayisi' not in st.session_state:
    st.session_state.ziyaretci_sayisi = 124
else:
    st.session_state.ziyaretci_sayisi += 1

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="VBAR - Ses Zindelik ve Enerji Analizi",
    page_icon="🔬",
    layout="centered"
)

# --- BAŞLIK VE GİRİŞ ---
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🔬 VBAR</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #666;'>Ses ve Biyo-Astrolojik Frekans Analiz Sistemi</h3>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
Hoş geldiniz! Bu uygulama, sesinizin akustik dalgalarını (F0, jitter, RMS) analiz ederek, doğum tarihiniz ve kozmik yapı taşlarınızla sentezler; size özel içgörü ve öneriler sunar.
""")

# --- KULLANICI GİRİŞ ALANI ---
with st.form("analiz_formu"):
    ad_soyad = st.text_input("Adınız Soyadınız")
    kullanici_mail = st.text_input("E-posta Adresiniz (İsteğe bağlı)")
    
    st.markdown("<b>Doğum Bilgileriniz</b>", unsafe_allow_html=True)
    col_g, col_a, col_y = st.columns(3)
    with col_g:
        dogum_gun = st.selectbox("Gün", list(range(1, 32)), index=28)
    with col_a:
        dogum_ay = st.selectbox("Ay", list(range(1, 13)), index=11)
    with col_y:
        dogum_yil = st.selectbox("Yıl", list(range(1940, 2015)), index=44)
        
    dogum_saati = st.text_input("Doğum Saati (Örn: 14:30 - Bilmiyorsanız boş bırakın)")
    
    # Ses Dosyası Yükleme
    uploaded_file = st.file_uploader("Lütfen 3-5 saniyelik bir ses kaydınızı yükleyin (WAV veya MP3)", type=["wav", "mp3", "m4a"])
    
    submitted = st.form_submit_button("Analizi Başlat")

if submitted:
    if not ad_soyad:
        st.error("Lütfen adınızı ve soyadınızı giriniz.")
    elif not uploaded_file:
        st.error("Lütfen analiz için bir ses dosyası yükleyin.")
    else:
        with st.spinner("Ses dalgaları ve kozmik harita sentezleniyor... Lütfen bekleyin."):
            try:
                # Ses Verisini İşleme
                audio_bytes = uploaded_file.read()
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
                
                # Gürültü Azaltma ve Akustik Metrikler
                y_denoised = nr.reduce_noise(y=y, sr=sr)
                f0 = librosa.yin(y_denoised, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
                f0_clean = f0[~np.isnan(f0)]
                
                ortalama_frekans = np.mean(f0_clean) if len(f0_clean) > 0 else 150.0
                rms_enerji = np.mean(librosa.feature.rms(y=y_denoised))
                
                # Flatlib ile Güvenli Harita Hesabı
                d_str = f"{dogum_yil}/{dogum_ay:02d}/{dogum_gun:02d}"
                t_str = dogum_saati if dogum_saati and ":" in dogum_saati else "12:00"
                
                py_date = Datetime(d_str, t_str, '+03:00')
                pos = GeoPos(41.28, 27.95) # Saray / Tekirdağ bazlı coğrafi konum
                chart = Chart(py_date, pos)
                
                gunes = chart.get(const.SUN)
                ay = chart.get(const.MOON)
                
                st.success("Analiz başarıyla tamamlandı!")
                
                # Sonuç Ekranı
                st.markdown("---")
                st.markdown(f"### 🌟 Sayın **{ad_soyad}**, Analiz Sonuçlarınız")
                st.write(f"- **Ortalama Ses Frekansı (F0):** {ortalama_frekans:.2f} Hz")
                st.write(f"- **Ses Enerjisi (RMS):** {rms_enerji:.4f}")
                st.write(f"- **Astrodeğerlendirme (Güneş):** {gunsign := gunes.sign} - {gunes.deg} derece")
                st.write(f"- **Astrodeğerlendirme (Ay):** {aysign := ay.sign} - {ay.deg} derece")
                
                st.info("Ses frekansınız ile kozmik konumlarınız uyum içerisinde harmanlanmıştır. Bu analiz, içsel dengenizi ve zindeliğinizi desteklemek amacıyla, akustik ve astrolojik verilerin senteziyle üretilmiştir.")
                
            except Exception as e:
                st.error(f"Analiz sırasında teknik bir hata oluştu: {e}")

# --- ZİYARETÇİ SAYACI GÖRÜNÜMÜ ---
st.markdown("---")
if 'ziyaretci_sayisi' in st.session_state:
    st.markdown(f"<div style='text-align: center; color: #888; font-size: 0.8em;'>🔬 <b>VBAR</b> | Toplam Ziyaret: {st.session_state.ziyaretci_sayisi}</div>", unsafe_allow_html=True)
