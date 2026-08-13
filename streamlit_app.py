import streamlit as st
import librosa
import numpy as np
import io

st.set_page_config(page_title="VBAR - Ses Zindelik Analizi", page_icon="🎙️")
st.title("🎙️ Ses Zindelik Analizi")

audio_file = st.audio_input("Mikrofonla Kayıt Yapın")
if not audio_file:
    audio_file = st.file_uploader("Veya Ses Dosyası Yükleyin", type=["wav", "mp3", "m4a", "ogg"])

if audio_file:
    st.audio(audio_file)
    if st.button("Analiz Et"):
        with st.spinner("İşleniyor..."):
            audio_bytes = audio_file.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            rms_energy = float(np.mean(librosa.feature.rms(y=y)))
            score = min(100, int((rms_energy * 1000 * 0.35) + 42))
            st.metric("Zindelik Skoru", f"{score} / 100")
            
