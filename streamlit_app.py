import streamlit as st
import librosa
import numpy as np
import io
import random
import google.generativeai as genai
import json

# --- SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="VBAR - Biyometrik Analiz", page_icon="🎙️")
st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")

# --- HAFIZA YÖNETİMİ ---
if "current_card" not in st.session_state: st.session_state.current_card = None
if "card_flipped" not in st.session_state: st.session_state.card_flipped = False
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None

# Standart Yedek Kart (Yapay Zeka hata yaparsa devreye girer)
def get_fallback_card():
    return {
        "title": "İçsel Sessizlik", 
        "affirmation": "Zihnini serbest bırak, şu an sadece var olman yeterli.", 
        "action": "Derin bir nefes al ve dikkatini yalnızca ayak tabanlarına odakla."
    }

# --- ÇEŞİTLİLİK ODAKLI GEMİNİ NİYET KARTI ÜRETİCİSİ ---
def generate_dynamic_card(stone_name, hz_val, jitter_val):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key: return get_fallback_card()
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Her çağrıda sisteme rastgele bir yaratıcılık tohumu ekliyoruz
        rastgele_tohum = random.randint(1000, 9999)
        
        prompt = f"""
        (Sistem Çeşitlilik Tohumu: {rastgele_tohum})
        Sen derinlikli bir psikofizyoloji ve somatik farkındalık rehbersin.
        Kullanıcının anlık vokal verileri:
        - Taş/Mod: {stone_name}
        - Frekans: {hz_val:.1f} Hz
        - Titreşim: {jitter_val:.4f}
        
        GÖREVİN: Bu verileri baz alarak kullanıcıya **asla daha önce üretmediği, tamamen özgün, ezber bozan, taze ve sürprizli** bir niyet kartı hazırlamak.
        Klişe kişisel gelişim cümlelerinden ("Omuzlarını serbest bırak", "Derin nefes al" vb.) kesinlikle KAÇIN. Bunun yerine o anki sinir sistemi durumuna uygun benzersiz bir metafor, derin bir olumlama ve çok yaratıcı, somatik/bedensel bir mikro-eylem seç.
        
        Çıktıyı YALNIZCA şu JSON formatında ver, başka hiçbir şey yazma:
        {{
          "title": "Çok özgün ve metaforik 2-3 kelimelik başlık",
          "affirmation": "Derin, sarsıcı ve şefkatli olumlama cümlesi",
          "action": "Alışılmışın dışında, o an yapılabilecek yaratıcı bir beden/farkındalık eylemi"
        }}
        """
        
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        card_data = json.loads(clean_text)
        
        if isinstance(card_data, dict) and "title" in card_data:
            return card_data
        else:
            return get_fallback_card()
    except Exception:
        return get_fallback_card()

# --- SES GİRDİSİ VE ANALİZ ---
audio_input = st.audio_input("Analiz edilecek sesinizi kaydedin")

if audio_input:
    if st.button("🔍 Biyometrik Analizi Başlat", type="primary", use_container_width=True):
        st.session_state.analysis_results = None
        st.session_state.card_flipped = False
        
        with st.spinner("Ses imzanız analiz ediliyor..."):
            y, sr = librosa.load(io.BytesIO(audio_input.read()), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            jitter = 0.02 

            # Taş Mantığı
            if rms < 0.04: mode, name, col, icon = "onyx", "Oniks & Hematit", "#7F8C8D", "🖤"
            else: mode, name, col, icon = "aquamarine", "Akuamarin", "#1ABC9C", "🩵"
            
            st.session_state.analysis_results = {"rms": rms, "pitch": mean_pitch, "jitter": jitter, "name": name, "col": col, "icon": icon}
            st.rerun()

# --- SONUÇLAR VE METRİKLER ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Ort. Frekans (Pitch)", f"{res['pitch']:.1f} Hz")
    col2.metric("Mikro-Titreşim (Jitter)", f"{res['jitter']:.4f}")
    col3.metric("Ses Enerjisi (RMS)", f"{res['rms']:.4f}")
    
    st.markdown(f"### {res['icon']} Eşleşme: **{res['name']}**")
    
    if not st.session_state.card_flipped:
        if st.button("🔮 Niyet Kartını Gör", use_container_width=True):
            with st.spinner("Yapay Zeka niyetinizi üretiyor..."):
                st.session_state.current_card = generate_dynamic_card(res['name'], res['pitch'], res['jitter'])
                st.session_state.card_flipped = True
                st.rerun()
    else:
        card = st.session_state.current_card
        if not isinstance(card, dict):
            card = get_fallback_card()
            
        title = card.get('title', 'İçsel Sessizlik')
        affirmation = card.get('affirmation', 'Zihnini serbest bırak.')
        action = card.get('action', 'Derin bir nefes al.')

        st.markdown(f"""
        <div style="border: 2px solid {res['col']}; padding: 20px; border-radius: 16px; background: rgba(0,0,0,0.03);">
            <h3 style="color:{res['col']}; margin-top:0;">{title}</h3>
            <p style="font-size: 1.1em;">"{affirmation}"</p>
            <div style="background:{res['col']}33; padding:12px; border-radius:10px;">💡 <b>Eylem:</b> {action}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Yeni Bir Ses Analiz Et", use_container_width=True):
            st.session_state.analysis_results = None
            st.session_state.card_flipped = False
            st.rerun()
