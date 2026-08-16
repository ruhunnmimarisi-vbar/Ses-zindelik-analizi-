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

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="VBAR | Akıllı Ses Analitiği", page_icon="⚡", layout="centered")

# --- GELİŞMİŞ VE OKUNABİLİR MİSTİK/TEKNİK CSS ---
st.markdown("""
<style>
    /* Arka Plan */
    .stApp {
        background: linear-gradient(135deg, #181124 0%, #2b1b3a 50%, #120919 100%);
        color: #f1f1f1;
        font-family: 'Inter', sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* TÜM YAZI VE ETİKETLERİ GÖRÜNÜR YAP */
    label, .stMarkdown, p, span, div {
        color: #fce4ec !important;
    }

    /* Karşılama Kartı */
    .hero-box {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.3);
        padding: 25px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .hero-title {
        color: #ffd700 !important;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    /* Ana Buton */
    div.stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa000 100%) !important;
        color: #120919 !important;
        border-radius: 40px !important;
        padding: 12px 20px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        width: 100%;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.3);
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #ffea79 0%, #ffb300 100%) !important;
        transform: translateY(-2px);
    }

    /* Sonuç Kartı */
    .result-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(12px);
        border-left: 4px solid #ffd700;
        border-radius: 16px;
        padding: 18px;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    
    .metrics-header {
        color: #ffd700 !important;
        font-weight: bold;
        font-size: 1.05rem;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []

# --- DİNAMİK YEDEK YORUM MOTORU (API YOKSA BİLE ASLA TEKRAR ETMEDAN YAZAR) ---
def generate_dynamic_analysis(pitch, rms):
    if pitch < 180:
        durum = "Derin, oturmuş ve kararlı bir ses yapısı."
        tavsiye = "Zihinsel netliğiniz yüksek, odağınızı koruyarak kararlarınızı hayata geçirebilirsiniz."
    elif pitch < 350:
        durum = "Dengeli, ritmik ve akıcı bir frekans aralığı."
        tavsiye = "İletişim gücünüzün ve ifade kabiliyetinizin öne çıktığı bir an."
    else:
        durum = "Yüksek dinamizme ve yoğun bir efora işaret eden frekans."
        tavsiye = "Zihninizi biraz dinlendirmek ve nefes ritminize odaklanmak dengenizi tazeleyecektir."
        
    enerji_durumu = "Enerji ivmeniz oldukça belirgin." if rms > 0.05 else "Enerji akışınız sakin ve içsel bir seyirde."
    
    return f"{durum} {enerji_durumu} {tavsiye}"

# --- UYGULAMA AKIŞI ---

st.markdown("""
<div class="hero-box">
    <div class="hero-title">⚡ VBAR Biyometrik Ses & Frekans Analizi</div>
    <div style="font-size: 0.95rem; opacity: 0.9;">Sesinizin frekans ve enerji parametreleri gerçek zamanlı taranır.</div>
</div>
""", unsafe_allow_html=True)

# Görünür Başlık
st.markdown("<p style='font-weight: 600; font-size: 1.1rem; color: #ffd700 !important; margin-bottom: 5px;'>🎙️ Analiz İçin Sesinizi Kaydedin:</p>", unsafe_allow_html=True)
audio_input = st.audio_input("")

if audio_input:
    st.write("")
    if st.button("🚀 Ses Analizini Başlat", key="btn_run"):
        with st.spinner("Ses verileriniz işleniyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            pitches, _ = librosa.piptrack(y=y, sr=sr)
            mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
            
            yorum = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Kullanıcının ses analizi sonuçları:
                    - Temel Frekans (Pitch): {mean_pitch:.1f} Hz
                    - Ses Enerjisi (RMS): {rms:.4f}
                    
                    GÖREVİN:
                    Ezberlenmiş, jenerik kalıplardan uzak dur. Bu sesin temel frekansı ve enerjisine dayanarak kişinin zihinsel odaklanma, sakinlik veya efor durumunu 2-3 cümlelik somut, akıcı ve özgün bir dille yorumla.
                    """
                    resp = model.generate_content(prompt)
                    yorum = resp.text.strip()
                except Exception:
                    yorum = generate_dynamic_analysis(mean_pitch, rms)
            else:
                yorum = generate_dynamic_analysis(mean_pitch, rms)

            kayit = {
                "id": random.randint(1000, 9999),
                "pitch": mean_pitch,
                "rms": rms,
                "yorum": yorum
            }
            st.session_state.history.append(kayit)
            st.rerun()

# --- GEÇMİŞ LİSTELEME ---
if st.session_state.history:
    st.markdown("---")
    st.markdown("<h3 style='color: #ffd700 !important;'>📊 Analiz Geçmişiniz</h3>", unsafe_allow_html=True)
    
    for i, item in enumerate(reversed(st.session_state.history)):
        idx = len(st.session_state.history) - 1 - i
        
        st.markdown(f"""
        <div class="result-card">
            <div class="metrics-header">Frekans: {item['pitch']:.1f} Hz | Enerji: {item['rms']:.4f}</div>
            <p style="margin: 0; line-height: 1.5;">{item['yorum']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button(f"🗑️ Kaydı Sil", key=f"del_{item['id']}"):
                st.session_state.history.pop(idx)
                st.rerun()
