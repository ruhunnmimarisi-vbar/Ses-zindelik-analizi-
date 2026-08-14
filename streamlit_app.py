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
st.set_page_config(page_title="VBAR - Kişisel Enerji & Koçluk Rehberi", page_icon="🎙️")

# --- ÖZEL TASARIM ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fce4ec 0%, #f8bbd0 50%, #f48fb1 100%);
        color: #3e2723;
    }
    h1 { color: #880e4f; text-align: center; }
    .stButton>button {
        background-color: #c2185b; color: white; border-radius: 12px;
        border: none; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- BAŞLIK VE AÇIKLAMA ---
st.markdown("<h1>VBAR Biyometrik Enerji Rehberi</h1>", unsafe_allow_html=True)

with st.expander("✨ VBAR Nedir?", expanded=True):
    st.markdown("""
    **VBAR**, sesinizin frekansını analiz ederek çakra sisteminizle hizalanan bir farkındalık alanıdır.
    * **Ses Analizi:** Sesiniz taranır ve enerji merkeziniz tespit edilir.
    * **Size Özel Niyet:** Analiz sonucunuza göre özel niyet kartı oluşturulur.
    * **Birebir Rehberlik:** Ruhunnmimarisi@gmail.com üzerinden iletişime geçebilirsiniz.
    """)

# --- GÜNCELLENMİŞ ÇAKRA EŞİKLERİ (SEZGİSEL TONUNUZ İÇİN) ---
def get_chakra_profile(rms, pitch):
    if pitch < 100 or rms < 0.015:
        return "Kök Çakra (Muladhara)", "🔴", "Kırmızı Akik", "#C0392B", "Dünya ile bağ, fiziksel güven, köklenme ve aidiyetin merkezidir."
    elif pitch < 140:
        return "Sakral Çakra (Svadhisthana)", "🟠", "Kaplan Gözü", "#E67E22", "Duygu akışı, yaratım enerjisi ve yaşam coşkusunun merkezidir."
    elif pitch < 180:
        return "Solar Pleksus (Manipura)", "🟡", "Kehribar", "#F1C40F", "Özdeğer, irade, özgüven ve bireysel gücün merkezidir."
    elif pitch < 250:
        return "Kalp Çakra (Anahata)", "🟢", "Yeşim", "#27AE60", "Koşulsuz sevgi, şefkat, merhamet ve içsel dengenin merkezidir."
    elif pitch < 350:
        return "Boğaz Çakra (Vishuddha)", "🩵", "Akuamarin", "#1ABC9C", "Hakikat, ilahi ifade, sesin özgürce ve dürüstçe akışının merkezidir."
    elif pitch < 600: # Sezgisel tonunuz için burayı genişlettik
        return "Üçüncü Göz Çakra (Ajna)", "🔵", "Lapis Lazuli", "#2980B9", "Sezgi, içsel bilgelik, ötesini görebilme ve idrakin merkezidir."
    else:
        return "Tepe Çakra (Sahasrara)", "🟣", "Ametist", "#8E44AD", "İlahi olanla bağ, saf bilinç, evrensel birlik ve Hakikat ile bütünleşme merkezidir."

def generate_dynamic_card(chakra_name, stone_name):
    havuz = [
        {"title": "İlahi Akış", "affirmation": "Evrenin akışına güveniyorum.", "action": "Derin bir nefes alın."},
        {"title": "Saf Bilinç", "affirmation": "Özümdeki huzuru seçiyorum.", "action": "Gözlerinizi kapatın."},
        {"title": "Hakikat", "affirmation": "İç sesimi duyuyorum.", "action": "Kalbinize odaklanın."}
    ]
    return random.choice(havuz)

if "analysis_results" not in st.session_state: st.session_state.analysis_results = None

st.markdown("🎤 **Analiz için mikrofona dokunun:**")
audio_input = st.audio_input("")

if audio_input:
    if st.button("Analizi Başlat"):
        audio_bytes = audio_input.read()
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        rms = float(np.mean(librosa.feature.rms(y=y)))
        pitches, _ = librosa.piptrack(y=y, sr=sr)
        mean_pitch = float(np.mean(pitches[pitches > 0])) if len(pitches[pitches > 0]) > 0 else 150.0
        
        chakra_name, icon, stone_name, color, chakra_desc = get_chakra_profile(rms, mean_pitch)
        
        st.session_state.analysis_results = {
            "chakra": chakra_name, "icon": icon, "stone": stone_name, "desc": chakra_desc, "col": color
        }
        st.rerun()

if st.session_state.analysis_results:
    res = st.session_state.analysis_results
    st.markdown(f"## {res['icon']} {res['chakra']} — {res['stone']} Frekansı")
    st.info(res['desc'])
    
    if st.button("🔄 Tekrar Dene"):
        st.session_state.analysis_results = None
        st.rerun()
