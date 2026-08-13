import streamlit as st
import librosa
import numpy as np
import io
import google.generativeai as genai
import json

st.set_page_config(page_title="VBAR - Biyometrik Analiz", page_icon="🎙️")

# Session state reset
if "current_card" not in st.session_state: st.session_state.current_card = None
if "card_flipped" not in st.session_state: st.session_state.card_flipped = False
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None

st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")

# Ses Girdileri
audio_value = st.audio_input("Analiz edilecek sesinizi kaydedin", key="a1")
uploaded_file = st.file_uploader("Veya dosya yükleyin", type=["wav", "mp3"], key="u1")
target_audio = audio_value or uploaded_file

# --- ANALİZ MANTIĞI ---
if target_audio:
    # "Analiz Et" Butonu
    if st.button("🔍 SESİ ANALİZ ET", type="primary", use_container_width=True):
        with st.spinner("İşleniyor..."):
            y, sr = librosa.load(io.BytesIO(target_audio.read()), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            if rms < 0.04: mode, name, col, icon = "onyx", "Oniks & Hematit", "#7F8C8D", "🖤"
            else: mode, name, col, icon = "aquamarine", "Akuamarin", "#1ABC9C", "🩵"
            
            st.session_state.analysis_results = {"rms": rms, "pitch": pitch, "mode": mode, "name": name, "col": col, "icon": icon}
            st.rerun()

# Sonuç Ekranı
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    st.success(f"Analiz Tamamlandı: {res['icon']} {res['name']}")
    
    if st.button("🔮 Niyet Kartını Aç", use_container_width=True):
        st.session_state.card_flipped = True
        st.rerun()
        
    if st.session_state.card_flipped:
        st.markdown(f"""
        <div style="border: 2px solid {res['col']}; padding: 20px; border-radius: 16px;">
            <h3>Sana Özel Niyet</h3>
            <p>Taşın: {res['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Sıfırla"):
            st.session_state.analysis_results = None
            st.session_state.card_flipped = False
            st.rerun()
