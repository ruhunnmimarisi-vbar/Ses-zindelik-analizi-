import streamlit as st
import librosa
import numpy as np
import io
import random
import google.generativeai as genai

# --- API VE MODEL AYARLARI ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    AI_READY = True
except Exception:
    AI_READY = False

st.set_page_config(page_title="VBAR | VIP Mistik Deneyim", page_icon="💎", layout="centered")

# --- CSS TASARIM ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #2c1630 0%, #4a154b 50%, #1a0b1c 100%); color: #fce4ec;}
    .vip-hero {background: rgba(255, 255, 255, 0.04); backdrop-filter: blur(20px); border: 1px solid rgba(255, 215, 0, 0.25); padding: 35px 20px; border-radius: 30px; text-align: center; margin-bottom: 25px;}
    .result-card {background: rgba(255, 255, 255, 0.06); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.15); padding: 20px; border-radius: 20px; margin-bottom: 15px;}
    div.stButton > button {background: linear-gradient(135deg, #ffd700 0%, #ffa000 100%); color: #1a0b1c !important; border-radius: 50px !important; font-weight: 700 !important; width: 100%;}
</style>
""", unsafe_allow_html=True)

# --- HAFIZA YÖNETİMİ ---
if "history" not in st.session_state: st.session_state.history = []

# --- ANALİZ MANTIĞI (Önceki fonksiyonlarınız aynı) ---
def get_chakra_profile(rms, pitch):
    if pitch < 180: return "Kök Çakra", "🔴", "Kırmızı Akik", "#E74C3C"
    elif pitch < 270: return "Sakral Çakra", "🟠", "Kaplan Gözü", "#E67E22"
    elif pitch < 360: return "Solar Pleksus", "🟡", "Kehribar", "#F1C40F"
    elif pitch < 450: return "Kalp Çakra", "🟢", "Yeşim", "#2ECC71"
    elif pitch < 540: return "Boğaz Çakra", "🩵", "Akuamarin", "#1ABC9C"
    elif pitch < 650: return "Üçüncü Göz Çakra", "🔵", "Lapis Lazuli", "#3498DB"
    else: return "Tepe Çakra", "🟣", "Ametist", "#9B59B6"

# --- UYGULAMA AKIŞI ---
st.markdown("<div class='vip-hero'><h2>✨ VBAR Mistik Frekans</h2></div>", unsafe_allow_html=True)

audio_input = st.audio_input("🎙️ Analiz için sesinizi kaydedin")

if audio_input:
    if st.button("✨ Analizi Kaydet"):
        audio_bytes = audio_input.read()
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        rms = float(np.mean(librosa.feature.rms(y=y)))
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
        
        c_name, icon, stone, col = get_chakra_profile(rms, mean_pitch)
        
        # Analizi geçmişe ekle
        yeni_kayit = {"id": random.randint(1000, 9999), "c": c_name, "i": icon, "s": stone, "f": mean_pitch}
        st.session_state.history.append(yeni_kayit)
        st.rerun()

# --- GEÇMİŞİ LİSTELE VE SİL ---
if st.session_state.history:
    st.markdown("---")
    st.subheader("🔮 Geçmiş Analizleriniz")
    
    for i, item in enumerate(st.session_state.history):
        with st.container():
            st.markdown(f"""<div class='result-card'>
                <b>{item['i']} {item['c']}</b> | Frekans: {item['f']:.1f} Hz
            </div>""", unsafe_allow_html=True)
            
            if st.button(f"🗑️ Bu kaydı sil", key=f"del_{item['id']}"):
                st.session_state.history.pop(i)
                st.rerun()
