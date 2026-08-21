import streamlit as st
import librosa
import numpy as np
import io
import noisereduce as nr
import os

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | VBAR", layout="centered", page_icon="🏛️")

# LOGO EKLEME
if os.path.exists("1783526207831.png"):
    st.image("1783526207831.png", width=200)

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Bütünsel Ses, Enerji ve Farkındalık Analizi")

# SOMATİK KAYIT BÖLÜMÜ
st.markdown("---")
st.subheader("🧘 Somatik Uyum Alanı")
if os.path.exists("rahatlama .mp3"):
    st.audio("rahatlama .mp3", format="audio/mp3")
    st.caption("Analize başlamadan önce bu somatik ses kaydı ile merkezlenebilirsiniz.")
else:
    st.warning("Somatik ses kaydı dosyası (rahatlama .mp3) bulunamadı.")

# --- KULLANICI GİRDİLERİ ---
with st.container(border=True):
    st.subheader("✨ Doğum Haritası / Astrolojik Altyapı")
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1: gun = st.number_input("Gün", 1, 31, 29)
    with col_b2: ay = st.selectbox("Ay", ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"], 11)
    with col_b3: yil = st.number_input("Yıl", 1940, 2015, 1984)
    burc = st.selectbox("Güneş Burcunuz", ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], 9)

st.markdown("---")

# SES VERİSİ
upload_option = st.radio("Ses Verisi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle"])
audio_bytes = None

if upload_option == "Mikrofon ile Kayıt Yap":
    audio_file = st.audio_input("Lütfen konuşun")
    if audio_file: audio_bytes = audio_file.read()
else:
    uploaded_file = st.file_uploader("Ses dosyanızı seçin", type=["mp3", "wav", "m4a"])
    if uploaded_file: audio_bytes = uploaded_file.read()

if audio_bytes:
    if st.button("✨ Akustik ve Bütünsel Analizi Başlat"):
        with st.spinner("Analiz ediliyor..."):
            try:
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                
                with st.container(border=True):
                    st.subheader("🔬 Akustik Biyometrik Rapor")
                    st.metric("Ortalama Frekans", f"{anlik_f0:.1f} Hz")
                    
                    # ELEMENT ANALİZİ
                    elements = {"Koç":"Ateş", "Aslan":"Ateş", "Yay":"Ateş", "Boğa":"Toprak", "Başak":"Toprak", "Oğlak":"Toprak", "İkizler":"Hava", "Terazi":"Hava", "Kova":"Hava", "Yengeç":"Su", "Akrep":"Su", "Balık":"Su"}
                    element = elements.get(burc, "Toprak")
                    
                    st.markdown(f"**Burç & Element:** {burc} ({element})")
                    tas = {"Ateş": "Obsidyen", "Toprak": "Onyx", "Hava": "Labradorit", "Su": "Akuamarin"}[element]
                    st.markdown(f"**Önerilen Taş:** {tas}")
                    st.markdown(f"**Rehberlik:** Ses titreşiminiz {anlik_f0:.1f} Hz seviyesinde. {element} elementinin dengeleyici enerjisini hissetmek için {tas} taşını yanınızda taşıyabilirsiniz.")
            except Exception as e:
                st.error(f"Hata: {e}")
