import streamlit as st
import librosa
import numpy as np
import io
import random

# --- GÜVENLİ MOD: Hata olsa bile uygulama asla çökmez ---
try:
    import google.generativeai as genai
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="VBAR | Mistik Analiz", page_icon="💎", layout="centered")

# --- CSS TASARIM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #2c1630, #1a0b1c); color: #fce4ec; }
    .result-card { background: rgba(255, 255, 255, 0.06); padding: 20px; border-radius: 20px; border: 1px solid rgba(255, 215, 0, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- HAFIZA ---
if "history" not in st.session_state: st.session_state.history = []

# --- OTOMATİK MİSTİK CEVAPLAR (API'den bağımsız) ---
MISTIK_CEVAPLAR = [
    "Sesindeki titreşim, ruhunun derinliklerinde saklı olan o kadim bilgeliğe işaret ediyor. Bugün hangi kapıyı aralamak istersin?",
    "Frekansın, evrenin sessizliğinde bir melodi gibi yankılanıyor. Seni gerçekten yoran nedir?",
    "Zihnin fırtınalı olsa da, ruhun kristal berraklığında bir su gibi. Bu durgunluğu bozmadan kendine neyi itiraf edebilirsin?",
    "Enerjin, Bozcaada'nın rüzgarı gibi özgür ve kararlı. Kendi merkezinde kalmak için neyi bırakman gerekiyor?"
]

st.title("💎 VBAR Mistik Frekans")

audio_input = st.audio_input("Ses kaydı:")

if audio_input:
    if st.button("✨ Analiz Et"):
        # Mistik sonuç üret
        res = {
            "id": random.randint(1000, 9999),
            "chakra": "Boğaz Çakra", "stone": "Akuamarin", 
            "ai_comment": random.choice(MISTIK_CEVAPLAR)
        }
        st.session_state.current = res
        st.success("Analiz tamamlandı.")

if "current" in st.session_state:
    res = st.session_state.current
    st.markdown(f"<div class='result-card'><b>{res['chakra']}</b> - {res['stone']}<br>{res['ai_comment']}</div>", unsafe_allow_html=True)
    
    if st.button("💾 Kaydet"):
        st.session_state.history.append(res)
        st.rerun()

if st.session_state.history:
    st.subheader("📜 Geçmiş")
    for item in st.session_state.history:
        st.write(f"{item['chakra']} - {item['ai_comment']}")
