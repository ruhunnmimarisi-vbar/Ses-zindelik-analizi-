import streamlit as st
import librosa
import numpy as np
import io
import os
import noisereduce as nr

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Ruhun Mimarisi | Bütünsel Farkındalık Sentezi", layout="centered", page_icon="🏛️")

st.title("🏛️ Ruhun Mimarisi | VBAR")
st.subheader("Ses Kaydı ve Enerji Analizi")

# Mobil tarayıcılar için güvenli dosya / ses alma yöntemi
upload_option = st.radio("Veri Sağlama Yöntemi:", ["Mikrofon ile Kayıt Yap", "Ses Dosyası Yükle"], key="veri_saglama_yontemi")
audio_bytes = None

if upload_option == "Mikrofon ile Kayıt Yap":
    audio_file = st.audio_input("Lütfen konuşun", key="mobil_mikrofon_input")
    if audio_file is not None:
        audio_bytes = audio_file.read()
else:
    uploaded_file = st.file_uploader("Ses dosyanızı seçin", type=["mp3", "wav", "m4a"], key="dosya_yukleme_input")
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()

st.markdown("---")

if audio_bytes is not None:
    if st.button("✨ Akustik Analizi Başlat", key="analiz_baslat_btn"):
        with st.spinner("Ses dalgalarınız analiz ediliyor..."):
            try:
                # Ses Analizi
                y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
                y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.7)
                pitches, _ = librosa.piptrack(y=y_denoised, sr=sr, fmin=80, fmax=400)
                anlik_f0 = float(np.nanmean(pitches[pitches > 0])) if np.any(pitches > 0) else 210.0
                gerilim = float((np.mean(librosa.feature.rms(y=y_denoised)) * 50) + (np.mean(librosa.feature.spectral_centroid(y=y_denoised, sr=sr)) / 400))

                with st.container(border=True):
                    st.subheader("🔬 Akustik Biyometrik Rapor")
                    st.metric("Ortalama Ses Frekansı (F0)", f"{anlik_f0:.1f} Hz")
                    st.metric("Gerilim / Enerji İndeksi", f"{gerilim:.2f}")
                    st.write(f"Sesinizin {anlik_f0:.1f} Hz seviyesindeki titreşimi, içsel ritminiz ve enerji akışınız hakkında önemli ipuçları sunuyor.")

            except Exception as e:
                st.error(f"Hata oluştu: {e}")
