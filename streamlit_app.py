import streamlit as st
import librosa
import numpy as np
import io
from google import genai

# --- API VE MODEL BAĞLANTISI ---
# Anahtar artık kodun içinde değil, Streamlit'in gizli kasasından çekiliyor
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="VBAR - Biyometrik Analiz", page_icon="🎙️")
st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")

# --- HAFIZA YÖNETİMİ ---
if "current_card" not in st.session_state: st.session_state.current_card = None
if "card_flipped" not in st.session_state: st.session_state.card_flipped = False
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None

# --- YAPAY ZEKA İLE DİNAMİK NİYET KARTI ÜRETME ---
def generate_ai_card(stone_name, hz_val, jitter_val):
    prompt = f"""
    Sen ruhsal rehberlik ve kişisel gelişim konusunda uzman bir asistansın.
    Kullanıcının sesi analiz edildi:
    - Eşleştiği Doğal Taş: {stone_name}
    - Ses Frekansı: {hz_val:.1f} Hz
    
    Bu verilere dayanarak kullanıcının anlık enerjisine uygun, derin ve özgün bir niyet kartı üret.
    Format şu şekilde olsun:
    BAŞLIK: [Başlık]
    NİYET: [Derin niyet cümlesi]
    EYLEM: [Somut eylem önerisi]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text
        lines = text.strip().split('\n')
        title, affirmation, action = "İçsel Denge", "Anın tadını çıkar.", "Derin nefes al."
        
        for line in lines:
            if line.startswith("BAŞLIK:"): title = line.replace("BAŞLIK:", "").strip()
            elif line.startswith("NİYET:"): affirmation = line.replace("NİYET:", "").strip()
            elif line.startswith("EYLEM:"): action = line.replace("EYLEM:", "").strip()
        return {"title": title, "affirmation": affirmation, "action": action}
    except:
        return {"title": "Denge", "affirmation": "Şu an güvendesin.", "action": "Derin bir nefes al."}

# --- ANALİZ MANTIĞI (Aynı kalıyor) ---
audio_input = st.audio_input("Analiz edilecek sesinizi kaydedin")
if audio_input:
    if st.button("🔍 Analizi Başlat", type="primary", use_container_width=True):
        y, sr = librosa.load(io.BytesIO(audio_input.read()), sr=16000)
        rms = float(np.mean(librosa.feature.rms(y=y)))
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
        
        if rms < 0.04: name, col, icon = "Oniks & Hematit", "#7F8C8D", "🖤"
        else: name, col, icon = "Akuamarin", "#1ABC9C", "🩵"
        
        st.session_state.analysis_results = {"pitch": mean_pitch, "name": name, "col": col, "icon": icon}
        st.rerun()

if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    st.markdown(f"### {res['icon']} Eşleşme: **{res['name']}**")
    if not st.session_state.card_flipped:
        if st.button("🔮 Niyet Kartını Üret"):
            st.session_state.current_card = generate_ai_card(res['name'], res['pitch'], 0.02)
            st.session_state.card_flipped = True
            st.rerun()
    else:
        card = st.session_state.current_card
        st.markdown(f"""
        <div style="border: 2px solid {res['col']}; padding: 20px; border-radius: 16px;">
            <h3>{card['title']}</h3>
            <p>"{card['affirmation']}"</p>
            <div style="background:{res['col']}33; padding:10px;">💡 <b>Eylem:</b> {card['action']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Tekrar"):
            st.session_state.analysis_results = None
            st.session_state.card_flipped = False
            st.rerun()
        
