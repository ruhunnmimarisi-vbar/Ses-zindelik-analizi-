import streamlit as st
import librosa
import numpy as np
import io
import random
import google.generativeai as genai

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    AI_READY = True
except Exception:
    AI_READY = False

st.set_page_config(page_title="VBAR | Net Ses Analitiği", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1f1c2c 0%, #928dab 100%); color: #ffffff; font-family: 'Helvetica Neue', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .hero-box {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 20px;
    }
    div.stButton > button {
        background: #ff4757 !important; color: white !important; border-radius: 30px !important;
        font-weight: bold !important; width: 100%; border: none !important; padding: 12px;
    }
    .result-box {
        background: rgba(0, 0, 0, 0.5); border-left: 5px solid #ff4757;
        padding: 20px; border-radius: 12px; margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

st.markdown("""
<div class="hero-box">
    <h2>⚡ VBAR Ses ve Enerji Analitiği</h2>
    <p>Ezberlenmiş kalıplar yok; doğrudan ses dalgalarının frekans analizi ve gerçek zamanlı metrikler var.</p>
</div>
""", unsafe_allow_html=True)

audio_input = st.audio_input("🎙️ Ses kaydını başlat ve analiz et")

if audio_input:
    if st.button("🚀 Analizi Çalıştır"):
        with st.spinner("Ses verileri işleniyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            # Gemini ile daha akıllı, teknik ve net bir yorum
            yorum = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Ses analizi yapıldı:
                    - Pitch (Frekans): {mean_pitch:.1f} Hz
                    - RMS (Enerji): {rms:.4f}
                    
                    GÖREVİN: 
                    Asla "içindeki pusula, evrenin akışı" gibi klişe laflar etme. Keslikle bu ses frekansının ve enerji seviyesinin o anki zihinsel/fiziksel yorgunluk, stres veya kararlılık durumunu ne kadar yansıttığını net, analitik, dürüst ve akıcı bir dille yorumla.
                    """
                    resp = model.generate_content(prompt)
                    yorum = resp.text.strip()
                except:
                    yorum = "Ses frekansın yüksek bir efor sergilediğini, enerji dağılımının ise odaklanma gerektirdiğini gösteriyor."
            else:
                yorum = "Ses frekansın yüksek bir efor sergilediğini gösteriyor."

            kayit = {
                "id": random.randint(1000, 9999),
                "pitch": mean_pitch,
                "rms": rms,
                "yorum": yorum
            }
            st.session_state.history.append(kayit)
            st.rerun()

if st.session_state.history:
    st.markdown("---")
    st.subheader("📊 Analiz Geçmişi")
    
    for i, item in enumerate(reversed(st.session_state.history)):
        idx = len(st.session_state.history) - 1 - i
        st.markdown(f"""
        <div class="result-box">
            <b>Frekans:</b> {item['pitch']:.1f} Hz | <b>Enerji:</b> {item['rms']:.4f}<br><br>
            <p>{item['yorum']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🗑️ Bu Kaydı Sil #{item['id']}", key=f"del_{item['id']}"):
            st.session_state.history.pop(idx)
            st.rerun()
