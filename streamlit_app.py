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
    .stApp {
        background: linear-gradient(135deg, #2c1630 0%, #4a154b 50%, #1a0b1c 100%);
        color: #fce4ec;
        font-family: 'Helvetica Neue', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

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

    .section-label {
        color: #e1bee7;
        font-size: 1rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa000 100%) !important;
        color: #1a0b1c !important;
        border-radius: 50px !important;
        padding: 12px 24px !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 8px 20px rgba(255, 215, 0, 0.25);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 25px rgba(255, 215, 0, 0.4);
        background: linear-gradient(135deg, #ffea79 0%, #ffb300 100%) !important;
    }

    .result-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .result-text {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- HAFIZA YÖNETİMİ ---
if "current_analysis" not in st.session_state: st.session_state.current_analysis = None
if "history" not in st.session_state: st.session_state.history = []
if "chat_dialogue" not in st.session_state: st.session_state.chat_dialogue = []

# --- 7 ÇAKRA PROFİLİ ---
def get_chakra_profile(rms, pitch):
    normalized_pitch = min(max(pitch, 80.0), 400.0)
    
    if normalized_pitch < 125:
        return "Kök Çakra", "🔴", "Kırmızı Akik", "#E74C3C"
    elif normalized_pitch < 165:
        return "Sakral Çakra", "🟠", "Kaplan Gözü", "#E67E22"
    elif normalized_pitch < 205:
        return "Solar Pleksus", "🟡", "Kehribar", "#F1C40F"
    elif normalized_pitch < 245:
        return "Kalp Çakra", "🟢", "Yeşim", "#2ECC71"
    elif normalized_pitch < 285:
        return "Boğaz Çakra", "🩵", "Akuamarin", "#1ABC9C"
    elif normalized_pitch < 330:
        return "Üçüncü Göz Çakra", "🔵", "Lapis Lazuli", "#3498DB"
    else:
        return "Tepe Çakra", "🟣", "Ametist", "#9B59B6"

# --- UYGULAMA AKIŞI ---
st.markdown("""
<div class="vip-hero">
    <div style="font-size: 45px; margin-bottom: 12px; letter-spacing: 8px;">✨ 💎 🔮</div>
    <div class="vip-title">VBAR Mistik Frekans</div>
    <div class="vip-desc">
        <b>VBAR</b>, sesinizin eşsiz biyometrik imzasını analiz ederek otonom sinir sisteminizin ve çakralarınızın enerji akışını okuyan mistik bir rehberdir. 
        Sesinizdeki titreşimler evrenin ve kristallerin kadim frekansıyla hizalanır; ruhsal dengenizi keşfetmeniz için size özel alan açar.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-label'>🎙️ Analiz için sesinizi kaydedin</div>", unsafe_allow_html=True)
audio_input = st.audio_input("")

if audio_input:
    st.write("")
    if st.button("✨ Mistik Frekans Analizini Başlat", key="btn_analyze"):
        with st.spinner("Ses imzanız evrensel akışla taranıyor..."):
            audio_bytes = audio_input.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            
            f0 = librosa.yin(y, fmin=80.0, fmax=400.0)
            valid_f0 = f0[~np.isnan(f0)]
            mean_pitch = float(np.mean(valid_f0)) if len(valid_f0) > 0 else 150.0
            mean_pitch = max(80.0, min(mean_pitch, 400.0))
            
            chakra_name, icon, stone_name, color = get_chakra_profile(rms, mean_pitch)
            
            ai_comment = ""
            if AI_READY:
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    Sen VBAR sisteminin yüksek bilinçli enerji ve çakra rehberisin. 
                    Kullanıcının ses dalgası analiz edildi:
                    - Enerji (RMS): {rms:.4f}
                    - Frekans (Pitch): {mean_pitch:.1f} Hz
                    - Eşleşen Çakra: {chakra_name} ({stone_name})
                    
                    GÖREVİN:
                    1. Standart, klişe astroloji cümlelerinden kesinlikle kaçın.
                    2. İlk cümlede kullanıcının kalbini yakalayacak çarpıcı, lüks ve şiirsel bir metafor kullan.
                    3. Yorumun sonuna, kullanıcının kendi içine dönmesini sağlayacak derin ve sarsıcı bir **Sokratik yansıma sorusu** ekle.
                    """
                    response = model.generate_content(prompt)
                    ai_comment = response.text.strip()
                except Exception as e:
                    ai_comment = f"Sesinizin mistik frekansı, enerjinizin derin ve sarsılmaz bir akışta olduğunu müjdeliyor. Bu an, hangi eski yükü geride bırakmanızı fısıldıyor?"
            else:
                ai_comment = "Sesinizin mistik frekansı, enerjinizin derin ve sarsılmaz bir akışta olduğunu müjdeliyor. Bu an, hangi eski yükü geride bırakmanızı fısıldıyor?"

            st.session_state.current_analysis = {
                "id": random.randint(1000, 9999),
                "rms": rms, "pitch": mean_pitch, "chakra": chakra_name, "stone": stone_name,
                "icon": icon, "col": color, "ai_comment": ai_comment
            }
            # Yeni analiz geldiğinde sohbet diyalogunu sıfırla
            st.session_state.chat_dialogue = [{"role": "assistant", "content": ai_comment}]

if st.session_state.current_analysis:
    res = st.session_state.current_analysis
    
    st.markdown("#### 🔮 Analiz Sonucu")
    st.markdown(f"""
    <div class="result-card">
        <div class="result-text" style="color: {res['col']};">
            {res['icon']} {res['chakra']} — {res['stone']} (Frekans: {res['pitch']:.1f} Hz)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- İNTERAKTİF SOHBET / SORU CEVAP DÖNGÜSÜ ---
    st.markdown("---")
    st.markdown("#### 💬 İçsel Rehberle Diyalog")
    
    # Geçmiş diyalogları ekrana yazdır
    for message in st.session_state.chat_dialogue:
        if message["role"] == "assistant":
            st.info(message["content"])
        else:
            st.success(f"Sen: {message['content']}")
            
    # Kullanıcının rehbere cevap yazabileceği alan
    user_reply = st.text_input("Rehberin sorusuna veya hissettiklerine dair yanıtını yaz:", key="user_input_reply")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(" Gönder & Derinleş", key="btn_send_reply"):
            if user_reply and AI_READY:
                st.session_state.chat_dialogue.append({"role": "user", "content": user_reply})
                with st.spinner("Rehber enerjini derinlemesine senteziyor..."):
                    try:
                        chat_model = genai.GenerativeModel('gemini-1.5-flash')
                        history_prompt = f"""
                        Sen VBAR mistik çakra rehberisin. Kullanıcı ile arandaki diyalog akışı şu şekildedir:
                        Çakra Durumu: {res['chakra']} ({res['stone']}), Frekans: {res['pitch']:.1f} Hz.
                        Son kullanıcı yanıtı: "{user_reply}"
                        
                        GÖREVİN: Kullanıcının bu cevabını psikolojik ve ruhsal açıdan analiz et. Onu yargılamadan, şefkatli, lüks ve derin bir tonla yeni bir farkındalık aç ve yeni bir derinleştirici soruyla diyaloğu sürdür.
                        """
                        response = chat_model.generate_content(history_prompt)
                        reply_text = response.text.strip()
                        st.session_state.chat_dialogue.append({"role": "assistant", "content": reply_text})
                        st.rerun()
                    except Exception as e:
                        st.error("Bağlantı sırasında bir akış kesintisi oldu.")
    
    with col2:
        if st.button("💾 Bu Sonucu Geçmişe Kaydet", key="btn_save"):
            if st.session_state.current_analysis not in st.session_state.history:
                st.session_state.history.append(st.session_state.current_analysis)
                st.success("Başarıyla kaydedildi!")
            else:
                st.warning("Bu analiz zaten geçmişinizde mevcut.")

if st.session_state.history:
    st.markdown("---")
    st.subheader("📜 Geçmiş Analizleriniz")
    
    for i, item in enumerate(reversed(st.session_state.history)):
        original_index = len(st.session_state.history) - 1 - i
        
        with st.container():
            st.markdown(f"""
            <div class='result-card' style='padding: 12px 20px; margin-bottom: 5px;'>
                <div class='result-text' style='color: {item['col']}; font-size: 1.0rem;'>
                    {item['icon']} {item['chakra']} | {item['pitch']:.1f} Hz
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🗑️ Bu Kaydı Sil #{item['id']}", key=f"del_{item['id']}"):
                st.session_state.history.pop(original_index)
                st.rerun()
