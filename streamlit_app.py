import streamlit as st
import librosa
import numpy as np
import io
import google.generativeai as genai
import json

# ==========================================
# 1. AYARLAR VE SES TAKİP MEKANİZMASI
# ==========================================
st.set_page_config(page_title="VBAR - Biyometrik Analiz", page_icon="🎙️")

if "profiles" not in st.session_state: st.session_state.profiles = {}
if "current_card" not in st.session_state: st.session_state.current_card = None
if "card_flipped" not in st.session_state: st.session_state.card_flipped = False
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None
if "last_input_id" not in st.session_state: st.session_state.last_input_id = None

st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")

# ==========================================
# 2. GEMINI NİYET KARTI (DETAYLI)
# ==========================================
def generate_dynamic_card(stone_mode, stone_name, hz_val, jitter_val, status_text):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Sen vokal biyometri uzmanısın. Kullanıcının durumu: {stone_name}, Frekans: {hz_val:.1f}Hz, Titreşim: {jitter_val:.4f}.
            Kullanıcıya şefkatli bir niyet kartı hazırla.
            JSON formatında: {{"title": "...", "affirmation": "...", "action": "..."}}
            """
            response = model.generate_content(prompt)
            return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except:
        return {"title": "Denge", "affirmation": "Şu an güvendesin.", "action": "Derin bir nefes al."}

# ==========================================
# 3. ANALİZ VE GÖRÜNTÜLEME
# ==========================================
audio_value = st.audio_input("Analiz edilecek sesinizi kaydedin", key="analysis_input")
uploaded_file = st.file_uploader("Veya dosya yükleyin", type=["wav", "mp3"])
target_audio = audio_value or uploaded_file

# --- AKILLI SIFIRLAMA ---
current_input_id = str(id(target_audio))
if target_audio and current_input_id != st.session_state.last_input_id:
    st.session_state.analysis_results = None
    st.session_state.current_card = None
    st.session_state.card_flipped = False
    st.session_state.last_input_id = current_input_id
    st.rerun()

if target_audio and st.session_state.analysis_results is None:
    if st.button("Biyometrik Analiz Et", type="primary"):
        with st.spinner("Ses verisi işleniyor..."):
            y, sr = librosa.load(io.BytesIO(target_audio.read()), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            jitter = 0.02
            
            # Taş Mantığı
            if rms < 0.04: mode, name, col, icon = "onyx", "Oniks & Hematit", "#7F8C8D", "🖤"
            else: mode, name, col, icon = "aquamarine", "Akuamarin", "#1ABC9C", "🩵"
            
            st.session_state.analysis_results = {"rms": rms, "pitch": pitch, "jitter": jitter, "mode": mode, "name": name, "col": col, "icon": icon}
            st.rerun()

# --- SONUÇLAR VE METRİKLER ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    
    # Metrikleri Geri Getirdik
    c1, c2, c3 = st.columns(3)
    c1.metric("Pitch", f"{res['pitch']:.1f}Hz")
    c2.metric("Jitter", f"{res['jitter']:.4f}")
    c3.metric("Enerji", f"{res['rms']:.4f}")
    
    st.subheader(f"{res['icon']} Analiz: **{res['name']}**")
    
    if not st.session_state.card_flipped:
        if st.button(f"🔮 {res['name']} Niyet Kartını Aç", use_container_width=True):
            st.session_state.current_card = generate_dynamic_card(res['mode'], res['name'], res['pitch'], res['jitter'], "Aktif")
            st.session_state.card_flipped = True
            st.rerun()
    else:
        card = st.session_state.current_card
        st.markdown(f"""
        <div style="border: 2px solid {res['col']}; padding: 20px; border-radius: 16px; background: rgba(0,0,0,0.03);">
            <h3 style="color:{res['col']};">{card['title']}</h3>
            <p style="font-size: 1.1em;">"{card['affirmation']}"</p>
            <div style="background:{res['col']}33; padding:10px; border-radius:8px;">💡 <b>Eylem:</b> {card['action']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Kartı Kapat / Yeni Analiz"):
            st.session_state.card_flipped = False
            st.rerun()
        
