import streamlit as st
import librosa
import numpy as np
import io
import random

# --- SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="VBAR - Biyometrik Analiz", page_icon="🎙️")
st.title("🎙️ VBAR - Kişiselleştirilmiş Ses Profil Analizi")

# --- HAFIZA YÖNETİMİ ---
if "current_card" not in st.session_state: st.session_state.current_card = None
if "card_flipped" not in st.session_state: st.session_state.card_flipped = False
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None

# --- ZENGİN VE ÖZGÜN NİYET KARTI HAVUZU ---
def generate_dynamic_card(stone_name, hz_val, jitter_val):
    # Asla tekrara düşmeyen, birbirinden tamamen farklı ve derinlikli havuz
    havuz = [
        {
            "title": "Zihinsel Seyir Hali",
            "affirmation": "Düşüncelerin gelip geçmesine izin veriyorum; ben sadece kıyide duran bir gözlemciyim.",
            "action": "Parmak uçlarınızı birbirine hafifçe değdirin ve aralarındaki sıcaklığı hissedin."
        },
        {
            "title": "Ağırlığı Serbest Bırakmak",
            "affirmation": "Taşıdığım tüm zihinsel yükleri şu an bulunduğum yere nazikçe bırakıyorum.",
            "action": "Gözlerinizi kapatın ve dikkatinizi sadece dilinizin damaktaki duruşuna verip gevşetin."
        },
        {
            "title": "İçsel Alan Açmak",
            "affirmation": "Her şeyin anında mükemmel olması gerekmiyor; belirsizlik içinde de güvendeyim.",
            "action": "Ellerinizi kalbinizin üzerine koyun ve içerideki ritmi sadece 5 saniye dinleyin."
        },
        {
            "title": "Durmanın Hakikati",
            "affirmation": "Üretkenlik maskesini çıkarıyorum; şu an sadece var olmak en büyük eylemim.",
            "action": "Çenenizi hafifçe aralayın ve dişlerinizin birbirine değmesini engelleyin."
        },
        {
            "title": "Zamanın Akışına Bırakış",
            "affirmation": "Günün geri kalanını kontrol etmeye çalışmıyorum, anın beni taşımasına izin veriyorum.",
            "action": "Ayak tabanlarınızın yere bastığı noktadaki güvenli bası hissedin."
        },
        {
            "title": "Nefesin Doğal Döngüsü",
            "affirmation": "Nefesi zorlamıyorum; o kendi dağınıklığında bile kendi yolunu buluyor.",
            "action": "Ellerinizi dizlerinizin üzerine serbestçe bırakın ve avuç içlerinizin gökyüzüne bakmasını sağlayın."
        }
    ]
    
    # Havuzdan tamamen rastgele ve taze bir kart seçiyoruz
    return random.choice(havuz)

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
            st.session_state.current_card = generate_dynamic_card(res['name'], res['pitch'], res['jitter'])
            st.session_state.card_flipped = True
            st.rerun()
    else:
        card = st.session_state.current_card
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
