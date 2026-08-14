import streamlit as st
import librosa
import numpy as np
import io
import random
import google.generativeai as genai

# --- API VE MODEL BAĞLANTISI ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    AI_READY = True
except Exception:
    AI_READY = False

# --- SAYFA VE SES AYARLARI ---
st.set_page_config(page_title="VBAR | VIP Mistik Deneyim", page_icon="💎", layout="centered")

# --- ULTRA VIP MİSTİK TASARIM (CSS) ---
st.markdown("""
<style>
    /* Arka Plan - Derin Mistik Gradyan */
    .stApp {
        background: linear-gradient(135deg, #2c1630 0%, #4a154b 50%, #1a0b1c 100%);
        color: #fce4ec;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Gizlenecek Streamlit Elementleri */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* VIP Karşılama Kartı */
    .vip-hero {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 215, 0, 0.25);
        padding: 35px 20px;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }
    
    .vip-title {
        color: #ffd700;
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    
    .vip-desc {
        color: #f8bbd0;
        font-size: 1.05em;
        line-height: 1.6;
        font-weight: 300;
    }

    /* Ses Kayıt Bölümü Başlığı */
    .section-label {
        color: #e1bee7;
        font-size: 1rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    /* Özel Buton Tasarımı */
    div.stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa000 100%);
        color: #1a0b1c !important;
        border-radius: 50px !important;
        padding: 14px 28px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        box-shadow: 0 8px 20px rgba(255, 215, 0, 0.25);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(255, 215, 0, 0.4);
        background: linear-gradient(135deg, #ffea79 0%, #ffb300 100%);
    }

    /* Sonuç Kartları Tasarımı */
    .result-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 25px;
        border-radius: 24px;
        margin-top: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- VIP KARŞILAMA ALANI ---
st.markdown("""
<div class="vip-hero">
    <div style="font-size: 45px; margin-bottom: 12px; letter-spacing: 8px;">✨ 💎 🔮</div>
    <div class="vip-title">VBAR Mistik Frekans</div>
    <div class="vip-desc">Sesinizin eşsiz biyometrik imzası, evrenin ve kristallerin kadim frekansıyla hizalanıyor.</div>
</div>
""", unsafe_allow_html=True)

# --- 7 ÇAKRA VE TAŞ PROFİLİ ---
def get_chakra_profile(rms, pitch):
    normalized_pitch = min(max(pitch, 80.0), 800.0)
    
    if normalized_pitch < 180:
        return "Kök Çakra (Muladhara)", "🔴", "Kırmızı Akik", "#E74C3C", "Dünya ile bağ, fiziksel güven, köklenme ve aidiyetin merkezidir."
    elif normalized_pitch < 270:
        return "Sakral Çakra (Svadhisthana)", "🟠", "Kaplan Gözü", "#E67E22", "Duygu akışı, yaratım enerjisi ve yaşam coşkusunun merkezidir."
    elif normalized_pitch < 360:
        return "Solar Pleksus (Manipura)", "🟡", "Kehribar", "#F1C40F", "Özdeğer, irade, özgüven ve bireysel gücün merkezidir."
    elif normalized_pitch < 450:
        return "Kalp Çakra (Anahata)", "🟢", "Yeşim", "#2ECC71", "Koşulsuz sevgi, şefkat, merhamet ve içsel dengenin merkezidir."
    elif normalized_pitch < 540:
        return "Boğaz Çakra (Vishuddha)", "🩵", "Akuamarin", "#1ABC9C", "Hakikat, ilahi ifade, sesin özgürce ve dürüstçe akışının merkezidir."
    elif normalized_pitch < 650:
        return "Üçüncü Göz Çakra (Ajna)", "🔵", "Lapis Lazuli", "#3498DB", "Sezgi, içsel bilgelik, ötesini görebilme ve idrakin merkezidir."
    else:
        return "Tepe Çakra (Sahasrara)", "🟣", "Ametist", "#9B59B6", "İlahi olanla bağ, saf bilinç, evrensel birlik ve Hakikat ile bütünleşme merkezidir."

# --- NİYET KARTI HAVUZU ---
def generate_dynamic_card(chakra_name, stone_name):
    havuz = [
        {
            "title": "İçsel Bilgelik ve Vizyon",
            "affirmation": "Zihnimin berraklığıyla geleceği görüyor, attığım her adımda sezgilerime güveniyorum.",
            "action": "İki kaşınızın ortasındaki odak noktasına hafifçe dokunarak derin bir nefes alın."
        },
        {
            "title": "İlahi Akış ve Özgür İfade",
            "affirmation": "Yaratıcı enerjim ve sesim, hayatıma dilediğim bolluğu ve bereketi çekiyor.",
            "action": "Gözlerinizi kapatın ve hayalini kurduğunuz o geniş kitlelerin enerjisini hissedin."
        }
    ]
    return random.choice(havuz)

# --- HAFIZA YÖNETİMİ ---
if "analysis_results" not in st.session_state: st.session_state.analysis_results = None
if "current_card" not in st.session_state: st.session_state.current_card = None

# --- SES GİRDİSİ ---
st.markdown("<div class='section-label'>🎙️ Sesinizle hizalanmak için kaydı başlatın</div>", unsafe_allow_html=True)
audio_input = st.audio_input("")

if audio_input:
    st.write("")
    if st.button("✨ Mistik Frekans Analizini Başlat"):
        with st.spinner("Ses imzanız evrensel akışla taranıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            chakra_name, icon, stone_name, color, chakra_desc = get_chakra_profile(rms, mean_pitch)
            
            ai_comment = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Sen VBAR sisteminin manevi enerji ve çakra rehberisin. 
                    Kullanıcının ses dalgası analiz edildi:
                    - Frekans: {mean_pitch:.1f} Hz
                    - Enerji Seviyesi (RMS): {rms:.4f}
                    - Eşleşen Çakra: {chakra_name} ({stone_name})

                    GÖREVİN:
                    Asla mekanik veya tekrar eden cümleler kurma. Bu çakranın ruhsal derinliğini, kişinin yaydığı enerjiyi ve potansiyeli şiirsel, lüks ve büyüleyici bir dille yorumla.
                    """
                    response = model.generate_content(prompt)
                    ai_comment = response.text
                except Exception:
                    ai_comment = f"Sesinizin taşıdığı bu özel frekans, enerjinizin ne kadar yüksek ve akışta olduğunu gösteriyor."
            else:
                ai_comment = f"Sesinizin taşıdığı bu özel frekans, enerjinizin ne kadar yüksek ve akışta olduğunu gösteriyor."

            st.session_state.analysis_results = {
                "rms": rms, "pitch": mean_pitch, "chakra": chakra_name, "stone": stone_name,
                "icon": icon, "col": color, "desc": chakra_desc, "ai_comment": ai_comment
            }
            st.session_state.current_card = generate_dynamic_card(chakra_name, stone_name)
            st.rerun()

# --- SONUÇLAR VE METRİKLER ---
if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    
    st.markdown(f"""
    <div class="result-card">
        <h2 style="color: {res['col']}; margin-top:0; font-size: 22px;">{res['icon']} {res['chakra']} — {res['stone']}</h2>
        <p style="color: #fce4ec; font-style: italic; font-size: 1.05em;">{res['desc']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Frekans", f"{res['pitch']:.1f} Hz")
    with col2:
        st.metric("Enerji (RMS)", f"{res['rms']:.4f}")
    
    st.markdown("#### 🧠 Manevi Rehberlik & Yansıma")
    st.info(res['ai_comment'])
    
    st.markdown("#### 🔮 Size Özel Niyet Kartı")
    card = st.session_state.current_card
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.05); border-left: 4px solid {res['col']}; padding: 20px; border-radius: 12px; margin-top: 10px;">
        <h4 style="color: {res['col']}; margin-top:0;">{card['title']}</h4>
        <p style="font-size: 1.05em; font-weight: 400; color:#fff;">"{card['affirmation']}"</p>
        <p style="font-size: 0.95em; color: #ffd700; margin-bottom:0;">💡 <b>Eylem:</b> {card['action']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Yeni Bir Frekans Analiz Et"):
        st.session_state.analysis_results = None
        st.rerun()

# --- İLETİŞİM / ALT BİLGİ ---
st.markdown("""
<div style="text-align:center; padding: 40px 0 20px 0; color: #b39ddb; font-size: 0.9em;">
    Derinlemesine bireysel seanslar için: <a href="mailto:Ruhunnmimarisi@gmail.com" style="color: #ffd700; text-decoration: none; font-weight: bold;">Ruhunnmimarisi@gmail.com</a>
</div>
""", unsafe_allow_html=True)
